# -*- coding: utf-8 -*-
  
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.Qt import Qt
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QDialog
from PyQt5 import QtWidgets
import os,sys,win32api
import requests,json
import zipfile
 
class Ui_download(object):
    def setupUi(self, Dialog):
        Dialog.setWindowFlags(Qt.FramelessWindowHint)
        Dialog.setObjectName("Dialog")
        Dialog.resize(300, 56)
        Dialog.setFixedSize(Dialog.width(), Dialog.height())
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        Dialog.setSizeGripEnabled(True)
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.gridLayout.setObjectName("gridLayout")
        self.progressBar = QtWidgets.QProgressBar(Dialog)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.progressBar.setObjectName("progressBar")
        self.gridLayout.addWidget(self.progressBar, 1, 0, 1, 1)
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
 
        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
 
    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label.setText(_translate("Dialog", "客户端更新下载中..."))
 
 
 
class downloadThread(QThread):
 
    download_proess_signal = pyqtSignal(int)
 
    def __init__(self, download_url, filesize, fileobj, buffer):
        super(downloadThread, self).__init__()
        self.download_url = download_url
        self.filesize = filesize
        self.fileobj = fileobj
        self.buffer = buffer
 
    def run(self):
        try:
            f = requests.get(self.download_url, stream=True)
            offset = 0
            for chunk in f.iter_content(chunk_size=self.buffer):
                if not chunk:
                    break
                self.fileobj.seek(offset)
                self.fileobj.write(chunk)
                offset = offset + len(chunk)
                proess = offset / int(self.filesize) * 100
                self.download_proess_signal.emit(int(proess))
            self.fileobj.close()
            self.exit(0)
        except Exception as e:
            print(e)
 
 
class download(QDialog, Ui_download):
    """
    下载类实现
    """
    def __init__(self, download_url, auto_close=True, parent=None):
        """
        Constructor
        
        @download_url:下载地址
        @auto_close:下载完成后时候是否需要自动关闭
        """
        super(download, self).__init__(parent)
        self.setupUi(self)
        self.progressBar.setValue(0)
        self.downloadThread = None
        self.download_url = download_url
        self.filesize = None
        self.fileobj = None
        self.auto_close = auto_close
        self.download()
 
    def download(self):
        self.filesize = requests.get(self.download_url, stream=True).headers['Content-Length']
        path = 'ota.zip'
        self.fileobj = open(path, 'wb+')
        self.downloadThread = downloadThread(self.download_url, self.filesize, self.fileobj, buffer=10240)
        self.downloadThread.download_proess_signal.connect(self.change_progressbar_value)
        self.downloadThread.start()
 
    def change_progressbar_value(self, value):
        self.progressBar.setValue(value)
        if self.auto_close and value == 100:
            zip_file = zipfile.ZipFile('ota.zip')   
            zip_file.extractall()                     
            zip_file.close()  
            win32api.ShellExecute(0, 'open', 'JDRailgun.exe', '','',1)
            self.close()
 
 
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    try:
        _app_ver=sys.argv[1]
    except:
        _app_ver=9999
    _app_url='https://cdn.starchina.top/app/version'
    _app_data={'name':'某东的超电磁炮'}
    _r=requests.post(_app_url,data=_app_data)

    verdata=json.loads(_r.text)
    if verdata['ver'] <= float(_app_ver):
        win32api.ShellExecute(0, 'open', 'JDRailgun.exe', '','',1)
        sys.exit('程序已是最新版无需升级')

    ui = download(verdata['url'])
    ui.show()
    sys.exit(app.exec_())