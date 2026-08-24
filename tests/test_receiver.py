# test suite for receiver
# tets valid and invalid input 
from src.telemetryData import telemetryData
from src import receiver

# helper function
# data to decode for use in handle function
# since takes encoded bytes over utf-8
def bytePacket(sequence, deviceName="UAV-001"):
    packet = telemetryData(
        deviceName=deviceName,
        sequence=sequence,
        altitude=5000,
        speed = 300

    )
    data = packet.model_dump_json()
    sendData = data.encode("utf-8")
    return sendData





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
    assert highest["UAV-001"] == 1
    assert missingSequence["UAV-001"] == set()


# tests handling of packets sent out of order 
def testHandleLate(capsys):
    highest: dict[str, int] = {"UAV-001": 4}
    missingSequence: dict[str, set[int]] = {"UAV-001": set()}
    missingSequence["UAV-001"] = {1, 2, 3}

    receiver.handlePacket(bytePacket(2), highest, missingSequence)

    captured = capsys.readouterr()
    assert "Late packet received!" in captured.out
    assert missingSequence["UAV-001"] == {1, 3}
    assert highest["UAV-001"] == 4

# tests handling of packets when the very first packet is out of order
def testInitialGapInit(capsys):

    highest: dict[str, int] = {}
    missingSequence: dict[str, set[int]] = {}
    receiver.handlePacket(bytePacket(3), highest, missingSequence)
    captured = capsys.readouterr()
    assert "Initial sequence gap!" in captured.out
    assert highest["UAV-001"] == 3
    assert missingSequence["UAV-001"] == {1, 2}


# tests handling of packets that 
def testHandleUnexpected(capsys):
    highest: dict[str, int] = {"UAV-001": 1}
    missingSequence: dict[str, set[int]] = {"UAV-001": set()}
    receiver.handlePacket(bytePacket(5), highest, missingSequence)
    captured = capsys.readouterr()
    assert "unexpected sequence number!" in captured.out
    assert missingSequence["UAV-001"] == {2, 3, 4}
    assert highest["UAV-001"] == 5

# verify that multiple UAVs are handled correctly
def testMultiUav():
    highest: dict[str, int] = {}
    missingSequence: dict[str, set[int]] = {}
    receiver.handlePacket(bytePacket(1), highest, missingSequence)
    receiver.handlePacket(bytePacket(1, "UAV-002"), highest, missingSequence)
    assert highest["UAV-001"] == 1
    assert highest["UAV-002"] == 1

    assert missingSequence["UAV-001"] == set()
    assert missingSequence["UAV-002"] == set()

    receiver.handlePacket(bytePacket(3, "UAV-001"), highest, missingSequence)

    assert highest["UAV-001"] == 3
    assert highest["UAV-002"] == 1

    assert missingSequence["UAV-001"] == {2}
    assert missingSequence["UAV-002"] == set()