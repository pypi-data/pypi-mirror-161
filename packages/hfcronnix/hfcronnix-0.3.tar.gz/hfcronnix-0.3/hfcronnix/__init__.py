import pyautogui
import os
import time
import pyperclip as pc
import shutil
import random


dly=2
site=["CUDA","KALP","MACH","YANM","WASI","JGRI","GOPA","PURI","HTBY","PTBL"]
host1=["110.50.52.49","202.134.195.99","202.134.195.74","202.134.195.65","202.134.195.113","202.134.195.254","202.134.195.59","110.50.52.50","110.50.34.237","202.134.195.253"]

def comm():
    locate1=int(input("Enter location Number:\n'0 Cuda \n'1 Kalp\n'2 Mach\n'3 Yanm\n'4 Wasi\n'5 Jgri\n'6 Gopa\n'7 Puri\n'8 Htby\n'9 Ptbl\n:::>> "))
    time.sleep(dly)
    os.system("open /Applications/Utilities/Terminal.app")
    time.sleep(dly)
    pyautogui.typewrite("ssh codar@"+host1[locate1])
    time.sleep(dly)
    pyautogui.press("enter")
    os.system("open /Applications/Python\ 3.6/IDLE.app")
    print("ENTER PASSWORD IF REQUIRED")
    check=int(input("Continue to choose option if Loinnn Successfull and required option:::>>> "))
    if check==1:
        cron()
    elif check==2:
        pip()
        cron()
    elif check==3:
        delOld()
        pip()
        cron()   
    else:
        print("You may run cron() ")
    
    check1=int(input("Enter 5 if everythin is ok and quit terminal:::>>> "))
    if check1==5:
        os.system("""osascript -e 'quit app "Terminal"'""")
        os.system("open /Applications/Utilities/Terminal.app")
        pyautogui.press("tab")
        pyautogui.press("enter")
        
    
    #"open /Applications/Python\ 3.6/IDLE.app"
    
def delOld():
    os.system("open /Applications/Utilities/Terminal.app")
    time.sleep(dly)
    pyautogui.typewrite('cd')
    time.sleep(dly)
    pyautogui.press("enter")
    time.sleep(dly)
    pyautogui.typewrite('cd Desktop/')
    time.sleep(dly)
    pyautogui.press("enter")
    time.sleep(dly)
    pyautogui.typewrite('sudo rm -rf monthlyreport/')
    time.sleep(dly)
    pyautogui.press("enter")
    time.sleep(dly)
    pyautogui.typewrite('tnes')
    pyautogui.press("enter")
    time.sleep(dly)
    os.system("open /Applications/Python\ 3.6/IDLE.app")
    check=int(input("If Everythin is ok press 5:::>>> "))
    if check==5:
        return True
    
    
     
def pip():
     os.system("open /Applications/Utilities/Terminal.app")
     time.sleep(dly)
     pyautogui.typewrite('pip install hfmonthlyreport')
     time.sleep(dly)
     pyautogui.press("enter")
     time.sleep(dly)
     os.system("open /Applications/Python\ 3.6/IDLE.app")
     check=int(input("If Everythin is ok press 5:::>>> "))
     if check==5:
         return True
     

def cron():
    #text='0       0       1       1       1       echo "chl"'
    #pc.copy(text)
    #pyautogui.typewrite('export EDITOR=/usr/bin/nano')
    print("start")
    os.system("open /Applications/Utilities/Terminal.app")
    time.sleep(dly)
    #pyautogui.hotkey("command","n")
    #time.sleep(dly)
    time.sleep(dly)
    time.sleep(dly)
    pyautogui.typewrite('export EDITOR=/usr/bin/nano') # set default editor to nano
    time.sleep(dly)
    pyautogui.press("enter")
    time.sleep(dly)
    ########## Writing to Crontab editor ####################
    pyautogui.typewrite("crontab -e")  # open crontab
    time.sleep(dly)
    pyautogui.press("enter")
    time.sleep(dly)
    pyautogui.press("enter") # select new line
    time.sleep(dly)
    pyautogui.press("up") # take cursor to up arrow key
    time.sleep(dly)
    ########## Pasting to Crontab editor ####################
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
    ########## End of Crontab editor ####################
    print("End")
    #os.system("""osascript -e 'quit app "Cronnix"'""")

    ############# Restart Cronnixx #####################
    '''
    ttext="""osascript -e 'quit app "Cronnix"'"""
    pc.copy(ttext)
    time.sleep(dly)
    pyautogui.hotkey("command","v")
    pyautogui.press("enter")
    time.sleep(dly)
    ttext='open /Applications/CronniX.app/Contents/MacOS/CronniX'
    pc.copy(ttext)
    time.sleep(dly)
    pyautogui.hotkey("command","v")
    pyautogui.press("enter")
    time.sleep(dly)
    '''
    ############# Restart Cronnixx #####################
    ############## Restart Cronntab 2ns Way #################
    #pyautogui.typewrite("""osascript -e 'quit app "Cronnix"'""")
    #pyautogui.press("enter")
    #time.sleep(dly)
    ttext="""osascript -e 'quit app "Cronnix"'"""
    pc.copy(ttext)
    time.sleep(dly)
    pyautogui.hotkey("command","v")
    pyautogui.press("enter")
    time.sleep(dly)
    #pyautogui.typewrite('open /Applications/CronniX.app/Contents/MacOS/CronniX')
    pyautogui.typewrite('open -a "CronniX"')
    pyautogui.press("enter")
    #os.system('''open /Applications/CronniX.app/Contents/MacOS/CronniX''')
    print("End")
    time.sleep(dly)
    #os.system('killall Terminal')
    return("Done")



