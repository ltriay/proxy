#!/bin/bash

systemctl stop network-manager

ip addr del 192.168.0.1/24 dev eth0

ip link add br0 type bridge
ip addr add 192.168.0.1/24 dev br0

echo "route add"
ip route add default via 192.168.0.254 dev br0

ip addr

echo "eth0"
ip link set up dev eth0

sleep 3

echo "eth0 master br0"
ip link set eth0 master br0

echo "br0"
ip link set up dev br0
echo "lan1"
ip link set up dev lan1 
echo "lan2"
ip link set up dev lan2
echo "lan3"
ip link set up dev lan3
echo "lan4"
ip link set up dev lan4
echo "wan"
ip link set up dev wan

# Modify the nameservers according to your provider
# This are the DNS of free.fr
cat <<EOF > /etc/resolv.conf
nameserver 212.27.40.241
nameserver 212.27.40.240
EOF

#ip addr
bridge link show
ip ro

