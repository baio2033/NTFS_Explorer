import sys, os
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QStandardItemModel
from time import *
from functools import partial

class MainDialog(QDialog):
	num, name, size, path, mtime, atime, ctime, etime = range(8)
	def __init__(self, parent=None):
		super(MainDialog, self).__init__(parent)
		self.initUI()

	def initUI(self):
		self.setWindowTitle("NTFS Explorer")
		
		path = "\t\t\t\t\t"
		dirName = QLabel("Folder ")
		dirValue = QLabel(path)
		dirValue.setFrameStyle(QFrame.Panel | QFrame.Sunken)
		dirButton = QPushButton("Go")
		dirButton.clicked.connect(self.test)

		dirLayout = QGridLayout()
		dirLayout.setAlignment(Qt.AlignLeft)
		dirLayout.addWidget(dirName,0,0,Qt.AlignLeft)
		dirLayout.addWidget(dirValue,0,1,Qt.AlignLeft)
		dirLayout.addWidget(dirButton,0,2,Qt.AlignLeft)

		buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
		buttonBox.accepted.connect(self.accept)

		dView = QTreeView()
		dView.setRootIsDecorated(False)
		dView.setAlternatingRowColors(True)
		dView.doubleClicked.connect(self.test)

		self.model = self.createModel(self)
		dView.setModel(self.model)

		mainLayout = QVBoxLayout()
		mainLayout.addLayout(dirLayout)
		mainLayout.addWidget(dView)
		mainLayout.addWidget(buttonBox)

		self.setLayout(mainLayout)
		self.resize(1080, 780)

		self.show()

	def test():
		print("hihi")

	def createModel(self, parent):
		model = QStandardItemModel(0,5,parent)
		model.setHeaderData(self.num, Qt.Horizontal, "Num")
		model.setHeaderData(self.name, Qt.Horizontal, "Name")
		model.setHeaderData(self.size, Qt.Horizontal, "Size")
		model.setHeaderData(self.path, Qt.Horizontal, "Path")
		model.setHeaderData(self.mtime, Qt.Horizontal, "mtime")
		model.setHeaderData(self.atime, Qt.Horizontal, "atime")
		model.setHeaderData(self.ctime, Qt.Horizontal, "ctime")
		model.setHeaderData(self.etime, Qt.Horizontal, "etime")
		return model



if __name__ == "__main__":
	app = QApplication(sys.argv)
	dialog = MainDialog()
	sys.exit(app.exec_())