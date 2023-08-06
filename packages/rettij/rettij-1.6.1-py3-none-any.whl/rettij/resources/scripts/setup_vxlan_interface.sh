#!/bin/bash

# Sets up a VXLAN interface on a node of type 'container' or 'router'. The interface has an ip address assigned.

# Usage: setup_vxlan_interface.sh <iface_name> <iface_mac> <remote_ext_ip> <tun_ip_cidr> <vni> <parent_iface>

# Exit codes (custom, see code below):
# 0: "Command execution was successful",
# 11: "Wrong number of arguments",
# 12: "Validation of MAC address failed",
# 13: "Validation of remote IP failed",
# 14: "Validation of tunnel interface IP configuration failed",
# 15: "Validation of VNI failed",
# 16: "Failed to add tunnel adapter",
# 17: "Failed to set IP for tunnel adapter",
# 18: "Failed to activate tunnel adapter",

# exit when any command fails
set -e


# Helper function to validate if a MAC address is valid
validate_mac() {
  mac=$1
  if [[ $mac =~ ^([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}$ ]]; then
    return 0
  else
    return 1
  fi
}

# Helper function to validate if a string is a host IP like 192.168.16.0
validate_ip_host() {
  ip=$1
  if [[ $ip =~ ^(([0-9]|[1-8][0-9]|9[0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-8][0-9]|9[0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$ ]]; then
    return 0
  else
    return 1
  fi
}

# Helper function to validate if a string is a CIDR-notation IP like 192.168.16.0/24
validate_ip_cidr() {
  ip=$1
  if [[ $ip =~ ^(([0-9]|[1-8][0-9]|9[0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-8][0-9]|9[0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\/([0-9]|[1-2][0-9]|3[0-2])$ ]]; then
    return 0
  else
    return 1
  fi
}

# Helper function to validate that a variable is a valid VNI (0-16777215)
validate_vni() {

  vni=$1

  # Ensure that $vni represents a number (fail if it is not between 1 and 8 digits)
  if ! [[ "$vni" =~ ^[0-9]{1,8} ]]; then
    return 1
  fi

  # Ensure that the $vni value is within the bounds 0-16777215
  if [ "$vni" -gt 16777215 ]; then
    return 1
  elif [ "$vni" -lt 0 ]; then
    return 1
  fi

  return 0
}

main_function() {

  if [ "${#}" -eq 6 ]; then

    iface_name=$1           # Name for the VXLAN interface
    iface_mac=$2          # MAC address for the VXLAN interface
    remote_ext_ip=$3      # IP of partner endpoint
    tun_ip_cidr=$4        # IP address for the VXLAN interface
    vni=$5                # VNI for the VXLAN tunnel (unique for each tunnel pair)
    parent_iface=$6       # Name of the underlying ethernet interface

    if ! validate_mac "$iface_mac"; then
      echo "'$iface_mac' is not a valid MAC address!"
      echo "Valid MAC addresses look like this: '1A:2B:3C:4D:5E:01'"
      exit 12
    fi

    if ! validate_ip_host "$remote_ext_ip"; then
      echo "'$remote_ext_ip' is not a valid host IP!"
      echo "Valid host IPs look like this: '192.168.16.0'"
      exit 13
    fi

    if ! validate_ip_cidr "$tun_ip_cidr"; then
      echo "'$tun_ip_cidr' is not a valid CIDR-notation IP!"
      echo "Valid CIDR-notation IPs look like this: '192.168.16.0/24'"
      exit 14
    fi

    if ! validate_vni "$vni"; then
      echo "'$vni' is not a valid VXLAN VNI!"
      echo "Valid VXLAN VNIs are between 0 and 16777215"
      exit 15
    fi

    if [[ $EUID -gt 0 ]]; then
      echo "No permissions to modify network interfaces! Need to run as sudo/root!"
      exit 2
    fi

    # A unique ID / VNI is set for each channel during topology parsing, since channels are unique p2p connections
    if ! ip link add mtu 1400 address "$iface_mac" name "$iface_name" type vxlan id "$vni" dev "$parent_iface" remote "$remote_ext_ip" dstport 4789; then
      exit 16
    fi
    if ! [ "$tun_ip_cidr" = "0.0.0.0/0" ]; then
      if ! ip addr add "$tun_ip_cidr" dev "$iface_name"; then
        exit 17
      fi
    fi
    if ! ip link set "$iface_name" up; then
      exit 18
    fi

    exit 0

  else
    echo "Wrong number of arguments: ${#} instead of 6"
    echo "Usage: setup_vxlan_interface.sh <iface_name> <iface_mac> <remote_ext_ip> <tun_ip_cidr> <vni> <parent_iface>"
    exit 11
  fi

}

main_function "$@"