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
:mag: To revert replace "hold" with "install".  
:mag: Squid will not been updated anymore. Watch for security updates !

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
http_port 3128 intercept
https_port 3129 intercept ssl-bump cert=/etc/pki/squid/proxy.pem key=/etc/pki/squid/proxy.key
http_port 8080
ssl_bump none all
```

# Installing e2guardian
- Project is here: http://e2guardian.org  
- Github is here: http://e2guardian.org
- Packages for x86 are here: https://github.com/e2guardian/e2guardian/releases/tag/v3.5.0
- Compilation instructions are here: https://groups.google.com/forum/#!topic/e2guardian/lSJlggzIsSA

Default compilation according to documentation (links upper):
```
apt-get install adduser perl bzip2 libc6 libgcc1 libpcre3 libstdc++ libtommath0 zlib1g
mkdir e2guardian-package
cd e2guardian-package
git clone https://github.com/e2guardian/e2guardian.git
cd e2guardian
./autogen.sh
./configure '--prefix=/usr' '--enable-clamd=yes' '--with-proxyuser=e2guardian' '--with-proxygroup=e2guardian' '--sysconfdir=/etc' '--localstatedir=/var' '--enable-icap=yes' '--enable-commandline=yes' '--enable-email=yes' '--enable-ntlm=yes' '--enable-trickledm=yes' '--mandir=${prefix}/share/man' '--infodir=${prefix}/share/info' 'CXXFLAGS=-g -O2 -fstack-protector --param=ssp-buffer-size=4 -Wformat -Werror=format-security' 'LDFLAGS=-Wl,-z,relro' 'CPPFLAGS=-D_FORTIFY_SOURCE=2' 'CFLAGS=-g -O2 -fstack-protector --param=ssp-buffer-size=4 -Wformat -Werror=format-security' '--enable-pcre=yes'
make -j2
make install
useradd e2guardian
mkdir -p /var/log/e2guardian
touch /var/log/e2guardian//access.log
chown -R e2guardian:e2guardian /var/log/e2guardian/
```
E2guardian configuration
- filterports = 8081
- filterip = 127.0.0.1


CHANGED '--enable-pcre=no'

# Install privproxy
```
sudo -u user bash
 autoheader
 autoconf
 ./configure --disable-toggle --disable-editor  --disable-force  sysconfdir=/etc/privoxy localstatedir=/var --with-user=privproxy --with-group=privproxy
 make -j2          
 make -n install  # (to see where all the files will go)
 make install 

```
In /etc/init.d/privoxy modify line `P_CONF_FILE=/usr/local/etc/privoxy/config` with `P_CONF_FILE=/etc/privoxy/config`.

# Install mitmproxy
Installing python3.6
```
wget https://www.python.org/ftp/python/3.6.0/Python-3.6.0.tar.xz
xz -d Python-3.6.0.tar.xz 
tar xvf Python-3.6.0.tar
apt-get install build-essential
apt-get install libbz2-dev libsqlite3-dev libreadline-dev zlib1g-dev libssl-dev libgdbm-dev libncurses5-dev liblzma-dev
./configure OR ./configure --prefix=/opt/python --enable-optimizations
make -j2
make install OR make altinstall OR ADD -j2

apt-get install virtualenv
```

```
sudo apt-get install python3-dev python3-pip libffi-dev libssl-dev
virtualenv --python=/usr/bin/pythonX.Y python_for_mitmproxy
pip3 install --user mitmproxy
```
