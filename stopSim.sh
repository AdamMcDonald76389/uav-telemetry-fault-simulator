#!/bin/bash

echo "Stopping simulation..."

pkill -f "receiver.py"
pkill -f "simulator.py"


echo "Simulation concluded!"