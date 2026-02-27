#!/home/ansible/deploy_k8s/k8senv/bin/python
#
#   Create inventory list from all hosts groups vars
#


# Imports
import dotenv, json, pyone, os

# Load Ansible environment variables
dotenv.load_dotenv()

# Global and env variables
vars, vms, nodes, grouped, hostvars = {}, {}, {}, {}, {}
masters_cpu = masters_mem = workers_cpu = workers_mem = master_nodes = worker_nodes = 0
active_env = os.getenv('ACTIVE_ENV').split(' ')
vars['vagrant'] = os.getenv('VAGRANT').split(' ')
vars['iaas'] = os.getenv('IAAS').split(' ')
iaas_url = os.getenv('IAAS_URL')
iaas_user = os.getenv('IAAS_USER')
iaas_pass = os.getenv('IAAS_PASS')
proxy_nodes = int(os.getenv('PROXY_NODES'))
proxy_cpu = int(os.getenv('PROXY_CPU'))
proxy_mem = int(os.getenv('PROXY_MEM'))

# Meta (hostvars) group
nodes['_meta'] = {}
nodes['_meta']['hostvars'] = {}

# Local group
nodes['local'] = {}
nodes['local']['hosts'] = []
nodes['local']['hosts'].append('localhost')
nodes['local']['vars'] = { 'ansible_connection': 'local', 'ansible_python_interpreter': '/usr/bin/python' }

# Proxies group
nodes['proxies'] = {}
nodes['proxies']['hosts'] = []

# Masters group
nodes['masters'] = {}
nodes['masters']['hosts'] = []

# Workers group
nodes['workers'] = {}
nodes['workers']['hosts'] = []

# Inventory vars
for g in active_env:
# for g in vars.keys():
    vm_prefix = vars[g][0]
    domain = vars[g][1]
    default_user = vars[g][2]
    masters_cpu = int(vars[g][3])
    masters_mem = int(vars[g][4])
    subnet = ''
    workers_cpu = workers_mem = master_nodes = worker_nodes = 0
    if (len(vars[g])) > 5:
        subnet = vars[g][5]
        workers_cpu = int(vars[g][6])
        workers_mem = int(vars[g][7])
        master_nodes = int(vars[g][8])
        worker_nodes = int(vars[g][9])

    # Given environment group
    grouped[g] = {}
    grouped[g]['proxies'] = []
    grouped[g]['masters'] = []
    grouped[g]['workers'] = []
    nodes[g] = {}
    nodes[g]['hosts'] = []

    # Load OpenNebula (TeideHPC) data
    if g == 'iaas':
        one = pyone.OneServer(iaas_url + '/RPC2', session=iaas_user + ':' + iaas_pass, https_verify=False)
        vm_pool = one.vmpool.info(-3, -1, -1, -1)
        num_vms = len(vm_pool.VM)
        master_nodes = 3
        if num_vms < 6:
            master_nodes = 1
        worker_nodes = num_vms - master_nodes - 1
        i = 0
        vms[g] = {}
        for vm in vm_pool.VM:
            id = vm_pool.VM[i].ID
            vms[g][id] = {}
            vms[g][id]['name'] = vm_pool.VM[i].NAME
            data = dict(vm_pool.VM[i].TEMPLATE)
            vms[g][id]['cpu'] = int(data['CPU'])
            vms[g][id]['mem'] = int(data['MEMORY'])
            vms[g][id]['ip'] = data['NIC'][0]['IP'] if isinstance(data['NIC'], list) else data['NIC']['IP']
            i += 1
        # Proxy hosts
        for p in range(1, proxy_nodes + 1):
            n = f"0{p}" if p < 10 else f"{p}"
            nodename = vm_prefix + f"proxy{n}." + domain
            grouped[g]['proxies'].append(nodename)
            nodes['proxies']['hosts'].append(nodename)
            nodes[g]['hosts'].append(nodename)
            # print(f"Proxies: {grouped[g]['proxies']}")

    # Master hosts
    for m in range(1, master_nodes + 1):
        n = f"0{m}" if m < 10 else f"{m}"
        nodename = vm_prefix + f"master{n}." + domain
        grouped[g]['masters'].append(nodename)
        nodes['masters']['hosts'].append(nodename)
        nodes[g]['hosts'].append(nodename)
        # print(f"Masters: {grouped[g]['masters']}")

    # Worker hosts
    for w in range(1, worker_nodes + 1):
        n = f"0{w}" if w < 10 else f"{w}"
        nodename = vm_prefix + f"node{n}." + domain
        grouped[g]['workers'].append(nodename)
        nodes['workers']['hosts'].append(nodename)
        nodes[g]['hosts'].append(nodename)
        # print(f"Workers: {grouped[g]['workers']}")

    # Load local Vagrant data
    if g == 'vagrant':
        i = n = 0
        vms[g] = {}
        for m in range(master_nodes):
            n = i + 1
            vms[g][i] = {}
            nodename = grouped[g]['masters'][m]
            vms[g][i]['name'] = nodename.replace("." + domain, "")
            vms[g][i]['cpu'] = masters_cpu
            vms[g][i]['mem'] = masters_mem
            vms[g][i]['ip'] = f"{subnet}{n}"
            i += 1
        for w in range(worker_nodes):
            n = i + 1
            vms[g][i] = {}
            nodename = grouped[g]['workers'][w]
            vms[g][i]['name'] = nodename.replace("." + domain, "")
            vms[g][i]['cpu'] = workers_cpu
            vms[g][i]['mem'] = workers_mem
            vms[g][i]['ip'] = f"{subnet}{n}"
            i += 1

    # Set IPs and other variables for every node in _meta hostvars group
    p = m = w = 0
    for id in sorted(vms[g]):
        if g == 'iaas' and p < proxy_nodes and vms[g][id]['cpu'] == proxy_cpu and vms[g][id]['mem'] == proxy_mem:
            h = grouped[g]['proxies'][p]
            hostvars[h] = {}
            p += 1
        elif m < master_nodes and vms[g][id]['cpu'] == masters_cpu and vms[g][id]['mem'] == masters_mem:
            h = grouped[g]['masters'][m]
            hostvars[h] = {}
            m += 1
        elif w < worker_nodes:
            h = grouped[g]['workers'][w]
            hostvars[h] = {}
            w += 1
        hostvars[h]['name'] = vms[g][id]['name']
        hostvars[h]['cpu'] = vms[g][id]['cpu']
        hostvars[h]['mem'] = vms[g][id]['mem']
        hostvars[h]['ansible_host'] = vms[g][id]['ip']
        hostvars[h]['def_user'] = default_user

nodes['_meta']['hostvars'] = hostvars

print(json.dumps(nodes))

