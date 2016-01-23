# Simple network verification for Mirantis Openstack environments

It supports linux bonding and vlans. It uses <i>ssh/scp</i> to run commands on boostrap nodes.
It works with the nodes in turns not in parallel.

Limitation: You can create and check only 1 bond now. 

# How to test network settings with network_verification.py.

1) You supposed to have Fuel and nodes that booted by PXE in a bootstrap mode.

2) You describe desirable network configuration in small INI file.
   You can specify node list (ip addresses), linux bonds, vlans, ip subnets and command to test connectivity.
   Please, see the example.

3) You can use <i>network_verification.py -s</i>  to generate bash script for every node. It doesn't make any changes, just shows you a scripts.

4) If you are satisfied how bash scripts look you can use <i>network_verification.py -d</i>  to distribute bash scripts to every node by scp.

5) Then you can use <i>network_verification.py -a</i>  to apply network configuration on every node.

6) You can use <i>network_verification.py -r</i>  to check the result. It just run any command on every node.

7) Finally you can use <i>network_verification.py -t</i>  to run test command on every node. Also you can change test command in INI file or use <i>network_verification.py -r</i>  to perform another tests.
