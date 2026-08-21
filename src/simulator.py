# simulator for uav. currently only sends data to receiver via simple message
from telemetryData import telemetryData
import socket
import time
import random
import sys
import argparse

# fixed network consants
UDP_IP = "127.0.0.1"
UDP_PORT = 5005

def main():

    args = parseArguments()

    print(f"Packet loss: {args.packet_loss}")
    print(f"Repeat chance: {args.repeat_chance}")
    print(f"Hold chance: {args.hold_chance}")
    print(f"Corruption rate: {args.corruption_rate}")
    print(f"UAVs: {args.uavs}")



    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Internet, UDP
    held = {} # for held packets
    packets = []
    for i in range(1, args.uavs + 1):
        packets.append(createUAV(i))
    for packet in packets:
        held.setdefault(packet.deviceName, {})
    while True:
        for packet in packets:
            processPacket(packet, held, sock, args)

            updatePacket(packet)
        time.sleep(1)   

#function to encode and send data to receiver using JSON
def encodeAndSend(packet: telemetryData, sock: socket.socket, targetAddress: tuple):
    
    # turn telemetry data into JSON->Bytes
    data = packet.model_dump_json()
    dataBytes = data.encode("utf-8")

    # send to receiver
    sock.sendto(dataBytes, targetAddress)
    

#update data involving packet to simulate telemtry
def updatePacket(packet : telemetryData):
    packet.sequence += 1
    packet.altitude += random.randint(-20, 20)
    packet.speed += random.uniform(-5, 5)

# function to process packets 
# process packets and uses conditionals for
# determing simulated network faults
def processPacket(packet, held, sock, args):
    dropped = random.random()
    repeat = random.random()
    hold = random.random()
    corrupt = random.random()
    sentCurrentPacket = False
    
    # drop packet
    if dropped < args.packet_loss:
        print(f"Packet {packet.sequence} dropped!")

    # repeat send packet twice
    elif repeat < args.repeat_chance:
        print(f"Packet {packet.sequence} duplicated!")

        encodeAndSend(packet, sock, (UDP_IP, UDP_PORT))
        encodeAndSend(packet, sock, (UDP_IP, UDP_PORT))

        sentCurrentPacket = True
    # dont send packet and add to hold 
    elif hold < args.hold_chance:
        print(f"Holding packet {packet.sequence}")

        # redundant but argument exists whether to keep this one
        # or the code in the for loop to initialize UAVS
        
        held[packet.deviceName][packet.sequence] = packet.model_copy(deep=True)

    elif corrupt < args.corruption_rate:
        print(f"sending corrupted packet {packet.sequence}")
        sendCorrupted(packet, sock, (UDP_IP, UDP_PORT))
        sentCurrentPacket = True
    
    else:
        encodeAndSend(packet, sock, (UDP_IP, UDP_PORT))
        sentCurrentPacket = True

    # make sure to actually send a newer packet before sending
    # previously held packet
    if sentCurrentPacket and held.get(packet.deviceName):
        minseq = min(held[packet.deviceName])

        if minseq < packet.sequence:
            heldPacket = held[packet.deviceName].pop(minseq)

            print(f"Releasing held packet {minseq}")
            encodeAndSend(heldPacket, sock, (UDP_IP, UDP_PORT))

# send corrupted packets to receiver 
def sendCorrupted(packet, sock, targetAddress):

    data = packet.model_dump_json()
    dataBytes = bytearray(data.encode("utf-8"))
    
    index = random.randrange(len(dataBytes))
    dataBytes[index] ^= 0x01
    
    sock.sendto(bytes(dataBytes), targetAddress)


def createUAV(index):
    return telemetryData(
        deviceName = f"UAV-{index:03d}",
        sequence = 1,
        altitude = random.randint(5000, 25000),
        speed = random.uniform(100, 400)
    )
     
    
def parseArguments():
    parser = argparse.ArgumentParser(
        description="UAV Telemetry Fault Simulator"
    )

    parser.add_argument(
        "--packet-loss",
        type=probability,
        default=0.0,
        help="Chance of dropping a packet"
    )

    parser.add_argument(
        "--repeat-chance",
        type=probability,
        default=0.0,
        help="Chance of duplicating a packet"
    )

    parser.add_argument(
        "--hold-chance",
        type=probability,
        default=0.0,
        help="Chance of holding a packet"
    )

    parser.add_argument(
        "--corruption-rate",
        type=probability,
        default=0.0,
        help="Chance of corrupting a packet"
    )

    parser.add_argument(
        "--uavs",
        type=positiveInteger,
        default=5,
        help="Number of UAVs to simulate"
    )

    return parser.parse_args()

def probability(value):
    value = float(value)

    if not 0.0 <= value <= 1.0:
        raise argparse.ArgumentTypeError(
            "value must be between 0.0 and 1.0"
        )

    return value

def positiveInteger(value):
    value = int(value)
    if value < 1:
        raise argparse.ArgumentTypeError(
            "must have at least 1 UAV"
        )
    return value


if __name__ == "__main__":
    main()