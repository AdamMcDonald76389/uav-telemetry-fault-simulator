import pytest
from unittest.mock import Mock
from src.telemetryData import telemetryData
from src import simulator

@pytest.fixture
def mockSock():
    return Mock()


def testCorrupt(monkeypatch):
    packet = telemetryData(
        deviceName="UAV-002",
        sequence = 1,
        altitude= 5000,
        speed = 330
    )
    mockSock = Mock()
    targetAddress =("127.0.0.1", 500)

    data = packet.model_dump_json().encode("utf-8")

    monkeypatch.setattr(simulator.random, "randrange", lambda _: 0)

    simulator.sendCorrupted(packet, mockSock, targetAddress)

    sentData, sentAddress = mockSock.sendto.call_args.args
    assert sentAddress == targetAddress
    assert sentData != data
    assert len(sentData) == len(data)
    assert sentData[0] == data[0] ^ 0x01

def testLoss():
    pass




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


def testHold():
    pass


def testRepeat():
    pass

