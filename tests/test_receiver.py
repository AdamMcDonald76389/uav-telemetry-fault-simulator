# Test suite for receiver behavior

from src import receiver
from src.telemetryData import telemetryData


# Create encoded telemetry bytes for receiver tests
def bytePacket(sequence, deviceName="UAV-001"):
    packet = telemetryData(
        deviceName=deviceName,
        sequence=sequence,
        altitude=5000,
        speed=300,
    )

    data = packet.model_dump_json()
    sendData = data.encode("utf-8")

    return sendData


# Test the first correctly received packet with no anomalies
def testInitialization():
    highest: dict[str, int] = {}
    missingSequence: dict[str, set[int]] = {}

    receiver.handlePacket(
        bytePacket(1),
        highest,
        missingSequence,
    )

    assert highest["UAV-001"] == 1
    assert missingSequence["UAV-001"] == set()


# Test normal in-order packet handling after initialization
def testBaseCase():
    highest: dict[str, int] = {"UAV-001": 1}
    missingSequence: dict[str, set[int]] = {"UAV-001": set()}

    receiver.handlePacket(
        bytePacket(2),
        highest,
        missingSequence,
    )

    assert highest["UAV-001"] == 2
    assert missingSequence["UAV-001"] == set()


# Test duplicate packet handling
def testHandleDuplicate(capsys):
    highest: dict[str, int] = {"UAV-001": 1}
    missingSequence: dict[str, set[int]] = {"UAV-001": set()}

    receiver.handlePacket(
        bytePacket(1),
        highest,
        missingSequence,
    )

    captured = capsys.readouterr()

    assert "Duplicate packet received" in captured.out
    assert highest["UAV-001"] == 1
    assert missingSequence["UAV-001"] == set()


# Test handling of packets received out of order
def testHandleLate(capsys):
    highest: dict[str, int] = {"UAV-001": 4}
    missingSequence: dict[str, set[int]] = {
        "UAV-001": {1, 2, 3}
    }

    receiver.handlePacket(
        bytePacket(2),
        highest,
        missingSequence,
    )

    captured = capsys.readouterr()

    assert "Late packet received" in captured.out
    assert missingSequence["UAV-001"] == {1, 3}
    assert highest["UAV-001"] == 4


# Test when the first received packet contains an initial sequence gap
def testInitialGapInit(capsys):
    highest: dict[str, int] = {}
    missingSequence: dict[str, set[int]] = {}

    receiver.handlePacket(
        bytePacket(3),
        highest,
        missingSequence,
    )

    captured = capsys.readouterr()

    assert "Initial sequence gap!" in captured.out
    assert highest["UAV-001"] == 3
    assert missingSequence["UAV-001"] == {1, 2}


# Test a forward sequence jump that creates missing packets
def testHandleUnexpected(capsys):
    highest: dict[str, int] = {"UAV-001": 1}
    missingSequence: dict[str, set[int]] = {"UAV-001": set()}

    receiver.handlePacket(
        bytePacket(5),
        highest,
        missingSequence,
    )

    captured = capsys.readouterr()

    assert "Unexpected sequence number" in captured.out
    assert missingSequence["UAV-001"] == {2, 3, 4}
    assert highest["UAV-001"] == 5


# Verify that sequence state is tracked independently for multiple UAVs
def testMultiUav():
    highest: dict[str, int] = {}
    missingSequence: dict[str, set[int]] = {}

    receiver.handlePacket(
        bytePacket(1),
        highest,
        missingSequence,
    )
    receiver.handlePacket(
        bytePacket(1, "UAV-002"),
        highest,
        missingSequence,
    )

    assert highest["UAV-001"] == 1
    assert highest["UAV-002"] == 1
    assert missingSequence["UAV-001"] == set()
    assert missingSequence["UAV-002"] == set()

    receiver.handlePacket(
        bytePacket(3, "UAV-001"),
        highest,
        missingSequence,
    )

    assert highest["UAV-001"] == 3
    assert highest["UAV-002"] == 1
    assert missingSequence["UAV-001"] == {2}
    assert missingSequence["UAV-002"] == set()