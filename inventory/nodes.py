#!/usr/bin/python
#
#   Create inventory list from all group vars
#


# Imports
import json

# Inventory vars
var = {}
with open("inventory/group_vars/all/vars.yaml") as conf:
    for line in conf:
        if ":" in line:
            name, value = line.split(":")
            var[name] = str(value).replace(" ", "").rstrip()

vm_prefix = var["VM_PREFIX"].replace('"', '')
domain = var["DOMAIN"].replace('"', '')
master_nodes = int(var["MASTER_NODES"])
worker_nodes = int(var["WORKER_NODES"])

# Inventory in JSON format
nodes = {}

# Local group
nodes['local'] = {}
nodes['local']['hosts'] = []
nodename = "localhost"
nodes['local']['hosts'].append(nodename)
nodes['local']['vars'] = { 'ansible_connection': 'local', 'ansible_python_interpreter': '/usr/bin/python' }

# Masters group
nodes['masters'] = {}
nodes['masters']['hosts'] = []
for m in range(1, int(master_nodes) + 1):
    n = f"0{m}" if m < 10 else f"{m}"
    nodename = vm_prefix + f"master{n}." + domain
    nodes['masters']['hosts'].append(nodename)

# Workers group
nodes['workers'] = {}
nodes['workers']['hosts'] = []
for w in range(1, int(worker_nodes) + 1):
    n = f"0{w}" if w < 10 else f"{w}"
    nodename = vm_prefix + f"node{n}." + domain
    nodes['workers']['hosts'].append(nodename)

print(json.dumps(nodes))
