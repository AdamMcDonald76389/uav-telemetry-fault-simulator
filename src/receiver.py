# receiver simulator, listens for and receives packets from
# simulator
import socket
import telemetryData
from pydantic import ValidationError



# fixed global constants
UDP_IP = "127.0.0.1"
UDP_PORT = 5005
START_SEQUENCE = 1
def main():

    # dictionary to check sequence numbers for validation
    # highest sequence number associated with current telemetry
    # compared against incoming packets
    highest: dict[str, int] = {}
    missingSequence: dict[str, set[int]] = {}
    
    
    # network vars
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Internet, #UDP

    sock.bind((UDP_IP, UDP_PORT))
    print("Server started and waiting for data...")

    # receive raw bytes, convert to json and then to custom class
    # latter is done inside of handlePacket function
    while True:
        # adr received from recv tuple but not used
        data, _ = sock.recvfrom(1024) # buffer size max for testing
        try:
            handlePacket(data, highest, missingSequence)


        except ValidationError as e:
            print("Rejected invalid telemetry packet!")
            print(e)
        # except Exception as e:
        #    print("Error processing packet")


# prints stats about telemetry
def printUavStats(packet):
    print(
    f"{packet.deviceName} | "
    f"Seq: {packet.sequence} | "
    f"Altitude: {packet.altitude} | "
    f"Speed: {packet.speed:.2f}"
)

def handlePacket(data, highest, missingSequence):
    rawJson = data.decode("utf-8")
    
    packet = telemetryData.telemetryData.model_validate_json(rawJson)
    printUavStats(packet)

    # very first instance of this UAV
    # is added to dictionary
    # also checks for if first sequence # was dropped
    if packet.deviceName not in highest:
        missingSequence[packet.deviceName] = set()

        # gap outside of expected init sequence #
        if packet.sequence > START_SEQUENCE:
            missingSequence[packet.deviceName].update(
                range(START_SEQUENCE, packet.sequence)
            )
            print(
                f"Initial sequence gap! "
                f"Expected: {START_SEQUENCE}, "
                f"Received {packet.sequence}"
            )
        highest[packet.deviceName] = packet.sequence


    elif packet.sequence > highest[packet.deviceName] + 1:
        print(f"unexpected sequence number!: {packet.sequence}")
        for seq in range(highest[packet.deviceName] + 1, packet.sequence):
            missingSequence[packet.deviceName].add(seq)
        highest[packet.deviceName] = packet.sequence
    
    elif packet.sequence in missingSequence[packet.deviceName]:
        print(f" Late packet received: {packet.sequence}")
        missingSequence[packet.deviceName].remove(packet.sequence)
    
    elif packet.sequence == highest[packet.deviceName] + 1:
        highest[packet.deviceName] = packet.sequence
    else:
        print(f"duplicate packet received!: {packet.sequence}")




if __name__ == "__main__":
    main()


