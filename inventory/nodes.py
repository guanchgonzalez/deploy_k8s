#!/home/ansible/deploy_k8s/.environ/bin/python
#
#   Create inventory list from all hosts groups vars
#


# Imports
import dotenv, json, pyone, os

# Load Ansible environment variables
dotenv.load_dotenv()

# Global and env variables
vars, one_vms, nodes, grouped, hostvars = {}, {}, {}, {}, {}
vars['vagrant'] = os.getenv('VAGRANT').split(' ')
vars['iaas'] = os.getenv('IAAS').split(' ')
iaas_url = os.getenv('IAAS_URL')
iaas_user = os.getenv('IAAS_USER')
iaas_pass = os.getenv('IAAS_PASS')
masters_cpu = int(os.getenv('MASTERS_CPU'))
masters_mem = int(os.getenv('MASTERS_MEM'))
default_user = os.getenv('DEF_USER')

# Meta (hostvars) group
nodes['_meta'] = {}
nodes['_meta']['hostvars'] = {}

# Local group
nodes['local'] = {}
nodes['local']['hosts'] = []
nodes['local']['hosts'].append('localhost')
nodes['local']['vars'] = { 'ansible_connection': 'local', 'ansible_python_interpreter': '/usr/bin/python' }

# Masters group
nodes['masters'] = {}
nodes['masters']['hosts'] = []

# Workers group
nodes['workers'] = {}
nodes['workers']['hosts'] = []

# Open OpenNebula session
one = pyone.OneServer(iaas_url + '/RPC2', session=iaas_user + ':' + iaas_pass, https_verify=False)

# Load OpenNebula (TeideHPC) data
vm_pool = one.vmpool.info(-3, -1, -1, -1)
num_vms = len(vm_pool.VM)
vars['iaas'].append(3)
if num_vms < 6:
    vars['iaas'][2] = 1
vars['iaas'].append(num_vms - vars['iaas'][2])
i = 0
for vm in vm_pool.VM:
    id = vm_pool.VM[i].ID
    one_vms[id] = {}
    one_vms[id]['one_name'] = vm_pool.VM[i].NAME
    data = dict(vm_pool.VM[i].TEMPLATE)
    one_vms[id]['cpu'] = int(data['CPU'])
    one_vms[id]['mem'] = int(data['MEMORY'])
    one_vms[id]['ip'] = data['NIC'][0]['IP'] if isinstance(data['NIC'], list) else data['NIC']['IP']
    i += 1

# Inventory vars
for g in vars.keys():
    VM_PREFIX = vars[g][0]
    DOMAIN = vars[g][1]
    MASTER_NODES = vars[g][2]
    WORKER_NODES = vars[g][3]

    # Given environment group
    grouped[g] = {}
    grouped[g]['masters'] = []
    grouped[g]['workers'] = []
    nodes[g] = {}
    nodes[g]['hosts'] = []

    # Master hosts
    for m in range(1, int(MASTER_NODES) + 1):
        n = f"0{m}" if m < 10 else f"{m}"
        nodename = VM_PREFIX + f"master{n}." + DOMAIN
        grouped[g]['masters'].append(nodename)
        nodes['masters']['hosts'].append(nodename)
        nodes[g]['hosts'].append(nodename)

    # Workers hosts
    for w in range(1, int(WORKER_NODES) + 1):
        n = f"0{w}" if w < 10 else f"{w}"
        nodename = VM_PREFIX + f"node{n}." + DOMAIN
        grouped[g]['workers'].append(nodename)
        nodes['workers']['hosts'].append(nodename)
        nodes[g]['hosts'].append(nodename)

# Set IPs and other variables for OpenNebula nodes in _meta hostvars group
m = w = 0
for id in sorted(one_vms):
    if m < vars['iaas'][2] and one_vms[id]['cpu'] == masters_cpu and one_vms[id]['mem'] == masters_mem:
        h = grouped['iaas']['masters'][m]
        hostvars[h] = {}
        hostvars[h]['one_name'] = one_vms[id]['one_name']
        hostvars[h]['ansible_host'] = one_vms[id]['ip']
        hostvars[h]['def_user'] = default_user
        m += 1
    else:
        if w < vars['iaas'][3]:
            h = grouped['iaas']['workers'][w]
            hostvars[h] = {}
            hostvars[h]['one_name'] = one_vms[id]['one_name']
            hostvars[h]['ansible_host'] = one_vms[id]['ip']
            hostvars[h]['def_user'] = default_user
            w += 1
nodes['_meta']['hostvars'] = hostvars

print(json.dumps(nodes))

