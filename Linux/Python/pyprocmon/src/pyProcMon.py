#!/usr/bin/python

# This program will watch the creation and termination of processes on a machine
# I used it to hunt down third-party software creating scripts in /tmp which were running as root.  <-- OMG
# This program was tested exclusively on Ubuntu 12.04 LTS.

import psutil
from datetime import datetime

# Get a list of current processes
initialDict = dict.fromkeys(psutil.process_iter())

while True:

    # Grab an updated list
    secondDict = dict.fromkeys(psutil.process_iter())

    # Are any processes from the first list gone?
    terminatedProcesses = initialDict.viewkeys() - secondDict.viewkeys()

    for dead in terminatedProcesses:
        try:
            print "\n\n[-] Terminated: Pid: {:<10s}\tProcess: {}".format(str(dead.pid), dead.name(), width=10)

        except:
            print "\n\n[-] Process terminated, but data no longer exists."

    # Are there any processes in the second list that don't appear in the first?
    newProcesses = secondDict.viewkeys() - initialDict.viewkeys()

    # At this point, it is safe to designate the newer process list our standard for comparison.
    initialDict = secondDict

    for created in newProcesses:

        try:
            print "\n\n[+] Created: Pid: {:<10s}\tProcess: {}".format(str(created.pid), created.name(), width=10)

        except:
            print "\n\n[+] Process created, but data no longer exists."

        try:
            print "Command line: {}\nAbsolute path: {}\nCreation time: {}".format(
                created.cmdline(),
                created.exe(),
                datetime.fromtimestamp(created.create_time()).strftime("%Y-%m-%d %H:%M:%S"))

        except:
            print "Additional process creation data unavailable."

        try:
            print "Parent Pid: {:<10s}\tParent Process: {}".format(str(
                created.ppid()), created.parent().name(), width=10)
        except:
            print "Parent unknown."

        try:
            print "Process is running as {}".format(created.username())
        except:
            print "No owner information for the process is available."

