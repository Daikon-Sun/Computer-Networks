import argparse
import hashlib
import pickle


def parse_args():
    parser = argparse.ArgumentParser(description='TCP by UDP')
    parser.add_argument('-ai', '--agent_ip', type=str, default='127.0.0.1')
    parser.add_argument('-ap', '--agent_port', type=int, default=8888)
    parser.add_argument('-bs', '--buffer_size', type=int, default=32)
    parser.add_argument('-if', '--input_file', type=str, default='data/numbers.txt')
    parser.add_argument('-lr', '--loss_rate', type=int, default=0.05)
    parser.add_argument('-of', '--output_file', type=str, default='data/result')
    parser.add_argument('-ps', '--packet_size', type=int, default=1000)
    parser.add_argument('-ri', '--receiver_ip', type=str, default='127.0.0.1')
    parser.add_argument('-rp', '--receiver_port', type=int, default=8889)
    parser.add_argument('-si', '--sender_ip', type=str, default='127.0.0.1')
    parser.add_argument('-sp', '--sender_port', type=int, default=8887)
    parser.add_argument('-th', '--threshold', type=int, default=16)
    parser.add_argument('-to', '--time_out', type=int, default=1)

    args = parser.parse_args()
    args.output_file += args.input_file[args.input_file.rfind('.'):]
    return args


def pack(length, seqNum, ackNum, fin, syn, ack, rawPacket):
    return length.to_bytes(4, 'little', signed=True) \
         + seqNum.to_bytes(4, 'little', signed=True) \
         + ackNum.to_bytes(4, 'little', signed=True) \
         +    fin.to_bytes(4, 'little', signed=True) \
         +    syn.to_bytes(4, 'little', signed=True) \
         +    ack.to_bytes(4, 'little', signed=True) + rawPacket


def unpack(packet):
    length = int.from_bytes(packet[:4],    'little', signed=True)
    seqNum = int.from_bytes(packet[4:8],   'little', signed=True)
    ackNum = int.from_bytes(packet[8:12],  'little', signed=True)
    fin    = int.from_bytes(packet[12:16], 'little', signed=True)
    syn    = int.from_bytes(packet[16:20], 'little', signed=True)
    ack    = int.from_bytes(packet[20:24], 'little', signed=True)
    rawPacket = packet[24:]
    return length, seqNum, ackNum, fin, syn, ack, rawPacket


def receive_and_unpack(socket, args, sendOrg=False):
    packet, address = socket.recvfrom(args.packet_size << 1)
    length, seqNum, ackNum, fin, syn, ack, rawPacket = unpack(packet)
    if sendOrg:
        return length, seqNum, ackNum, fin, syn, ack, rawPacket, address, packet
    else:
        return length, seqNum, ackNum, fin, syn, ack, rawPacket, address


def send_to_agent(socket, packet, args):
    socket.sendto(packet, (args.agent_ip, args.agent_port))
