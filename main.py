import sys, os, subprocess, shutil
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *
from Button import *
from Effect import *
from LoginTextBox import *
import httplib, urllib, json
import hashlib, bz2
class Main(QMainWindow):

	########################
	#		 EVENTS		   #
	########################
	
	def mousePressEvent(self, event):
		# get mouse position to calculate where to move window
		self.mouseOffset = event.pos()
	def mouseMoveEvent(self, event):
		# get current window position and apply offset
		try:
			x = event.globalX()
			y = event.globalY()
			x_w = self.mouseOffset.x()
			y_w = self.mouseOffset.y()
			self.move(x-x_w, y-y_w)
		except AttributeError:
			# if someone tries to drag a button
			pass
	def loginEvent(self):
		# make sure text can show up before the request hangs the application for some reason
		self.statusLabel.setText("Logging in...")
		timer = QTimer(self.bgImage)
		QObject.connect(timer, SIGNAL("timeout()"), self.checkForUpdates)
		timer.setSingleShot(True)
		timer.start(100)
	def startLogin(self):
		print("Sending username/password to server...")
		# assemble a request with username and password as parameters
		params = urllib.urlencode({"username": str(self.usernameTextBox.text()), "password": str(self.passwordTextBox.text())})
		headers = {"Content-type": "application/x-www-form-urlencoded",
				   "Accept": "text/plain"}
		# start a connection
		self.connection = httplib.HTTPSConnection("www.toontownrewritten.com")
		# send data to login API
		self.connection.request("POST", "/api/login?format=json", params, headers)
		# get server response
		response = self.connection.getresponse()
		data = response.read()
		# turn json into pythonic format
		formattedData = json.loads(data)
		if formattedData["success"] == "true":
			# we now have a cookie and gameserver, we can log in now.
			print("Success! Starting the game...")
			self.statusLabel.setText("Starting game...")
			self.startGame(formattedData["cookie"], formattedData["gameserver"])
			self.connection.close()
		elif formattedData["success"] == "delayed":
			# waiting in the queue, save the token for later, try again after 0.5 seconds (DOS them in oblivion)
			print("Now waiting in queue! ETA: " + formattedData["eta"] + ", Position in line: " + formattedData["position"])
			self.statusLabel.setText("ETA: " + formattedData["eta"] + ", Position in line: " + formattedData["position"])
			self.queueToken = formattedData["queueToken"]
			timer = QTimer(self.bgImage)
			QObject.connect(timer, SIGNAL("timeout()"), self.pingQueue)
			timer.setSingleShot(True)
			timer.start(500)
		elif formattedData["success"] == "partial":
			# TODO: i dont have two-factor on my account
			print("Two-factor auth not yet implemented")
			self.statusLabel.setText("Two-factor not implemented.")
			self.connection.close()
		else:
			# can't log in, probably because of invalid password
			print("Unable to log into the game. Reason: " + formattedData["banner"])
			self.statusLabel.setText(formattedData["banner"])
			self.connection.close()
		
	def pingQueue(self):
		print("Pinging server for position in line...")
		params = urllib.urlencode({"queueToken": self.queueToken})
		headers = {"Content-type": "application/x-www-form-urlencoded",
				   "Accept": "text/plain"}
		self.connection.request("POST", "/api/login?format=json", params, headers)
		try:
			response = self.connection.getresponse()
		except httplib.BadStatusLine:
			self.statusLabel.setText("Unknown Error.")
		data = response.read()
		formattedData = json.loads(data)
		if formattedData["success"] == "true":
			# after 300 hours in line
			print("Success! Starting the game...")
			self.statusLabel.setText("Starting game...")
			self.startGame(formattedData["cookie"], formattedData["gameserver"])
			self.connection.close()
		elif formattedData["success"] == "delayed":
			# still waiting... schedule another ping...
			print("Still waiting in queue... ETA: " + formattedData["eta"] + ", Position in line: " + formattedData["position"])
			self.statusLabel.setText("ETA: " + formattedData["eta"] + ", Position in line: " + formattedData["position"])
			self.queueToken = formattedData["queueToken"]
			timer = QTimer(self.bgImage)
			QObject.connect(timer, SIGNAL("timeout()"), self.pingQueue)
			timer.setSingleShot(True)
			timer.start(500)
		else:
			# server goes down or something
			print("Unable to log into the game. Reason: " + formattedData["banner"])
			self.statusLabel.setText(formattedData["banner"])
			self.connection.close()
	
	########################
	#		  GAME		   #
	########################
		
	def startGame(self, cookie, gameserver):
		# set the working directory to install directory
		os.chdir("C:/Program Files (x86)/Toontown Rewritten")
		# set environment variables
		os.environ["TTR_PLAYCOOKIE"] = cookie
		os.environ["TTR_GAMESERVER"] = gameserver
		# start the game
		subprocess.Popen("TTREngine.exe")
		# we're done here
		sys.exit()
	def checkForUpdates(self):
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
					self.statusLabel.setText("Patch found for " + file)
					print("Patch found for " + file)
					newFileData = self.downloadFile(file)
					print("Decompressing")
					newFile = open(self.gameInstallPath + "temp/" + file, "wb")
					newFile.write(newFileData)
					newFile.close()
					try:
						os.remove(self.gameInstallPath + file)
					except WindowsError, IOError:
						pass
					shutil.move(self.gameInstallPath + "temp/" + file, self.gameInstallPath + file)
					
		self.startLogin()
	def downloadFile(self, file):
		newFileComp = urllib.URLopener()
		newFileComp.retrieve("http://kcmo-1.download.toontownrewritten.com/content/" + file,
						 self.gameInstallPath + "temp/" + file + ".bz2")
		return bz2.BZ2File(self.gameInstallPath + "temp/" + file + ".bz2").read()
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
		
	########################
	#		 WINDOW		   #
	########################
	
	def decorateWindow(self):
		# chalkboard image
		self.chalkboardImage = QLabel(self.bgImage)
		self.chalkboardImage.setStyleSheet("background-image: url(./images/window_chalkboard.png)")
		self.chalkboardImage.resize(900,680)
		self.chalkboardImage.show()
		
		# floodlights
		self.floodlightImage = QLabel(self.bgImage)
		self.floodlightImage.setStyleSheet("background-image: url(./images/window_floodlights.png)")
		self.floodlightImage.resize(900,680)
		self.floodlightImage.show()
		
		
		# machine image
		self.machineImage = QLabel(self.bgImage)
		self.machineImage.setStyleSheet("background-image: url(./images/window_machine.png)")
		self.machineImage.resize(900,680)
		self.machineImage.show()
		
		# add the close button
		self.closeButton = CloseButton(self.bgImage)
		self.closeButton.move(740, 50)
		
		# add minimize button, pass self so it can minimize
		self.minimizeButton = MinimizeButton(self, self.bgImage)
		self.minimizeButton.move(685, 50)
		
		# username and password
		self.usernameTextBox = LoginTextBox(self.bgImage)
		self.usernameTextBox.move(515,328)
		self.usernameTextBox.setPlaceholderText("Username")
		self.usernameTextBox.setFocus()
		
		self.passwordTextBox = LoginTextBox(self.bgImage)
		self.passwordTextBox.move(515, 362)
		self.passwordTextBox.setEchoMode(QLineEdit.Password)
		self.passwordTextBox.setPlaceholderText("Password")
		
		# go button
		self.goButton = GoButton(self.bgImage)
		self.goButton.move(735, 328)
		
		# electricity
		self.electricity = ElectricEffect(self.bgImage)
		self.electricity.move(360, 53)
		
		# dials
		self.firstDial = DialEffect(2, self.bgImage)
		self.firstDial.move(780, 270)
		
		self.secondDial = DialEffect(-1, self.bgImage)
		self.secondDial.move(780, 240)
		
		# status label
		font = QFont()
		font.setPointSize(9)
		
		self.statusLabel = QLabel(self.bgImage)
		self.statusLabel.setStyleSheet("color: white;")
		self.statusLabel.setFont(font)
		self.statusLabel.move(430, 174)
		self.statusLabel.resize(400, 18)
		self.statusLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
		self.statusLabel.show()
	
		# news page
		self.newsPage = QWebView(self.bgImage)
		self.newsPage.resize(296, 220)
		self.newsPage.move(72, 162)
		self.newsPage.load(QUrl("news.html"))
		self.newsPage.show()
		self.newsPage.enterEvent = self.fadePapers
		self.newsPage.leaveEvent = self.unfadePapers
		
		# chalkboard papers
		self.chalkboardPapers = QLabel(self.bgImage)
		self.chalkboardPapers.setStyleSheet("background-image: url(./images/window_chalkboard_papers.png); opacity: 50%")
		self.chalkboardPapers.resize(136, 136)
		self.chalkboardPapers.move(20, 132)
		self.chalkboardPapers.show()
		
		# surlee
		self.monkey = QLabel(self.bgImage)
		self.monkey.setStyleSheet("background-image: url(./images/window_monkey.png)")
		self.monkey.resize(269, 350)
		self.monkey.move(240, 285)
		self.monkey.show()
	
	def fadePapers(self, event):
		self.chalkboardPapers.setStyleSheet("background-image: url(./images/window_chalkboard_papers_half.png); opacity: 50%")
	def unfadePapers(self, event):
		self.chalkboardPapers.setStyleSheet("background-image: url(./images/window_chalkboard_papers.png); opacity: 50%")
	########################
	#		  MAIN		   #
	########################

	def __init__(self):
		# create app, init parent
		app = QApplication(sys.argv)
		QMainWindow.__init__(self)
		
		# make sure we're doing stuff in the right place
		self.gameInstallPath = "C:/Program Files (x86)/Toontown Rewritten/"
		
		# resize to size of background image
		self.resize(900,680)
		# make background transparent
		self.setAttribute(Qt.WA_TranslucentBackground)
		# get rid of decorations
		self.setWindowFlags(Qt.FramelessWindowHint)
		# set window title
		self.setWindowTitle("Toontown Launcher")
		# show window
		self.show()
		
		# put background image into a label (wtf)
		self.bgImage = QLabel()
		self.bgImage.setStyleSheet("background-image: url(./images/window_background.png)")
		# set background image as main widget
		self.setCentralWidget(self.bgImage)
		
		# add pretty stuff
		self.decorateWindow()
		
        # listen for login signal
		QObject.connect(self.goButton, SIGNAL("loginEvent()"), self.loginEvent)
		QObject.connect(self.passwordTextBox, SIGNAL("loginEvent()"), self.loginEvent)
		
		sys.exit(app.exec_())
		
if __name__ == "__main__":
	main = Main()	