# Original code ostensibly by Justin Seitz
## Upgrades made by rmoulton


import os
import sys
import win32api
import win32con
import win32security
import wmi


def get_privileges(process_id):
    try:
        # Get handle to the target process
        process_handle = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION, False, process_id)

        # Get the main process token
        token_handle = win32security.OpenProcessToken(process_handle, win32con.TOKEN_QUERY)

        # Get the list of process privileges
        process_privileges = win32security.GetTokenInformation(token_handle, win32security.TokenPrivileges)

        # Get the subset of privileges that are enabled
        privilege_list = []
        for priv_id, priv_flags in process_privileges:
            # check if the privilege is enabled
            if priv_flags == 3:
                privilege_list.append(win32security.LookupPrivilegeName(None, priv_id))

    except:
        privilege_list.append("N/A")

    return "|".join(privilege_list)


log = "process_log.csv"

def log_to_file(log_message):
    fd = open(log, "ab")
    fd.write("{}\r\n".format(log_message))
    fd.close()


def main():
    try:
        # If it doesn't exist, create a log file with header
        if not os.path.isfile(log):
            log_to_file("Time,User,Executable,CommandLine,PID,ParentPID,Privileges")

        # instantiate the WMI interface
        wmi_interface = wmi.WMI()

        # create our process monitor
        process_watcher = wmi_interface.Win32_Process.watch_for("creation")

        while True:

            # Note that the process_watcher will block until a new process is created
            try:
                new_process = process_watcher()
            except:
                print "Unexpected error:", sys.exc_info()[0]
                raise
            
            else:

                try:
                    proc_owner  = new_process.GetOwner()
                    proc_owner  = "{}\\{}".format(proc_owner[0],proc_owner[2])
                    create_date = new_process.CreationDate
                    executable  = new_process.ExecutablePath
                    cmdline     = new_process.CommandLine
                    pid         = new_process.ProcessId
                    parent_pid  = new_process.ParentProcessId
                    privileges  = get_privileges(pid)
                    process_log_message = "{},{},{},{},{},{},{}".format(
                        create_date, proc_owner, executable, cmdline, pid, parent_pid,privileges)

                    print "{}\r\n".format(process_log_message)

                    log_to_file(process_log_message)

                except (KeyboardInterrupt):
                    sys.exit()
                except:
                    print "Unexpected error:", sys.exc_info()[0]
                    raise

    except (KeyboardInterrupt):
        sys.exit()
    except:
        print "Unexpected error:", sys.exc_info()[0]
        raise

if __name__ == '__main__':
    main()
