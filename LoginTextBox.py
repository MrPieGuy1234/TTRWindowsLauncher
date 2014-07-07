import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class LoginTextBox(QLineEdit):
	def __init__(self, parent=None):
		QLineEdit.__init__(self, parent)
		
		font = QFont()
		font.setPointSize(13)
		
		# make it pretty
		self.setFrame(False)
		self.setStyleSheet("border-image: url(./images/input_normal.png); color: white;")
		self.setTextMargins(4, 0, 0, 0)
		self.setFont(font)
		self.setContextMenuPolicy(Qt.NoContextMenu)
		self.resize(218, 30)
		self.show()
	def focusInEvent(self, event):
		# called when clicked on
		self.setStyleSheet("border-image: url(./images/input_highlighted.png); color: white;")
		# call super to prevent some graphical glitches
		super(LoginTextBox, self).focusInEvent(event)
	def focusOutEvent(self, event):
		self.setStyleSheet("border-image: url(./images/input_normal.png); color: white;")
		super(LoginTextBox, self).focusOutEvent(event)
	def keyPressEvent(self, event):
		super(LoginTextBox, self).keyPressEvent(event)
		if event.key() == Qt.Key_Return:
			self.emit(SIGNAL("loginEvent()"))