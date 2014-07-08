from PyQt4.QtCore import *
from PyQt4.QtGui import *
import json

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
class InvasionTrackerDialog(QDialog):
	newInvasion = pyqtSignal(str)
	def __init__(self):
		QDialog.__init__(self)
		self.resize(336, 300)
		self.setWindowTitle("Invasion Tracker")
		
		font = QFont()
		font.setPointSize(13)
		
		self.currentInvasionsLabel = QLabel("Current Invasions", self)
		self.currentInvasionsLabel.setFont(font)
		self.currentInvasionsLabel.resize(self.width(), self.currentInvasionsLabel.height())
		self.currentInvasionsLabel.move(0, 5)
		self.currentInvasionsLabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
		self.currentInvasionsLabel.show()
		
		margin = 15
		header = ["Cog Type", "District", "Cogs Defeated"]
		tempData = []
		self.tableModel = InvasionTableModel(tempData, header, self)
		self.invasionTable = QTableView(self)
		self.invasionTable.setModel(self.tableModel)
		self.invasionTable.resize(self.width()-(margin*2), 225)
		self.invasionTable.move(margin, 50)
		self.invasionTable.show()
	def newInvasionData(self, data):
		formattedData = json.loads(str(data))
		tableData = []
		for inv in formattedData["invasions"]:
			tableData.append([formattedData["invasions"][inv]["type"], inv, formattedData["invasions"][inv]["progress"]])
		self.tableModel.setData(tableData)
		self.tableModel.layoutChanged.emit()
class InvasionTableModel(QAbstractTableModel):
	def __init__(self, dataIn, headerData, parent=None):
		QAbstractTableModel.__init__(self, parent)
		self.arrayData = dataIn
		self.headerData = headerData
	def rowCount(self, parent):
		return len(self.arrayData)
	def columnCount(self, parent):
		return len(self.headerData)
	def setData(self, data):
		self.arrayData = data
	def data(self, index, role):
		if not index.isValid():
			return QVariant()
		elif role != Qt.DisplayRole:
			return QVariant()
		return QVariant(self.arrayData[index.row()][index.column()])
	def headerData(self, col, orientation, role):
		if orientation == Qt.Horizontal and role == Qt.DisplayRole:
			return QVariant(self.headerData[col])
		return QVariant()
		