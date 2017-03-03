# Installation

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
# Installing docker images
Docker images can only works on the architecture they are made for.
Most images starts with keyword `armhf-`
