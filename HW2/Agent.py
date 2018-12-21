# Standard Libs
import socket
import random

# Local Libs
from utils import parse_args, receive_and_unpack


args = parse_args()

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as agentSocket:
    agentSocket.bind((args.agent_ip, args.agent_port))


    def send_packet(isAck, packet):
        if isAck:
            agentSocket.sendto(packet, (args.sender_ip, args.sender_port))
        else:
            agentSocket.sendto(packet, (args.receiver_ip, args.receiver_port))


    packet_cnt, loss_cnt = 0, 0

    while True:
        length, seqNum, ackNum, fin, syn, ack, rawPacket, address, packet = \
            receive_and_unpack(agentSocket, args, sendOrg=True)
        if address[0] == args.sender_ip and address[1] == args.sender_port:
            packet_cnt += 1
            if fin == 1:
                print('get\tfin')
                send_packet(0, packet)
                print('fwd\tfin')
            else:
                if random.random() < args.loss_rate:
                    loss_cnt += 1
                    print('drop\tdata\t#{},\tloss rate = {:4f}'.format(seqNum, loss_cnt / packet_cnt))
                else:
                    print('get\tdata\t#{}'.format(seqNum))
                    send_packet(0, packet)
                    print('fwd\tdata\t#{},\tloss rate = {:4f}'.format(seqNum, loss_cnt / packet_cnt))

        elif address[0] == args.receiver_ip and address[1] == args.receiver_port:
            if fin == 1:
                print('get\tfinack')
                send_packet(1, packet)
                print('fwd\tfinack')
                break
            else:
                print('get\tack\t#{}'.format(ackNum))
                send_packet(1, packet)
                print('fwd\tack\t#{}'.format(ackNum))
