import pytest
from unittest.mock import Mock
from src.telemetryData import telemetryData
from src import simulator

@pytest.fixture
def mockSock():
    return Mock()

@pytest.fixture
def mock_args():
    return Mock()


def testCorrupt(monkeypatch, mockSock):
    packet = telemetryData(
        deviceName="UAV-002",
        sequence = 1,
        altitude= 5000,
        speed = 330
    )
    
    targetAddress =("127.0.0.1", 500)

    data = packet.model_dump_json().encode("utf-8")

    monkeypatch.setattr(simulator.random, "randrange", lambda _: 0)

    simulator.sendCorrupted(packet, mockSock, targetAddress)

    sentData, sentAddress = mockSock.sendto.call_args.args
    assert sentAddress == targetAddress
    assert sentData != data
    assert len(sentData) == len(data)
    assert sentData[0] == data[0] ^ 0x01

def testLoss(monkeypatch, mockSock, mock_args):
    mock_args.packet_loss = 0.1
    monkeypatch.setattr(simulator.random, "random", lambda: 0.0)
    packet = simulator.telemetryData(deviceName="UAV-002", sequence=1, altitude=5000, speed=330)
    held = {
            packet.deviceName: {}
        }

    simulator.processPacket(packet, held, mockSock, mock_args)
    mockSock.sendto.assert_not_called()



def testSend():
    packet = telemetryData(
        deviceName="UAV-002",
        sequence = 1,
        altitude= 5000,
        speed = 330
    )
    mockSock = Mock()
    targetAddress =("127.0.0.1", 500)



    simulator.encodeAndSend(packet, mockSock, targetAddress)

    sentData, sentAddress = mockSock.sendto.call_args.args
    assert sentAddress == targetAddress
    rawJson = sentData.decode("utf-8")
    
    sentPacket = telemetryData.model_validate_json(rawJson)
    assert packet == sentPacket

# tests first part of the holding feature of packets
# adds delayed packet to dictionary and does not invoke send
def testHold(monkeypatch, mockSock, mock_args):
    packet = telemetryData(
            deviceName="UAV-002",
            sequence=1,
            altitude=5000,
            speed = 330
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



# tests second part of the holding feature of packets
# sends delayed packet from dictionary and then normal packet
# also removes delayed packet from dictionary after
def testDelaySend(monkeypatch, mockSock, mock_args):
    pass

def testRepeat(monkeypatch, mockSock, mock_args):
   
    packet = telemetryData(
        deviceName="UAV-002",
        sequence=1,
        altitude=5000,
        speed = 330
    )
    held = {
        packet.deviceName: {}
    }
    
    mock_args.packet_loss = 0.0
    mock_args.repeat_chance = 0.0
    mock_args.hold_chance = 0.0
    mock_args.corruption_rate = 0.0  
    mock_args.repeat_chance = 0.1
    monkeypatch.setattr(simulator.random, "random", lambda: 0.0)
    simulator.processPacket(packet, held, mockSock, mock_args)
    firstData, firstAddress = mockSock.sendto.call_args_list[0].args
    secondData, secondAddress = mockSock.sendto.call_args_list[1].args
    assert mockSock.sendto.call_count == 2
    assert firstData == secondData
    assert secondAddress == firstAddress