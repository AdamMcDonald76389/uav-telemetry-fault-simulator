import logging
import socket

from src import receiver, simulator
from src.telemetryData import telemetryData


def sendAndHandle(
    packet: telemetryData,
    sendSock: socket.socket,
    receiveSock: socket.socket,
    targetAddress: tuple[str, int],
    highest: dict[str, int],
    missingSequence: dict[str, set[int]],
) -> None:
    """Send one telemetry packet over real UDP and process it with the receiver."""
    simulator.encodeAndSend(packet, sendSock, targetAddress)
    data, _ = receiveSock.recvfrom(receiver.BUFFER_SIZE)
    receiver.handlePacket(data, highest, missingSequence)


def testUdpSendReceive(caplog):
    highest: dict[str, int] = {}
    missingSequence: dict[str, set[int]] = {}

    receiveSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sendSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        receiveSock.bind(("127.0.0.1", 0))
        receiveSock.settimeout(1.0)
        targetAddress = receiveSock.getsockname()

        packet = telemetryData(
            deviceName="UAV-001",
            sequence=1,
            altitude=5000,
            speed=300,
        )

        caplog.set_level(logging.DEBUG, logger=receiver.__name__)

        sendAndHandle(
            packet,
            sendSock,
            receiveSock,
            targetAddress,
            highest,
            missingSequence,
        )

        assert highest["UAV-001"] == 1
        assert missingSequence["UAV-001"] == set()
        assert "UAV-001" in caplog.text

    finally:
        sendSock.close()
        receiveSock.close()


def testUdpSequenceTracking(caplog):
    highest: dict[str, int] = {}
    missingSequence: dict[str, set[int]] = {}

    receiveSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sendSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        receiveSock.bind(("127.0.0.1", 0))
        receiveSock.settimeout(1.0)
        targetAddress = receiveSock.getsockname()

        packet1 = telemetryData(
            deviceName="UAV-001",
            sequence=1,
            altitude=5000,
            speed=300,
        )
        packet3 = telemetryData(
            deviceName="UAV-001",
            sequence=3,
            altitude=5010,
            speed=302,
        )
        packet2 = telemetryData(
            deviceName="UAV-001",
            sequence=2,
            altitude=5005,
            speed=301,
        )

        caplog.set_level(logging.WARNING, logger=receiver.__name__)

        # Receive the first packet normally.
        sendAndHandle(
            packet1,
            sendSock,
            receiveSock,
            targetAddress,
            highest,
            missingSequence,
        )

        assert highest["UAV-001"] == 1
        assert missingSequence["UAV-001"] == set()

        # Skip sequence 2. The receiver should record it as missing.
        sendAndHandle(
            packet3,
            sendSock,
            receiveSock,
            targetAddress,
            highest,
            missingSequence,
        )

        assert highest["UAV-001"] == 3
        assert missingSequence["UAV-001"] == {2}
        assert "Sequence gap" in caplog.text
        assert "UAV=UAV-001" in caplog.text
        assert "Expected=2" in caplog.text
        assert "Received=3" in caplog.text

        # Sequence 2 then arrives late and should clear the missing entry.
        sendAndHandle(
            packet2,
            sendSock,
            receiveSock,
            targetAddress,
            highest,
            missingSequence,
        )

        assert highest["UAV-001"] == 3
        assert missingSequence["UAV-001"] == set()
        assert "Late packet received" in caplog.text
        assert "Seq=2" in caplog.text

    finally:
        sendSock.close()
        receiveSock.close()


def testUdpMultiUavIndependentState(caplog):
    highest: dict[str, int] = {}
    missingSequence: dict[str, set[int]] = {}

    receiveSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sendSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        receiveSock.bind(("127.0.0.1", 0))
        receiveSock.settimeout(1.0)
        targetAddress = receiveSock.getsockname()

        uav1Sequence1 = telemetryData(
            deviceName="UAV-001",
            sequence=1,
            altitude=5000,
            speed=300,
        )
        uav2Sequence1 = telemetryData(
            deviceName="UAV-002",
            sequence=1,
            altitude=7000,
            speed=250,
        )
        uav1Sequence3 = telemetryData(
            deviceName="UAV-001",
            sequence=3,
            altitude=5020,
            speed=304,
        )
        uav2Sequence2 = telemetryData(
            deviceName="UAV-002",
            sequence=2,
            altitude=7010,
            speed=252,
        )
        uav1Sequence2 = telemetryData(
            deviceName="UAV-001",
            sequence=2,
            altitude=5010,
            speed=302,
        )

        caplog.set_level(logging.WARNING, logger=receiver.__name__)

        sendAndHandle(
            uav1Sequence1,
            sendSock,
            receiveSock,
            targetAddress,
            highest,
            missingSequence,
        )
        sendAndHandle(
            uav2Sequence1,
            sendSock,
            receiveSock,
            targetAddress,
            highest,
            missingSequence,
        )
        sendAndHandle(
            uav1Sequence3,
            sendSock,
            receiveSock,
            targetAddress,
            highest,
            missingSequence,
        )

        # UAV-001 has a gap, while UAV-002's state remains unaffected.
        assert highest["UAV-001"] == 3
        assert missingSequence["UAV-001"] == {2}
        assert highest["UAV-002"] == 1
        assert missingSequence["UAV-002"] == set()
        assert "Sequence gap | UAV=UAV-001 | Expected=2 | Received=3" in caplog.text

        sendAndHandle(
            uav2Sequence2,
            sendSock,
            receiveSock,
            targetAddress,
            highest,
            missingSequence,
        )

        # UAV-002 advances normally and does not alter UAV-001's missing state.
        assert highest["UAV-002"] == 2
        assert missingSequence["UAV-002"] == set()
        assert missingSequence["UAV-001"] == {2}

        sendAndHandle(
            uav1Sequence2,
            sendSock,
            receiveSock,
            targetAddress,
            highest,
            missingSequence,
        )

        # UAV-001's late packet repairs only UAV-001's state.
        assert highest["UAV-001"] == 3
        assert highest["UAV-002"] == 2
        assert missingSequence["UAV-001"] == set()
        assert missingSequence["UAV-002"] == set()
        assert "Late packet received | UAV=UAV-001 | Seq=2" in caplog.text

    finally:
        sendSock.close()
        receiveSock.close()