#!/usr/bin/env python
import sys
import re
import os.path
import io
__metaclass__ = type
class AbstractBuildLogFileAnalyzer:
	"""@class AbstractBuildLogFileAnalyzer
	@brief This interface describe an analyzer of build log file. It is meant to be subclassed, to analyzed for instance build log form Visual Studio, from gcc etc"""
	def __init__(self,logfile,nativeencoding='utf-8'):
		self.m_logfile=logfile
		self.logfileexist=True
		self.valid=False
		if (not os.path.isfile(self.m_logfile)):
			self.logfileexist=False
		self.content = [line.rstrip('\r\n').rstrip('\n') for line in io.open(self.m_logfile,mode="r", encoding=nativeencoding)]


class DevenvBuildLogFileAnalyzer(AbstractBuildLogFileAnalyzer):
	"""@class DevenvBuildLogFileAnalyzer
	@brief This class analyze the build log file of MS Visual Studio"""
	def __init__(self,logfile,nativeencoding):
		AbstractBuildLogFileAnalyzer.__init__(self,logfile,nativeencoding)
		self.attempted=list()
		self.succeeded=list()
		self.uptodate=list()
		self.failed=list()
		self.n_failed=-1		#Initialize return code at -1. We will see if we find it !
		self.n_succeeded=0
		self.valid=False
		
		if not self.logfileexist:
			return
		currentcontext=dict()
		print("Analyzing content of logfile {}".format(self.m_logfile))
		try:
			for row in self.content:
				if ("========== Build: " in row ): #That is the final line  e.g. ========== Build: 12 succeeded, 0 failed, 55 up-to-date, 0 skipped ==========
					self.n_succeeded=re.sub(r' succeeded,.*','',re.sub(r'========== Build: ','',row))
					self.n_failed=re.sub(r' failed,.*','',re.sub(r'.* succeeded, ','',row))
			try:
				self.n_failed=int(self.n_failed)
			except ValueError:
				print("Could not properly read the number of faild builds form {}".format(self.m_logfile))
				self.n_failed=len(self.failed)
			try:
				self.n_succeeded=int(self.n_succeeded)
			except ValueError:
				print("Could not properly read the number of successfull builds form {}".format(self.m_logfile))
				self.n_succeeded=len(self.succeeded)
		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			print("Exception {} when analyzing {}		{} {}".format(exc_type,self.m_logfile, fname, exc_tb.tb_lineno))
			self.valid=False 
			return 
		self.valid=True if self.n_failed==0 else False
		print("Logfile {} has been analyzed. Sucess {} Failed {} ".format(self.m_logfile,self.n_succeeded,self.n_failed))
		
class MsiExecInstallLogFileAnalyzer(AbstractBuildLogFileAnalyzer):
	def __init__(self,logfile,nativeencoding='utf-16-le'):
		AbstractBuildLogFileAnalyzer.__init__(self,logfile,nativeencoding)
		if not self.logfileexist:
			return
		try:
			self.errorstatuscode=-1
			print("Analyzing content of logfile {}".format(self.m_logfile))
			for row in self.content:
				if "Installation success or error status" in row:
					self.errorstatuscode=re.sub(r'\.','',re.sub(r'.*Installation success or error status: ','',row))
					try:
						self.errorstatuscode = int(self.errorstatuscode)
					except ValueError:
						print ("Error when analyzing log file: Error Status Code could not be converted to int :{}".format(self.errorstatuscode))
			if self.errorstatuscode==0:
				self.valid=True
			else:
				print("ErrorStatusCode not zero :{}".format(self.errorstatuscode))
			print("Logfile {} has been analyzed. statuscode {} ".format(self.m_logfile,self.errorstatuscode))
		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			print("Exception {} when analyzing {}		{} {}".format(exc_type,self.m_logfile, fname, exc_tb.tb_lineno))
			self.valid=False 
			return 

class BootstrapperInsllerLogFileAnalyzer(AbstractBuildLogFileAnalyzer):
	def __init__(self,logfile,nativeencoding='utf-8'):
		AbstractBuildLogFileAnalyzer.__init__(self,logfile,nativeencoding)
		if not self.logfileexist:
			return 
		try: 
			self.errorstatuscode=-1
			print("Analyzing content of logfile {}".format(self.m_logfile))
			self.valid=False 
			for row in self.content:
				if ": Exit code:" in row:
					self.errorstatuscode=re.sub(r'.*: Exit code: ','',re.sub(r'\,.*','',row))
			try:
				self.errorstatuscode=int(str(self.errorstatuscode),0)
			except:
				print("Can not read statuserrorcode from {}. Catched: ".format(self.m_logfile,self.errorstatuscode))
				return
			if self.errorstatuscode in [0,3010]:
				self.valid=True
			return
		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			print("Exception {} when analyzing {}		{} {}".format(exc_type,self.m_logfile, fname, exc_tb.tb_lineno))
			self.valid=False 
			return

class WindowsUpdateInstallLogFileAnalyzer(MsiExecInstallLogFileAnalyzer):
	def __init__(self,logfile,nativeencoding='utf-16-le'):
		MsiExecInstallLogFileAnalyzer.__init__(self,logfile,nativeencoding)
	#TODO implement the difference between a Windosws update installer (*.msu and an Msi installer *.msi) log files


class BashScriptAnalyzer(AbstractBuildLogFileAnalyzer):
	def __init__(self,logfile,nativeencoding='utf-8'):
		AbstractBuildLogFileAnalyzer.__init__(self,logfile,nativeencoding)
		if not self.logfileexist:
			return 
		try: 
			self.errorstatuscode=-1
			print("Analyzing content of logfile {}".format(self.m_logfile))
			self.valid=False 
			for row in self.content:
				if "Test completed successfully" in row:
					self.errorstatuscode=0
					self.valid=True 
					return			
			return
		except Exception as e:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			print("Exception {} when analyzing {}		{} {}".format(exc_type,self.m_logfile, fname, exc_tb.tb_lineno))
			self.valid=False 
			return



#def main():
	##DevenvBuildLogFileAnalyzer("/home/max/Public/build.log",'utf-8')
	#analyzer=BootstrapperInsllerLogFileAnalyzer("/home/max/Public/bootstrapper.log")
	#print(analyzer.errorstatuscode)
	#print(analyzer.valid)
			
		
			
			
if __name__ == "__main__":
	# execute only if run as a script
	main()
