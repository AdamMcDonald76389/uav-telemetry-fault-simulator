import pytest
from unittest.mock import Mock

from src import simulator
from src.telemetryData import telemetryData


@pytest.fixture
def mockSock():
    return Mock()


@pytest.fixture
def mock_args():
    return Mock()


# Test byte corruption logic
def testCorrupt(monkeypatch, mockSock):
    packet = telemetryData(
        deviceName="UAV-002",
        sequence=1,
        altitude=5000,
        speed=330,
    )

    targetAddress = ("127.0.0.1", 500)
    data = packet.model_dump_json().encode("utf-8")

    monkeypatch.setattr(simulator.random, "randrange", lambda _: 0)

    simulator.sendCorrupted(packet, mockSock, targetAddress)

    sentData, sentAddress = mockSock.sendto.call_args.args

    assert sentAddress == targetAddress
    assert sentData != data
    assert len(sentData) == len(data)

    # Verify that the expected bitwise corruption was applied
    assert sentData[0] == data[0] ^ 0x01


# Test packet loss conditional flow
def testLoss(monkeypatch, mockSock, mock_args):
    mock_args.packet_loss = 0.1
    mock_args.repeat_chance = 0.0
    mock_args.hold_chance = 0.0
    mock_args.corruption_rate = 0.0

    monkeypatch.setattr(simulator.random, "random", lambda: 0.0)

    packet = telemetryData(
        deviceName="UAV-002",
        sequence=1,
        altitude=5000,
        speed=330,
    )
    held = {
        packet.deviceName: {}
    }

    simulator.processPacket(packet, held, mockSock, mock_args)

    mockSock.sendto.assert_not_called()


# Test basic packet serialization and sending
def testSend():
    packet = telemetryData(
        deviceName="UAV-002",
        sequence=1,
        altitude=5000,
        speed=330,
    )
    mockSock = Mock()
    targetAddress = ("127.0.0.1", 500)

    simulator.encodeAndSend(packet, mockSock, targetAddress)

    sentData, sentAddress = mockSock.sendto.call_args.args

    assert sentAddress == targetAddress

    rawJson = sentData.decode("utf-8")
    sentPacket = telemetryData.model_validate_json(rawJson)

    assert packet == sentPacket


# Test storing a delayed packet without sending it
def testHold(monkeypatch, mockSock, mock_args):
    packet = telemetryData(
        deviceName="UAV-002",
        sequence=1,
        altitude=5000,
        speed=330,
    )
    held = {
        packet.deviceName: {}
    }

    mock_args.packet_loss = 0.0
    mock_args.repeat_chance = 0.0
    mock_args.hold_chance = 0.1
    mock_args.corruption_rate = 0.0

    monkeypatch.setattr(simulator.random, "random", lambda: 0.0)

    simulator.processPacket(packet, held, mockSock, mock_args)

    mockSock.sendto.assert_not_called()

    heldPacket = held[packet.deviceName][packet.sequence]

    assert heldPacket == packet
    assert heldPacket is not packet


# Test sending the current packet before releasing a held packet
def testDelaySend(monkeypatch, mockSock, mock_args):
    mock_args.packet_loss = 0.0
    mock_args.repeat_chance = 0.0
    mock_args.hold_chance = 0.0
    mock_args.corruption_rate = 0.0

    packet = telemetryData(
        deviceName="UAV-002",
        sequence=1,
        altitude=5000,
        speed=330,
    )
    held = {
        packet.deviceName: {}
    }

    monkeypatch.setattr(simulator.random, "random", lambda: 0.0)

    held[packet.deviceName][packet.sequence] = packet.model_copy(deep=True)
    packet.sequence = 2

    simulator.processPacket(packet, held, mockSock, mock_args)

    firstData, _ = mockSock.sendto.call_args_list[0].args
    secondData, _ = mockSock.sendto.call_args_list[1].args

    firstPacket = telemetryData.model_validate_json(firstData)
    secondPacket = telemetryData.model_validate_json(secondData)

    assert firstPacket.sequence == 2
    assert secondPacket.sequence == 1
    assert mockSock.sendto.call_count == 2
    assert held[packet.deviceName] == {}


# Test duplicate send logic
def testRepeat(monkeypatch, mockSock, mock_args):
    packet = telemetryData(
        deviceName="UAV-002",
        sequence=1,
        altitude=5000,
        speed=330,
    )
    held = {
        packet.deviceName: {}
    }

    mock_args.packet_loss = 0.0
    mock_args.repeat_chance = 0.1
    mock_args.hold_chance = 0.0
    mock_args.corruption_rate = 0.0

    monkeypatch.setattr(simulator.random, "random", lambda: 0.0)

    simulator.processPacket(packet, held, mockSock, mock_args)

    firstData, firstAddress = mockSock.sendto.call_args_list[0].args
    secondData, secondAddress = mockSock.sendto.call_args_list[1].args

    assert mockSock.sendto.call_count == 2
    assert firstData == secondData
    assert secondAddress == firstAddress


# Test normal packet sending with no injected faults
def testProcessPacket(mock_args, mockSock):
    mock_args.packet_loss = 0.0
    mock_args.repeat_chance = 0.0
    mock_args.hold_chance = 0.0
    mock_args.corruption_rate = 0.0

    packet = telemetryData(
        deviceName="UAV-002",
        sequence=1,
        altitude=5000,
        speed=330,
    )
    held = {
        packet.deviceName: {}
    }

    simulator.processPacket(packet, held, mockSock, mock_args)

    assert mockSock.sendto.call_count == 1

    data, _ = mockSock.sendto.call_args_list[0].args
    dataPacket = telemetryData.model_validate_json(data)

    assert dataPacket == packet


# Test corruption through processPacket
def testProcessCorrupt(monkeypatch, mock_args, mockSock):
    mock_args.packet_loss = 0.0
    mock_args.repeat_chance = 0.0
    mock_args.hold_chance = 0.0
    mock_args.corruption_rate = 0.1

    monkeypatch.setattr(simulator.random, "random", lambda: 0.0)

    packet = telemetryData(
        deviceName="UAV-002",
        sequence=1,
        altitude=5000,
        speed=330,
    )
    held = {
        packet.deviceName: {}
    }

    simulator.processPacket(packet, held, mockSock, mock_args)

    assert mockSock.sendto.call_count == 1

    data, _ = mockSock.sendto.call_args_list[0].args
    packetBytes = packet.model_dump_json().encode("utf-8")

    assert packetBytes != data
    assert len(packetBytes) == len(data)

def testIntentionalFailure():
    assert False