#!/bin/bash
#
#  Initial configuration for Vagrant local VM's (RHEL 8)
#
# @author	rgonzalez
# @version	v0.1	04/IX/2024
#

set -e

# VM network configuration
NW_PREFIX=$1
ANSIBLE_SSH_AUTH=$2
ADDRESS="$(ip -oneline -4 addr | grep "${NW_PREFIX}" | awk '{print $4}' | cut -d/ -f1)"
sed -i "s/^.*${HOSTNAME}.*/${ADDRESS} ${HOSTNAME} ${HOSTNAME}.local/" /etc/hosts
printf '\n\n[global-dns-domain-*]\nservers=8.8.8.8, 8.8.4.4\n' >> /etc/NetworkManager/NetworkManager.conf
ip -oneline -6 addr | while read line; do d=$(echo ${line} | awk '{print $2}'); echo "net.ipv6.conf.${d}.disable_ipv6 = 1" >> /etc/sysctl.d/80-sysctl.conf; done
sysctl -p >/dev/null
systemctl restart NetworkManager.service

# VM SSH server configuration
#   Centos Stream 9 config:
# echo "PasswordAuthentication no
# PubkeyAuthentication yes" > /etc/ssh/sshd_config.d/10-ansible.conf
# chmod 600 /etc/ssh/sshd_config.d/10-ansible.conf
#   RHEL 8 config:
sed -i 's/^PermitRootLogin yes$/PermitRootLogin no/' /etc/ssh/sshd_config
sed -i 's/^#PubkeyAuthentication yes$/PubkeyAuthentication yes/' /etc/ssh/sshd_config
systemctl restart sshd.service

# VM ansible user creation
sed -i 's/^# *\%wheel/\%wheel/' /etc/sudoers
useradd -b /home -G wheel -m ansible
chmod 755 /home/ansible
sudo -u ansible ssh-keygen -q -t ed25519 -N '' -f /home/ansible/.ssh/id_ed25519 <<<y >/dev/null 2>&1
echo ${ANSIBLE_SSH_AUTH} > /home/ansible/.ssh/authorized_keys
chown -R ansible:ansible /home/ansible/ && chmod 600 /home/ansible/.ssh/authorized_keys

