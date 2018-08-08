# VMRequests 
## Presentation
The goal of this Programm is to automatically execute predefined request in a Virtual Machine (Oracle Virtualbox), analyze their result and report if the request was executed successfully or not.
A "request" can be the compilation of a programm, the installation or whatever can be executed as a script.
The *ExecuteRequest.py* take one or more requests name as argument and execute them one by one. 
The typical execution process of a request is 
1. Starting the virtual machine 
2. Checking out the relevant snapshot 
3. Carry out the request itself (by calling a command/script into the guest OS)
4. Analyzing the log file to find out if the request was successfull or not 

## Requests
Request are defined in the *requests.json* file that must lay plain relative to *ExecuteRequest.py*. 
The following is an example of a request description 
    "DummyBuild":
	{
		"Machine":"MyVM",
		"Type":"Build",
		"Snapshot": "Current State",
		"User": "myuser",
		"Password": "mypassword",
		"Execution":"E:\\WindowsScripts\\build_with_devenv.bat",
		"Exeargs": "Arg1 Arg2 anotherarg",
		"Arg1": "C:\\Users\\myuser\\Documents",
		"Arg2": "whatever",
		"anotherarg" : "whaterveragain",
		"Logfiletype": "MSdevenvBuildlog",
		"LogGuestPOV":"C:\\Users\\myuser\\Documents\\build.log",
		"LogHostPOV":"/home/myuser/Public/build.log"}

Mandatory argument, are 
* Machine: which virtual machine to use
* Snapshot: which snapshot should be cheked out. Type "Current State" if you don't want / don't have a Snapshot. **WARNING** bare in mind that if you enter a snapshot here, you **will loose** the data you have in your current state.
* Type: the type of request you want to execute. Right now only "Build" and "Install" are supported. You can easily add more request type by subclassing *MachineRequest* in *ExecuteRequest.py*
* User: the user name (in the Guest OS) under which the execution will take place
* Password: password for that user
* LogGuestPOV: the place of the logfile of the *Execution* in the **GUEST OS** filesystem!
* LogHostPOV: The place of the logfile of the *Execution* in the **HOST OS** filesystem! **WARNING** those are here to inform *ExecuteRequest.py* on where to find those file. This is the responsability of the *Execution* script (hence yours...) to make sure that those two file match!
* Logfiletype: The type of logfile type, so that *ExecuteRequest.py* knows how to parse the result and find out if succcess or failure. You can easily add your custom type by subclassing *AbstractBuildLogFileAnalyzer* from *LogFileAnalyzer.py*. See under for a list of log file analyzer
* Execution: path to script/ programm that must be executed (in the Guest OS file system!) 
* Exeargs: arguments to will be path to the Execution command. Exeargs itself can be composed of various (as much as you want additional parameter that you will write in the entry)

## Log file analyzer 
Currently supported *"Logfiletype"* option are :
* MSdevenvBuildlog: This analyze a log file comming from *devenv.exe* (alias Microsoft Visual Studio). It will declare itself not valid (```self.valid=False```) if the last line says that there is more than 0 Failed.
* MSIexecInstalllog: This analyze a log file comming from *msiexec.exe* (alias the programm that launches the installation of an msi installer. It will declare itself not valid if the return code is not correct
* BootsrapperInstalllog: Same thing as MSIexecInstalllog but with an *.exe* installer instead of an *.msi*.


