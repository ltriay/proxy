
* Archlinux configuration

chown root:root /
chmod 755 /

Blacklist kernel: replace #IgnorePkg with IgnorePkg   = linux-armv7 in
/etc/pacman.conf

cp etc.netctl.eth0 /etc/netctl/eth0
netctl enable eth0

pacman -Syu
pacman -S sudo openntpd bindtools btrfs-progs squid

cat KEYMAP=fr-latin1 EOF>>
/etc/vconsole.conf
EOF

Replace following line in /etc/sudoer
# %sudo	ALL=(ALL) ALL
with
%sudo	ALL=(ALL) ALL
groupadd sudo
usermod alarm -a -G sudo

mkdir -p /mnt/cache
Use fdisk /dev/sda (see man fdisk) to create 2 partitions
mkfs.btrfs -L cache /dev/sda2

* Squid configuration

touch /var/log/squid/cache.log
chown proxy:proxy /var/log/squid/cache.log
mkdir -p /mnt/cache/squid
chown proxy:proxy /mnt/cache/squid

cat /etc/squid/squid.conf >>EOF
cache_dir diskd /mnt/cache/squid 2000 16 256
dns_defnames on
visible_hostname alarm
EOF

squid -k check
squid -zN
systemctl enable squid
systemctl start squid

** Yaourt installation

sudo -u alarm bash
pacman -S git binutils gcc make fakeroot pkg-config --noconfirm
cd /tmp
git clone https://aur.archlinux.org/package-query.git
cd package-query
makepkg -si
cd ..
git clone https://aur.archlinux.org/yaourt.git
cd yaourt
makepkg -si --noconfirm
cd ..
rm -Rf package-query
exit

* e2guardian installation

https://github.com/e2guardian/e2guardian

pacman -S patch automake autoconf
yaourt -S e2guardian
Edit PKGBUILD and add armv7h architecture 

* Notes

/etc/fstab
LABEL=cache /mnt/cache btrfs defaults,noatime,compress=lzo,commit=120 1 0
