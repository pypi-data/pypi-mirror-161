import requests
import subprocess

import os
import getpass


def InstallPip():
    script = requests.get('https://bootstrap.pypa.io/get-pip.py')
    os.chdir(f"C:\\Users\\{getpass.getuser()}\\Appdata\\local\\programs\\python\\{GetPythonVersion()}\\")
    with open('temp.py', 'w') as file:
        file.write(script.text)
    os.system('python temp.py')

    os.system("del temp.py")
def Upgrade():
    script = requests.get('https://bootstrap.pypa.io/get-pip.py')
    os.chdir(f"C:\\Users\\{getpass.getuser()}\\Appdata\\local\\programs\\python\\{GetPythonVersion()}\\")
    with open('temp.py', 'w') as file:
        file.write(script.text)
    os.system('python temp.py')

    os.system("del temp.py")
def GetPythonVersion():
    os.chdir(f'C:\\Users\\{getpass.getuser()}\\Appdata\\local\\programs\\python\\')
    if os.listdir()[0]:
        return os.listdir()[0]
    else:
        return
def UnInstall():
    os.chdir(f"C:\\Users\\{getpass.getuser()}\\Appdata\\local\\programs\\python\\{GetPythonVersion()}\\Scripts")
    if "pip.exe" in os.listdir():
        print(f'--- Found pip.exe! installing RobloxPyApi3 ----')
        subprocess.run("pip Uninstall RobloxPyApi3")
    else:
        print(f"---- Pip not found, installing pip ----\n")
        InstallPip()
        print(f'--- Pip installed successfully! UnInstalling RobloxPyApi3 ----')
        subprocess.run("pip uninstall RobloxPyApi3")
        print(f'--- Success! ----')

def Install():
    os.chdir(f"C:\\Users\\{getpass.getuser()}\\Appdata\\local\\programs\\python\\{GetPythonVersion()}\\Scripts")
    if "pip.exe" in os.listdir():
        print(f'--- Found pip.exe! installing RobloxPyApi3 ----')
        subprocess.run("pip install RobloxPyApi3")
    else:
        print(f"---- Pip not found, installing pip ----\n")
        InstallPip()
        print(f'--- Pip installed successfully! installing RobloxPyApi3 ----')
        subprocess.run("pip install RobloxPyApi3")
        print(f'--- Success! ----')
def Update():
    os.chdir(f"C:\\Users\\{getpass.getuser()}\\Appdata\\local\\programs\\python\\{GetPythonVersion()}\\Scripts")
    try:
        import RobloxPyApi3
    except:
        print("---- RobloxPyApi3 package not found ----")
        Install()
    request = requests.get('https://pypi.org/pypi/RobloxPyApi3/json')
    global vers
    if request.json()["info"]['version'] != RobloxPyApi3.__Version__:
        vers = request.json()["info"]['version']
    else:
        vers = request.json()["info"]['version']
    if "pip.exe" in os.listdir():
        print(f'--- Found pip.exe! Updating RobloxPyApi3, (2/1) Uninstall ----')
        subprocess.run("pip uninstall RobloxPyApi3")
        print(f'--- Updating RobloxPyApi3, (2/2) install ----')
        subprocess.run("pip install RobloxPyApi3")
        print("---- Successfully updated RobloxPyApi3 ----")
    else:
        print(f"---- Pip not found, installing pip ----\n")
        InstallPip()
        print(f'--- installed pip! Updating RobloxPyApi3, (2/1) Uninstall ----')
        subprocess.run(f"pip uninstall RobloxPyApi3=={RobloxPyApi3.__Version__}")
        print(f'--- Updating RobloxPyApi3, (2/2) install ----')
        subprocess.run(f"pip install RobloxPyApi3=={request.json()['info']['version']}")
        print("---- Successfully updated RobloxPyApi3 ----")

def InstallVersion(version):
    os.chdir(f"C:\\Users\\{getpass.getuser()}\\Appdata\\local\\programs\\python\\{GetPythonVersion()}\\Scripts")
    if "pip.exe" in os.listdir():
        print(f'--- Found pip.exe! installing RobloxPyApi3 ----')
        subprocess.run(f"pip install RobloxPyApi3=={version}")
    else:
        print(f"---- Pip not found, installing pip ----\n")
        InstallPip()
        print(f'--- Pip installed successfully! installing RobloxPyApi3 ----')
        subprocess.run(f"pip install RobloxPyApi3=={version}")
        print(f'--- Successfully Installed RobloxPyApi3! ----')
#def SetupPythonForCmd():
    #print('this feature is unavailable. sorry')
    #return

     #try:
        #file = open(f'C:\\Users\\{getpass.getuser()}\\AppData\\Local\\Programs\\Python\\data.txt')
        #if file:
            #print("Data found, delete data.txt to continue, or risk at ENVIRON spam .\n you need to delete every python variable after that.")
            #print(f'file located in C:\\Users\\{getpass.getuser()}\\AppData\\Local\\Programs\\Python\\data.txt')

     #except:
        #os.environ['Path'] = os.environ[
                            #'Path'] + f"C:\\Users\\{getpass.getuser()}\\AppData\\Local\\Programs\\Python\\{GetPythonVersion()};C:\\Users\\{getpass.getuser()}\\AppData\\Local\\Programs\\Python\\{GetPythonVersion()}\\Scripts;"
        #os.environ['Python'] = f"C:\\Users\\{getpass.getuser()}\\AppData\\Local\\Programs\\Python\\{GetPythonVersion()}\\python.exe"
        #with open('data.txt','w') as file:
            #file.write('SetupPythonForCmdSaved98822932')

def DeleteFileData():
    os.chdir(f"C:\\Users\\{getpass.getuser()}\\AppData\\Local\\Programs\\Python\\")
    os.system('del data.txt')
def CheckForUpdates():
    try:
        import RobloxPyApi3
    except:
        print("---- RobloxPyApi3 package not found ----")
        Install()
    request = requests.get('https://pypi.org/pypi/RobloxPyApi3/json')
    if request.json()["info"]['version'] != RobloxPyApi3.__Version__:
        print("Update Found")
    else:
        print('Updated')