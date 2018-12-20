import argparse
import hashlib


def pack(seqNum, rawPacket):
    hash_md5 = hashlib.md5()
    packet = [seqNum, rawPacket]
    hash_md5.update(packet)
    packet.append(hash_md5.digest())
    return packet


def unpack(packet):
    checksum = packet.pop()
    hash_md5 = hashlib.md5()
    hash_md5.update(packet)
    return seqNum, rawPacket, hash_md5.digest() != checksum


def receive_and_unpack(socket, args):
    packet, address = socket.recvfrom(args.packet_size << 1)
    seqNum, rawPacket, corrupt = unpack(packet)
    return seqNum, rawPacket, address, corrupt


def load_packets(filename, packet_size):
    packets = []
    f = open(filename, 'rb')
    seqNum = 0
    while True:
        rawPacket = f.read(packet_size)
        if rawPacket:
            packets.append(pack(seqNum, rawPacket))
        else:
            packets.append(pack(seqNum, b''))
            break
        seqNum += 1
    return packets


def parse_args():
    parser = argparse.ArgumentParser(description='TCP by UDP')
    # parser.add_argument('-ac', '--add_checksum', type=int, default=1)
    parser.add_argument('-ai', '--agent_ip', type=int, default='127.0.0.1')
    parser.add_argument('-ap', '--agent_port', type=int, default=8888)
    parser.add_argument('-bs', '--buffer_size', type=int, default=32)
    parser.add_argument('-fn', '--filename', type=str, default='./data/alphabet.txt')
    parser.add_argument('-ps', '--packet_size', type=int, default=(1<<10))
    parser.add_argument('-ri', '--receiver_ip', type=str, default='127.0.0.1')
    parser.add_argument('-rp', '--receiver_port', type=int, default=8889)
    parser.add_argument('-si', '--sender_ip', type=str, default='127.0.0.1')
    parser.add_argument('-sp', '--sender_port', type=int, default=8887)
    parser.add_argument('-th', '--threshold', type=int, default=16)
    parser.add_argument('-to', '--time_out', type=int, default=1)

    args = parser.parse_args()
    return args


def sent_to_agent(socket, packet, args):
    socket.sendto(packet, (args.agent_ip, args.agent_port))
