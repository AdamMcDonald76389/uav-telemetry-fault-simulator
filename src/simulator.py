import socket

UDP_IP = "127.0.0.1"
UDP_PORT = 5005
MESSAGE = b"Received!"


print("Sending message to receiver")
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Internet, UDP
sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))

