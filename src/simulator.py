import argparse
import random
import socket
import time
import logging

from .telemetryData import telemetryData


UDP_IP = "127.0.0.1"
UDP_PORT = 5005
TARGET_ADDRESS = (UDP_IP, UDP_PORT)
UPDATE_INTERVAL = 1


def main() -> None:
    args = parseArguments()

    print(f"Packet loss: {args.packet_loss}")
    print(f"Repeat chance: {args.repeat_chance}")
    print(f"Hold chance: {args.hold_chance}")
    print(f"Corruption rate: {args.corruption_rate}")
    print(f"UAVs: {args.uavs}")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    packets = [createUAV(i) for i in range(1, args.uavs + 1)]
    held: dict[str, dict[int, telemetryData]] = {
        packet.deviceName: {} for packet in packets
    }

    while True:
        for packet in packets:
            processPacket(packet, held, sock, args)
            updatePacket(packet)

        time.sleep(UPDATE_INTERVAL)


def encodeAndSend(
    packet: telemetryData,
    sock: socket.socket,
    targetAddress: tuple[str, int]
) -> None:
    """Serialize a telemetry packet to JSON and send it over UDP."""
    dataBytes = packet.model_dump_json().encode("utf-8")
    sock.sendto(dataBytes, targetAddress)


def updatePacket(packet: telemetryData) -> None:
    """Advance a UAV's sequence number and update its telemetry."""
    packet.sequence += 1

    # Clamp generated values to the telemetry model's valid ranges
    packet.altitude = max(
        0,
        min(
            30000,
            packet.altitude + random.randint(-20, 20)
        )
    )

    packet.speed = max(
        0.0,
        min(
            500.0,
            packet.speed + random.uniform(-5, 5)
        )
    )


def processPacket(
    packet: telemetryData,
    held: dict[str, dict[int, telemetryData]],
    sock: socket.socket,
    args: argparse.Namespace
) -> None:
    """Apply simulated network faults and transmit a telemetry packet."""
    dropped = random.random()
    repeat = random.random()
    hold = random.random()
    corrupt = random.random()

    sentCurrentPacket = False

    if dropped < args.packet_loss:
        print(f"Packet {packet.sequence} dropped!")

    elif repeat < args.repeat_chance:
        print(f"Packet {packet.sequence} duplicated!")

        encodeAndSend(packet, sock, TARGET_ADDRESS)
        encodeAndSend(packet, sock, TARGET_ADDRESS)

        sentCurrentPacket = True

    elif hold < args.hold_chance:
        print(f"Holding packet {packet.sequence}")

        # Store a copy so later telemetry updates do not modify the held packet
        held[packet.deviceName][packet.sequence] = packet.model_copy(
            deep=True
        )

    elif corrupt < args.corruption_rate:
        print(f"Sending corrupted packet {packet.sequence}")

        sendCorrupted(packet, sock, TARGET_ADDRESS)
        sentCurrentPacket = True

    else:
        encodeAndSend(packet, sock, TARGET_ADDRESS)
        sentCurrentPacket = True

    # Release the oldest held packet only after a newer packet was sent
    if sentCurrentPacket and held[packet.deviceName]:
        minSequence = min(held[packet.deviceName])

        if minSequence < packet.sequence:
            heldPacket = held[packet.deviceName].pop(minSequence)

            print(f"Releasing held packet {minSequence}")
            encodeAndSend(heldPacket, sock, TARGET_ADDRESS)


def sendCorrupted(
    packet: telemetryData,
    sock: socket.socket,
    targetAddress: tuple[str, int]
) -> None:
    """Corrupt one bit in a serialized telemetry packet before sending it."""
    dataBytes = bytearray(packet.model_dump_json().encode("utf-8"))

    index = random.randrange(len(dataBytes))
    dataBytes[index] ^= 0x01

    sock.sendto(bytes(dataBytes), targetAddress)


def createUAV(index: int) -> telemetryData:
    """Create a UAV with randomized initial telemetry."""
    return telemetryData(
        deviceName=f"UAV-{index:03d}",
        sequence=1,
        altitude=random.randint(5000, 25000),
        speed=random.uniform(100, 400)
    )


def parseArguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="UAV Telemetry Fault Simulator"
    )

    parser.add_argument(
        "--packet-loss",
        type=probability,
        default=0.0,
        help="Chance of dropping a packet"
    )

    parser.add_argument(
        "--repeat-chance",
        type=probability,
        default=0.0,
        help="Chance of duplicating a packet"
    )

    parser.add_argument(
        "--hold-chance",
        type=probability,
        default=0.0,
        help="Chance of delaying a packet for out-of-order delivery"
    )

    parser.add_argument(
        "--corruption-rate",
        type=probability,
        default=0.0,
        help="Chance of corrupting a packet"
    )

    parser.add_argument(
        "--uavs",
        type=positiveInteger,
        default=5,
        help="Number of UAVs to simulate"
    )

    return parser.parse_args()


def probability(value: str) -> float:
    value = float(value)

    if not 0.0 <= value <= 1.0:
        raise argparse.ArgumentTypeError(
            "value must be between 0.0 and 1.0"
        )

    return value


def positiveInteger(value: str) -> int:
    value = int(value)

    if not 1 <= value <= 999:
        raise argparse.ArgumentTypeError(
            "number of UAVs must be between 1 and 999"
        )

    return value


if __name__ == "__main__":
    main()