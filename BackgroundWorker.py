from PyQt4.QtCore import *
import time
import httplib, urllib, json
class APIWorker(QThread):
	
	def __init__(self, rawParams, headers, connection=None):
		QThread.__init__(self)
		self.connection = connection
		self.rawParams = rawParams
		self.headers = headers
		
	def run(self):
		# encode params
		self.params = urllib.urlencode(self.rawParams)
		if self.connection == None:
			# start a connection
			self.connection = httplib.HTTPSConnection("www.toontownrewritten.com")
		# send provided params and headers
		self.connection.request("POST", "/api/login?format=json", self.params, self.headers)
		
		self.response = self.connection.getresponse()
	def getresponse(self):
		return self.response
	def getconnection(self):
		return self.connection