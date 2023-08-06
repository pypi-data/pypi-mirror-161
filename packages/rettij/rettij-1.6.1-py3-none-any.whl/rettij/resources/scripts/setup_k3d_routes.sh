#!/usr/bin/env bash

# Usage: setup_k3d_routes.sh [<cluster-name>]

# exit when any command fails
set -e

if [[ $EUID -gt 0 ]]; then
  echo "No permissions to modify route information! Need to run as sudo/root!"
  exit 2
fi

if [ -n "$1" ]; then
  k3d_cluster_name="$1"
else
  k3d_cluster_name="rettij"
fi

# Verify that supplied cluster actually exists
k3d cluster list $k3d_cluster_name > /dev/null
k3d_master_node="k3d-$k3d_cluster_name-server-0"

pod_ip_ranges_file="pod_ip_ranges.txt"

# Get Pod ip address ranges for each node in the cluster
pod_ip_ranges=$(kubectl get nodes -o jsonpath="{range .items[*]}{@.metadata.managedFields[0].fieldsV1.f:spec.f:podCIDRs}{'\n'}{end}" | \
grep -Eo "(([0-9]|[1-8][0-9]|9[0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-8][0-9]|9[0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\/([1-9]|1[0-9]|2[0-4]|3[0-2])" | \
sort)

# Get master node Docker ip address
master_node_ip=$(docker inspect "$k3d_master_node" --format '{{$network := index .NetworkSettings.Networks "k3d-rettij"}}{{$network.IPAddress}}')

echo "Pod IP ranges"
echo "$pod_ip_ranges"

echo "$pod_ip_ranges" > $pod_ip_ranges_file

echo "Master node IP"
echo "$master_node_ip"

for pod_ip_range in $pod_ip_ranges; do
  ip route add "$pod_ip_range" via "$master_node_ip"
done