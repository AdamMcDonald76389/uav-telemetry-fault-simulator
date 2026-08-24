# test suite for receiver
# tets valid and invalid input 
import pytest
from unittest.mock import Mock
from src.telemetryData import telemetryData
from src import receiver

# helper function
# data to decode for use in handle function
# since takes encoded bytes over utf-8
def bytePacket(sequence):
    packet = telemetryData(
        deviceName="UAV-001",
        sequence=sequence,
        altitude=5000,
        speed = 300

    )
    data = packet.model_dump_json()
    sendData = data.encode("utf-8")
    return sendData


@pytest.fixture
def mockSock():
    return Mock()



# test very first correctly sent packet with no anomalies
def testInitialization():
    highest: dict[str, int] = {}
    missingSequence: dict[str, set[int]] = {}
    receiver.handlePacket(bytePacket(1), highest, missingSequence)

    assert highest["UAV-001"] == 1
    assert missingSequence["UAV-001"] == set()

# tests receiving of packets besides the first packet
def testBaseCase():
    highest: dict[str, int] = {"UAV-001": 1}
    missingSequence: dict[str, set[int]] = {"UAV-001": set()}

    receiver.handlePacket(bytePacket(2), highest, missingSequence)

    assert highest["UAV-001"] == 2
    assert missingSequence["UAV-001"] == set()

# tests handling of duplicate logic
def testHandleDuplicate(capsys):
    highest: dict[str, int] = {"UAV-001": 1}
    missingSequence: dict[str, set[int]] = {"UAV-001": set()}
    receiver.handlePacket(bytePacket(1), highest, missingSequence)
    captured = capsys.readouterr()
    assert "duplicate packet received" in captured.out


# tests handling of packet sent out of order 
def testHandleLate():
    pass

# tests handling of packets when the very first packet is out of order
def testInitialGap():
    pass


# tests handling of packets that 
def testHandleUnexpected():
    pass