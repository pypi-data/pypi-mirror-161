#!/usr/bin/env bash

# exit when any command fails
set -e

pod_ip_ranges_file="pod_ip_ranges.txt"

if [[ $EUID -gt 0 ]]; then
  echo "No permissions to modify route information! Need to run as sudo/root!"
  exit 2
fi

while read -r pod_ip_range; do
  ip route del "$pod_ip_range"
  echo "Deleted route to $pod_ip_range"
done < $pod_ip_ranges_file

rm $pod_ip_ranges_file
