* Building uBoot

https://wiki.archlinux.org/index.php/Banana_Pi
http://linux-sunxi.org/Mainline_U-Boot#Install_U-Boot

** Prepare SDcard
dd if=/dev/zero of=/dev/sdg bs=1M count=8

fdisk /dev/sdg
mkfs.ext4 -O ^metadata_csum,^64bit /dev/sdg1

** Install uBoot

git clone git://git.denx.de/u-boot.git

check last stable branch here: http://git.denx.de/?p=u-boot.git

git checkout -b old v2017.01
make -j4 ARCH=arm CROSS_COMPILE=arm-none-eabi- Lamobo_R1_defconfig
Possibly: make CROSS_COMPILE=arm-none-eabi- menuconfig
make -j4 ARCH=arm CROSS_COMPILE=arm-none-eabi-
sudo dd if=u-boot-sunxi-with-spl.bin of=/dev/sdX bs=1024 seek=8

dd if=u-boot/u-boot-sunxi-with-spl.bin of=/dev/sdX bs=1024 seek=8
sync;sync

** Install base distrib

> #Edit boot.cmd
vi boot.cmd

export $MOUNT=/mnt/a
wget http://archlinuxarm.org/os/ArchLinuxARM-armv7-latest.tar.gz
sudo bsdtar -xpf ArchLinuxARM-armv7-latest.tar.gz -C $MOUNT

mkimage -A arm -O linux -T script -C none -a 0 -e 0 -n "BananPI boot script" -d boot.cmd $MOUNT/boot/boot.scr

sync;sync
umount $MOUNT


* Kernel compilation

gpg --recv-keys 79BE3E4300411886 \<as current user add Linus Torval gpg key \>
gpg --recv-keys 16792B4EA25340F8
yaourt -S arm-linux-gnueabihf-gcc

git clone -b sunxi-next --depth 1 https://github.com/linux-sunxi/linux-sunxi.git
cd linux-sunxi
make ARCH=arm CROSS_COMPILE=arm-linux-gnueabihf- sunxi_defconfig 
make ARCH=arm CROSS_COMPILE=arm-linux-gnueabihf- menuconfig

Activate → Device Drivers → Network device support → Distributed Switch Architecture drivers → B53
Select as builtin (*) same for MDIO (*)

make -j4 ARCH=arm CROSS_COMPILE=arm-linux-gnueabihf- zImage modules 
make ARCH=arm CROSS_COMPILE=arm-linux-gnueabihf- INSTALL_MOD_PATH=output modules_install
ls -lh ./arch/arm/boot/zImage
ls -ldh ./output/lib/modules/*
\< cp ./output/lib/modules/* FILE_SYSTEM/lib/modules \>
sync;sync
\<eject SD card\>

* Archlinux customization

Blacklist kernel: replace #IgnorePkg with IgnorePkg   = linux-armv7 in /etc/pacman.conf

** Kernel doc
http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/tree/Documentation?id=HEAD


