#!/home/ansible/deploy_k8s/.environ/bin/python
#
#   Create inventory list from all hosts groups vars
#


# Imports
import dotenv, json, os

# Load Ansible environment variables
dotenv.load_dotenv()

# Global variables
vars, nodes = {}, {}
vars['vagrant'] = os.getenv('VAGRANT').split(' ')
vars['iaas'] = os.getenv('IAAS').split(' ')

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
for e in vars.keys():
    VM_PREFIX = vars[e][0]
    DOMAIN = vars[e][1]
    MASTER_NODES = vars[e][2]
    WORKER_NODES = vars[e][3]

    # Given environment group
    nodes[e] = {}
    nodes[e]['hosts'] = []

    # Master hosts
    for m in range(1, int(MASTER_NODES) + 1):
        n = f"0{m}" if m < 10 else f"{m}"
        nodename = VM_PREFIX + f"master{n}." + DOMAIN
        nodes['masters']['hosts'].append(nodename)
        nodes[e]['hosts'].append(nodename)

    # Workers hosts
    for w in range(1, int(WORKER_NODES) + 1):
        n = f"0{w}" if w < 10 else f"{w}"
        nodename = VM_PREFIX + f"node{n}." + DOMAIN
        nodes['workers']['hosts'].append(nodename)
        nodes[e]['hosts'].append(nodename)

print(json.dumps(nodes))
