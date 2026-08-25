# UAV Telemetry & Fault Simulator

A Python-based simulator for transmitting UAV telemetry over UDP and testing receiver behavior under unreliable network conditions.

## Simulator

The simulator creates a configurable number of simulated UAVs and sends telemetry packets for each UAV to the receiver.

The simulator can also inject several types of faults to simulate unreliable network conditions:

* Packet loss
* Delayed / out-of-order packet delivery
* Packet duplication
* Data corruption

Fault probabilities default to `0` and can be configured through the command line:

* `--packet-loss`
* `--hold-chance`
* `--repeat-chance`
* `--corruption-rate`

Values must be between `0.0` and `1.0`, where the value represents the probability of the fault occurring. For example, `0.10` represents a 10% chance.

The number of UAVs to simulate can also be configured using:

`--uavs <number>`

The number of UAVs must be between 1 and 999 and defaults to 5.

## Telemetry Format

Each UAV sends telemetry as a JSON-serialized Pydantic model containing:

* `deviceName` – unique UAV identifier such as `UAV-001`
* `sequence` – monotonically increasing packet sequence number
* `altitude` – simulated UAV altitude
* `speed` – simulated UAV speed

Pydantic is used to validate incoming telemetry before it is processed by the receiver.

Example:

```json
{
  "deviceName": "UAV-001",
  "sequence": 42,
  "altitude": 10500,
  "speed": 245.7
}
```

## Receiver

The receiver listens for incoming UAV telemetry packets over UDP and displays the telemetry associated with each packet.

It also tracks packet sequences independently for each UAV and handles faults introduced by the simulator, including:

* Missing packets
* Duplicate packets
* Late / out-of-order packets
* Invalid or corrupted telemetry

Detected faults are logged by the receiver.

## Installation

Requires Python 3 and Pydantic.

Install the required dependencies:

```bash
pip install pydantic pytest
```

Alternatively, install the project and development dependencies using pyproject.toml:
```bash
pip install -e ".[dev]"
```
## Usage

Start the receiver and simulator in separate terminals.

Start the receiver:

```bash
python3 -m src.receiver
```

Start the simulator:

```bash
python3 -m src.simulator
```

Example with multiple UAVs and simulated network faults:

```bash
python3 -m src.simulator --uavs 50 --packet-loss 0.01 --hold-chance 0.02
```

To view all available command-line options:

```bash
python3 -m src.simulator --help
```

## Testing

Run the test suite from the project root:

```bash
pytest
```

The test suite covers telemetry validation, packet handling, simulated network faults, integration tests, and command-line argument validation.
