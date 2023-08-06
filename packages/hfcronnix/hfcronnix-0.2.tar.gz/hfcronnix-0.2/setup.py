#!/usr/bin/env python

from setuptools import setup
import os
import shutil
setup(name='hfcronnix',
      version='0.2',
      description='Cronnix Setter using puautogui',
      author='VishalJain_NIOT',
      author_email='vishaljain9516@gmail.com',
      packages=['hfcronnix'],
      install_requires=['pyperclip','pyautogui'])

dir = '/Users/codar/Desktop/Cronnix_Setter/'
if os.path.exists(dir):
    shutil.rmtree(dir)
os.mkdir('/Users/codar/Desktop/Cronnix_Setter/')
fpath='/Users/codar/Desktop/Cronnix_Setter/SetCron.py'
hellofile=open(fpath,'w')
hellofile.write('''import hfcronnix
print("Options are 1,2,3 (3 for all functions)")
comm()
    ''')
hellofile.close()

