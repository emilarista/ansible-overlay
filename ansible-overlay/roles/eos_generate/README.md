eos_generate
=========

A role used to generate Arista EOS overlay configuration for a pre-existing EVPN fabric.

Requirements
------------

Nothing special for this role. However, the cvp_deploy role used in conjunction with this one uses arista.cvp collection.

Role Variables
--------------

This role relies on mainly host- and group variables that are used for j2 template rendering. A hostvars file is required for each individual leaf, containing the following variables:

rd_base - set to the leafs loopback address

A group vars file is needed for each mlag leaf pair, containing the following variables:

bgp_asn - BGP Autonomous system number

Most of the variables that are used to generate the configuration are set in the overlay.yml groupvars file for the leaf group (containing all leafs). This file is used to generate overlay configuration based on a datamodel of vrfs (tenants) containing vlans, along with vni mappings and other parameters. The file could look like this (more tenants or vlans can be added as per your requirements):

    tenants:
      RED:
        vrf_vni: 50001
        vlan_vni_base: 10000
        tenant_tag: red
        vlan_aware_bundle: true
        redist_hostroutes: yes
        route_target: 10
        vlans:
          10: 
            name: RED_WEB
            l3: true
            ip: 10.10.0.1
            host_route_export: yes
            mask: 24
            tags: 
              - web
          11:
            name: RED_APP
            l3: true
            ip: 10.11.0.1
            host_route_export: no
            mask: 24
            tags:
              - app
          12:
            name: RED_VMOTION
            l3: false
            tags:
              - vmotion


Dependencies
------------

None at the moment since this is just rendering a j2 template with some variables.

Example Playbook
----------------

    ---
    - name: Generate arista overlay configs
      hosts: leaf
      gather_facts: false
      
      roles:
      - eos_generate

License
-------

BSD

Author Information
------------------

Main author:
Emil Landström, ASE at Arista Networks - emil@arista.com
