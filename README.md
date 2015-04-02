# network_verification
Simple network verification for Mirantis Openstack environments

It supports linux bonding and vlans. It use ssh/scp to run commands on boostrap nodes.
It works with the nodes in turns not in parallel.


# How to test network settings with network_verification.py.

1) You supposed to have Fuel and nodes that booted by PXE in a bootstrap mode.

2) You describe desirable network configuration in small INI file.
   You can specify node list (ip addresses), linux bonds, vlans, ip subnets and command to test connectivity.
   Please, see the example.

3) You can use network_verification.py -s to generate bash script for every node. It doesn't make any changes, just shows you a scripts.

4) If you are satisfied how bash scripts look you can use network_verification.py to distribute bash scripts to every node by _scp_.

5) Then you can use network_verification.py -a to apply network configuration on every node.

6) You can use network_verification.py -r to check the result. It just run any command on every node.

7) Finally you can use network_verification.py -t to run test command on every node. Also you can change test command in INI file or use network_verification.py -r to
   perform another tests.
