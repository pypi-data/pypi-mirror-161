#Functions files:
import os
#import numpy as np
import sys
import calendar
from calendar import monthrange
from datetime import datetime, timedelta
import json
import requests


import time
import pyperclip as pc
import shutil
import random


URL = "http://hfradarniot.pythonanywhere.com/upldTsuData"
URL1 = "http://niothfradar.pythonanywhere.com/upldTsuData"
TIMEOUT =  10
class SendData():
    def __init__(self):
        self.url = URL
        self.timeout = TIMEOUT
    def send(self, datam):
        flag = 0
        try:
            req2 = json.dumps({"cred1": datam})
            headers = {'Content-Type': 'application/json'}
            r = requests.post(self.url, headers=headers, data=req2,timeout=self.timeout)
            print (r.text)
            r.raise_for_status()
            if r.status_code==201 or r.status_code==200:
                flag = 1
        except Exception as e:
            print ("Check Internet or send through Mobile App ")        
        return flag

class SendData1():
    def __init__(self):
        self.url = URL1
        self.timeout = TIMEOUT
    def send(self, datam):
        flag = 0
        try:
            req2 = json.dumps({"cred1": datam})
            headers = {'Content-Type': 'application/json'}
            r = requests.post(self.url, headers=headers, data=req2,timeout=self.timeout)
            print (r.text)
            r.raise_for_status()
            if r.status_code==201 or r.status_code==200:
                flag = 1
        except Exception as e:
            print ("Check Internet or send through Mobile App ")        
        return flag

s = SendData()
s1=SendData1()


def countlogic1(a):# input hex string and gget numerical values
   n=int(a,16)
   count = 0
   while (n):
      count += n & 1
      n >>= 1
   return count

def realTotals(a,b):
    e=hex(int(a, 16) & int(b, 16))
    return str(countlogic1(e))
    
def dicttoTotals(a,b):
    Totsum=0
    if len(a)!=len(b):
        return 0
    else:
        for i in range(len(a)):
            #print(i)
            bits=int(realTotals(a[i]['rchex'],b[i]['rchex']))
            Totsum=Totsum+bits
        return Totsum


def getHexValue(binaryFile):
    return hex(int(binaryFile,2))



#get sitecode
def siteCode():
    pa='/Codar/SeaSonde/Configs/RadialConfigs/Header.txt'
    if os.path.isfile(pa)==True:
        read=open(pa)
        cont=read.readlines()
        read.close()
    else:
        print("Check config file or contact NIOT ")
        sys.exit()
    dd=cont[0].split(' ')[1]
    return dd

def validflg(rl):
    if all(isinstance(x, int) for x in rl):
        if (all(i <= 24 for i in rl)):
            sum(rl)<=744
            return True
    else:
        return False

def RfolderName(sitecode,ftype,year,month,pad):
        dt=str(year)+'/'+str(month)+'/'+'25'
        dt1=datetime.strptime(dt, "%Y/%m/%d")
        dt2=dt1+ timedelta(days=10)
        dt1name=calendar.month_name[int(dt1.month)][0:3]
        dt2name=calendar.month_name[int(dt2.month)][0:3]
        dt0=dt1-timedelta(days=35)
        dt0name=calendar.month_name[int(dt0.month)][0:3]
        fname=[]
        pa=[]
        if pad==1:
            pad='/Codar/SeaSonde/Archives/Radials/'

        if os.path.exists(pad):
                d=os.listdir(pad)
        else:
                print("Radial folder location is wrong ")
                sys.exit()
        for file in d:
                if (ftype in file.split('_') and sitecode in file.split('_')):
                        if str(dt1.year) in file.split('_') and str(dt1name) in file.split('_'):
                                #print(file)
                                fname.append(file)
                        if str(dt2.year) in file.split('_') and str(dt2name) in file.split('_'):
                                fname.append(file)
                                #print(file)
                        if str(dt0.year) in file.split('_') and str(dt0name)+str(dt1name) in file.split('_'):
                                fname.append(file)
                        if str(dt1.year) in file.split('_') and str(dt1name)+str(dt2name) in file.split('_'):
                                fname.append(file)
        if not fname:
                print("There are no Radials folder present ")
                return 0
                #sys.exit()
        fname = list(set(fname))
        #print(fname)
        for f1 in fname:
                if os.path.exists(os.path.join(pad,f1)):
                        pa.append(os.path.join(pad,f1))
        return(pa)

def validflg(rl,num_days):
    if all(isinstance(x, int) for x in rl):
        #print(rl)
        if (all(i <= 24 for i in rl)):
            if sum(rl)<=744 and len(rl)==num_days:
                return True
            else:
                print("total count is greater than 744 or number of radials greater than no.of days")
        else:
            print("Some values greater than 24 ")
    else:
        print("validity failed ")
        return False

def filecount(autosite,ft,year,month,pad):
        num_days=int(monthrange(year,month)[1])
        autosite=str(autosite)
        if autosite=='1':
                sitecode=siteCode()
        else:
                sitecode=autosite
        if ft==1:
                ftype='RDLi'
        else:
                ftype='RDLm'
                
        pa=RfolderName(sitecode,ftype,year,month,pad)
        #print(pa)
        years=str(year)
        filename=[]
        monthlyfilespath = []
        daysinfile=[]
        hoursinFile=[]
        for dir in pa:
                filename.extend(os.listdir(dir))
        
        if filename:
                for file in filename:
                        if '.ruv' and years and ftype in file:
                                if int(file.split('_')[3])==month:
                                        monthlyfilespath.append(file)
        else:
                print("there are no files in radial folders ")
                return 0
        
        sortedMonthlyfile = sorted(monthlyfilespath)
        radialList=[]
        for filep1 in sortedMonthlyfile:
                daysinfile.append(int(filep1.split("_")[4]))
        sorteddaysinfile=sorted(daysinfile)
        for i in range(1,num_days+1):
                radialList.append(int(sorteddaysinfile.count(i)))
        for filep1 in sortedMonthlyfile: 
                daysinfile.append(int(filep1.split("_")[4]))
                hoursinFile.append(filep1[18:25])

        khex=''
        flghex=0
        global ghex
        ghex=[]
        
        for i in range(1,num_days+2):
            if flghex==1:
                ghex.append(getHexValue(khex))
                khex=''
            for j in range(24):
                flghex=1
                if format(i,'02')+'_'+format(j,'02')+'00' in hoursinFile:
                    khex=khex+'1'
                else:
                    khex=khex+'0'
        #print(ghex)  
        global radiallist1
        radiallist1=[]
        for i in ghex:
            radiallist1.append(countlogic1(i))
            
        if validflg(radiallist1,num_days)==True:
                return radiallist1,sitecode,num_days,month,year
        else:
                print("Data is wrongly calculated please count manually ")
                sys.exit()
                      
def dataDisplay(radialList,sitecode,num_days,month,year,qr):
        print("Site Code:"+str(sitecode))
        qrstring=''
        qrstringHex=''
        print("Total no. of days in month: "+str(num_days))
        TotalRadialcount=num_days*24
        print("Total no. of Radial count should be: "+str(TotalRadialcount))
        for i in range(1,num_days+1):
                print("Date: "+str(i)+"/"+str(month)+"/"+str(year)+" :  "+ str(radialList[i-1]))
                qrstringHex+=str(ghex[i-1])+':'
                qrstring+=str(radialList[i-1])+':'
        TotalActualRadialCount=sum(radialList)
        print("Total no. of Actual Radial Count: "+str(TotalActualRadialCount))
        PercentageRadial= (float(TotalActualRadialCount)/TotalRadialcount)*100
        print("Percentage of radial count for month: "+str(round(PercentageRadial)))
        print(" ###### Please Check if above data is Correct with proper Date and Radial count ")
        qrstring=sitecode+':'+str(month)+':'+str(year)+':'+qrstring+str(TotalActualRadialCount)+':'+qrstringHex
        if qr==1:
                print(qrstring)
                os.system('qr '+qrstring)

def serverlist(radialList,sitecode,num_days,month,year):
        a={}
        i=0
        temp_list =[]
        for i in range(1,num_days+1):
                a={'id':sitecode, 'dt':str(year)+'-'+"%02d" % (month,)+'-'+"%02d" % (i,),'rc':str(radialList[i-1]),'rchex':str(ghex[i-1])}
                temp_list.append(a)
                a={}
        return temp_list

    
def control1(year,month,display,qr,sts,pad,autosite,ft):
    radialList,sitecode,num_days,month,year=filecount(autosite,ft,year,month,pad)
    #hg=filecount(autosite,ft,year,month,pad)
    #print(hg)
    if display==1:
        dataDisplay(radialList,sitecode,num_days,month,year,qr)
    if sts==1 :
        temp_list=serverlist(radialList,sitecode,num_days,month,year)
        if temp_list and ft!=1:
            flg = s.send(temp_list)
            #s1.send(temp_list)
            if flg!=1:
                s.send(temp_list)
            else:
                print("You can't send Ideal files on server")
    
    if sts==2:
        print("sts2 entered")
        temp_list=serverlist(radialList,sitecode,num_days,month,year)
        #print(temp_list)
        sending_server=int(input("DO YOU WANT TO SEND TO SERVER PRESS NUMBER 5 AND PRESS 'ENTER' TO SEND: "))
        if sending_server==5:
            print("5 selected ")
            if temp_list and ft!=1:
                print("Wait for 10 seconds ")
                flg = s.send(temp_list)
                #s1.send(temp_list)
                if flg!=1:
                    flg = s.send(temp_list)
                    if flg!=1:
                        print("Not able to send data for month: "+str(month)+" "+str(year))
                    
        
    if sts==3:
        temp_list=serverlist(radialList,sitecode,num_days,month,year)
        if temp_list and ft!=1:
            flg = s.send(temp_list)
            #s1.send(temp_list)
            if flg!=1:
                flg = s.send(temp_list)
                if flg!=1:
                    dataDisplay(radialList,sitecode,num_days,month,year,qr)
        else:
            print("You can't send Ideal files on server")

 
def default():
    d3= datetime.today() - timedelta(days=10)
    year3=int(d3.year)
    month3=int(d3.month)
    control1(year3,month3,1,1,3,1,1,0)
    
    
def shortcut():
    dir = '/Users/codar/Desktop/MonthlyReport/'
    if os.path.exists(dir):
        shutil.rmtree(dir)
    os.mkdir('/Users/codar/Desktop/MonthlyReport/')
    fpath='/Users/codar/Desktop/MonthlyReport/Click_me_Twice.command'
    hellofile=open(fpath,'w')
    hellofile.write('''#!/usr/bin/env python
import hfmonthlyreport
hfmonthlyreport.default()
    ''')
    hellofile.close()
    os.chmod(fpath, 0o744)
    print("Done Creating file")
    return("Done")

def cronprint():
    text=str(random.randint(10,40))+'      03      1       *       *       /usr/bin/open /Users/codar/Desktop/MonthlyReport/Click_me_Twice.command'
    return(text)
    

def cron():
    import pyautogui
    dly=2
    #text='0       0       1       1       1       echo "chl"'
    #pc.copy(text)
    #pyautogui.typewrite('export EDITOR=/usr/bin/nano')
    print("start")
    os.system("open /Applications/Utilities/Terminal.app")
    time.sleep(dly)
    pyautogui.hotkey("command","n")
    time.sleep(dly)
    time.sleep(dly)
    time.sleep(dly)
    pyautogui.typewrite('export EDITOR=/usr/bin/nano') # set default editor to nano
    time.sleep(dly)
    pyautogui.press("enter")
    time.sleep(dly)
    pyautogui.typewrite("crontab -e")  # open crontab
    time.sleep(dly)
    pyautogui.press("enter")
    time.sleep(dly)
    pyautogui.press("enter") # select new line
    time.sleep(dly)
    pyautogui.press("up") # take cursor to up arrow key
    time.sleep(dly)
    
    text=str(random.randint(10,40))+'      03      1       *       *       /usr/bin/open /Users/codar/Desktop/MonthlyReport/Click_me_Twice.command'
    #text='0       0       1       1       1       echo "chl"'
    pc.copy(text)
    time.sleep(dly)
    pyautogui.hotkey("command","v")
    #pc.paste()
    #pyautogui.hotkey("ctrl","c")
    #pyautogui.typewrite('0       0       1       1       1       echo "chl"',interval=0.25)
    time.sleep(dly)
    pyautogui.hotkey("ctrl","x")
    time.sleep(dly)
    pyautogui.typewrite('y')
    pyautogui.press("enter")
    print("End")
    os.system("""osascript -e 'quit app "Cronnix"'""")
    time.sleep(dly)
    os.system('''open /Applications/CronniX.app/Contents/MacOS/CronniX''')
    print("End")
    time.sleep(dly)
    os.system('killall Terminal')
    return("Done")

def impPack():
    os.system("pip2 install PyAutoGUI==0.9.53")
    return("pip2 install PyAutoGUI==0.9.53")
    
def install(a,b,c):
    print("Pass parameter 1,1 for installing shortcut and crontab")
    if a==1:
        print(shortcut())
    if b==1:
        print(cron())
    if c==1:
        print(cronprint())
    return("Done") 
        





