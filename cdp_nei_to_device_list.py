import re 
import sys
import string
import json
import os

from getpass import getpass
from netmiko import ConnectHandler
from netmiko.ssh_exception import NetMikoTimeoutException
from paramiko.ssh_exception import SSHException
from netmiko.ssh_exception import AuthenticationException

##############################################
# Request username and password for SSH
#

username = input('Enter your SSH username: ')
password = getpass()

##############################################
# Open device list
#

with open('cdp_test') as f:
    device_list = f.read().splitlines()

##############################################
# Define variables
#

device = ""
mgmt_address = ""

##############################################
# For each entry in device list repeat the
# following
#

for devices in device_list:
    print("Gathering cdp information from device " + devices)
    ip_address = devices
    ios_device = {
            'device_type': 'cisco_ios',
            'ip': ip_address,
            'username': username,
            'password': password
    }

###############################################
# Exception handlings
#

    try:
        net_connect = ConnectHandler(**ios_device)
    except (AuthenticationException):
        print ('Authentication failure: ' + ip_address)
        continue
    except (NetMikoTimeoutException):
        print ('Timeout to device: ' + ip_address)
        continue
    except (EOFError):
        print ("End of file while attempting device " + ip_address)
        continue
    except (SSHException):
        print ('SSH Issue. Are you sure SSH is enabled? ' + ip_address)
        continue
    except Exception as unknown_error:
        print ('Some other error: ' + str(unknown_error))
        continue


################################################
# Capture cdp neighbors, use textfsm to grab variables for each entry
#

    neighbors = net_connect.send_command('show cdp neighbor detail', use_textfsm=True)

################################################
# For each line in show cdp nei detail output
# Split out variables and save to file in CSV format
#

    for neighbor in neighbors:
        print(f"{neighbor['destination_host']}, {neighbor['management_ip']}")
        
        with open('cdp_found.txt') as myfile:
            if str(f"{neighbor['destination_host']}") in myfile.read():
                 print("Device has already been discovered, skipping...")
            else:
                 print(f"{neighbor['destination_host']}, {neighbor['management_ip']}", file=open("cdp_found.txt", "a"))
