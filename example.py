import sys, os, pytsk3
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QStandardItemModel
from time import *
from functools import partial
from struct import *
from datetime import datetime

DEBUG = False

class MainDialog(QDialog):
    num, name, size, ftype, path, mtime, atime, ctime, etime = range(9)
    file_info = []

    def __init__(self, parent=None):
        super(MainDialog, self).__init__(parent)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("NTFS Explorer")

        path = "\t\t\t\t\t"
        dirName = QLabel("Folder ")
        self.dirValue = QLineEdit()
        dirButton = QPushButton("Go")
        dirButton.clicked.connect(self.gotoDir)

        dirLayout = QGridLayout()
        dirLayout.setAlignment(Qt.AlignLeft)
        dirLayout.addWidget(dirName,0,0,Qt.AlignLeft)
        dirLayout.addWidget(self.dirValue,0,1,Qt.AlignLeft)
        dirLayout.addWidget(dirButton,0,2,Qt.AlignLeft)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        buttonBox.accepted.connect(self.accept)

        self.dView = QTreeView()
        self.dView.setRootIsDecorated(False)
        self.dView.setAlternatingRowColors(True)
        self.dView.doubleClicked.connect(self.selectDir)

        self.model = self.createModel(self)
        self.dView.setModel(self.model)
        self.dView.sortByColumn(0,Qt.AscendingOrder)
        self.loadRootDir('C:')


        mainLayout = QVBoxLayout()
        mainLayout.addLayout(dirLayout)
        mainLayout.addWidget(self.dView)
        mainLayout.addWidget(buttonBox)

        self.setLayout(mainLayout)
        self.resize(1080, 780)

        self.show()

    def test(self):
        print("hihi")

    def loadRootDir(self, volumename):
        self.img = pytsk3.Img_Info('\\\\.\\'+volumename)
        self.fs_info = pytsk3.FS_Info(self.img)

        if str(self.fs_info.info.ftype) != "TSK_FS_TYPE_NTFS_DETECT":
            msg = QMessageBox(QMessageBox.Critical, "Error", "None NTFS File System!", QMessageBox.NoButton, self)
            msg.addButton("&Close", QMessageBox.RejectRole)
            msg.exec_()
            sys.exit()
        self.rootDir = self.fs_info.open_dir('/')
        path = self.getPath(self.rootDir)
        self.cwd = path
        cnt = 0
        for f in self.rootDir:  
            try:
                fname = f.info.name.name
                mtime = TimeFormat(f.info.meta.mtime)
                atime = TimeFormat(f.info.meta.atime)
                ctime = TimeFormat(f.info.meta.ctime)
                etime = TimeFormat(f.info.meta.crtime)
                size = f.info.meta.size
                if f.info.meta.type:
                    if str(f.info.meta.type) == "TSK_FS_META_TYPE_DIR":
                        ftype = "DIR"
                    elif str(f.info.meta.type) == "TSK_FS_META_TYPE_REG":
                        ftype = "REG"
                    else:
                        ftype = ""
                else:
                    ftype = ""
                self.file_info.append([fname, size, ftype, path, mtime, atime, ctime ,etime])
            except:
                pass

        self.createTree()

    def gotoDir(self):
        self.delData()
        pathname = self.dirValue.text()
        try:
            selectedPath = self.fs_info.open_dir(pathname)
        except:
            msg = QMessageBox(QMessageBox.Critical, "Error", "Select only Directory!", QMessageBox.NoButton, self)
            msg.addButton("&Close", QMessageBox.RejectRole)
            msg.exec_()
            self.dirValue.setText(str(self.cwd))
            self.gotoDir()
            return
        self.file_info = []
        path = self.getPath(selectedPath)
        self.cwd = path
        for f in selectedPath:
            try:
                fname = f.info.name.name
                mtime = TimeFormat(f.info.meta.mtime)
                atime = TimeFormat(f.info.meta.atime)
                ctime = TimeFormat(f.info.meta.ctime)
                etime = TimeFormat(f.info.meta.crtime)
                size = f.info.meta.size
                if f.info.meta.type:
                    if str(f.info.meta.type) == "TSK_FS_META_TYPE_DIR":
                        ftype = "DIR"
                    elif str(f.info.meta.type) == "TSK_FS_META_TYPE_REG":
                        ftype = "REG"
                    else:
                        ftype = ""
                else:
                    ftype = ""
                self.file_info.append([fname, size, ftype, path, mtime, atime, ctime ,etime])
            except:
                pass

        self.createTree()

    def selectDir(self):
        data = self.model.itemData(self.dView.selectedIndexes()[1])
        path = self.cwd + str(data[0])
        if self.cwd.endswith("/") == False:
            path += "/"
        if path.endswith(".") or path.endswith(".."):
            tmp = path.split("/")
            path = ""
            for i in range(1,len(tmp)-2):
                path += "/" + tmp[i]
        self.dirValue.setText(path)

        self.gotoDir()

    def getPath(self,directory):
        name = ""      
        while True:
            chk = False
            prev_inode = directory.info.addr           
            for f in directory:
                if f.info.name.name == b'..':
                    chk = True
                    tmp_inode = f.info.meta.addr
                    directory = self.fs_info.open_dir(inode=tmp_inode)
            for f in directory:
                if f.info.meta:
                    if f.info.meta.addr == prev_inode:
                        name = decode_name(f.info.name.name) + "/" + name

            if chk == False:
                break
        return name[1:]

    def createModel(self, parent):
        model = QStandardItemModel(0,9,parent)
        model.setHeaderData(self.num, Qt.Horizontal, "Num")
        model.setHeaderData(self.name, Qt.Horizontal, "Name")
        model.setHeaderData(self.size, Qt.Horizontal, "Size")
        model.setHeaderData(self.ftype, Qt.Horizontal, "Type")
        model.setHeaderData(self.path, Qt.Horizontal, "Path")
        model.setHeaderData(self.mtime, Qt.Horizontal, "mtime")
        model.setHeaderData(self.atime, Qt.Horizontal, "atime")
        model.setHeaderData(self.ctime, Qt.Horizontal, "ctime")
        model.setHeaderData(self.etime, Qt.Horizontal, "etime")
        return model

    def addData(self, num, name, size, ftype, path, mtime, atime, ctime, etime):
        self.model.insertRow(0)
        self.model.setData(self.model.index(0, self.num), num)
        self.model.setData(self.model.index(0, self.name), name)
        self.model.setData(self.model.index(0, self.size), size)
        self.model.setData(self.model.index(0, self.ftype), ftype)
        self.model.setData(self.model.index(0, self.path), path)
        self.model.setData(self.model.index(0, self.mtime), mtime)
        self.model.setData(self.model.index(0, self.atime), atime)
        self.model.setData(self.model.index(0, self.ctime), ctime)
        self.model.setData(self.model.index(0, self.etime), etime)

    def delData(self):
        self.model.removeRows(0,self.model.rowCount())

    def createTree(self):
        cnt = 0
        for f in self.file_info:
            self.addData(str(cnt), decode_name(f[0]),f[1],f[2],f[3],f[4],f[5],f[6],f[7])
            cnt += 1
        #self.dView.sortByColumn(0,Qt.DescendingOrder)

def decode_name(name):
    decoded_name = ""
    for i in name:
        if i != 0:
            decoded_name += chr(i)
    return decoded_name

def TimeFormat(filetime):
    tmp = datetime.fromtimestamp(filetime).strftime("%Y-%m-%d %H:%M:%S")
    return tmp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = MainDialog()
    sys.exit(app.exec_())