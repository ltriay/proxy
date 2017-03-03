# Installation

Download mainline Debian kernel for Lamobo R1 https://www.armbian.com/lamobo-r1/

Install Armbian image according to https://docs.armbian.com/User-Guide_Getting-Started/#how-to-check-download-authenticity

```
apt-get install docker
apt-get install aufs-tools 
```
Recommanded package cgroupfs-mount cannot be installed because it breaks dependencies.
```
usermod user -a -G docker
```
Show an available btrfs filesystem `blkid` UUID is used below.
```
cat <<EOF > /etc/fstab
UUID=8a0528f0-9899-4800-93cb-814b30ed712a	/mnt/cache	btrfs	defaults,noatime,nodiratime,compress=lzo			0	2
EOF
```
Setup static IP, change /etc/network/interfaces with below content. This configuration works for the French provider free.fr. For other providers modify the parameters accordingly.
```
auto eth0
iface eth0 inet static
	address	192.168.0.1
	netmask 255.255.255.0
	gateway 192.168.0.254
dns-nameservers 212.27.40.240 212.27.40.241
```

