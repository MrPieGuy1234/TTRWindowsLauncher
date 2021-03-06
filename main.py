import sys, os, subprocess, shutil
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *
from Button import *
from Effect import *
from LoginTextBox import *
from Dialog import *
import httplib, urllib, json
import hashlib, bz2
from BackgroundWorker import *
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
		self.checkForUpdates()
	def startLogin(self):
		self.statusLabel.setText("Logging in...")
		print("Sending username/password to server...")
		# assemble a request with username and password as parameters
		params = {"username": str(self.usernameTextBox.text()), "password": str(self.passwordTextBox.text())}
		headers = {"Content-type": "application/x-www-form-urlencoded",
				   "Accept": "text/plain"}
		# send data to login API
		self.apiWorker = APIWorker(params, headers)
		self.apiWorker.finished.connect(self.continueLogin)
		self.apiWorker.start()
		
	def continueLogin(self):
		# get server response
		response = self.apiWorker.getresponse()
		self.connection = self.apiWorker.getconnection()
		data = response.read()
		# turn json into pythonic format
		try:
			formattedData = json.loads(data)
		except ValueError:
			self.statusLabel.setText("Could not log in, try again later.")
			return
		if formattedData["success"] == "true":
			# we now have a cookie and gameserver, we can log in now.
			print("Success! Starting the game...")
			self.statusLabel.setText("Starting game...")
			self.startGame(formattedData["cookie"], formattedData["gameserver"])
			self.connection.close()
		elif formattedData["success"] == "delayed":
			# waiting in the queue, save the token for later, try again after 0.5 seconds (DOS them into oblivion)
			print("Now waiting in queue! ETA: " + formattedData["eta"] + ", Position in line: " + formattedData["position"])
			self.statusLabel.setText("ETA: " + formattedData["eta"] + ", Position in line: " + formattedData["position"])
			self.queueToken = formattedData["queueToken"]
			timer = QTimer(self.bgImage)
			QObject.connect(timer, SIGNAL("timeout()"), self.pingQueue)
			timer.setSingleShot(True)
			timer.start(500)
		elif formattedData["success"] == "partial":
			# store response token
			self.authToken = formattedData["responseToken"]
			# show dialog
			self.testDialog.show()
			# connect submit and cancel buttons to functions
			self.testDialog.accepted.connect(self.continueTwoFactor)
			self.testDialog.rejected.connect(self.cancelTwoFactor)
		else:
			# can't log in, probably because of invalid password
			print("Unable to log into the game. Reason: " + formattedData["banner"])
			self.statusLabel.setText(formattedData["banner"])
			self.connection.close()
	
	def continueTwoFactor(self):
		# tell api user's token and the response token from earlier
		params = {"appToken": self.testDialog.appToken, "authToken": self.authToken}
		headers = {"Content-type": "application/x-www-form-urlencoded",
				   "Accept": "text/plain"}
		self.apiWorker.setProps(params, headers, self.connection)
		self.apiWorker.finished.connect(self.continueLogin)
		self.apiWorker.start()
	def cancelTwoFactor(self):
		# user cancelled login
		self.statusLabel.setText("Login cancelled")
	def pingQueue(self):
		print("Pinging server for position in line...")
		params = {"queueToken": self.queueToken}
		headers = {"Content-type": "application/x-www-form-urlencoded",
				   "Accept": "text/plain"}
		self.apiWorker.setProps(params, headers, self.connection)
		self.apiWorker.finished.connect(self.continueLogin)
		self.apiWorker.start()
	
	########################
	#		  GAME		   #
	########################
		
	def startGame(self, cookie, gameserver):
		# save current working directory for later
		oldCWD = os.getcwd()
		# set the working directory to install directory
		os.chdir(self.gameInstallPath)
		# set environment variables
		os.environ["TTR_PLAYCOOKIE"] = cookie
		os.environ["TTR_GAMESERVER"] = gameserver
		# start the game
		self.gameInstance = subprocess.Popen("TTREngine.exe")
		# switch back to old
		os.chdir(oldCWD)
		# hide the launcher
		self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)
		# monitor game
		self.gameChecker = GameWorker(self.gameInstance)
		# tell us when the game exits
		self.gameChecker.gameExit.connect(self.gameExited)
		self.gameChecker.start()
		# start tracking invasions
		self.invasionWorker = InvasionWorker()
		# send new data to dialog
		self.invasionWorker.newInvasionData.connect(self.itDialog.newInvasionData)
		self.invasionWorker.start()
		# show tray icon
		self.trayIcon.show()
		self.trayIcon.showMessage("Invasions", "Now gathering invasion data. Click for details.", QSystemTrayIcon.Information, 6000)
		
	def gameExited(self, errCode):
		# show the launcher
		self.setWindowFlags(Qt.FramelessWindowHint)
		self.statusLabel.setText("")
		self.show()
		self.trayIcon.hide()
		self.invasionWorker.terminate()
		self.itDialog.hide()
		if errCode != 0:
			self.statusLabel.setText("Looks like the game crashed!")
	def checkForUpdates(self):
		self.dlWorker = DownloadWorker(self.gameInstallPath)
		self.dlWorker.finished.connect(self.startLogin)
		self.dlWorker.status.connect(self.statusLabel.setText)
		self.dlWorker.start()
	
	
	########################
	#		 TRACKER	   #
	########################
	
	def quitInvasionTracker(self):
		self.trayIcon.hide()
	def showTrackerUI(self):
		self.itDialog.show()
	
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
		self.chalkboardPapers.setStyleSheet("background-image: url(./images/window_chalkboard_papers_half.png);")
	def unfadePapers(self, event):
		self.chalkboardPapers.setStyleSheet("background-image: url(./images/window_chalkboard_papers.png);")
	########################
	#		  MAIN		   #
	########################

	def __init__(self):
		# create app, init parent
		app = QApplication(sys.argv)
		# make sure we quit only when we tell it to
		app.setQuitOnLastWindowClosed(False)
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
		
		# create the two-factor dialog for later
		self.twoFactorDialog = TwoFactorDialog()
		
		# create invasion tracker dialog for later
		self.itDialog = InvasionTrackerDialog()
		# initialize tray icons
		self.trayIcon = QSystemTrayIcon(QIcon("images/trayIcon.png"), self)
		self.trayMenu = QMenu(self)
		self.trayMenu.addAction("Exit", self.quitInvasionTracker)
		self.trayMenu.addAction("Show Tracker", self.showTrackerUI)
		self.trayIcon.setContextMenu(self.trayMenu)
		
		sys.exit(app.exec_())
		
if __name__ == "__main__":
	main = Main()	