import re 
import sys
import string

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

with open('interrogate_devices') as f:
    device_list = f.read().splitlines()

##############################################
# Define variables
#

name = ""
desc = ""
pid = ""
vid = ""
serial = ""
hostname = ""
lineno = 0

##############################################
# For each entry in device list repeat the
# following
#

for devices in device_list:
    print("Gathering inventory from device " + devices)
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
# Capture inventory, and split on new line
#

    output = net_connect.send_command('show inventory')
    output_lines = output.split('\n')

################################################
# For each line in show inventory output
# Split out variables and print in CSV format
# on every second line, to ensure two line
# output for a chassis/module is captured
#

    for line in output_lines:
        hostname = devices
        if re.search('DESC', line):
            line1split = line.split(',')
            namefield = line1split[0].strip()
            namesplit = namefield.split(':')
            name = (namesplit[1].strip())
            descfield = line1split[1].strip()
            descsplit = descfield.split(':')
            desc = (descsplit[1].strip())
            lineno = lineno + 1
        elif re.search('PID', line):
            line2split = line.split(',')
            pidfield = line2split[0].strip()
            pidsplit = pidfield.split(':')
            pid = (pidsplit[1].strip())
            vidfield = line2split[1].strip()
            vidsplit = vidfield.split(':')
            vid = (vidsplit[1].strip())
            serialfield = line2split[2].strip()
            serialsplit = serialfield.split(':')
            serial = (serialsplit[1].strip())
            lineno = lineno + 1
        else:
            pass
        if lineno == 2:
            with open('inventory.txt') as myfile:
                if serial in myfile.read():
                    print("Chassis or module serial number already exists in inventory file, skipping...")
                    lineno = 0
                else:
                    print("%s, %s, %s, %s, %s, %s" %(hostname,name,desc,pid,vid,serial), file=open("inventory.txt", "a"))
                    lineno = 0
        else:
            pass

