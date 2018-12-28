# appsynthesizer
Application Synthesizer

There are several assumptions here to be noted:
1. Host or management node should has Ansible installed already, recommended version is 2.5.2
2. Inside /etc/ansible/ansible.cfg modify this line
   [default]
   inventory=/path/to/host/file/inside/the/clone/directory
   host_key_checking=False
3. There will be new network created "prepnet" which will be fully used by this project. It is DHCP and NAT forwarding with IP 192.168.0.1/24
4. Forwarder only considers 1 db server as its branchout
5. The platform OS of the components is CentOS7
6. New folder will be created in the management node "/home/synthesizer" contains all the XMLs file of component, the image of component, and the XML file of the "prepnet" network
7. All the components (socket-based) are running at port 8011
8. The access to the component's machine: root/123
9. Because this project uses KVM, make sure it is installed already
10. Make sure that python-libvirt and python-lxml already exist in the host node
11. Make sure the three images already placed inside roles/clonecomponents/files/


https://drive.google.com/drive/folders/1xUj0f5l5E6i0MeTf1up9fsDif-KrNxFG?ogsrc=32
