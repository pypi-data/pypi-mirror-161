from asyncio.subprocess import PIPE
from ctypes import WinError
import os
import sys
import subprocess
if sys.version_info < (3, 0):
    import _winreg as reg
else:
    import winreg as reg
import json


Dependencies = ['PyMySQL']


# def CheckPIP(rootpath = ''):
#     TargetPath = rootpath + 'Python/Scripts/pip.exe'
#     if not os.path.exists(TargetPath):
#         print('PIP Module Missing, try install PIP')
#         MayaPyPath = rootpath + 'bin/mayapy.exe'
#         subprocess.call('{} -m ensurepip'.format(MayaPyPath), shell=True)
#         subprocess.call('{} -m pip install --upgrade pip==20.3'.format(MayaPyPath), shell=True)
#         subprocess.call('{} -m pip install --upgrade pip'.format(MayaPyPath), shell=True)
#         # os.system('{} -m ensurepip'.format(MayaPyPath))
#         # os.system('{} -m pip install --upgrade pip==20.3'.format(MayaPyPath))
#         # os.system('{} -m pip install --upgrade pip'.format(MayaPyPath))
#     else:
#         print('PIP Exists')

# def GetMayaPath():
#     key = reg.HKEY_LOCAL_MACHINE
#     key_value = "SOFTWARE\\Autodesk\\Maya\\2018\\Setup\\InstallPath"
#     open = reg.OpenKey(key, key_value, 0, reg.KEY_READ)
#     value, type = reg.QueryValueEx(open, "MAYA_INSTALL_LOCATION")
#     print('MayaPath : [{}]'.format(value))
#     return value

# def CheckDependency():
#     CheckPIP(GetMayaPath())

#     MayaPyPath = GetMayaPath() + 'bin/mayapy.exe'

#     ModuleList = []
#     with subprocess.Popen('"{}" -m pip freeze'.format(MayaPyPath), shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True) as Process:
#         for line in Process.stdout:
#             ModuleList.append(line)

#     ModuleListOneLine = ' '.join(ModuleList)

#     for Dependency in Dependencies:
#         if len(ModuleList) <= 0 or Dependency not in ModuleListOneLine:
#             print('Python Module [{}] is missing, try install with PIP.'.format(Dependency))
#             subprocess.call('{} -m pip install {}'.format(MayaPyPath, Dependency), shell=True)
#         else:
#             print('Required Module [{}] is already installed.'.format(Dependency))







################ Legacy ##################

### Global Variables ###
Dependencies = {}

### Function ###
def LoadDependenciesJson(JsonPath):
    global Dependencies
    with open(JsonPath, "r") as json_file:
        Dependencies = json.load(json_file)


def GetInstalledPath(Key_Path='', FinalKey=''):
    KeyArray = []
    KeyArray.append(reg.HKEY_LOCAL_MACHINE)
    KeyArray.append(reg.HKEY_CURRENT_USER)

    for Key in KeyArray:
        try:
            open = reg.OpenKey(Key, Key_Path, 0, reg.KEY_READ)
            Path, type = reg.QueryValueEx(open, FinalKey)
            return Path
        except WindowsError as ErrorMsg:
            continue
    return None


def GetMayaPath():
    return GetInstalledPath("SOFTWARE\\Autodesk\\Maya\\2018\\Setup\\InstallPath", "MAYA_INSTALL_LOCATION")


def GetPythonPath(PythonVersion=''):
    return GetInstalledPath("SOFTWARE\\Python\\pythonCore\\{}\\InstallPath".format(PythonVersion), "")


def GetMayaPython():
    MayaPyPath = GetMayaPath() + 'bin\\mayapy.exe'
    if os.path.exists(MayaPyPath):
        return MayaPyPath
    else:
        return None

def GetPython(PythonVersion=''):
    PythonPath = GetPythonPath(PythonVersion) + 'python.exe'
    if os.path.exists(PythonPath):
        return PythonPath
    else:
        return None


def GetMayaPIP():
    MayaPIPPath = GetMayaPath() + 'Python\\Scripts\\pip.exe'
    if os.path.exists(MayaPIPPath):
        return MayaPIPPath
    else:
        return None

def GetPIP(PythonVersion):
    PIPPath = GetPythonPath(PythonVersion) + 'Scripts\\pip.exe'
    if os.path.exists(PIPPath):
        return PIPPath
    else:
        return None


def IntallPIP(PythonPath):
    subprocess.call('{} -m ensurepip'.format(PythonPath), shell=True)
    subprocess.call('{} -m pip install --upgrade pip==20.3'.format(PythonPath), shell=True)
    subprocess.call('{} -m pip install --upgrade pip'.format(PythonPath), shell=True)


def CheckMayaPIP():
    MayaPIPPath = GetMayaPIP()
    if MayaPIPPath == None:
        IntallPIP(GetMayaPython())





def CheckPIP(RootPath = ''):
    TargetPath = RootPath + "/Scripts/pip.exe"
    if not os.path.exists(TargetPath):
        MayaPyPath = RootPath + 'bin/mayapy.exe'
        subprocess.call('{} -m ensurepip'.format(MayaPyPath), shell=True)
        subprocess.call('{} -m pip install --upgrade pip==20.3'.format(MayaPyPath), shell=True)
        subprocess.call('{} -m pip install --upgrade pip'.format(MayaPyPath), shell=True)
    else:
        print('PIP already exists')




print(GetMayaPath())
print(GetPythonPath(3.9))

print(GetMayaPython())
print(GetPython(3.9))

print(GetMayaPIP())
print(GetPIP(3.9))