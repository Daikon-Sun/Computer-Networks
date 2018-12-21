# Standard Libs
import socket

# Local Libs
from utils import parse_args, send_to_agent, pack, receive_and_unpack


args = parse_args()

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as receiverSocket:
    receiverSocket.bind((args.receiver_ip, args.receiver_port))

    expectedSeqNum = 1
    bufs = []

    def send_ack():
        packet = pack(0, ackNum, expectedSeqNum-1, expectedSeqNum==0, 0, 1, b'')
        send_to_agent(receiverSocket, packet, args)

    with open(args.output_file, 'wb') as output_f:
        while expectedSeqNum != 0:
            length, seqNum, ackNum, fin, syn, ack, rawPacket, agentAddress = \
                receive_and_unpack(receiverSocket, args)
            if fin:
                print('recv\tfin')
                expectedSeqNum = 0
                send_ack()
                print('send\tfinack')
            elif seqNum == expectedSeqNum and len(bufs) < args.buffer_size:
                print('recv\tdata\t#{}'.format(expectedSeqNum))
                expectedSeqNum += 1
                bufs.append(rawPacket)
                send_ack()
                print('send\tack\t#{}'.format(expectedSeqNum-1))
            else:
                print('drop\tdata\t#{}'.format(seqNum))
                send_ack()
                print('send\tack\t#{}'.format(expectedSeqNum-1))
                if len(bufs) == args.buffer_size:
                    print('flush')
                    output_f.write(b''.join(bufs))
                    bufs = []
        if len(bufs) > 0:
            print('flush')
            output_f.write(b''.join(bufs))
