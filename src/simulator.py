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
    encodeAndSend(data, sock, (UDP_IP, UDP_PORT))

#function to encode and send data to receiver using JSON
def encodeAndSend(message : dict, sock: socket.socket, targetAdress: tuple):
    
    # message serialized and then encoded 
    data = json.dumps(message)
    dataBytes = data.encode("utf-8")

    # send to receiver
    sock.sendto(dataBytes, targetAdress)
    




if __name__ == "__main__":
    main()