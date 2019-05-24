ansible-playbook playbook-for-preparenet.yml
ansible-playbook playbook-for-clonecomponents.yml
ansible-playbook playbook-for-bootvm.yml
ansible-playbook -i hosts playbook-for-uploadscript.yml
