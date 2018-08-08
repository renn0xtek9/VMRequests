#!/usr/bin/env python
import sys
import virtualbox
import json
import time
import os
import getopt
from LogFileAnalyzer import DevenvBuildLogFileAnalyzer, MsiExecInstallLogFileAnalyzer, BootstrapperInsllerLogFileAnalyzer




__metaclass__ = type
vbox = virtualbox.VirtualBox()

class SnapshotNotFound(Exception):
	pass

class MachineAlreadyInUse(Exception):
	pass
class ProblemOpenningSession(Exception):
	pass 

class ProblemClosingMachine(Exception):
	pass

class ProblemCheckingOutSnapshot(Exception):
	pass

class MachineRequest(object):
	def __init__(self,jsonkey,requestname):
		self.name=requestname
		self.jsonkey=jsonkey
		self.valid=True
		self.requestExecutedSuccessfully=False
		for key in ['Machine','User','Password','Snapshot','Execution','Exeargs']:
			self.valid=self.valid and self._checkjsonkey(key)
		if self.valid:
			for key in self.jsonkey['Exeargs'].split(' '):
				self.valid=self.valid and self._checkjsonkey(key)
		try:
			if not self._doesSnapshotExistForThisMachine(self.jsonkey["Machine"],self.jsonkey["Snapshot"]):
				self.valid=False
				raise SnapshotNotFound()
				self._handleExceptions()
		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			print("Exception {} when using machine {}		{} {}".format(exc_type,self.jsonkey["Machine"], fname, exc_tb.tb_lineno))
			self.valid=False 
	def _doesSnapshotExistForThisMachine(self,machine,snapshot):
		if snapshot=="Current State":
			return True
		try: 
			vm=vbox.find_machine(machine)
			snaphot=vm.find_snapshot(snapshot)
			if (snapshot!=None):
				return True
			return False
		except: 
			return False
		
	def _checkjsonkeys(self,keylist):
		ret=True 
		for key in keylist:
			ret=ret and self._checkjsonkey(key)
		return ret

	def _checkjsonkey(self,keyname):
		try:
			dontcare=self.jsonkey[keyname]
		except KeyError:
			print("{} entry not found in {}".format(keyname,self.name))
			return False
		return True
		
	def _startthevm(self):
		self.session=virtualbox.Session()
		self.vm=vbox.find_machine(self.jsonkey["Machine"])
		
		if self.vm.session_state==virtualbox.library.SessionState.locked:
			raise MachineAlreadyInUse
		
		if self.jsonkey["Snapshot"]!="Current State":
			try:
				self.vm.lock_machine(self.session,virtualbox.library.LockType.write)
				


				snap=self.session.machine.find_snapshot(self.jsonkey["Snapshot"])
				print("Checking out snapshot {}".format(snap.name))
				snapshotcheckoutprogress=self.session.machine.restore_snapshot(snap)
				timeout=snapshotcheckoutprogress.wait_for_completion(60000)
				if timeout:
					raise ProblemCheckingOutSnapshot
				self.session.unlock_machine()
			except Exception as e:
    				exc_type, exc_obj, exc_tb = sys.exc_info()
				fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
				print(exc_type, fname, exc_tb.tb_lineno)
				print("Exception while checking out the right snapshot. Exiting")
				sys.exit(1)


		self.progress=self.vm.launch_vm_process(self.session,'gui','')
		timeout=self.progress.wait_for_completion(30000)
		if timeout:
			print("Timeout while starting machine")
			raise ProblemOpenningSession
		pass
			

	
	def _closethevm(self):
		self.session.console.pause()
		while self.vm.state!=virtualbox.library.MachineState.paused:
			time.sleep(1.0)
			print("Waiting for machine {} to pause. Current state is {}".format(self.jsonkey["Machine"],self.vm.state))
        	savestateprogress=self.session.machine.save_state()
        	timeout=savestateprogress.wait_for_completion(60000)
        	if timeout: 
			raise ProblemClosingMachine
        	print("Machine {} closed".format(self.jsonkey["Machine"]))
	
	def _execute(self):
		while self.vm.state!=virtualbox.library.MachineState.running:
			print(self.vm.state)
		arglst=' '.join([str('"'+self.jsonkey[key]+'"') for key in  self.jsonkey['Exeargs'].split(' ')])
		lst=[self.jsonkey[key] for key in  self.jsonkey['Exeargs'].split(' ')]
		execution=str("\"{}\" {}".format(self.jsonkey["Execution"],arglst))
		print ("{} will execute \n{}".format(self.jsonkey["Machine"],execution))
	 	gs=self.session.console.guest.create_session(self.jsonkey['User'],self.jsonkey['Password'])
	 	process,stdout,stderr=gs.execute(self.jsonkey["Execution"],lst)
	 	print (stdout)
	 	print (process.exit_code)
	 	
	def _analyzelogfile(self):
		import os.path
		self.requestExecutedSuccessfully=False
		if not self._checkjsonkeys(['Logfiletype','LogHostPOV']):
			return self.requestExecutedSuccessfully
		if (os.path.isfile(self.jsonkey['LogHostPOV'])):
			if self.jsonkey['Logfiletype']=="MSdevenvBuildlog":
				self.analyzer=DevenvBuildLogFileAnalyzer(self.jsonkey['LogHostPOV'],'utf-8')
				self.requestExecutedSuccessfully=self.analyzer.valid
				return self.requestExecutedSuccessfully
			if self.jsonkey['Logfiletype']=="MSIexecInstalllog":
				self.analyzer=MsiExecInstallLogFileAnalyzer(self.jsonkey['LogHostPOV'])
				self.requestExecutedSuccessfully=self.analyzer.valid 
				return self.requestExecutedSuccessfully
			if self.jsonkey['Logfiletype']=='BootsrapperInstalllog':
				self.analyzer=BootstrapperInsllerLogFileAnalyzer(self.jsonkey['LogHostPOV'])
				self.requestExecutedSuccessfully=self.analyzer.valid 
				return self.requestExecutedSuccessfully
			print("No log file analyzer have been implemented for {}".format(self.jsonkey['LogHostPOV']))
		else:
			print("No build log file found for {}".format(self.name))
		return self.requestExecutedSuccessfully
	
	def _handleExceptions(self):
		try: 
			pass
		except SnapshotNotFound:
			print ("Snapshot {} not found for the machine {}".format(str(self.jsonkey["Snapshot"]),str(self.jsonkey["Machine"])))
		except MachineAlreadyInUse:
			print("The machine {} appears to be locked by another sesssion!".format(self.jsonkey["Machine"]))
		except ProblemOpenningSession:
			print("Timeout when openning session on machine {}".format(self.jsonkey["Machine"]))
		except ProblemClosingMachine:
			print("A problem has been encoutered while saving the state of the machine {}".format(self.jsonkey["Machine"]))
	

class BuildRequest(MachineRequest):
	def __init__(self,jsonkey,requestname):
		MachineRequest.__init__(self,jsonkey,requestname)
		try:
			if not self.valid:
				return
			super(BuildRequest,self)._startthevm()
			super(BuildRequest,self)._execute()
			super(BuildRequest,self)._closethevm()
			super(BuildRequest,self)._analyzelogfile()
			super(BuildRequest,self)._handleExceptions()
			
		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			print("Exception {} when using machine {}		{} {}".format(exc_type,self.jsonkey["Machine"], fname, exc_tb.tb_lineno))
			self.valid=False 
			


class InstallRequest(MachineRequest):
	def __init__(self,jsonkey,requestname):
		MachineRequest.__init__(self,jsonkey,requestname)
		try:
			if not self.valid:
				return
			super(InstallRequest,self)._startthevm()
			super(InstallRequest,self)._execute()
			super(InstallRequest,self)._closethevm()
			super(InstallRequest,self)._analyzelogfile()
			super(InstallRequest,self)._handleExceptions()
			
		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			print("Exception {} when using machine {}		{} {}".format(exc_type,self.jsonkey["Machine"], fname, exc_tb.tb_lineno))
			self.valid=False 
			self.valid




def Request(req):
	with open("requests.json","r") as read_file:
        	data=json.load(read_file)
        	if (data["requests"]):
			requests=data["requests"]
		else:
			print ("No \"requests\" entry found in requests.json".format(buildtype))
            		sys.exit(0)
		if requests[req]:
			try :
				typ=requests[req]['Type']
				if typ=="Build":
					action=BuildRequest(requests[req],req)
				if typ=="Install":
					action=InstallRequest(requests[req],req)

				if 'action' in locals():
					return action.requestExecutedSuccessfully
				else: 
					print("Request type \"{}\" is not implemented".format(typ))
					return False

			except KeyError:
				print("No Type entry in {} requests description of requests.json".format(req))
				return False

			
        	else:
            		print ("{} not found in requests.json".format(buildtype))



























class bcolors:
	NC='\033[0m'
	Bold='\033[1m'
	Underlined='\033[4m'
	Blink='\033[5m'
	Inverted='\033[7m'
	Hidden='\033[8m'
	Black='\033[1;30m'
	Red='\033[1;31m'
	Green='\033[1;32m'
	Yellow='\033[1;33m'
	Blue='\033[1;34m'
	Purple='\033[1;35m'
	Cyan='\033[1;36m'
	LightGray='\033[1;37m'
	DarkGray='\033[1;30m'
	LightRed='\033[1;31m'
	LightGreen='\033[1;32m'
	LightYellow='\033[1;93m'
	LightBlue='\033[1;34m'
	LightPurple='\033[35m'
	LightCyan='\033[1;36m'

	White='\033[1;97m'
	BckgrDefault='\033[49m'
	BckgrBlack='\033[40m'
	BckgrRed='\033[41m'
	BckgrGreen='\033[42m'
	BckgrYellow='\033[43m'
	BckgrBlue='\033[44m'
	BckgrPurple='\033[45m'
	BckgrCyan='\033[46m'
	BckgrLightGray='\033[47m'
	BckgrDarkGray='\033[100m'
	BckgrLightRed='\033[101m'
	BckgrLightGreen='\033[102m'
	BckgrLightYellow='\033[103m'
	BckgrLightBlue='\033[104m'
	BckgrLightPurple='\033[105m'
	BckgrLightCyan='\033[106m'
	BckgrWhite='\033[107m'	
	#Typical format
	Achtung=LightRed+Bold+Blink
	Error=LightRed+Bold


def usage():
	print(bcolors.LightRed +sys.argv[0] + bcolors.LightPurple+ '[-h -v --errocode ]' +bcolors.NC)
	print(bcolors.LightGreen +"\tWhere:")
	print(bcolors.LightGreen +"\n\n\tDescription:")
	print(bcolors.LightCyan +"\tDescribe_what_it_does")	
	print(bcolors.LightGreen +"\n\n\tExample of use:")
	print(bcolors.LightRed +"\t"+sys.argv[0] + bcolors.LightPurple)
	print(bcolors.NC)
	
def errorlist():
	print(bcolors.Red+"--------------------------------------------------------")
	print("EXIT CODE       |MEANING")
	print("--------------------------------------------------------")
	print("0               |Success")
	print("1               |Error when parsing argument")
	print("255             |Exit returning information (help, version, list of error codes etc)"+bcolors.NC)

def CheckAndQuitUponFolderMissing(folderlist,errorcode):
	for folder in folderlist:
		if (not os.path.isdir(folder)):
			print(bcolors.LightRed+"Exit error code "+str(errorcode)+": folder "+folder+" does not exist"+bcolors.NC)
			sys.exit(errorcode)

def main(argv):
	varnamea = ''
	varnameb = ''
	try:
		opts, args = getopt.getopt(argv,"ha:b:",["errorcode","longarga=","longargb="])
		
	except getopt.GetoptError:
		usage
		sys.exit(1)
	
	for opt, arg in opts:
		if opt == '-h':
			usage()
			sys.exit()
			
		if opt == '--errorcode' :
			errorlist()
			sys.exit()
	
	if 'arg' in locals():
		requestlist=argv[argv.index(arg)+1:]
	else:
		requestlist=argv
	
	for req in requestlist:
		print( "Request {} Status {}".format(req,str(bcolors.Green+"OK"+bcolors.NC) if Request(req)==True else str(bcolors.Red+"NOK"+bcolors.NC)))

if __name__ == "__main__":
        main(sys.argv[1:])
















