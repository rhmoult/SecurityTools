__author__ = 'rmoulton'

# This is a basic implementation of a bind shell.  You may enter exactly one command line before connection cutoff.
# Type one_shot.py for usage.

import getopt
import socket
import sys
import subprocess

# Client mode: Client connects to server; then, user can enter one command and client returns results
# Server mode: When server receives client connection, server allows client to put in one command, then returns results


def create_socket():
    return socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def display_usage():
    print ("one_shot")
    print ("")
    print ("Usage: one_shot.py -l -p port")
    print ("")
    print ("Server mode examples: ")
    print ("Create a listener that will allow you to execute one arbitrary command\n\tone_shot.py -l -p 31337")
    print ("")
    print ("Client mode examples: ")
    print ("Connect to a remote machine on the elite port\n\tone_shot.py -t 127.0.0.1 -p 31337")


def engage_client(rhost, rport):

    # Create a socket
    sock = create_socket()
    print ("Connecting to {} port {}".format(rhost, rport))

    server_address = (rhost, rport)

    # Connect to remote address
    sock.connect(server_address)

    try:
        # Get command from user
        message = raw_input("# ")

        # Send command
        sock.sendall(message)

        amount_expected = 2048

        # Get reply & print
        reply = sock.recv(amount_expected)
        sys.stdout.write("{}".format(reply))

    except socket.errno, e:
        print ("Socket error: {}".format(str(e)))
    except Exception, e:
        print ("Another exception: {}".format(str(e)))
    finally:
        print ("\nClosing connection to the server.")
        sock.close()


def engage_server(lhost, lport, bind_shell):
    # This mode of operation will put the server in a loop, listening on a port
    # The server will close immediately after connection closes
    shutdown_server = False

    # Max number of queued connections
    backlog = 5
    # Payload size
    buffer_size = 2048
    # Create TCP socket
    sock = create_socket()
    # Enable reuse address/port
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # Bind the socket to the port
    server_address = (lhost, lport)
    sock.bind(server_address)
    # Listen to clients
    sock.listen(backlog)
    while shutdown_server == False:
        client, address = sock.accept()
        data = client.recv(buffer_size)
        if data:
            if bind_shell:
                proc = subprocess.Popen(
                    data, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
                data = proc.stdout.read() + proc.stderr.read()
                client.send(data)
            while len(data) % 16 != 0:
                data += ' '
            client.send(data)
        else:
            shutdown_server = True
        client.close()


def main():

    # Variable declarations
    server_mode = False
    client_mode = False
    bind_shell = False
    port = 0
    lhost = '0.0.0.0'
    rhost = '127.0.0.1'

    # If the user does not put the software into server or client mode, give them a usage message
    if not len(sys.argv[1:]):
        display_usage()
    try:
        # Listen mode does not require additional args, port and target do
        opts, args = getopt.getopt(sys.argv[1:], "lp:t:")
    except getopt.GetoptError as err:
        print (str(err))
        display_usage()

    for option, argument in opts:
        # If users ask for help...
        if option in "-h":
            display_usage()
        elif option in "-l":
            # If the user starts the script in listen mode, we are a server.
            if client_mode == True:
                display_usage()
                client_mode = False
            else:
                server_mode = True
                bind_shell = True
        elif option in "-p":
            # We need the port ags as an int rather than string
            port = int(argument)
        elif option in "-t":
            # If we are providing a target, we are a client.
            if server_mode == False:
                rhost = argument
                client_mode = True
            else:
                display_usage()
                server_mode = False

    if server_mode:
        engage_server(lhost, port, bind_shell)
    elif client_mode:
        engage_client(rhost, port)

    print ("Connect again for more shenanigans!")

if __name__ == "__main__":
    main()