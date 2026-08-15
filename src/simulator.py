# simulator for uav. currently only sends data to receiver via simple message
import telemetryData
import socket
import json
import time
import random

def main():
    UDP_IP = "127.0.0.1"
    UDP_PORT = 5005

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
    packet.sequence +=1
    packet.altitude += random.randint(-20, 20)
    packet.speed += random.uniform(-5, 5)



if __name__ == "__main__":
    main()