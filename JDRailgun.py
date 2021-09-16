#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os,sys,random
import json,requests,time
from datetime import datetime
from urllib.parse import quote
from PyQt5.QtWidgets import (QWidget,QMessageBox, QApplication, QVBoxLayout, QHBoxLayout,QTextBrowser, QDesktopWidget, QTextEdit, QLabel, QLineEdit, QPushButton,QFileDialog, QProgressBar,)
from PyQt5.QtCore import QUrl, pyqtSlot,Qt
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEngineScript, QWebEnginePage
_app_ver=1.0
_app_url='https://cdn.starchina.top/app/version'
_app_data={'name':'某东的超电磁炮'}
_r=requests.post(_app_url,data=_app_data)
verdata=json.loads(_r.text)

class MyWebEngineView(QWebEngineView):
    def __init__(self, *args, **kwargs):                          
        super(MyWebEngineView, self).__init__(*args, **kwargs)              
        QWebEngineProfile.defaultProfile().cookieStore().deleteAllCookies()        
        QWebEngineProfile.defaultProfile().cookieStore().deleteSessionCookies()
        QWebEngineProfile.defaultProfile().cookieStore().cookieAdded.connect(self.onCookieAdd)
        self.cookies = {}  
 
    def onCookieAdd(self, cookie):
        name = cookie.name().data().decode('utf-8')
        value = cookie.value().data().decode('utf-8')
        self.cookies[name] = value

    def get_cookie(self):
        cookie_str = ''
        for key, value in self.cookies.items():
            cookie_str += (key + '=' + value + ';')
        return cookie_str


class Browser(QWidget):
    def __init__(self):
        super().__init__()        
        self.init_ui()

    def clicklink(self,url):
        nowtext=self.logEdit.toHtml()
        s.load(url)
        s.loadProgress.connect(self.showlog)
        s.resize(500, 400)
        s.setWindowTitle('更多明细拉取中')
        s.show()
        self.logEdit.setHtml(nowtext)

    def showlog(self,a):
        s.setWindowTitle('详更多明细拉取中,进度%s%%' % a)
        if a==0:
            s.setWindowTitle('更多明细拉取中，请稍等')
        if a==100:
            s.setWindowTitle('更多明细日志')

    def init_ui(self):
        self.webView = MyWebEngineView()
        QWebEngineProfile.defaultProfile().cookieStore().cookieAdded.connect(self.get_cookie)
        self.logEdit = QTextBrowser()
        self.logEdit.setFixedHeight(200)
        self.logEdit.textChanged.connect(self.text_changed)
        self.logEdit.anchorClicked.connect(self.clicklink)
        self.logEdit.setOpenExternalLinks(False)
        self.addrEdit = QLineEdit()
        self.addrEdit.returnPressed.connect(self.load_url)
        self.webView.urlChanged.connect(
            lambda i: self.addrEdit.setText(i.toDisplayString()))
        self.ckEdit = QLineEdit()

        self.advEdit = QTextBrowser()
        self.advEdit.setFixedHeight(20)
        self.advEdit.setOpenExternalLinks(True)
        self.advEdit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.advEdit.setStyleSheet("background:transparent;border-width:0;border-style:outset")

        loadUrlBtn = QPushButton('抓取Cookies')
        loadUrlBtn.clicked.connect(self.get_cookie)
        chooseJsBtn = QPushButton('提交到代挂系统')
        chooseJsBtn.clicked.connect(self.post_to_cloud)
        top = QWidget()
        top.setFixedHeight(80)
        topBox = QVBoxLayout(top)
        topBox.setSpacing(0)
        topBox.setContentsMargins(5, 0, 0, 5)

        progBar = QProgressBar()
        progBox = QHBoxLayout()
        progBox.addWidget(progBar)
        topBox.addLayout(progBox)

        naviBox = QHBoxLayout()
        naviBox.addWidget(QLabel('URL:'))
        naviBox.addWidget(self.addrEdit)
        naviBox.addWidget(loadUrlBtn)
        topBox.addLayout(naviBox)

        naviBox = QHBoxLayout()
        naviBox.addWidget(QLabel('Cookie:'))
        naviBox.addWidget(self.ckEdit)
        naviBox.addWidget(chooseJsBtn)
        topBox.addLayout(naviBox)
        self.webView.loadProgress.connect(progBar.setValue)
        
      
        layout = QVBoxLayout(self)
        layout.addWidget(self.webView)
        layout.addWidget(top)
        layout.addWidget(self.advEdit)
        layout.addWidget(self.logEdit)
        self.show()
        self.resize(1024, 900)
        self.center()        
        self.setWindowTitle('某东的超电磁炮')
    
    def msg(self,title,content):
        QMessageBox.information(self,title,content)
 
    def update(self,title,content,url):
        r=QMessageBox.information (self,title,content,QMessageBox.Yes|QMessageBox.No,QMessageBox.Yes)
        if r==QMessageBox.Yes:
            QDesktopServices.openUrl(QUrl(url))

    def text_changed(self):
        cursor = self.logEdit.textCursor()
        self.logEdit.moveCursor(cursor.End)
    
    def get_cookie(self,status):
        cookie = self.webView.get_cookie()
        cookieDict = {}
        cookies = cookie.split(";")
        for co in cookies:
            co = co.strip()
            p = co.split('=')
            value = co.replace(p[0]+'=', '').replace('"', '')
            cookieDict[p[0]]=value

        if "pt_pin" in cookieDict.keys() and "pt_key" in cookieDict.keys():
            cookiekey="pt_key=%s;pt_pin=%s" %(cookieDict["pt_key"], cookieDict["pt_pin"])
            self.ckEdit.setText(str(cookiekey))            
            QWebEngineProfile.defaultProfile().cookieStore().deleteAllCookies()        
            QWebEngineProfile.defaultProfile().cookieStore().deleteSessionCookies()            
            if not status:
                self.log('抓取成功%s' % (cookieDict))
        else:
            self.ckEdit.setText('请先登录')
            if not status:
                self.log('未提取到有效的Cookies，请重新登陆')

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    @pyqtSlot()
    def load_url(self):
        url = self.addrEdit.text().strip()
        if not url.lower().startswith('http://') \
                and not url.lower().startswith('https://'):
            url = 'http://{}'.format(url)
        self.load(url)

    @pyqtSlot()
    def post_to_cloud(self):
        cookie=self.ckEdit.text().strip()        
        if "pt_pin" in cookie and "pt_key" in cookie:
            cookiekey={"ck": cookie}        
            cloud_url=verdata['server']['postck']
            r=requests.post(cloud_url,data=cookiekey)
            r_data=r.json()
            self.log('结果：<font color="#0000FF">%s</font><font color="#FF0000">%s</font>' % (r_data.get('name'),r_data.get('msg')))
            if r_data['code']==200:
                username=r_data.get('name')
                userinfo[username]={
                    "nickName":username,
                    "timestamp":time.time(),
                    "cookie":cookie
                }
                with open ('jdck.json','w+') as f:
                    f.write(json.dumps(userinfo))                
                self.msg('提交成功',r_data.get('name')+r_data.get('msg'))
            else:
                self.msg('提交失败',r_data.get('name')+r_data.get('msg'))

        else:            
            self.log('无效的Cookies，请重新输入或登陆提取')


    def log(self, msg, *args, **kwargs):
        m = str(msg)
        self.logEdit.append('{} {}'.format(
            datetime.now().strftime('%H:%M:%S'), m))

    def load(self, url):       
        self.addrEdit.setText(url)
        self.webView.load(QUrl(url))        
        self.log(f'加载完成，请输入你的Cookies，或登陆提取')

class logform(QWebEngineView):    
    def __init__(self, *args, **kwargs):                          
        super(logform, self).__init__(*args, **kwargs)   
    

if __name__ == '__main__':    
    app = QApplication(sys.argv)    
    b = Browser()    
    b.log(u'<font color="#FF0000">%s</font> Design by <a href=\'https://www.starchina.top\'>Kim</a> & Powerd by <a href=\'http://mads.vip/\'>Mads</a> &copy; GPL Licensed' % verdata['readme'])
    s = logform()
    if (verdata['ver'] > _app_ver):        
        b.update('有新版本','版本号:%s\n\n更新内容:%s\n\n是否现在下载新版?'%(verdata['ver'],verdata['whatsnew']),verdata['url'])

    r=requests.get('http://api.mads.vip/update.txt')
    r_data=json.loads(r.content.decode('utf8'))
    r_msg=r_data.get('JD代挂').get('公告')
    if r_msg:
        b.log('📢%s'% r_msg)
    r=requests.get('https://api.starchina.top/shop/promotion?site=%E4%BA%AC%E4%B8%9CPC')
    r_data=r.json()
    r_sa = random.sample(r_data.items(), 6) 
    m=''
    for n in r_sa:
        m += '<a href="%s">%s</a>  '%(n[1],n[0])
    b.advEdit.append('🎉 %s' % m)

    try:
        with open ('jdck.json','r') as f:
            userinfo=json.loads(f.read())
    except:
        userinfo={}
    for k,v in userinfo.items():
        headers={
            'user-agent':"jdapp;iPhone;10.0.2;14.3;network/4g;Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
            'cookie':v['cookie']
        }
        r=requests.get('https://me-api.jd.com/user_new/info/GetJDUserInfoUnion',headers=headers)
        r_json=r.json()
        ck_alive=(r_json.get('retcode')=='0')
        if ck_alive:
            alive='🔵'
            userlevel=r_json['data']['userInfo']['baseInfo']['levelName']
            if '钻石' in userlevel:
                ul='💎'
            elif '金牌' in userlevel:
                ul='🥇'
            elif '银牌' in userlevel:
                ul='🥈'                
            elif '铜牌' in userlevel:
                ul='🥉'            
            else:
                ul=''
            timestamp=v['timestamp']
            time_now=time.time()
            alive_time=int(30-((time_now-timestamp))/60/60/24)
            readlog="<a href='%s?cookies=%s'><span>更多明细</span></a>" % (verdata['server']['getbean'],quote(v['cookie']))
            user_msg='小白分数:%s 🌱京豆:%s 🧧红包:%s 预计有效期还剩：%s天  %s' % (r_json['data']['userInfo']['xbScore'],r_json['data']['assetInfo']['beanNum'],r_json['data']['assetInfo']['redBalance'],alive_time,readlog)
        else:
            alive='🔴'
            ul=''
            user_msg='Cookie状态已过期，请重新登陆'
        b.log('%s<strong>%s</strong>%s:%s' % (alive,k,ul,user_msg))
    b.logEdit.append('------------------------------------------------------------------------------<br>')
    
    b.load('https://mcr.jd.com/credit_home/pages/index.html?btPageType=BT&channelName=024') 
    sys.exit(app.exec_())