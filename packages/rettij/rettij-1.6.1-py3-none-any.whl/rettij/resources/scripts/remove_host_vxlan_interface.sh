#!/bin/bash

# Usage: remove_host_vxlan_interface.sh <iface_id>

iface_id=$1

if [[ $EUID -gt 0 ]]; then
  echo "No permissions to modify network interfaces! Need to run as sudo/root!"
  exit 2
fi

ip link del "$iface_id"