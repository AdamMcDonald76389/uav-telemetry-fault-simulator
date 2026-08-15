# receiver simulator, listens for and receives packets from
# simulator
import json
import socket
import telemetryData
from pydantic import ValidationError

def main():

    #dictionary to check sequence numbers for validation
    #key = devicename, val = sequence num
    sequenceNum = {}
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
            

            # verify packet wasn't currupted by converting into
            # telemetry and checking against strict type safety
            packet = telemetryData.telemetryData.model_validate_json(rawJson)
            printUavStats(packet)
            if packet.deviceName not in sequenceNum:
                sequenceNum[packet.deviceName] = packet.sequence
            elif packet.sequence != sequenceNum[packet.deviceName] + 1:
                print("unexpected sequence number!")
            else:
                sequenceNum[packet.deviceName] +=1
                


        except ValidationError as e:
            print("Rejected invalid telemetry packet!")
            print(e)
        except Exception as e:
            print("Error processing packet")


# prints stats about telemetry
def printUavStats(packet):
    print(
    f"{packet.deviceName} | "
    f"Seq: {packet.sequence} | "
    f"Altitude: {packet.altitude} | "
    f"Speed: {packet.speed:.2f}"
)


if __name__ == "__main__":
    main()


