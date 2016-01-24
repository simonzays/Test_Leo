# -*- mode: ruby -*-
# vi: set ft=ruby :

# You can define the number of webserver nodes you want to start
NODE_COUNT = 3

# Generating and storing the ips for the nodes
# it can handle more than 255 nodes
require 'ipaddr'
start_ip = IPAddr.new "172.16.1.10"
node_ips = []
NODE_COUNT.times do |i|
    ip = start_ip.to_i + i
    nip = [24, 16, 8, 0].collect {|b| (ip >> b) & 255}.join('.')
    # we will pass this to the lb config
    node_ips << nip
end
node_ips_list = node_ips.join(",")


VAGRANTFILE_API_VERSION = "2"
Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.provider "virtualbox" do |v|
    v.customize ["modifyvm", :id, "--memory", 256]
    v.customize ["modifyvm", :id, "--cpus", 1]
  end
  config.ssh.forward_agent = true
  config.ssh.insert_key = false
  config.vm.box_url = "https://dl.dropboxusercontent.com/u/197673519/debian-7.2.0.box"
  config.vm.box = "debian-7.2.0"

  # this is needed because the base box i'm using is crocked
  config.vm.provision "shell", inline: "apt-get update"


  NODE_COUNT.times do |i|
    nid = "n#{i}"
    config.vm.define nid do |node|
      node.vm.hostname = "#{nid}"
      node.vm.network "private_network", ip: node_ips[i]
      # it provisions all the nodes together in one run
      if i == NODE_COUNT-1
        node.vm.provision "ansible" do |ansible|
          ansible.limit = 'all'
          ansible.verbose = "v"
          ansible.playbook = "provisioning/playbook.yml"
          ansible.extra_vars = {
            nginx: {
              role: "node",
            }
          }
        end
      end
    end
  end

  config.vm.define "lb" do |lb|
    lb.vm.hostname = "lb"
    lb.vm.network "private_network", ip: "172.16.0.10"
    lb.vm.network "forwarded_port", guest: 80 ,host: 8080

    lb.vm.provision "ansible" do |ansible|
      ansible.verbose = "v"
      ansible.playbook = "provisioning/playbook.yml"
      ansible.extra_vars = {
        node_ips: "#{node_ips_list}",
        nginx: {
          role: "lb"
        }
      }
    end
  end

end
