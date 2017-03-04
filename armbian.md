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

# Building Squid with ssl support
Squid3 for Debian isn't build with ssl support. We must rebuild it.
Display the build options with `squid3 -v`.
Remove # in front of the source line in /etc/apt/sources.list (uncomment)

```
apt-get update
apt-get install build-essential
cd /tmp
apt-get source squid3
cd squid*
sed -i -e "s/--enable-esi/--enable-esi --enable-ssl/g" debian/rules
```
NOTE –enable-ssl-crtd is for creating certificates on the fly. Add it to the build options for SSL termination and full interception of the encrypted connections.

Check missing packages with `dpkg-buildpackage -us -uc` then run it again to create a package. Build take very long time. Then install the packages.
```
dpkg -i squid3_3.4.8-6+deb8u4_armhf.deb
dpkg -i squid3-common_3.4.8-6+deb8u4_all.deb
```
Blacklist the package from being update. 
```
echo "squid3 hold" | dpkg --set-selections
echo "squid3-common hold" | dpkg --set-selections
```
:mag: to revert replace "hold" with "install".
:mag: squid will not been updated anymore. Watch for security updates !

For not bumping (not terminating) SSL connection see https://forum.pfsense.org/index.php?topic=123461.0

## Create certificates
This is mandatory even if the SSL connections are not terminated. In this scenario we will not use the certificate.

```
mkdir -p /etc/pki/squid/
cd /etc/pki/squid/
openssl req -new -newkey rsa:1024 -days 3650 -nodes -x509 -keyout  /etc/pki/squid/proxy.key -out /etc/pki/squid/proxy.pem
```

Edit /etc/squid3/squid.conf

```
http_port 3128
https_port 3129 transparent cert=/etc/pki/squid/proxy.pem key=/etc/pki/squid/proxy.key
```
