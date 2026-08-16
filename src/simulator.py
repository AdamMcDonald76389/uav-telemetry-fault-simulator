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
PACKETLOSS = 0

REPEATEDCHANCE = 0.10

def main():
    global PACKETLOSS
    if len(sys.argv) == 2:
        PACKETLOSS = float(sys.argv[1]) 
        if not 0.0 <= PACKETLOSS <= 1.0:
            print("Error, invalid packet loss entered")
            print("Valid values are betwen 0.0 - 1.0")
            sys.exit()
    print(PACKETLOSS)
    data = {
        "deviceName": "UAV-001",
        "sequence": 1,
        "altitude": 5000,
        "speed": 240.1

    }
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Internet, UDP
    packet = telemetryData.telemetryData(**data)
    while True:
        
        print(packet)
        
        print("Sending message to receiver")
        
        dropped = random.uniform(0, 1.0)
        repeat = random.uniform(0, 1.0)
        print(dropped)
        if dropped <= PACKETLOSS:
            print("Packet dropped!")
            updatePacket(packet)
            continue
        elif repeat <= REPEATEDCHANCE:
            encodeAndSend(packet, sock, (UDP_IP, UDP_PORT))
            continue
        else:
            encodeAndSend(packet, sock, (UDP_IP, UDP_PORT))
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



if __name__ == "__main__":
    main()