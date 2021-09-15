from tkinter import *
import tkinter.messagebox as mb
import requests
import json
import re
import webbrowser
import threading
import random
import time

def getToken(ws):
    headers = {
        'cookie': ws,
        'User-Agent': 'okhttp/3.12.1;jdmall;android;version/10.1.2;build/89743;screen/1440x3007;os/11;network/wifi;',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'charset': 'UTF-8',
        'accept-encoding': 'br,gzip,deflate'
    }
    params = {
        'functionId': 'genToken',
        'clientVersion': '10.1.2',
        'client': 'android',
        'lang': 'zh_CN',
        'uuid': '09d53a5653402b1f',
        'st': '1630392618706',
        'sign': '53904736db53eebc01ca70036e7187d6',
        'sv': '120'
    }
    url = 'https://api.m.jd.com/client.action'
    data = 'body=%7B%22action%22%3A%22to%22%2C%22to%22%3A%22https%253A%252F%252Fplogin.m.jd.com%252Fcgi-bin%252Fm%252Fthirdapp_auth_page%253Ftoken%253DAAEAIEijIw6wxF2s3bNKF0bmGsI8xfw6hkQT6Ui2QVP7z1Xg%2526client_type%253Dandroid%2526appid%253D879%2526appup_type%253D1%22%7D&'
    res = requests.post(url=url, params=params, headers=headers, data=data, verify=False)
    res_json = json.loads(res.text)
    totokenKey = res_json['tokenKey']
    ck = appjmp(totokenKey)
    return ck


def appjmp(token):
    headers = {
        'User-Agent': 'jdapp;android;10.1.2;11;0393465333165363-5333430323261366;network/wifi;model/M2102K1C;addressid/938507929;aid/09d53a5653402b1f;oaid/2acbcab5bb3f0e68;osVer/30;appBuild/89743;partner/lc023;eufv/1;jdSupportDarkMode/0;Mozilla/5.0 (Linux; Android 11; M2102K1C Build/RKQ1.201112.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/77.0.3865.120 MQQBrowser/6.2 TBS/045714 Mobile Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    }
    params = {
        'tokenKey': token,
        'to': 'https://plogin.m.jd.com/cgi-bin/m/thirdapp_auth_page?token=AAEAIEijIw6wxF2s3bNKF0bmGsI8xfw6hkQT6Ui2QVP7z1Xg',
        'client_type': 'android',
        'appid': 879,
        'appup_type': 1,
    }
    url = 'https://un.m.jd.com/cgi-bin/app/appjmp'
    res = requests.get(url=url, headers=headers, params=params, verify=False, allow_redirects=False)
    res_set = res.cookies.get_dict()
    pt_key = 'pt_key=' + res_set['pt_key']
    pt_pin = 'pt_pin=' + res_set['pt_pin']
    ck = str(pt_key) + ';' + str(pt_pin) + ';'
    return ck

def replace():    
    ws = entry.get() 
    pattern = re.compile(r"pin=.*?;") 
    result1 = pattern.findall(ws)
    pattern = re.compile(r"wskey=.*?;") 
    result2 = pattern.findall(ws)
    result="".join(result1+result2)
    if result:
        ck = getToken(result)
        text = ck        
        output.configure(state='normal')
        output.delete(0, END) 
        output.insert(END, str(text))
        output.configure(state='readonly')
        if 'pt_key=fake_' in ck:
            l4.configure(text='您输入的cookie可能有错误或已经过期')
        else:
            l4.configure(text='转换成功')
    else:
        l4.configure(text='请输入含有pin=xxx;wskey=xxx;的cookie')

    
def copy(event):
    win.clipboard_clear() 
    context=output.get()
    win.clipboard_append(context) 
    l4.configure(text='结果已复制到剪贴板')

def open(event):
    url="https://www.starchina.top"
    webbrowser.open(url, new=0, autoraise=True)

def flash():
    color = ['orange red', 'red', 'hot pink', 'deep pink', 'pink', 'light pink','pale violet red', 'maroon', 'medium violet red', 'violet red',]
    c=random.choice(color)
    l4.configure(fg=c)
    l4.after(500,flash)

def clear(event):
    l4.configure(text='')

if __name__ == '__main__':
    
    win = Tk()
    win.title("京东wskey转换pt_pin")
    win.resizable(0,0) 

    l1 = Label(win, text="请输入wskey的cookie:") 
    entry = Entry(win, width=50) 
    button = Button(win, text="转换", width=20) 
    l2 = Label(win, text="转换结果:") 
    output = Entry(win, width=50) 
    
    l3 = Label(win, text="Design by Kim",fg="blue") 
    
    l4 = Label(win, text="") 

    l1.grid(row=1, column=1, padx=5, sticky=W) 
    entry.grid(row=2, column=1, columnspan=2, padx=5, pady=(0,10)) 
    button.grid(row=3, column=1, columnspan=2, pady=5) 
    l2.grid(row=4, column=1, padx=5, sticky=W) 
    output.grid(row=5, column=1, columnspan=2, padx=5, pady=(0,10)) 
    l3.grid(row=6, column=2,  sticky=E)
    l4.grid(row=6, column=1, padx=5, sticky=W)    
    l4.after(500,flash)
    l4.bind("<Leave>", clear)

    button.configure(command=replace) 
    entry.focus()
    output.configure(state='readonly')
    output.bind("<Button-1>", copy)
    l3.bind("<Button-1>", open)

    win.mainloop() 



