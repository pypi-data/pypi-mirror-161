#!/usr/bin/env python

from setuptools import setup
import os
import shutil
setup(name='hfmonthlyreport',
      version='0.6',
      description='Send monthly file count only to monthly report server',
      author='VishalJain_NIOT',
      author_email='vishaljain9516@gmail.com',
      packages=['hfmonthlyreport'],
      install_requires=['requests','pyperclip==1.8.2','qrcode'])

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
