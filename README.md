# UAV Telemetry & Fault Simulator

Project for sending simulated UAV telemetry data over UDP to a receiver.

## Simulator

The simulator creates a configurable number of simulated UAVs and sends
telemetry packets for each UAV to the receiver.

The simulator can also inject several types of faults to simulate unreliable
network conditions:

- Packet loss
- Delayed / out-of-order packet delivery
- Packet duplication
- Data corruption

Fault probabilities default to 0 and can be configured through the command line:

- `--packet-loss`
- `--hold-chance`
- `--repeat-chance`
- `--corruption-rate`

Values must be between `0.0` and `1.0`, where the value represents the
probability of the fault occurring. For example, `0.10` represents a 10% chance.

The number of UAVs to simulate can also be configured using:

`--uavs <number>`

The number of UAVs defaults to 5.

## Telemetry Format

Each UAV sends telemetry as a JSON-serialized Pydantic model containing:

- `deviceName` – unique UAV identifier such as `UAV-001`
- `sequence` – monotonically increasing packet sequence number
- `altitude` – simulated UAV altitude
- `speed` – simulated UAV speed

Pydantic is used to validate incoming telemetry before it is processed by the receiver.

Example:

```json
{
  "deviceName": "UAV-001",
  "sequence": 42,
  "altitude": 10500,
  "speed": 245.7
}
'''

## Receiver

The receiver listens for incoming UAV telemetry packets over UDP and displays
the telemetry associated with each packet.

It also tracks packet sequences independently for each UAV and handles faults
introduced by the simulator, including:

- Missing packets
- Duplicate packets
- Late / out-of-order packets
- Invalid or corrupted telemetry

Detected faults are logged by the receiver.

## Usage Examples

```bash
python3 src/simulator.py --uavs 50 --packet-loss 0.01 --hold-chance 0.02

