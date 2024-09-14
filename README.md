<!--Repo Readme file in HTML format-->

<h1><b>Deployment of a Kubernetes cluster with Ansible</b></h1>

<p>There are two ways to deploy: for <b>development and testing</b> purposes on a local environment, the <b>Vagrant + VirtualBox</b> choice; for <b>production</b> purposes, the VM's will be delivered by an <b>external IaaS</b> provider and the Ansible playbook will implement the task from this point.</p>

<h3><b>Prerequisites for a Vagrant deployment with local VM's of a Kubernetes cluster</b></h3>

<p>Instructions based on this documentation:</p>

<p><a href="https://developer.hashicorp.com/vagrant/tutorials/getting-started/getting-started-index" title="Vagrant documentation">How to install and deploy Vagrant VMs</a></p>

<p>Execute these shell commands in your Fedora or RedHat based host machine (notebook) with <b><i>root</i></b> user.</p>

<ol>

  <li> Install Virtualbox:
    <div style="margin:10px;padding:10px;background-color:#f4f4f4;font-family: 'Courier New', Courier, monospace">
      <pre><code class="language-shell">echo "[virtualbox]
name=Fedora \$releasever - \$basearch - VirtualBox
baseurl=http://download.virtualbox.org/virtualbox/rpm/fedora/\$releasever/\$basearch
enabled=1
gpgcheck=1
repo_gpgcheck=1
gpgkey=https://www.virtualbox.org/download/oracle_vbox_2016.asc" > /etc/yum.repos.d/virtualbox.repo

dnf -y update
dnf -y upgrade
dnf -y install virtualbox</code></pre>
    </div>
    <p>If you get the <code>vboxdrv.sh: You must sign these kernel modules before using VirtualBox</code> error during the installation, disable the UEFI Secure Boot in your BIOS.</p>
  </li>

  <li> Install Vagrant:
    <div style="margin:10px;padding:10px;background-color:#f4f4f4;font-family: 'Courier New', Courier, monospace">
      <pre><code class="language-shell">dnf install -y dnf-plugins-core
dnf config-manager --add-repo https://rpm.releases.hashicorp.com/fedora/hashicorp.repo
dnf -y install vagrant</code></pre>
    </div>
  </li>

</ol>

<h3><b>Common installation and execution tasks</b></h3>

<p>Execute these shell commands in your Fedora or RedHat based host machine (notebook) with <b><i>root</i></b> user.</p>

<ol>

  <li> Install Ansible:
    <div style="margin:10px;padding:10px;background-color:#f4f4f4;font-family: 'Courier New', Courier, monospace">
      <pre><code class="language-shell">dnf install ansible</code></pre>
    </div>
  </li>

  <li> Create management user for Ansible:
    <div style="margin:10px;padding:10px;background-color:#f4f4f4;font-family: 'Courier New', Courier, monospace">
      <pre><code class="language-shell">useradd -b /home -m -G wheel ansible</code></pre>
    </div>
  </li>

</ol>

<p>Execute these steps in your Fedora or RedHat based host machine (notebook) with the new management user:</p>

<ol>

  <li> Clone this repo:
    <div style="margin:10px;padding:10px;background-color:#f4f4f4;font-family: 'Courier New', Courier, monospace">
      <pre><code class="language-shell">git clone git@github.com:guanchgonzalez/deploy_k8s.git</code></pre>
    </div>
  </li>

<li> Create a soft link of the proper main playbook: <b><i>site_vagrant.yaml</i></b> for the local deployment or <b><i>site_iaas.yaml</i></b> for the IaaS deployment.
    <div style="margin:10px;padding:10px;background-color:#f4f4f4;font-family: 'Courier New', Courier, monospace">
      <pre><code class="language-shell">cd deploy_k8s
ln -s [site_vagrant.yaml|site_iaas.yaml] site.yaml</code></pre>
    </div>
  </li>  

  <li> Execute the Ansible playbook
    <div style="margin:10px;padding:10px;background-color:#f4f4f4;font-family: 'Courier New', Courier, monospace">
      <pre><code class="language-shell">ansible-playbook site.yaml</code></pre>
    </div>
  </li>

</ol>

