cvp_deploy
=========

This role takes generated overlay configuration (created by eos_generate role) and deploys it to Arista fabric devices through CVP.

Requirements
------------

arista.cvp along with its requirements, such as cvprac.

Role Variables
--------------

The variables used by this role can be kept in a group vars directory for CVP, in a file called for example devices.yml. The vars file needs to contain a structure like this, containing the devices, their parent container, and a list of configlets to be merged:

    ---
    CVP_DEVICES:
      LEAF1A:
        name: 'LEAF1A'
        parentContainerName: ANSIBLE_TEST
        imageBundle: [] # Not yet supported
        configlets:
            - 'ANSIBLE_OVERLAY_LEAF1A'
      LEAF1B:
        name: 'LEAF1B'
        parentContainerName: ANSIBLE_TEST
        imageBundle: [] # Not yet supported
        configlets:
            - 'ANSIBLE_OVERLAY_LEAF1B'
      LEAF2A:
        name: 'LEAF2A'
        parentContainerName: ANSIBLE_TEST
        imageBundle: [] # Not yet supported
        configlets:
            - 'ANSIBLE_OVERLAY_LEAF2A'
      LEAF2B:
        name: 'LEAF2B'
        parentContainerName: ANSIBLE_TEST
        imageBundle: [] # Not yet supported
        configlets:
            - 'ANSIBLE_OVERLAY_LEAF2B'

It is important to name the devices correctly, change the name parameter and make sure the parent container name matches what has been configured in CVP, and to name the configlet appropriately. The naming scheme for the configlets generated by this role is ANSIBLE_OVERLAY_{{ device }}.

Dependencies
------------

arista.cvp

Example Playbook
----------------

Including an example of how to use your role (for instance, with variables passed in as parameters) is always nice for users too:

    ---
    - name: Generate arista overlay configs
      hosts: CVP
      gather_facts: false

      roles:
      - cvp_deploy

License
-------

BSD

Author Information
------------------

Main author:
Emil Landström, ASE at Arista Networks - emil@arista.com

