# Standard Libs
import time
import socket
import select

# Local Libs
from utils import load_packets, parse_args, send_to_agent, unpack


args = parse_args()

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as senderSocket:
    # senderSocket.setblocking(False)
    senderSocket.bind((args.sender_ip, args.sender_port))
    print('Sender bind to {}, {}'.format(args.sender_ip, args.sender_port))

    packets = load_packets(args.filename, args.packet_size)

    def send_packet(num):
        packet = packets[num]
        send_to_agent(senderSocket, packet, args)
        if packet[0] == -1:
            print('send   fin')
        else:
            print('send   data   #{},   winSize = {}'.format(nxtSeqNum+1, windowLen))

    base = nxtSeqNum = 0
    windowLen = 1
    lastAckTime = time.time()

    while base < len(packets):

        if nxtSeqNum < base + windowLen:
            send_packet(nxtSeqNum)
            nxtSeqNum += 1

        if lastAckTime - time.time() > args.time_out:
            args.threshold = max(windowLen // 2, 1)
            windowLen = 1
            send_packet(base)
            lastAckTime = time.time()

        ready = select.select([senderSocket], [], [], 0)[0]
        if len(ready) > 0:
            seqNum, rawPacket, agentAddress, corrupt = receive_and_unpack(senderSocket, args)
            if corrupt:
                print('corrupted')
            else:
                if rawPacket[0] == -1:
                    print('recv   finack')
                    base += 1
                else:
                    print('recv   ack    #{}'.format(rawPacket[0]))
                    lastAckTime = time.time()

