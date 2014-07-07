from PyQt4.QtCore import *
from PyQt4.QtGui import *
from random import randint
from random import randrange

class ElectricEffect(QLabel):
	def __init__(self, parent=None):
		QLabel.__init__(self, parent)
		self.setStyleSheet("background-image: url(./images/window_machine_electricity.png)")
		self.resize(85, 65)
		self.parent = parent
		self.hide()
		
		# the most complicated animation sequence ever
		self.startElectricEffect(randrange(0,10))
	def startElectricEffect(self, type):
		if type <= 5:
			self.electricTiming = 1500
		else:
			self.electricTiming = 500
		electricTimer = QTimer(self.parent)
		QObject.connect(electricTimer, SIGNAL("timeout()"), self.showElectric)
		electricTimer.setSingleShot(True)
		electricTimer.start(self.electricTiming)
	def showElectric(self):
		self.show()
		electricTimer = QTimer(self.parent)
		QObject.connect(electricTimer, SIGNAL("timeout()"), self.hideElectric)
		electricTimer.setSingleShot(True)
		electricTimer.start(250)
	def hideElectric(self):
		self.hide()
		self.startElectricEffect(randrange(0,10))
		
class DialEffect(QLabel):
	def __init__(self, dialVel, parent=None):
		QLabel.__init__(self, parent)
		self.setStyleSheet("background-image: url(./images/window_machine_dial_background.png)")
		self.resize(30,30)
		self.show()
		
		self.dialAngle = 0
		self.dialVelocity = dialVel
		
		self.dial = QLabel(self)
		self.dial.resize(30,30)
		self.dial.show()
		self.dial.paintEvent = self.rotateDial
		
		# tell dial hand to repaint every 10ms
		dialTimer = QTimer(parent)
		QObject.connect(dialTimer, SIGNAL("timeout()"), self.dial.repaint)
		dialTimer.start(10)
		
	def rotateDial(self, event):
		# add velocity (read: degrees) to dial hand
		self.dialAngle += self.dialVelocity
		
		image = QImage("images/window_machine_dial_hand.png")
		
		painter = QPainter()
		painter.begin(self.dial)
		painter.translate(self.width()/2, self.height()/2)
		painter.rotate(self.dialAngle)
		painter.translate(-self.width()/2, -self.height()/2)
		painter.drawImage(self.dial.rect(), image)
		painter.end()
	
		