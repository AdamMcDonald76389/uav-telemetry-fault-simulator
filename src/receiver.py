# receiver simulator, listens for and receives packets from
# simulator
import json
import socket
import telemetryData
from pydantic import ValidationError

def main():
    UDP_IP = "127.0.0.1"
    UDP_PORT = 5005

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Internet, #UDP

    sock.bind((UDP_IP, UDP_PORT))
    print("Server started and waiting for data...")

    # receive raw bytes, convert to json and then to custom class
    # validates that no corruption occured to data during transfer
    while True:
        data, addr = sock.recvfrom(1024) # buffer size max for testing
        try:
            rawJson = data.decode("utf-8")
            print(f"received JSON from client {data}")

            # verify packet wasn't curropted by converting into
            # telemetry and checking against strict type safety
            packet = telemetryData.telemetryData.model_validate_json(rawJson)
            print(packet)

        except ValidationError as e:
            print("Rejected invalid telemetry packet!")

        except Exception as e:
            print("Error processing packet")




if __name__ == "__main__":
    main()