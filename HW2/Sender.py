# Standard Libs
import time
import socket
import select

# Local Libs
from utils import parse_args, send_to_agent, pack, receive_and_unpack


def load_packets(filename, packet_size):
    packets = [pack(0, 0, 0, 0, 0, 0, b'')]
    f = open(filename, 'rb')
    seqNum = 1
    while True:
        rawPacket = f.read(packet_size)
        if rawPacket:
            packets.append(pack(len(rawPacket), seqNum, 0, 0, 0, 0, rawPacket))
        else:
            packets.append(pack(0, -1, 0, 1, 0, 0, b''))
            break
        seqNum += 1
    return packets


args = parse_args()

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as senderSocket:
    # senderSocket.setblocking(False)
    senderSocket.bind((args.sender_ip, args.sender_port))
    print('sender bind to {}, {}'.format(args.sender_ip, args.sender_port))

    packets = load_packets(args.input_file, args.packet_size)
    print('number of packets = {}'.format(len(packets)))

    base = nxtSeqNum = 1
    windowLen = 1
    lastAckTime = None

    def send_packet(num):
        packet = packets[num]
        send_to_agent(senderSocket, packet, args)
        if num == len(packets) - 1:
            print('send   fin')
        else:
            print('send   data   #{},   winSize = {}, thres = {}'.format(nxtSeqNum, windowLen, args.threshold))

    while base < len(packets):

        if nxtSeqNum < base + windowLen:
            # print('here1')
            send_packet(nxtSeqNum)
            if base == nxtSeqNum:
                lastAckTime = time.time()
            nxtSeqNum += 1

        if time.time() - lastAckTime > args.time_out:
            # print('here2')
            args.threshold = max(windowLen // 2, 1)
            windowLen = 1
            nxtSeqNum = base
            send_packet(nxtSeqNum)
            lastAckTime = time.time()

        ready = select.select([senderSocket], [], [], 0)[0]
        if len(ready) > 0:
            # print('here3')
            length, seqNum, ackNum, fin, syn, ack, rawPacket, agentAddress = \
                receive_and_unpack(senderSocket, args)
            if ackNum == -1:
                print('recv   finack')
                base += 1
            else:
                print('recv   ack    #{}'.format(ackNum))
                newBase = ackNum + 1
                if newBase == nxtSeqNum:
                    lastAckTime = None
                    windowLen = windowLen * 2 if windowLen < args.threshold else windowLen + 1
                elif base != newBase:
                    lastAckTime = time.time()
                base = newBase

