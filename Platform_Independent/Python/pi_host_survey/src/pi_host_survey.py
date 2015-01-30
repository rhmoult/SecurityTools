#!/usr/bin/python
__author__ = 'nclifton'

# Linux crashes fixed,
# code halved,
# unused imports removed,
# PEP 8 implemented,
# Object shadows refactored
# Variable names refactored by Rich Moulton

import sys
import struct
import socket
import platform
import subprocess
from uuid import getnode as ether_addr


def get_data(output):

    hostname = socket.gethostname()
    fqdn = socket.getfqdn()

    # Get architecture pointer size in bytes
    _void_ptr_size = struct.calcsize('P')
    operating_system = platform.system()

    # 4 bytes is 32 bits!
    if _void_ptr_size == 4:
        architecture = 'x86'
    # 8 bytes is 64 bits!
    elif _void_ptr_size == 8:
        architecture = 'x64'
    # What is this?!?
    else:
        architecture = 'Unknown'

    # OS Version may not be the same as processor arch
    os_version = platform.release()

    # This should agree with our arch pointer size check
    processor = platform.processor()

    machine = platform.machine()

    # What's my IP?
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    mac_address = ether_addr()

    output.write('Operating System:'+operating_system+'\n')
    output.write('Operating System Version:'+os_version+'\n')
    output.write('Hostname:'+hostname+'\n')
    output.write('Fully Qualified Domain Name:'+fqdn+'\n')
    output.write('Processor:'+processor+'\n')
    output.write('Processor Architecture:'+machine+'\n')
    output.write('OS Architecture:'+architecture+'\n')

    if operating_system is 'Windows':
        # Why not wmic fu?
        hot_fixes = subprocess.check_output("wmic qfe list")
        run_processes = subprocess.check_output("tasklist")

        # Why not net fu?
        user_list = subprocess.check_output("net user")
        group_list = subprocess.check_output("net localgroup")
        output.write('Hotfixes:'+hot_fixes+'\n')
        output.write('Running Processes:'+run_processes+'\n')
        output.write('Local Users:'+user_list+'\n')
        output.write('Local User groups:'+group_list+'\n')

    else:
        # Assume OS is Linux...yeah, yeah...
        # Bash fu...
        run_processes = subprocess.check_output(["/bin/ps", "-Af"])
        user_list = subprocess.check_output(["/bin/ls", "/home"])
        group_list = subprocess.check_output(["/bin/cat", "/etc/group"])
        output.write('Running Processes:'+run_processes+'\n')
        output.write('Local Users:'+user_list+'\n')
        output.write('Local User groups:'+group_list+'\n')

    # First field is the sender's address
    output.write('IP Address:'+s.getsockname()[0]+'\n')

    # Six groups of two hex digits...
    output.write('MAC Addresses:'+':'.join(("%012X" % mac_address)[i:i+2] for i in range(0, 12, 2))+'\n')


def main():
    # If first arg is a filename, write to file
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'w') as f:
            get_data(f)
    # Else, write to standard out
    else:
        f = sys.stdout
        get_data(f)

if __name__ == '__main__':
    main()
