#!/bin/bash
echo "Starting IRRd in foreground..."
irrd --config /etc/irrd/irrd.yaml --foreground
echo "IRRd has exited. Keeping container alive for debugging..."
# Sleep indefinitely so the container doesn’t exit immediately.
tail -f /dev/null
