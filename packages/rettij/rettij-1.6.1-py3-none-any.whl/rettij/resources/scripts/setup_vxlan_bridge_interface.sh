#!/bin/bash

# Sets up a VXLAN interface on a node of type 'switch'. Thus, this interface doesn't have an ip address.

# Usage: setup_vxlan_brigde_interface.sh <bridge_name> <iface_name> <remote_ext_ip> <vni> <parent_iface> [<ageing_time>]

# Exit codes (custom, see code below):
# 0: "Command execution was successful",
# 11: "Wrong number of arguments",
# 12: "Validation of remote IP failed",
# 13: "Validation of VNI failed",
# 14: "Creation of new bridge failed",
# 15: "Failed to activate bridge",
# 16: "Failed to add tunnel adapter",
# 17: "Failed to add tunnel adapter to bridge",
# 18: "Failed to activate tunnel adapter",

# exit when any command fails
set -e


# Helper function to validate if a string is a host IP like 192.168.16.0
validate_ip_host() {
  ip=$1
  if [[ $ip =~ ^(([0-9]|[1-8][0-9]|9[0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-8][0-9]|9[0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$ ]]; then
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

  # Ensure that the $vni value is within th bounds 0-16777215
  if [ "$vni" -gt 16777215 ]; then
    return 1
  elif [ "$vni" -lt 0 ]; then
    return 1
  fi

  return 0
}

main_function() {

  if [ "${#}" -eq 5 ] || [ "${#}" -eq 6 ]; then

    bridge_name=$1          # Name of/for the ethernet bridge
    iface_name=$2           # Name for the VXLAN interface
    remote_ext_ip=$3      # IP of partner endpoint
    vni=$4                # VNI for the VXLAN tunnel (unique for each tunnel pair)
    parent_iface=$5       # Name of the underlying ethernet interface
    ageing_time=$6        # ageing_time=0 equals the behaviour of a hub; for "switch" behaviour, don't set any ageing_time

    if ! validate_ip_host "$remote_ext_ip"; then
      echo "'$remote_ext_ip' is not a valid host IP!"
      echo "Valid host IPs look like this: '192.168.16.0'"
      exit 12
    fi

    if ! validate_vni "$vni"; then
      echo "'$vni' is not a valid VXLAN VNI!"
      echo "Valid VXLAN VNIs are between 0 and 16777215"
      exit 13
    fi

    if [[ $EUID -gt 0 ]]; then
      echo "No permissions to modify network interfaces! Need to run as sudo/root!"
      exit 2
    fi

    # Only try to add bridge if it does not already exist
    if ! ip link show "$bridge_name" >/dev/null 2<&1; then
      if [ "$ageing_time" ] ; then
        if ! ip link add name "$bridge_name" type bridge ageing_time "$ageing_time"; then
          exit 14
        fi
      else
        if ! ip link add name "$bridge_name" type bridge; then
          exit 14
        fi
      fi
      if ! ip link set dev "$bridge_name" up; then
        exit 15
      fi
    fi

    # A unique ID / VNI is set for each channel during topology parsing, since channels are unique p2p connections
    if ! ip link add name "$iface_name" type vxlan id "$vni" dev "$parent_iface" remote "$remote_ext_ip" dstport 4789; then
      exit 16
    fi

    if ! ip link set dev "$iface_name" master "$bridge_name"; then
      exit 17
    fi

    if ! ip link set dev "$iface_name" up; then
      exit 18
    fi

    exit 0

  else
    echo "Wrong number of arguments: ${#} instead of 7 or 8"
    echo "Usage: setup_vxlan_brigde_interface.sh <bridge_name> <iface_name> <remote_ext_ip> <vni> <parent_iface> [<ageing_time>]"
    exit 11
  fi
}

main_function "$@"