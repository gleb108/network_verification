#!/usr/bin/env python


from ConfigParser import SafeConfigParser
from netaddr import IPNetwork, IPAddress
import argparse
import os


def do (cmd):
    if (os.system(cmd)):
        print "Can't do command:", cmd
        exit(1)


def delete_admin_ip_gen(admin_ip):
    if admin_ip:
        result = "admin_ipaddr = `ip addr show | grep {0} | awk '{{print $2}}'`\n".format(admin_ip)
        result += "admin_interface = `ip addr show | grep {0} | awk '{{print $7}}'`\n".format(admin_ip)
        result += "ip addr del $admin_ipaddr dev $admin_interface\n" 
    return result


def bond_setup_gen(bond, mode, slaves, assign_admin_ip=False):
    result = 'modprobe bonding mode={0} miimon=100\nifconfig {1} up\n'.format(mode, bond)

    for slave in slaves:
        result += 'ifenslave {0} {1}\n'.format(bond, slave)
         
    if assign_admin_ip:
        result += 'ip addr add $admin_ipaddr dev {0}\n'.format(bond)

    return result

def vlan_create_gen(vlan_dict):
    result = '';
    for interface in vlan_dict.keys():
        for vlan in vlan_dict[interface]:
            result += 'vconfig add {0} {1}\n'.format(interface, vlan) 

    return result

def ip_assign_gen(interface, ip_addr, netmask):
    result = 'ip addr add {0}/{1} dev {2}\n'.format(ip_addr, netmask, interface)
    result += 'ip link set up dev {0}\n'.format(interface)
    return result

#parsing CLI arguments       
parser = argparse.ArgumentParser()
parser.add_argument('-s', '--show-scripts', action="store_true", default=False, dest="show_scripts", help="Show scripts and exit")
parser.add_argument('-c', '--config', action="store", default="config.ini", dest="config", help="Config file")
parser.add_argument('-d', '--distribute', action="store_true", default=False, dest="distribute", help="Distribute bash scripts on all the nodes")
parser.add_argument('-r', '--run-network-setup', action="store_true", default=False, dest="run_network_setup", help="Run network setup on all the nodes")
parser.add_argument('-t', '--test', action="store_true", default=False, dest="runtest", help="Run test on all the nodes")

args = parser.parse_args()

#parsing config file
parser = SafeConfigParser()
parser.read(args.config)
nodes = parser.get("main", "nodes")
nodes_list = nodes.replace(' ','').split(',')

bond = parser.get("bond", "name")
bond_mode = parser.get("bond", "mode")
bond_slaves = parser.get("bond", "slaves")
bond_slaves_list = bond_slaves.replace(' ','').split(',')

bond_assign_admin_ip = False
if parser.has_option("bond", "assign_admin_ip"):
    bond_assign_admin_ip = bool(parser.get("bond", "assign_admin_ip"))

vlan_dict = {} 
vlans = parser.items("vlan")
for vlan_str in vlans:
    interface = vlan_str[0]
    vlan_list = vlan_str[1].replace(' ','').split(',')
    vlan_dict[interface] = vlan_list

ip ={}
cidr = parser.items("cidr")
for cidr_str in cidr:
    interface = cidr_str[0]
    network = cidr_str[1]
    ip[interface] = network

testcmd = parser.get("test_plan", "cmd")


#dict to keep the last used IPs for every CIDR
ip_addresses_in_use = {} 

for     network in ip.values():
    net = IPNetwork(network)
    ip_addresses_in_use[network] = net.ip
    
    #checking if we have enough ip addresses for all the nodes
    if len(net) < len(nodes_list):
        raise NameError("Network {0} isn't enough for {1} nodes".format(network,len(nodes_list)))





for node in nodes_list:

    if args.distribute or args.show_scripts: 
        script = '#!/bin/bash\n\n'   
 
        if bond_assign_admin_ip:
            script += delete_admin_ip_gen(node)

        if bond and bond_mode and bond_slaves_list:
            script += bond_setup_gen(bond, bond_mode, bond_slaves_list, bond_assign_admin_ip)

        if len(vlan_dict):
           script += vlan_create_gen(vlan_dict)

        if len(ip):
           for interface in ip.keys():
              network = ip[interface]
              netmask = IPNetwork(network).prefixlen
              ip_addresses_in_use[network] = ip_addresses_in_use[network]+1
              current_ip_addr = str(ip_addresses_in_use[network])

              script += ip_assign_gen(interface, current_ip_addr, netmask)   

    if args.show_scripts:
       print '----------- node {0} -----------'.format(node)
       print script
       exit

    if args.distribute:
       f = open('tmp.tmp','w')
       f.write(script)
       f.close()
       do("chmod 755 tmp.tmp; scp tmp.tmp {0}:network_setup.sh".format(node))

    if args.run_network_setup:
       do("ssh {0} ./network_setup.sh".format(node))

 
    if args.runtest:
       do("ssh {0} {1}".format(node, testcmd))
