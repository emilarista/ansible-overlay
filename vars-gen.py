from jinja2 import Template
import sys
import yaml
import json
import os
from pathlib import Path

rootpath = "."

clear = lambda: os.system('clear')

def to_json(input):
    return json.dumps(input, indent = 2, sort_keys=True)

def save_config():
    with open("project.json", "w") as f:
        f.write(to_json(config))

config_loaded = False


def add_vlan(config, tenant_name):
    vlan_id = input("Vlan ID: ")
    vlan_name = input("Vlan name: ")
    vlan_l3 = input("Will vlan have an SVI? [Y/n]: ")
    if vlan_l3 and vlan_l3[0].lower() == "n":
        vlan_l3 = False
    else:
        vlan_l3 = True
    vlan = {
        "name": vlan_name,
        "vlan_l3": vlan_l3
    }   
    if vlan_l3 == True:
        vlan_ip = input("Input Vlan SVI IP (like 10.0.0.1/24): ")
        vlan_mask = vlan_ip.split("/")[1]
        vlan_ip = vlan_ip.split("/")[0]
        host_export = input("Export host routes? [y/N]: ")
        if host_export[0].lower() == "y":
            host_export = True
        else:
            host_export = False
        
        vlan["ip"] = vlan_ip
        vlan["mask"] = vlan_mask
        vlan["host_route_export"] = host_export
    
    config["overlay"]["tenants"][tenant_name]["vlans"][vlan_id] = vlan
    return config

    
def generate_hostvars(config):
    # Creating folders
    Path(rootpath+"/group_vars/CVP").mkdir(parents=True, exist_ok=True)
    Path(rootpath+"/group_vars/leaf").mkdir(parents=True, exist_ok=True)
    Path(rootpath+"/host_vars").mkdir(parents=True, exist_ok=True)

    # Create devices.yml dict from config:
    devices = {
        "CVP_DEVICES": {}
    }
    for device, devicedata in config["devices"]["leaf"].items():
        devicedict = {
            "name": device,
            "parentContainerName": devicedata["parent_container"],
            "imageBundle": [],
            "configlets": ["ANSIBLE_OVERLAY_{}".format(device)]
        }
        devices["CVP_DEVICES"][device] = devicedict

    # Dump to CVP/devices.yml
    with open(rootpath+"/group_vars/CVP/devices.yml", "w") as f:
        f.write("---\n")
        f.write(yaml.dump(devices))
    
    # Writing hostvars for the devices
    for device, devicedata in config["devices"]["leaf"].items():
        hostvars = """
bgp_asn: {}
rd_base: {}
""".format(devicedata["bgp_asn"], devicedata["rd_base"])

        with open(rootpath+"/host_vars/{}.yml".format(device), "w") as f:
            f.write("---")
            f.write(hostvars)
    
    # Dumping the overlay config to yaml file.
    with open(rootpath+"/group_vars/leaf/overlay.yml", "w") as f:
        f.write("---\n")
        f.write(yaml.dump(config["overlay"]))


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
    3. Dump config to host/group vars folder structure (will be placed in cwd)
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
            config["devices"][dev_type][dev_name]["parent_container"] = parent_folder
        
        while True:
            print("Devices dict updated, this is the current status: ")
            print(to_json(config))
            save = input("""Save and continue or discard?
    1. Save
    2. Discard

: """)
            if save == "1":
                save_config()
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
            3. Back to main menu
            x. Save and exit
: """)
            if action == "1":
                print("################")
                tenant_name = input("Tenant name: ")
                ten_vni_base = input("Tenant vlan vni base: ")
                ten_vrf_vni = input("Tenant vrf vni: ")
                rt_base = input("Route target base (will be used like <base>:<base>): ")
                redist_host = input("Redistribute hostroutes? [y/N]: ")
                if redist_host[0].lower() == "y":
                    redist_host = True
                else:
                    redist_host = False

                tenant = {
                    "vrf_vni_base": ten_vrf_vni,
                    "vlan_vni_base": ten_vni_base,
                    "redist_hostroutes": redist_host,
                    "route_target": rt_base,
                    "vlans": {}
                }

                config["overlay"]["tenants"][tenant_name] = tenant

                addvlans = input("Add vlans to tenant now? [Y/n]: ")
                if addvlans and addvlans[0].lower() == "n":
                    while True:
                        print("Tenants dict updated, this is the current overlay state: ")
                        print(to_json(config["overlay"]))
                        save = input("""Save and continue or discard?
    1. Save
    2. Discard

: """)
                        if save == "1":
                            save_config()
                            break
                        else:
                            del config["overlay"]["tenants"][tenant_name]
                            break
                else:
                    while True:
                        clear()
                        print("#"*15+" TENANT {} VLANS ".format(tenant_name)+"#"*15)
                        config = add_vlan(config, tenant_name)
                        another = input("Add another? [Y/n]")
                        if another[0].lower() == "n":
                            save = input("Ok, saving overlay state, press any key to continue: ")
                            save_config()
                            break
                        else:
                            continue

            elif action == "2":
                print("################")
                print("Ok, these are the available tenants: ")
                for tenant in config["overlay"]["tenants"]:
                    print("* "+tenant)

                chosen_tenant = input("Which tenant do you want to add to?: ")
                if chosen_tenant in config["overlay"]["tenants"]:
                    while True:
                        config = add_vlan(config, chosen_tenant)
                        add_another = input("Add another? [Y/n]: ")
                        if add_another and add_another[0].lower() == "n":
                            save_config()
                            break
                        else:
                            save_config()
                            continue
                else:
                    print("Sorry, the tenant you specified doesn't exist, try again.")

            elif action == "3":
                save_config()
                break

            elif action == "x":
                save_config()
                sys.exit()

    elif prompt == "3":
        generate_hostvars(config)

    elif prompt == "x":
        sys.exit()





