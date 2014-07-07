import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class CloseButton(QLabel):
	def __init__(self, parent=None):
		QLabel.__init__(self, parent)
		self.setStyleSheet("background-image: url(./images/buttons/close/window_close_button_normal.png)")
		self.resize(44,44)
		self.show()
		
	def mousePressEvent(self, event):
		self.setStyleSheet("background-image: url(./images/buttons/close/window_close_button_down.png)")
	def mouseReleaseEvent(self, event):
		self.setStyleSheet("background-image: url(./images/buttons/close/window_close_button_normal.png)")
		sys.exit()
	def enterEvent(self, event):
		self.setStyleSheet("background-image: url(./images/buttons/close/window_close_button_hover.png)")
	def leaveEvent(self, event):
		self.setStyleSheet("background-image: url(./images/buttons/close/window_close_button_normal.png)")
class MinimizeButton(QLabel):
	def __init__(self, window, parent=None):
		QLabel.__init__(self, parent)
		self.window = window
		self.setStyleSheet("background-image: url(./images/buttons/minimize/window_minimize_button_normal.png)")
		self.resize(44,44)
		self.show()
		
	def mousePressEvent(self, event):
		self.setStyleSheet("background-image: url(./images/buttons/minimize/window_minimize_button_down.png)")
	def mouseReleaseEvent(self, event):
		self.setStyleSheet("background-image: url(./images/buttons/minimize/window_minimize_button_normal.png)")
		self.window.showMinimized()
	def enterEvent(self, event):
		self.setStyleSheet("background-image: url(./images/buttons/minimize/window_minimize_button_hover.png)")
	def leaveEvent(self, event):
		self.setStyleSheet("background-image: url(./images/buttons/minimize/window_minimize_button_normal.png)")
class GoButton(QLabel):
	def __init__(self, parent=None):
		QLabel.__init__(self, parent)
		self.setStyleSheet("background-image: url(./images/buttons/go/window_go_button_normal.png)")
		self.resize(100,100)
		self.show()
	def mousePressEvent(self, event):
		self.setStyleSheet("background-image: url(./images/buttons/go/window_go_button_click.png)")
	def mouseReleaseEvent(self, event):
		self.setStyleSheet("background-image: url(./images/buttons/go/window_go_button_normal.png)")
		self.emit(SIGNAL("loginEvent()"))
	def enterEvent(self, event):
		self.setStyleSheet("background-image: url(./images/buttons/go/window_go_button_hover.png)")
	def leaveEvent(self, event):
		self.setStyleSheet("background-image: url(./images/buttons/go/window_go_button_normal.png)")