#!/bin/bash
cd /mnt/cache/lists
rm blacklists.tar.gz
rm -Rf blacklists
wget http://dsi.ut-capitole.fr/blacklists/download/blacklists.tar.gz
tar xfz blacklists.tar.gz
rm hosts.txt
wget https://adaway.org/hosts.txt
./convert-lists.py  -w=192.168.0.1 blacklists/adult/domains blacklists/adult/urls blacklists/warez/domains blacklists/warez/urls hosts.txt myblacklist.txt
sudo /bin/systemctl restart dnsmasq.service
