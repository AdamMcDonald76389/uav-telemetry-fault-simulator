# simulator for uav. currently only sends data to receiver via simple message
import telemetryData
import socket
import json
def main():
    UDP_IP = "127.0.0.1"
    UDP_PORT = 5005

    data = {
        "deviceName": "UAV-001",
        "sequence": 1,
        "altitude": 5000,
        "speed": 240.1

    }

    packet = telemetryData.telemetryData(**data)
    print(packet)
    
    print("Sending message to receiver")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Internet, UDP
    encodeAndSend(packet, sock, (UDP_IP, UDP_PORT))

#function to encode and send data to receiver using JSON
def encodeAndSend(packet : telemetryData, sock: socket.socket, targetAddress: tuple):
    
    # message serialized and then encoded 
    data = packet.model_dump_json()
    dataBytes = data.encode("utf-8")

    # send to receiver
    sock.sendto(dataBytes, targetAddress)
    




if __name__ == "__main__":
    main()