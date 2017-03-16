# OS installation

Download mainline Debian kernel for Lamobo R1 https://www.armbian.com/lamobo-r1/ or you own device.

Install Armbian image according the [Armbian documentation](https://docs.armbian.com/User-Guide_Getting-Started).

The Lamobo R1/Banana Pi has a SATA port. /mnt/cache will be used to mount a partition of a SATA disk connected to this port. You should use a SSD. On a Raspberry you have to use the SD card or an external disk (recommended). Armbian can be installed on this disk instead of the SD card. This is the preferred way to do. Follow [this how-to](https://docs.armbian.com/User-Guide_Getting-Started/#how-to-install-to-emmc-nand-sata-usb).

Add a partition as btrfs file system. Archlinux doc about btrfs is nice [here](https://wiki.archlinux.org/index.php/Btrfs) for that.

Show an available btrfs filesystem by using `blkid`, the UUID is used below (replace with your own UUID).
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
# Proxy setup
At this day there is no open source software able to act as a transparent proxy and able to filter SSL. E2guardian v4.1 should be able to do the job but it's not available yet. The architecture selected is the following. With the configuration describe below, transparent proxy and regular proxy are both available but don't give the same functionalities.  

- Transparently intercepting http and https
```
                        +---------------- ROUTER --------------------+
Browser using http  --> | --> iptables --> e2guardian --> squid3 --> | --> outside world  
Browser using https --> | --> iptables -----------------> squid3 --> | --> outside world
                        +--------------------------------------------+
```
- Client has configured proxy
```
                        +---------------- ROUTER --------------------+
Browser             --> | --> iptables --> e2guardian --> squid3 --> | --> outside world  
                        +--------------------------------------------+
```

- Https connexions on clients not using proxy configuration will not be filtered. 
- Iptables is in charge of filtering blacklisted IPs.
- Name resolution facility is in charge of filtering blacklisted domain names.
- E2guardian is in charge of filtering content based on keywords for unencrypted connexions.  

[SSL termination](https://en.wikipedia.org/wiki/TLS_termination_proxy) also named SSL bump can be activated - this is explained in this documentation -, it allow to decrypt SSL, therefore filtering on keywords is available even with https. But beware of the consequences, the security of the users will be LOWERED.

## Building Squid with ssl support
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
Blacklist the packages from being updated. 
```
echo "squid3 hold" | dpkg --set-selections
echo "squid3-common hold" | dpkg --set-selections
```
:mag: To revert replace "hold" with "install".  
:mag: Squid will not been updated anymore. Watch for security updates !

For not terminating SSL connection see [here](https://forum.pfsense.org/index.php?topic=123461.0).

### Create certificates
This is mandatory even if the SSL connections are not terminated. In this scenario we will not use the certificate.

```
mkdir -p /etc/pki/squid/
cd /etc/pki/squid/
openssl req -new -newkey rsa:1024 -days 3650 -nodes -x509 -keyout  /etc/pki/squid/proxy.key -out /etc/pki/squid/proxy.pem
```

## Setup squid
Edit /etc/squid3/squid.conf

```
#http_port 3128 intercept
https_port 3129 intercept ssl-bump cert=/etc/pki/squid/proxy.pem key=/etc/pki/squid/proxy.key
http_port 8080
ssl_bump none all
```
Launch squid3 with `systemctl start squid3`.

## Installing e2guardian
- Project is [here](http://e2guardian.org).
- Github is [here](http://e2guardian.org).
- Packages for x86 are [here](https://github.com/e2guardian/e2guardian/releases/tag/v3.5.0).
- Compilation instructions are [here](https://groups.google.com/forum/#!topic/e2guardian/lSJlggzIsSA).

Default compilation according to documentation (links upper):
```
apt-get install adduser perl bzip2 libc6 libgcc1 libpcre3 libstdc++ libtommath0 zlib1g
mkdir e2guardian-package
cd e2guardian-package
git clone https://github.com/e2guardian/e2guardian.git
cd e2guardian
./autogen.sh
./configure '--prefix=/usr' '--enable-clamd=yes' '--with-proxyuser=e2guardian' '--with-proxygroup=e2guardian' '--sysconfdir=/etc' '--localstatedir=/var' '--enable-icap=yes' '--enable-commandline=yes' '--enable-email=yes' '--enable-ntlm=yes' '--enable-trickledm=yes' '--mandir=${prefix}/share/man' '--infodir=${prefix}/share/info' 'CXXFLAGS=-g -O2 -fstack-protector --param=ssp-buffer-size=4 -Wformat -Werror=format-security' 'LDFLAGS=-Wl,-z,relro' 'CPPFLAGS=-D_FORTIFY_SOURCE=2' 'CFLAGS=-g -O2 -fstack-protector --param=ssp-buffer-size=4 -Wformat -Werror=format-security' '--enable-pcre=no' --enable-sslmitm=yes
make -j2
make install
useradd e2guardian
mkdir -p /var/log/e2guardian
touch /var/log/e2guardian//access.log
chown -R e2guardian:e2guardian /var/log/e2guardian/
mkdir -p /cache/e2guardian/tmp
mkdir /mnt/cache/e2guardian/generatedcerts/
chown e2guardian:e2guardian /mnt/cache/e2guardian/generatedcerts/

```
E2guardian configuration
- language='\<select your language for ex french\>'
- filterports = 8080
- proxyport = 8888
- filterip = 127.0.0.1
- filecachedir = '/cache/e2guardian/tmp'
- minchildren = 5 
- minsparechildren = 5
- preforkchildren = 5
- maxsparechildren = 16
- cacertificatepath = '/etc/pki/e2guardian/my_rootCA.crt'
- caprivatekeypath = '/etc/pki/e2guardian/private_root.pem'
- certprivatekeypath = '/etc/pki/e2guardian/private_cert.pem'
e2guardianf1.conf:
- sslmitm = on 

:mag: There is an issue with the version of libpcre, therefore it is disabled during the compilation with '--enable-pcre=no'

# Using black lists
## Black list with iptables
Configure router networking see network.sh. 

In this scenario only 1 interface is connected and the proxy must be manually configured on each device either by configuring a proxy or by configuring the router as the default router of the device. Therefore one may access the internet by changing the configuration. Until the full configuration of the router is achieved this is recommended.

## Black list with dnsmasq
```
apt-get install dnsmasq
chown dnsmasq  /mnt/cache/dnsmasq
```
To `/etc/dnsmasq.conf` add lines
```
addn-hosts=/mnt/cache/lists/hosts
resolv-file=/mnt/cache/dnsmasq/resolv.conf
```

Change /etc/resolv.conf in order to use dnsmasq for local name resolution. This is mainly helpfull for testing purpose. The file will contain only 1 line.
```
nameserver 127.0.0.1
```
Edit `/mnt/cache/dnsmasq/resolv.conf` with your ISP DNS server. Ex:
```
nameserver 212.27.40.241
```

## Send blacklisted hosts to your own webserver
Requests to web sites referenced in dnsmasq will be resolved as a request to the local web server.  
Installing nginx
```
apt-get install nginx 
```
Copy `blocked.html` to `/var/www/html/index.html`.
Add `error_page 404             /index.html;` to the http section of `/etc/nginx/nginx.conf`.
```
cd /var/www/html
rm index.nginx-debian.html
systemctl restart nginx
```

## Generate black lists

Edit crontab `sudo -u user crontab -e` and add line:
```
0 3 * * * /mnt/cache/lists/lists.sh >/dev/null 2>&1
```
This will refresh the black lists every days à 3am.

Allow user `user` to restart dnsmasq. Add at the end of `/etc/sudoers` the line 
```
%user ALL=NOPASSWD: /bin/systemctl restart dnsmasq.service
```

## Black lists and e2guardian
`ln -s /mnt/cache/lists/blacklists/ /etc/e2guardian/lists/blacklists`

Modify following lines in `/etc/e2guardian/lists/bannedsslsitelist` according to your needs.
```
bannedsitelist = '/mnt/cache/e2guardian/lists/hosts'
bannedsslsitelist = '/mnt/cache/e2guardian/lists/hosts'
```
Restart e2guardian `systemctl restart e2guardian`

# To do
- Download and process lists
- Block blacklist with iptables
- Distribute proxy configuration https://en.wikipedia.org/wiki/Web_Proxy_Auto-Discovery_Protocol
  - Using web server
  - Using DHCP
  - Using configuration file
- IPv6
  - "NAT"
  - Router advertisement
- Statistics and logs
- Activate crypto acceleration for A20 on Lamobo R1
- Configure HTTPS on nginx
- Unify certificates (there is one for squid, one for e2guardian and an other for nginx !)
- Use elyptic curves instead of RSA. ANSSI EC file parameter is [here](https://www.ssi.gouv.fr/uploads/IMG/der/FRP256v1.der)
```
openssl ecparam -list_curves
openssl ecparam -out ec_key.pem -name sect571r1 -genkey 
openssl req -new -key ec_key.pem -x509 -nodes -days 3650 -out cert.pem
```

