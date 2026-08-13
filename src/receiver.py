# receiver simulator, listens for and receives packets from
# simulator
import json
import socket

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Internet, #UDP

sock.bind((UDP_IP, UDP_PORT))
print("Server started and waiting for data...")

while True:
    data, addr = sock.recvfrom(1024) # buffer size max for testing
    print(f"received message from client {data}")
