#!/bin/bash

echo "Stopping all Synergy processes..."

# Kill the GUI app and any underlying background processes (synergys/synergyc)
# -i makes it case-insensitive; -f looks at the full process name
pkill -i -f "Synergy"

# Wait a moment for the ports to clear
sleep 2

echo "Launching a fresh instance..."

# Open the Synergy application
open -a "Synergy"

echo "Done!"