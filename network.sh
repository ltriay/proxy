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

sysctl net.ipv4.ip_forward=1

rm /etc/sysctl.d/30-ipforward.conf
cat <<EOF > /etc/sysctl.d/30-ipforward.conf
net.ipv4.ip_forward=1
net.ipv6.conf.default.forwarding=1
net.ipv6.conf.all.forwarding=1
EOF

# Modify squid configuration


#
# Send http packets to squid
#
# http://wiki.squid-cache.org/ConfigExamples/Intercept/LinuxDnat
#
# The router must have a static IP address. For dynamic IPs use
# http://wiki.squid-cache.org/ConfigExamples/Intercept/LinuxRedirect
#
# Router/proxy private
PROXY_IP=192.168.0.1

# Proxy listening port
HTTP_PORT=8080
HTTPS_PORT=3129

# Start if needed, then reset iptables
# systemctl start iptables
iptables --flush
iptables -P INPUT ACCEPT
iptables -P OUTPUT ACCEPT
iptables -P FORWARD ACCEPT
iptables -X
iptables -t filter -F
iptables -t raw -F
iptables -t nat -F
iptables -t nat -X
iptables -t mangle -F
iptables -t mangle -X
ipset -F
ipset -X
# IPv6
ip6tables -F INPUT
ip6tables -F OUTPUT
ip6tables -F FORWARD
ip6tables -F
#ip6tables -P INPUT ACCEPT
#ip6tables -P OUTPUT ACCEPT
#ip6tables -P FORWARD ACCEPT

# Configure transparent proxy using DNAT
iptables -t nat -A PREROUTING -s $PROXY_IP -p tcp --dport 80 -j ACCEPT
iptables -t nat -A PREROUTING -s $PROXY_IP -p tcp --dport 443 -j ACCEPT
iptables -t nat -A PREROUTING -p tcp --dport $HTTP_PORT -j ACCEPT
iptables -t nat -A PREROUTING -p tcp --dport 80 -j DNAT --to-destination $PROXY_IP:$HTTP_PORT
iptables -t nat -A PREROUTING -p tcp --dport 443 -j DNAT --to-destination $PROXY_IP:$HTTPS_PORT
iptables -t nat -A POSTROUTING -j MASQUERADE
iptables -t mangle -A PREROUTING -p tcp --dport $HTTP_PORT -j DROP
iptables -t mangle -A PREROUTING -p tcp --dport $HTTPS_PORT -j DROP
# Reject http/https connexions if nat is dissabled
iptables -t mangle -A PREROUTING -p tcp --dport 80 -j REJECT
iptables -t mangle -A PREROUTING -p tcp --dport 443 -j REJECT

# Missing IPv6
