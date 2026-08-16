Project for sending simulated telemetry data from a UAV to a receiver;
Currently sends telemetry from simulator to receiver via UDP sockets.
receiver currently validates sequences to check if they are received in order using various checks
telemetryData represents a very simplified version of the kind of data a uav might send
packetloss can be determined via the cli by entering a value after python3 src/simulator.py "number"
Currently has basic packet loss