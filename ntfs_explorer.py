import sys, os, pytsk3
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QStandardItemModel
from time import *
from functools import partial
from struct import *
from datetime import datetime
import time

DEBUG = False
VOLUME = ""

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
        self.dirValue.setFixedWidth(600)
        dirButton = QPushButton("Go")
        dirButton.clicked.connect(self.gotoDir)
        exportBtn = QPushButton("Export HTML")
        exportBtn.clicked.connect(self.exportHtml)

        dirLayout = QGridLayout()
        dirLayout.setAlignment(Qt.AlignLeft)
        dirLayout.addWidget(dirName,0,0,Qt.AlignLeft)
        dirLayout.addWidget(self.dirValue,0,1,Qt.AlignLeft)
        dirLayout.addWidget(dirButton,0,2,Qt.AlignLeft)
        dirLayout.addWidget(exportBtn,0,3,Qt.AlignRight)


        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        buttonBox.accepted.connect(self.accept)

        self.dView = QTreeView()
        self.dView.setRootIsDecorated(False)
        self.dView.setAlternatingRowColors(True)
        self.dView.doubleClicked.connect(self.selectDir)
        self.dView.setSortingEnabled(True)

        self.model = self.createModel(self)
        self.dView.setModel(self.model)
        #self.dView.sortByColumn(0,Qt.AscendingOrder)
        self.loadRootDir(VOLUME)


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
        try:
            self.img = pytsk3.Img_Info('\\\\.\\'+volumename)
            self.fs_info = pytsk3.FS_Info(self.img)
        except:
            msg = QMessageBox(QMessageBox.Critical, "Error", "Check your Volume Name! (ex. C:)", QMessageBox.NoButton, self)
            msg.addButton("&Close", QMessageBox.RejectRole)
            msg.exec_()
            sys.exit()
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
                fname = f.info.name.name.decode('utf-8')
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
            selectFile = self.fs_info.open(pathname)
            self.exportFile(selectFile)
            self.dirValue.setText(str(self.cwd))
            self.gotoDir()
            return
        self.file_info = []
        path = self.getPath(selectedPath)
        self.cwd = path
        for f in selectedPath:
            try:
                fname = f.info.name.name.decode('utf-8')
                mtime = TimeFormat(f.info.meta.mtime)
                atime = TimeFormat(f.info.meta.atime)
                ctime = TimeFormat(f.info.meta.crtime)
                etime = TimeFormat(f.info.meta.ctime)
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
                        name = f.info.name.name.decode('utf-8') + "/" + name

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
            self.addData(str(cnt), f[0],f[1],f[2],f[3],f[4],f[5],f[6],f[7])
            cnt += 1
        #self.dView.sortByColumn(0,Qt.DescendingOrder)

    def exportFile(self,file):
        name = file.info.name.name.decode('utf-8')
        offset = 0
        if file.info.meta == None:
            msg = QMessageBox(QMessageBox.Information,"Error","Fail to read meta data",QMessageBox.NoButton,self)
            msg.addButton("&Close", QMessageBox.RejectRole)
            msg.exec_()
            return
        size = file.info.meta.size
        BUFF_SIZE = 1024 * 1024
        data = open('./export/'+name,'wb')
        while offset < size:
            av_to_read = min(BUFF_SIZE, size - offset)
            d = file.read_random(offset,av_to_read)
            if not d: break
            data.write(d)
            offset += len(d)
        msg = QMessageBox(QMessageBox.Information,"Success","File export Completed!",QMessageBox.NoButton,self)
        msg.addButton("&Close",QMessageBox.RejectRole)
        msg.exec_()

    def exportHtml(self):
        now = time.localtime()
        s = "%04d%02d%02d_%02d%02d%02d" % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)
        fname = "export_" + s + ".html"
        f = open('./html/'+fname, 'w')
        hdr_src = "<!DOCTYPE html><html><head><title>BoB6 NTFS</title><style>table, th, td {border: 1px solid black;border-collapse: collapse;}{padding: 5px;text-align: left;}table#t01 tr:nth-child(even) {background-color: #eee;}table#t01 tr:nth-child(odd) {background-color:#fff;}table#t01 th {background-color: black;color: white;}</style></head><body><h1> BoB6 Digital Forensics 6th Choi Jungwan </h1><hr>"
        vol_src = "<h2> Volume : " + VOLUME + "</h2><hr>"
        path_src = "<h2> Path: " + self.cwd 
        path_src += "</h2><hr><table id=\"t01\"><tr><th>Num</th><th>Name</th><th>Size</th><th>Type</th><th>mtime</th><th>atime</th><th>ctime</th><th>etime</th></tr>"
        tail_src ="</table></body><footer><hr><p>Made by: Jungwan Choi</p><p>Contact information: <a href=\"mailto:baio2033@korea.ac.kr\">baio2033@korea.ac.kr</a>.</p></footer></html>"
        f.write(hdr_src)
        f.write(vol_src)
        f.write(path_src)
        cnt = 0
        for e in self.file_info:
            entry_src = "<tr>"
            entry_src += "<td>" + str(cnt) + "</td>"
            entry_src += "<td>" + str(e[0]) + "</td>"
            entry_src += "<td>" + str(e[1]) + "</td>"
            entry_src += "<td>" + str(e[2]) + "</td>"
            entry_src += "<td>" + str(e[4]) + "</td>"
            entry_src += "<td>" + str(e[5]) + "</td>"
            entry_src += "<td>" + str(e[6]) + "</td>"
            entry_src += "<td>" + str(e[7]) + "</td>"
            f.write(entry_src)
            cnt += 1
        f.write(tail_src)
        f.close()


        msg = QMessageBox(QMessageBox.Information, "Success", "HTML export Completed!", QMessageBox.NoButton, self)
        msg.addButton("&Close", QMessageBox.RejectRole)
        msg.exec_()


class VolumePop(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Volume")

        layout = QGridLayout()
        self.setLayout(layout)

        self.volName = QLabel("Volume ")
        self.volValue = QLineEdit()
        self.volValue.setFixedWidth(200)
        self.volButton = QPushButton("Enter")
        self.volButton.clicked.connect(self.setVolume)

        layout.addWidget(self.volName,0,1)
        layout.addWidget(self.volValue,0,2)
        layout.addWidget(self.volButton,0,3)

        self.show()

    def setVolume(self):
        global VOLUME
        print(self.volValue.text())
        if self.volValue.text() != "":
            VOLUME = self.volValue.text()
            self.reject()

def TimeFormat(filetime):
    tmp = datetime.fromtimestamp(filetime).strftime("%Y-%m-%d %H:%M:%S")
    return tmp

if __name__ == "__main__":
    try:
        os.mkdir('./export')
    except:
        pass
    try:
        os.mkdir('./html')
    except:
        pass
    app = QApplication(sys.argv)
    
    volCheck = VolumePop()
    if volCheck.exec_():
        print("[+] please wait...")
    dialog = MainDialog()
    sys.exit(app.exec_())