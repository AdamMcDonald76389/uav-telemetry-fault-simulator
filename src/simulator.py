# simulator for uav. currently only sends data to receiver via simple message
import telemetryData
import socket
import json
import time
import random
import sys

# fixed network consants
UDP_IP = "127.0.0.1"
UDP_PORT = 5005
# packet loss adjustable via cli on launch 
PACKETLOSS = 0.10
# chance to repeat send packets
REPEATEDCHANCE = 0.10
# chance to send packets in wrong order/hold them
HOLDCHANCE = 0.10


def main():
    global PACKETLOSS
    global REPEATEDCHANCE
    global HOLDCHANCE
    if len(sys.argv) == 2:
        PACKETLOSS = float(sys.argv[1]) 
        if not 0.0 <= PACKETLOSS <= 1.0:
            print("Error, invalid packet loss entered")
            print("Valid values are betwen 0.0 - 1.0")
            sys.exit()
    

    # data section and creating list for packets
    # allows support for multiple UAVS
    # REFACTOR THIS 
    data = []
    data.append({
        "deviceName": "UAV-001",
        "sequence": 1,
        "altitude": 5000,
        "speed": 240.1

    })
    data.append({
        "deviceName": "UAV-002",
        "sequence": 1,
        "altitude": 20000,
        "speed": 300

    })
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Internet, UDP



    # REFACTOR
    packet = telemetryData.telemetryData(**data[0])
    packets = []
    packets.append(packet)
    packet = telemetryData.telemetryData(**data[1])
    packets.append(packet)
    held = {}
    held.setdefault(packet.deviceName, {})
    while True:
        # Refactor using process packets function later
        for packet in packets:
            print(packet)

            dropped = random.random()
            repeat = random.random()
            hold = random.random()

            sentCurrentPacket = False

            if dropped < PACKETLOSS:
                print(f"Packet {packet.sequence} dropped!")

            elif repeat < REPEATEDCHANCE:
                print(f"Packet {packet.sequence} duplicated!")

                encodeAndSend(packet, sock, (UDP_IP, UDP_PORT))
                encodeAndSend(packet, sock, (UDP_IP, UDP_PORT))

                sentCurrentPacket = True

            elif hold < HOLDCHANCE:
                print(f"Holding packet {packet.sequence}")

                held.setdefault(packet.deviceName, {})
                held[packet.deviceName][packet.sequence] = packet.model_copy(deep=True)

            else:
                encodeAndSend(packet, sock, (UDP_IP, UDP_PORT))
                sentCurrentPacket = True

            # Only release an old packet after a newer packet was actually sent
            if sentCurrentPacket and held.get(packet.deviceName):
                minseq = min(held[packet.deviceName])

                # Don't accidentally release the packet we just dealt with
                if minseq < packet.sequence:
                    heldPacket = held[packet.deviceName].pop(minseq)

                    print(f"Releasing held packet {minseq}")
                    encodeAndSend(heldPacket, sock, (UDP_IP, UDP_PORT))

            updatePacket(packet)

            time.sleep(1)

#function to encode and send data to receiver using JSON
def encodeAndSend(packet : telemetryData, sock: socket.socket, targetAddress: tuple):
    
    # message serialized and then encoded 
    data = packet.model_dump_json()
    dataBytes = data.encode("utf-8")

    # send to receiver
    sock.sendto(dataBytes, targetAddress)
    

#update data involving packet to simulate telemtry
def updatePacket(packet : telemetryData):
    packet.sequence += 1
    packet.altitude += random.randint(-20, 20)
    packet.speed += random.uniform(-5, 5)


def processPacket(packet):
    pass




if __name__ == "__main__":
    main()