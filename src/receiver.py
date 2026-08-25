import socket
import logging 

from pydantic import ValidationError

from .telemetryData import telemetryData


UDP_IP = "127.0.0.1"
UDP_PORT = 5005
BUFFER_SIZE = 1024
START_SEQUENCE = 1
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)


def main() -> None:
    # Track sequence state independently for each UAV
    highest: dict[str, int] = {}
    missingSequence: dict[str, set[int]] = {}
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        sock.bind((UDP_IP, UDP_PORT))
        logger.info("Server started and waiting for data...")

        while True:
            data, addr = sock.recvfrom(BUFFER_SIZE)

            try:
                handlePacket(data, highest, missingSequence)
            except ValidationError as e:
                logger.warning(
                    "Rejected invalid telemetry packet | Source=%s | Error=%s",
                    addr,
                    e.errors()[0]["msg"],
                    )
    except KeyboardInterrupt:
        logger.info("Shutdown requested")

    finally:
        sock.close()
        logger.info("Server stopped")


def handlePacket(
    data: bytes,
    highest: dict[str, int],
    missingSequence: dict[str, set[int]]
) -> None:
    packet = telemetryData.model_validate_json(data)

    logger.debug("%s", packet)

    # Initialize state for a newly observed UAV
    if packet.deviceName not in highest:
        missingSequence[packet.deviceName] = set()

        if packet.sequence > START_SEQUENCE:
            missingSequence[packet.deviceName].update(
                range(START_SEQUENCE, packet.sequence)
            )

            logger.warning(
                "Initial sequence gap | UAV=%s | Expected=%d | Received=%d",
                packet.deviceName,
                START_SEQUENCE,
                packet.sequence,
                )

        highest[packet.deviceName] = packet.sequence

    # A jump forward means one or more packets were missed
    elif packet.sequence > highest[packet.deviceName] + 1:
        expectedSequence = highest[packet.deviceName] + 1

        logger.warning(
            "Sequence gap | UAV=%s | Expected=%d | Received=%d",
            packet.deviceName,
            expectedSequence,
            packet.sequence,
        )

        missingSequence[packet.deviceName].update(
            range(
                highest[packet.deviceName] + 1,
                packet.sequence
            )
        )

        highest[packet.deviceName] = packet.sequence

    # A previously missing packet arrived late
    elif packet.sequence in missingSequence[packet.deviceName]:
        logger.warning(
            "Late packet received | UAV=%s | Seq=%d",
            packet.deviceName,
            packet.sequence,
        )
        missingSequence[packet.deviceName].remove(packet.sequence)

    # Normal in-order packet.
    elif packet.sequence == highest[packet.deviceName] + 1:
        highest[packet.deviceName] = packet.sequence

    # Any remaining sequence has already been received
    else:
        logger.warning(
            "Duplicate packet received | UAV=%s | Seq=%d",
            packet.deviceName,
            packet.sequence,
        )

if __name__ == "__main__":
    main()