#!/bin/bash

netctl stop eth0
netctl status eth0

ip link add br0 type bridge
ip addr add 192.168.0.1/24 dev br0

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

echo "route add"
ip route add default via 192.168.0.254 dev br0

#ip addr
bridge link show
ip ro

