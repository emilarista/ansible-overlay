# Overlay Automation

## Summary
The data model and set of roles included in this repo are designed to automate deployment of generic EVPN overlay configuration in a brownfield deployment. For greenfield deployments, arista.avd collection is recommended instead, since it is much more comprehensive and full-featured.

## Intended use
The intended usage is for ansible to manage a configlet on CVP for each fabric device containing this configuration. This configlet can coexist with any other overlay or underlay configuration, as long as vni assignments, vlan numbers, etc doesn't overlap. It is meant to function as an easy, entry-level way of automating part (or all) of your overlay configuration with ansible.

There is also a mechanism included to deploy the configuration directly to the switches via API. However, this is less desireable since only additive changes can be deployed if you're not managing your entire device config with ansible.

## Included files
An example inventory file is included, along with group and host vars files/folder structure plus example playbooks, both for deploying via CVP and directly via API.

## Requirements
The arista.cvp collection along with its dependencies is required for this to work, so install it before you continue:

    ansible-galaxy collection install arista.cvp

# Roles

The roles use information provided in group_vars and host_vars. This a tree view of the vars folder/file structure that is included in this repo as an example:

    ...
    |-- group_vars
    |   |-- CVP
    |   |   `-- devices.yml
    |   |-- leaf
    |   |   `-- overlay.yml
    |   |-- leaf1
    |   |   `-- leaf1.yml
    |   `-- leaf2
    |       `-- leaf2.yml
    |-- host_vars
    |   |-- LEAF1A.yml
    |   |-- LEAF1B.yml
    |   |-- LEAF2A.yml
    |   `-- LEAF2B.yml
    ...

## eos_generate
Used to generate the cli configuration for the configlets based on the vars included in the group_vars/leaf/overlay.yml file, host vars files and the group_vars/leaf1/leaf1.yml and ..../leaf2/leaf2.yml files.

The main template for this role is the templates/overlay.j2 template, which serves as a master index, and includes subtemplates located in templates/overlay/ directory.

Tasks:

1. The role loops through all hosts in the "leaf" inventory host group, renders the overlay.j2 template for each device and puts the result in files/{{ inventory_hostname }}_overlay.

### Playbook example:

    ---
    - name: Generate arista overlay configs
    hosts: leaf
    gather_facts: false
    
    roles:
    - eos_generate

## cvp_deploy
This role is designed to take the raw config generated with eos_generate and put it into configlets, push the configlets to a CVP instance, attach the configlets to the proper devices if needed and execute the resulting tasks, pushing the configuration to the fabric devices.

Tasks:

1. Vars are extracted from the group_vars/CVP/devices.yml file and the info is used to render the templates/configlet.j2 template. The result is registered to a variable to be used for conditional execution later.
2. The resulting CONFIGLETS.yml file is included with include_vars and basically just points to the files generated by the eos_generate role.
3. Facts are gathered from the CVP instance to be used in step 4.
4. Configlets are uploaded to the CVP instance. The result is registered to a variable to be used for conditional execution later.
5. Facts from CVP instance are refreshed.
6. (Only happens if task 1 results changed, typically at first execution or if a device is added). Devices are configured on the CVP instance. Configlets are attached to devices and they are put in the specified parent folder (hopefully not resulting in a device move).
7. Facts are refreshed from CVP to get pending tasks generated by task 4 and 6.
8. Pending tasks are executed and configuration is pushed to CVP.

If desired the last 2 tasks can be omitted and you can do a manual change control procedure instead.

### Playbook example:

    ---
    - name: Generate arista overlay configs
    hosts: leaf
    gather_facts: false
    
    roles:
    - eos_generate

    - name: Push configlets to CVP
    hosts: CVP
    gather_facts: false

    roles:
    - cvp_deploy

## api_deploy
This role can be used instead of cvp_deploy in order to deploy the changes directly to the devices via API. It uses the standard eos_config module, takes a backup of the configuration and places it in the backups folder, then pushes the changes line for line to the device.

Connection parameters for connecting to the Arista switches are placed in the role vars/main.yml file.

### Playbook example:

    ---
    - name: Generate arista overlay configs
    hosts: leaf
    gather_facts: false
    
    roles:
    - eos_generate

    - name: Generate arista overlay configs
    hosts: leaf
    gather_facts: true

    roles:
    - api_deploy

