from PyQt4.QtCore import *
from PyQt4.QtGui import *

class TwoFactorDialog(QDialog):
	def __init__(self):
		QDialog.__init__(self)
		self.setModal(True)
		self.resize(300, 200)
		self.setWindowTitle("Two-factor Auth")
		
		font = QFont()
		font.setPointSize(13)
		
		self.authTokenLabel = QLabel("Please enter an authenticator token.", self)
		self.authTokenLabel.setFont(font)
		self.authTokenLabel.resize(self.width(), self.authTokenLabel.height())
		self.authTokenLabel.move(0, 15)
		self.authTokenLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
		self.authTokenLabel.show()
		
		margin = 20
		self.tokenBox = QLineEdit(self)
		self.tokenBox.resize(self.width()-(margin*2), self.tokenBox.height())
		self.tokenBox.move(margin, 50)
		self.tokenBox.setContextMenuPolicy(Qt.NoContextMenu)
		self.tokenBox.textChanged.connect(self.tokenTextChanged)
		self.tokenBox.show()
		
		self.submitButton = QPushButton("Submit", self)
		self.submitButton.move(50, 100)
		self.submitButton.setEnabled(False)
		self.submitButton.setDefault(True)
		self.submitButton.clicked.connect(self.accept)
		self.submitButton.show()
		
		self.cancelButton = QPushButton("Cancel", self)
		self.cancelButton.move(175, 100)
		self.cancelButton.clicked.connect(self.reject)
		self.cancelButton.show()
	
	def accept(self):
		self.appToken = str(self.tokenBox.text())
		super(TwoFactorDialog, self).accept()
	
	def tokenTextChanged(self, text):
		if text == "":
			self.submitButton.setEnabled(False)
		else:
			self.submitButton.setEnabled(True)