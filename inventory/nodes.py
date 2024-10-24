#!/usr/bin/python
#
#   Create inventory list from all hosts groups vars
#


# Imports
import json

# Global variables
var, nodes = {}, {}
environ = ['vagrant', 'iter']

# Local group
nodes['local'] = {}
nodes['local']['hosts'] = []
nodename = "localhost"
nodes['local']['hosts'].append(nodename)
nodes['local']['vars'] = { 'ansible_connection': 'local', 'ansible_python_interpreter': '/usr/bin/python' }

# Masters group
nodes['masters'] = {}
nodes['masters']['hosts'] = []

# Workers group
nodes['workers'] = {}
nodes['workers']['hosts'] = []

# Inventory vars
for e in environ:
    var[e] = {}
    with open('group_vars/' + e + '/vars.yaml') as conf:
        for line in conf:
            if ":" in line:
                name, value = line.split(":")
                var[e][name] = str(value).replace(" ", "").rstrip()

    vm_prefix = var[e]["VM_PREFIX"].replace('"', '')
    domain = var[e]["DOMAIN"].replace('"', '')
    master_nodes = int(var[e]["MASTER_NODES"])
    worker_nodes = int(var[e]["WORKER_NODES"])

    # Given environment group
    nodes[e] = {}
    nodes[e]['hosts'] = []

    # Master hosts
    for m in range(1, int(master_nodes) + 1):
        n = f"0{m}" if m < 10 else f"{m}"
        nodename = vm_prefix + f"master{n}." + domain
        nodes['masters']['hosts'].append(nodename)
        nodes[e]['hosts'].append(nodename)

    # Workers hosts
    for w in range(1, int(worker_nodes) + 1):
        n = f"0{w}" if w < 10 else f"{w}"
        nodename = vm_prefix + f"node{n}." + domain
        nodes['workers']['hosts'].append(nodename)
        nodes[e]['hosts'].append(nodename)

print(json.dumps(nodes))
