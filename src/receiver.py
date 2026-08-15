# receiver simulator, listens for and receives packets from
# simulator
import json
import socket
import telemetryData
from pydantic import ValidationError

def main():

    #dictionary to check sequence numbers for validation
    # highest sequence number associated with current telemetry
    # compared against incoming packets
    highest: dict[str, int] = {}
    missingSequence: dict[str, set[int]] = {}
    
    
    # network vars
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
            

            # verify packet wasn't corrupted by converting into
            # telemetry and checking against strict type safety
            packet = telemetryData.telemetryData.model_validate_json(rawJson)
            printUavStats(packet)

            # first time this uav has been seen
            if packet.deviceName not in highest:
                highest[packet.deviceName] = packet.sequence
                # initialize empty set for potential missing packets later
                missingSequence[packet.deviceName] = set()

            # out of order or missing packet
            elif packet.sequence > highest[packet.deviceName] + 1:
                print(f"unexpected sequence number!: {packet.sequence}")
                for seq in range(highest[packet.deviceName] + 1, packet.sequence):
                    missingSequence[packet.deviceName].add(seq)
                highest[packet.deviceName] = packet.sequence

            elif packet.sequence in missingSequence[packet.deviceName]:
                print(f" Late packet received: {packet.sequence}")
                missingSequence[packet.deviceName].remove(packet.sequence)
            # 
            elif packet.sequence == highest[packet.deviceName] + 1:
                highest[packet.deviceName] = packet.sequence
            else:
                print(f"duplicate packet received!: {packet.sequence}")


        except ValidationError as e:
            print("Rejected invalid telemetry packet!")
            print(e)
        #except Exception as e:
        #    print("Error processing packet")


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


