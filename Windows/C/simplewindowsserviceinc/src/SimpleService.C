/*Chapter 13. SimpleService.c
	Simplest example of an Windows service
	All it does is update the checkpoint counter
	and accept basic controls. 
	You can also run it as a stand-alone application. */

#include "Everything.h"
#include <time.h>
#define UPDATE_TIME 1000	/* One second between updates */

VOID LogEvent (LPCTSTR, WORD), LogClose();
BOOL LogInit(LPTSTR);
void WINAPI ServiceMain (DWORD argc, LPTSTR argv[]);
VOID WINAPI ServerCtrlHandler(DWORD);
void UpdateStatus (int, int);
int  ServiceSpecific (int, LPTSTR *);

static BOOL shutDown = FALSE, pauseFlag = FALSE;
static SERVICE_STATUS hServStatus;
static SERVICE_STATUS_HANDLE hSStat; /* Service status handle for setting status */
									 
static LPTSTR serviceName = _T("Windows VService");
static LPTSTR logFileName = _T(".\\LogFiles\\SimpleServiceLog.txt");
static BOOL consoleApp = FALSE, isService;
									 
/*  Main routine that starts the service control dispatcher */
/*	Optionally, run as a stand-alone console program		*/
/*	Usage: simpleService [-c]								*/
/*			-c says to run as a console app, not a service	*/

VOID _tmain (int argc, LPTSTR argv[])
{
	SERVICE_TABLE_ENTRY DispatchTable[] =
	{
		{ serviceName,				ServiceMain	},
		{ NULL,						NULL }
	};
	
	Options (argc, argv, _T ("c"), &consoleApp, NULL);
	isService = !consoleApp;
	/* Initialize log file */
	if (!LogInit (logFileName)) return;

	if (!WindowsVersionOK (3, 1)) 
		ReportError (_T("This program requires Windows NT 3.1 or greater"), 1, FALSE);

	if (isService) {
		LogEvent(_T("Starting Service Control Dispatcher"), EVENTLOG_SUCCESS);
		StartServiceCtrlDispatcher (DispatchTable);
	} else {
		LogEvent(_T("Starting as a stand-alone application"), EVENTLOG_SUCCESS);
		ServiceSpecific (argc, argv);
	}

	LogClose();
	return;
}

/*	ServiceMain entry point, called when the service is created by
	the main program.  */
void WINAPI ServiceMain (DWORD argc, LPTSTR argv[])
{
	LogEvent (_T("Entering ServiceMain."), EVENTLOG_SUCCESS);

	hServStatus.dwServiceType = SERVICE_WIN32_OWN_PROCESS;
	hServStatus.dwCurrentState = SERVICE_START_PENDING;
	hServStatus.dwControlsAccepted = SERVICE_ACCEPT_STOP | 
		SERVICE_ACCEPT_SHUTDOWN | SERVICE_ACCEPT_PAUSE_CONTINUE;
	hServStatus.dwWin32ExitCode = NO_ERROR;
	hServStatus.dwServiceSpecificExitCode = 0;
	hServStatus.dwCheckPoint = 0;
	hServStatus.dwWaitHint = 2 * UPDATE_TIME;

	hSStat = RegisterServiceCtrlHandler( serviceName, ServerCtrlHandler);

	if (hSStat == 0) {
		LogEvent (_T("Cannot register control handler"), EVENTLOG_ERROR_TYPE);
		hServStatus.dwCurrentState = SERVICE_STOPPED;
		hServStatus.dwWin32ExitCode = ERROR_SERVICE_SPECIFIC_ERROR;
		hServStatus.dwServiceSpecificExitCode = 1;
		UpdateStatus (SERVICE_STOPPED, -1);
		return;
	}

	LogEvent (_T("Control handler registered successfully"), EVENTLOG_SUCCESS);
	SetServiceStatus (hSStat, &hServStatus);
	LogEvent (_T("Service status set to SERVICE_START_PENDING"), EVENTLOG_SUCCESS);

	/*  Start the service-specific work, now that the generic work is complete */
	if (ServiceSpecific (argc, argv) != 0) {
		/* Better: set dwCurrentState to SERVICE_STOP_PENDING; shutDown the server,
		 * then set dwCurrentState = SERVICE_STOPPED and return */
		hServStatus.dwCurrentState = SERVICE_STOPPED;
		hServStatus.dwWin32ExitCode = ERROR_SERVICE_SPECIFIC_ERROR;
		hServStatus.dwServiceSpecificExitCode = 1;  /* Server initilization failed */
		SetServiceStatus (hSStat, &hServStatus);
		return;
	}
	LogEvent (_T("Service threads shut down"), EVENTLOG_SUCCESS);
	LogEvent (_T("Set SERVICE_STOPPED status"), EVENTLOG_SUCCESS);
	/*  We will only return here when the ServiceSpecific function
	completes, indicating system shutDown. */
	UpdateStatus (SERVICE_STOPPED, 0);
	LogEvent (_T("Service status set to SERVICE_STOPPED"), EVENTLOG_SUCCESS);
	return;
}

/*	This is the service-specific function, or "main" and is 
	called from the more generic ServiceMain
	In general, you can take a server, such as ServerSK.c
	of Chapter 12 and rename "_tmain" as "ServiceSpecific"
	and put the code right here. */

int ServiceSpecific (int argc, LPTSTR argv[])
{	
	STARTUPINFO startUp;
	PROCESS_INFORMATION processInfo;
	DWORD delay = UPDATE_TIME * 125;

	GetStartupInfo (&startUp);
	UpdateStatus (-1, -1); /* Now change to status; increment the checkpoint */
	/* Start the server as a thread or process */
	/* Assume the service starts in 2 seconds. */
	UpdateStatus (SERVICE_RUNNING, -1);
	LogEvent (_T("Status update. Service is now running"), EVENTLOG_SUCCESS);
	
	/* Update the status periodically. */
	/*** The update loop could be on a separate thread to assure periodic updates ***/
	/* Also, check the pauseFlag - See Exercise 13-1 */
	LogEvent (_T("Starting main service server loop"), EVENTLOG_SUCCESS);
	while (!shutDown) { /* shutDown is set on a shutDown control */
		Sleep (UPDATE_TIME);
		/* Execute the python script */
		CreateProcess(NULL,_T("C:\\Python27\\python.exe c:\\tmp\\real_work.py"), NULL, NULL, TRUE, CREATE_NO_WINDOW, NULL, NULL, &startUp, &processInfo);
		Sleep (delay);
		UpdateStatus (-1, -1);  /* Assume no change */
		LogEvent (_T("Status update. No change"), EVENTLOG_SUCCESS);
	}

	LogEvent (_T ("Server process has shut down."), EVENTLOG_SUCCESS);

	return 0;
}


/*	Control Handler Function */

VOID WINAPI ServerCtrlHandler( DWORD dwControl)

 // requested control code 
{
	switch (dwControl) {
	case SERVICE_CONTROL_SHUTDOWN:
	case SERVICE_CONTROL_STOP:
		shutDown = TRUE;
		UpdateStatus (SERVICE_STOP_PENDING, -1);
		break;
	case SERVICE_CONTROL_PAUSE:
		pauseFlag = TRUE;
		/* Pause implementation is a chapter exercise */
		break;
	case SERVICE_CONTROL_CONTINUE:
		pauseFlag = FALSE;
		/* Continue is also a chapter exercise */
		break;
	case SERVICE_CONTROL_INTERROGATE:
		break;
	default:
		if (dwControl > 127 && dwControl < 256) /* User Defined */
		break;
	}
	UpdateStatus (-1, -1);
	return;
}

void UpdateStatus (int NewStatus, int Check)
/*  Set a new service status and checkpoint (either specific value or increment) */
{
	if (Check < 0 ) hServStatus.dwCheckPoint++;
	else			hServStatus.dwCheckPoint = Check;
	if (NewStatus >= 0) hServStatus.dwCurrentState = NewStatus;
	if (isService) {
		if (!SetServiceStatus (hSStat, &hServStatus)) {
			LogEvent (_T("Cannot set service status"), EVENTLOG_ERROR_TYPE);
			hServStatus.dwCurrentState = SERVICE_STOPPED;
			hServStatus.dwWin32ExitCode = ERROR_SERVICE_SPECIFIC_ERROR;
			hServStatus.dwServiceSpecificExitCode = 2;
			UpdateStatus (SERVICE_STOPPED, -1);
			return;
		} else {
			LogEvent (_T("Service Status updated."), EVENTLOG_SUCCESS);
		}
	} else {
		LogEvent (_T("Stand-alone status updated."), EVENTLOG_SUCCESS);
	}

	return;
}

static FILE * logFp = NULL;
/* Very primiitive logging service, using a file */
VOID LogEvent (LPCTSTR UserMessage, WORD type)
{
	TCHAR cTimeString[30] = _T("");
	time_t currentTime = time(NULL);
	_tcsncat (cTimeString, _tctime(&currentTime), 30);
	/* Remove the new line at the end of the time string */
	cTimeString[_tcslen(cTimeString)-2] = _T('\0');
	_ftprintf(logFp, _T("%s. "), cTimeString);
	if (type == EVENTLOG_SUCCESS || type == EVENTLOG_INFORMATION_TYPE) 
		_ftprintf(logFp, _T("%s"), _T("Information. "));
	else if (type == EVENTLOG_ERROR_TYPE)
		_ftprintf(logFp, _T("%s"), _T("Error.       "));
	else if (type == EVENTLOG_WARNING_TYPE)
		_ftprintf(logFp, _T("%s"), _T("Warning.     "));
	else
		_ftprintf(logFp, _T("%s"), _T("Unknown.     "));

	_ftprintf(logFp, _T("%s\n"), UserMessage);
	fflush(logFp);
	return;
}

BOOL LogInit(LPTSTR name)
{
	logFp = _tfopen (name, _T("a+"));
	if (logFp != NULL) LogEvent (_T("Initialized Logging"), EVENTLOG_SUCCESS);
	return (logFp != NULL);
}

VOID LogClose()
{
	LogEvent (_T("Closing Log"), EVENTLOG_SUCCESS);
	return;
}
