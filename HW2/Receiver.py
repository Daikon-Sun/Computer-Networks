# Standard Libs
import time
import socket
import select

# Local Libs
from utils import parse_args, send_to_agent, pack, receive_and_unpack


args = parse_args()

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as receiverSocket:
    # receiverSocket.setblocking(False)
    receiverSocket.bind((args.receiver_ip, args.receiver_port))
    print('receiver bind to {}, {}'.format(args.receiver_ip, args.receiver_port))

    expectedSeqNum = 1
    bufs = []

    def send_ack():
        packet = pack(0, 0, expectedSeqNum-1, expectedSeqNum==0, 0, 1, b'')
        send_to_agent(receiverSocket, packet, args)

    with open(args.output_file, 'wb') as output_f:
        while expectedSeqNum != -1:
            length, seqNum, ackNum, fin, syn, ack, rawPacket, agentAddress = \
                receive_and_unpack(receiverSocket, args)
            if seqNum == -1:
                print('recv   fin')
                expectedSeqNum = 0
                send_ack()
                print('send   finack')
            elif seqNum == expectedSeqNum and len(bufs) < args.buffer_size:
                print('recv   data   #{}'.format(expectedSeqNum))
                expectedSeqNum += 1
                bufs.append(rawPacket)
                send_ack()
                print('send   ack    #{}'.format(expectedSeqNum))
            else:
                print('drop   data   #{}'.format(seqNum))
                send_ack()
                print('send   ack    #{}'.format(expectedSeqNum-1))
                if len(bufs) == args.buffer_size:
                    print('flush')
                    output_f.write(b''.join(bufs))
                    bufs = []
        output_f.write(b''.join(bufs))
