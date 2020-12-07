from jinja2 import Template
import sys
import yaml
import json
import os

clear = lambda: os.system('clear')

def to_json(input):
    return json.dumps(input, indent = 2, sort_keys=True)

config_loaded = False

while True:
    clear()
    print("#"*15+" MAIN MENU "+"#"*15)
    if config_loaded == True:
        print("Successfully loaded existing project, now you can add to it!")
    
    mode = input("""Do you want to 
    1. Generate new fabric variables
    2. Open past project
    x. Exit

    :""")
    if mode == "1":
        mode = "create"
        if config_loaded == False:
            config = { 
                "devices": {
                    "leaf": {},
                    "CVP": {},
                },
                "overlay": {
                    "tenants": {}
                }
            }
        break

    elif mode == "2":
        try:
            with open("project.json", "r") as f:
                config = json.load(f)
                config_loaded = True

        except:
            print("Did not find any existing project file... Sorry.")
            prompt = input("Press return to continue: ")

    elif mode == "x":
        sys.exit()

    else:
        continue

while True: 
    clear()
    print("#"*15+" GENERATE VARIABLES "+"#"*15)

    prompt = input("""Add a device (leafs and CVP), or exit once you're done.
    1. Add a device
    2. Add overlay definition
    x. Exit

: """)
    if prompt == "1":
        while True:
            clear()
            print("#"*15+" ADD DEVICE "+"#"*15)
            dev_type    = input("""leaf or CVP?: 
    1. leaf
    2. CVP

: """)
            if dev_type == "1":
                dev_type = "leaf"
                break
            elif dev_type == "2":
                dev_type = "CVP"
                break
            else:
                continue
        
        dev_name    = input("Provide device name: ")
        dev_ip      = input("Provide device mgmt IP: ")
        cvp         = input("Are you using CVP? [Y/n]: ")

        if (str(cvp) and str(cvp.lower())[0] == "y") or not cvp:
            parent_folder = input("What is the devices' parent container name?: ")
        
        if dev_type == "leaf":
            bgp_asn = input("Please input device bgp ASN: ")
            rd_base = input("Please input device route distinguisher base, typically BGP loopback IP: ")

        config["devices"][dev_type][dev_name] = {}
        config["devices"][dev_type][dev_name]["mgmt_ip"] = dev_ip

        if dev_type == "leaf":
            config["devices"][dev_type][dev_name]["bgp_asn"] = bgp_asn
            config["devices"][dev_type][dev_name]["rd_base"] = rd_base
        
        while True:
            print("Devices dict updated, this is the current status: ")
            print(to_json(config))
            save = input("""Save and continue or discard?
    1. Save
    2. Discard

: """)
            if save == "1":
                with open("project.json", "w") as f:
                    f.write(to_json(config))
                break
            else:
                config["devices"][dev_type][dev_name] = {}
                break

    elif prompt == "2":
        while True:
            clear()
            print("#"*15+" OVERLAY CONFIGURATION "+"#"*15)
            action = input("""Add overlay configuration
            1. Add tenant (vrf)
            2. Add VLAN to existing tenant
            x. Exit
: """)
            if action == "1":
                print("################")
                tenant_name = input

    elif prompt == "x":
        sys.exit()





