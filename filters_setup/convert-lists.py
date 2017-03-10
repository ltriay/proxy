#!/usr/bin/env python3

import argparse
import sys
import ipaddress
import re

etchosts = ""
iptables = []

dns_names = re.compile('^[\w.-]+$')
hosts_file = re.compile(' +')

IPSET = """
ipset -N blacklist4 iphash --hashsize 4096 --maxelem 200000 --family inet
ipset -N blacklist6 iphash --hashsize 4096 --maxelem 200000 --family inet6
"""

"""
ipset -A myset 1.1.1.1
ipset -A myset 2.2.2.2
iptables -A INPUT -m set --set myset src -j DROP
"""

def error(msg):
  print(msg)
  
def warning(msg, verbose):
  if verbose:
    print(msg)
  
def is_ip_address(ip):
  try:
    ipaddress.ip_address(ip)
  except ValueError:
    return False
  except:
    raise
  return True
  
def is_global(ip):
  """Emulate is_global for python 3.4<="""
  if ip.is_private: 
    return False
  elif ip.is_multicast: 
    return False
  elif ip.is_reserved: 
    return False
  elif ip.is_unspecified: 
    return False  
  elif ip.is_link_local: 
    return False
  return True         

class filter_setup:
  def __init__(self, args):
    self.args = args
    self.count_iptables = 0
    self.count_hosts_file = 0
    
    self.fd_iptables = open(self.args.iptables, "w")
    self.fd_hosts = open(self.args.hosts, "w")
    
  def __del__(self):
    self.fd_iptables.close()
    self.fd_hosts.close()
    
  def read_files(self):
    for aFile in self.args.files:
      with open(aFile, 'r') as fd:
        host_file = fd.readlines()
        self.read_file(host_file)
      fd.closed
    
  def read_file(self, f):
    for aLine in f:
      aLine = aLine.strip()

      if len(aLine) == 0: continue # skip empty lines
      if aLine[0] == "#": continue # skip comments
        
      # Is it an IPv4/6 address ?
      if is_ip_address(aLine):
        self.write_iptables(ipaddress.ip_address(aLine))

      # Is it a dns name ?
      elif dns_names.match(aLine) is not None:
        if "." in aLine:
          self.write_hosts_file(aLine)
        else:
          warning("Can't process keywords (keyword %s)." % aLine, self.args.verbose)
        
      # It's an URL ?
      elif len(aLine.split("/")) > 1:
        url = aLine.split("/")
        if dns_names.match(url[0]) is not None:
          warning("Not blacklisting %s domain name despite URL %s. " % (url[0], aLine), self.args.verbose)
        else:
          warning("Don't know what to do with line (url ?) '%s'." % aLine, self.args.verbose) 

      # maybe it's the line of a hosts file ?
      elif len(hosts_file.split(aLine)) > 1:
        hosts = hosts_file.split(aLine)
        #print(hosts)
        for anHost in hosts:
          if is_ip_address(anHost):
            ip = ipaddress.ip_address(anHost)
            if is_global(ip):
              self.write_iptables(ip)
            else:
              warning("Refusing to blacklist non-global IPs %s." % aLine, self.args.verbose)
          else:
              self.write_hosts_file(anHost)
          
      # Don't know what it is
      else:
        warning("Don't know what to do with line '%s'." % aLine, self.args.verbose)
        
  def write_iptables(self, ip):
    if self.args.verbose:
      print("iptables: %s redirect" % str(ip))
    if ip.version == 4:
      self.fd_iptables.write("ipset -A blacklist4 %s\n" % str(ip))
    else:
      self.fd_iptables.write("ipset -A blacklist6 %s\n" % str(ip))
    return
    
  def write_hosts_file(self, host):  
    if self.args.verbose:
      print("hosts: file %s %s" % (self.args.ip, host))
    self.fd_hosts.write("%s %s\n" % (self.args.ip, host))      
    return        

def read_args():
  parser = argparse.ArgumentParser(description='Convert files from filtering lists to generate iptables and /etc/hosts file.')

  parser.add_argument('-s', "--setup", dest='setup', action='store_true', help='setup hosts and iptables. Root access is mandatory.')
  parser.add_argument('-e', '--error', dest='ip', default='127.0.0.1', help='IP where to redirect filtered IPs or web sites.')  
  parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', help='IP where to redirect filtered IPs or web sites.')    
  parser.add_argument('-f', '--hosts', dest='hosts', default='hosts', help='Hosts files to write (default is "hosts").')
  parser.add_argument('-i', '--iptables', dest='iptables', default='iptables.txt', help='Files to write iptables commands (default is "iptables.txt").')              
  parser.add_argument('files', nargs=argparse.REMAINDER, help='files to convert')

  args = parser.parse_args()
  
  print(args.setup, args.files)
  
  if len(args.files) < 1:
    error("Please provide at least 1 file to process")
    sys.exit(1)
    
  if not is_ip_address(args.ip):
    error("Please provide an IP address where to redirect filtered web sites.")
    if args.ip != None and args.ip != "":
      error("%s provided instead." % args.ip)      
    sys.exit(1)

  return args
    

args = read_args()
f = filter_setup(args)
f.read_files()


