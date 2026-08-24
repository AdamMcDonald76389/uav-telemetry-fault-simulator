# Test suite for telemetry data
# Tests valid and invalid inputs for each variable

import pytest
from pydantic import ValidationError

from src.telemetryData import telemetryData


@pytest.mark.parametrize(
    "deviceName, expectedValid",
    [
        ("UAV-000", True),
        ("UAV-001", True),
        ("UAV-500", True),
        ("UAV-999", True),
        ("UAV-01", False),
        ("UAV-1000", False),
        ("U@V-001", False),
        ("UAVA-001", False),
        ("UAV-ABC", False),
        ("UAV001", False),
        (555, False),
        (None, False),
    ],
)
def testDeviceName(deviceName, expectedValid):
    if expectedValid:
        packet = telemetryData(
            deviceName=deviceName,
            sequence=1,
            altitude=5000,
            speed=250,
        )
        assert packet.deviceName == deviceName

    else:
        with pytest.raises(ValidationError):
            telemetryData(
                deviceName=deviceName,
                sequence=1,
                altitude=5000,
                speed=250,
            )


@pytest.mark.parametrize(
    "speed, expectedValid",
    [
        (0, True),
        (500, True),
        (300, True),
        ("not a float", False),
        (-5, False),
        (-0.1, False),
        (500.1, False),
        (1000, False),
        (None, False),
    ],
)
def testSpeed(speed, expectedValid):
    if expectedValid:
        packet = telemetryData(
            deviceName="UAV-001",
            sequence=1,
            altitude=5000,
            speed=speed,
        )
        assert packet.speed == speed

    else:
        with pytest.raises(ValidationError):
            telemetryData(
                deviceName="UAV-001",
                sequence=1,
                altitude=5000,
                speed=speed,
            )


@pytest.mark.parametrize(
    "altitude, expectedValid",
    [
        (-1, False),
        (0, True),
        (30000, True),
        (30001, False),
        (22000, True),
        (500.5, False),
        ("not an alt", False),
        (None, False),
    ],
)
def testAltitude(altitude, expectedValid):
    if expectedValid:
        packet = telemetryData(
            deviceName="UAV-001",
            sequence=1,
            altitude=altitude,
            speed=250,
        )
        assert packet.altitude == altitude

    else:
        with pytest.raises(ValidationError):
            telemetryData(
                deviceName="UAV-001",
                sequence=1,
                altitude=altitude,
                speed=250,
            )


@pytest.mark.parametrize(
    "sequence, expectedValid",
    [
        (1, True),
        (0, False),
        (-5, False),
        (50, True),
        ("Not a sequence", False),
        (None, False),
        (1.5, False),
    ],
)
def testSequence(sequence, expectedValid):
    if expectedValid:
        packet = telemetryData(
            deviceName="UAV-001",
            sequence=sequence,
            altitude=20000,
            speed=250,
        )
        assert packet.sequence == sequence

    else:
        with pytest.raises(ValidationError):
            telemetryData(
                deviceName="UAV-001",
                sequence=sequence,
                altitude=20000,
                speed=250,
            )