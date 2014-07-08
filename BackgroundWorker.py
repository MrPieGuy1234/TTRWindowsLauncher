from PyQt4.QtCore import *
import sys, os, shutil
import httplib, urllib, json
import hashlib, bz2
import time
class GameWorker(QThread):
	gameExit = pyqtSignal(int)
	def __init__(self, gameInstance):
		QThread.__init__(self)
		self.gameInstance = gameInstance
		
	def run(self):
		while True:
			if self.gameInstance.poll() != None:
				code = self.gameInstance.poll()
				self.gameExit.emit(code)
				break
			time.sleep(0.5)
		
class APIWorker(QThread):
	
	def __init__(self, rawParams, headers, connection=None):
		QThread.__init__(self)
		self.setProps(rawParams, headers, connection)
	def run(self):
		# encode params
		self.params = urllib.urlencode(self.rawParams)
		if self.connection == None:
			# start a connection
			self.connection = httplib.HTTPSConnection("www.toontownrewritten.com")
		# send provided params and headers
		self.connection.request("POST", "/api/login?format=json", self.params, self.headers)
		
		self.response = self.connection.getresponse()
	def setProps(self, rawParams, headers, connection=None):
		self.connection = connection
		self.rawParams = rawParams
		self.headers = headers
	def getresponse(self):
		return self.response
	def getconnection(self):
		return self.connection
		
class DownloadWorker(QThread):
	status = pyqtSignal(str)
	def __init__(self, installPath):
		QThread.__init__(self)
		self.gameInstallPath = installPath
		
	def generateHash(self, filename):
		sha = hashlib.sha1()
		try:
			file = open(self.gameInstallPath + filename, "rb")
		except IOError:
			return None
		try:
			sha.update(file.read())
		finally:
			file.close()
		return sha.hexdigest()
	def run(self):
		self.status.emit("Checking for patches")
		# retrieve patch manifest
		patchmanifestRaw = urllib.urlopen("http://s3.amazonaws.com/cdn.toontownrewritten.com/content/patchmanifest.txt").read()
		# parse it
		patchmanifest = json.loads(patchmanifestRaw)
		# iterate over list
		for file in patchmanifest:
			# if file is for windows (we dont need to be checking darwin files (yet))
			if "win32" in patchmanifest[file]["only"]:
				# get hash of local version
				currentVerHash = self.generateHash(file)
				# get hash of server version
				serverHash = patchmanifest[file]["hash"]
				if currentVerHash != serverHash:
					# pull new file from server
					# TODO: instead of redownloading whole file, figure out how to use patches
					self.status.emit("Patch found for " + file)
					print("Patch found for " + file)
					newFileComp = urllib.URLopener()
					newFileComp.retrieve("http://kcmo-1.download.toontownrewritten.com/content/" + file,
									 self.gameInstallPath + "temp/" + file + ".bz2")
					data = bz2.BZ2File(self.gameInstallPath + "temp/" + file + ".bz2").read()
					print("Decompressing")
					newFile = open(self.gameInstallPath + "temp/" + file, "wb")
					newFile.write(data)
					newFile.close()
					try:
						os.remove(self.gameInstallPath + file)
					except WindowsError, IOError:
						pass
					shutil.move(self.gameInstallPath + "temp/" + file, self.gameInstallPath + file)
	def getData(self):
		return self.data