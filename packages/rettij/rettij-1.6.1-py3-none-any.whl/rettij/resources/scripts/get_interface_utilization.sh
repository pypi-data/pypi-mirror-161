#!/bin/bash

# Usage: get_interface_utilization.sh <interface>

# Verify that grep is installed
if ! type grep &> /dev/null; then
  echo "Tool 'grep' is not installed!" >&2
  exit 127
fi
# Verify that awk is installed
if ! type awk &> /dev/null; then
  echo "Tool 'awk' is not installed!" >&2
  exit 127
fi

if [ "${#}" -eq 1 ]; then
  iface=$1
else
  echo "Wrong number of arguments: ${#} instead of 1" >&2
  echo "Usage: get_interface_utilization.sh <interface>" >&2
  exit 1
fi

set -e

# Get interface statistics via 'ip' command
first_output=$(ip -s link show $iface)
sleep 1
second_output=$(ip -s link show $iface)

# Parse output of commands to retrieve total values in bytes
first_RX=$(echo $first_output | grep -oP 'RX:\s(\w+\s)+' | awk -F " " '{print $8}')
first_TX=$(echo $first_output | grep -oP 'TX:\s(\w+\s)+' | awk -F " " '{print $8}')
second_RX=$(echo $second_output | grep -oP 'RX:\s(\w+\s)+' | awk -F " " '{print $8}')
second_TX=$(echo $second_output | grep -oP 'TX:\s(\w+\s)+' | awk -F " " '{print $8}')

# Calculate differences to retrieve kB/s
diff_RX=$((second_RX - first_RX))
diff_TX=$((second_TX - first_TX))
diff_total=$((diff_RX + diff_TX))

echo $diff_RX,$diff_TX,$diff_total
