# Standard Libs
import time
import socket

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
    senderSocket.settimeout(args.time_out)
    senderSocket.bind((args.sender_ip, args.sender_port))
    # print('sender bind to {}, {}'.format(args.sender_ip, args.sender_port))

    packets = load_packets(args.input_file, args.packet_size)
    sendStatus = [False for _ in range(len(packets))]
    # print('number of packets = {}'.format(len(packets)))

    base = nxtSeqNum = 1
    windowLen = 1

    while base < len(packets):

        while nxtSeqNum < base + windowLen and nxtSeqNum < len(packets):
            packet = packets[nxtSeqNum]
            send_to_agent(senderSocket, packet, args)
            if nxtSeqNum == len(packets) - 1:
                print('send\tfin')
            else:
                print('{}\tdata\t#{},\twinSize = {}'.format('resnd' if sendStatus[nxtSeqNum] else 'send', nxtSeqNum, windowLen))
            sendStatus[nxtSeqNum] = True
            nxtSeqNum += 1

        while base < nxtSeqNum:
            try:
                length, seqNum, ackNum, fin, syn, ack, rawPacket, agentAddress = \
                    receive_and_unpack(senderSocket, args)
                if ackNum == -1:
                    print('recv\tfinack')
                    base += 1
                else:
                    print('recv\tack\t#{}'.format(ackNum))
                    base = ackNum + 1
                    if base == nxtSeqNum:
                        windowLen = windowLen * 2 if windowLen < args.threshold else windowLen + 1
            except socket.timeout:
                args.threshold = max(windowLen // 2, 1)
                print('time\tout,\tthreshold = {}'.format(args.threshold))
                windowLen = 1
                nxtSeqNum = base
                break
