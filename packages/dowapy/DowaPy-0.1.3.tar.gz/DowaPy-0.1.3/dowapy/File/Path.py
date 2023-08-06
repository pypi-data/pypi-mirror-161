import os
import sys
if sys.version_info < (3, 0):
    import _winreg as reg
else:
    import winreg as reg
import ctypes


def MakeDirectory(Path):
    try:
        if not os.path.exists(Path):
            os.makedirs(Path)
    except OSError:
        print(f"MakeDirectory Function got error : {Path}")


def GetEnginePath(EngineVersion):
    key = reg.HKEY_LOCAL_MACHINE
    RegistryPath = "SOFTWARE\\EpicGames\\Unreal Engine"
    key_value = RegistryPath + "\\" + EngineVersion
    try:
        OpenKey = reg.OpenKey(key, key_value, 0, reg.KEY_READ)
        value, ErrorType = reg.QueryValueEx(OpenKey, "InstalledDirectory")
    except FileNotFoundError:
        value, ErrorType = {"Version Not Founded", -1}
    return value, ErrorType


def GetMayaPath(MayaVersion):
    key = reg.HKEY_LOCAL_MACHINE
    RegistryPath = f'SOFTWARE\\Autodesk\\Maya\\{MayaVersion}\\Setup\\InstallPath'
    try:
        OpenKey = reg.OpenKey(key, RegistryPath, 0, reg.KEY_READ)
        value, ErrorType = reg.QueryValueEx(OpenKey, "MAYA_INSTALL_LOCATION")
    except FileNotFoundError:
        value, ErrorType = {"Version Not Founded", -1}
    return value, ErrorType


def GetDocumentsPath():
    import ctypes.wintypes
    CSIDL_PERSONAL = 5
    SHGFP_TYPE_CURRENT = 0

    buffer = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
    ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buffer)

    return buffer.value


class DirectoryTreeNode:
    def __init__(self, Name="", Parent=None, Path="", IsDir=True):
        self.Name = Name
        self.MyParent = Parent
        self.MyPath = Path
        self.Children = []
        self.IsDir = IsDir

    def GetChildren(self):
        return self.Children

    def SetTree(self):
        if not os.path.exists(self.MyPath):
            return -1
        for item in os.listdir(self.MyPath):
            ChildPath = os.path.join(self.MyPath, item).replace('\\', '/')
            if os.path.isdir(ChildPath):
                NewNode = DirectoryTreeNode(Name=item, Parent=self, Path=ChildPath)
                self.Children.append(NewNode)
                NewNode.SetTree()
            elif os.path.isfile(ChildPath):
                NewNode = DirectoryTreeNode(Name=item, Parent=self, Path=ChildPath, IsDir=False)
                self.Children.append(NewNode)
        return 0

    def FindExtension(self, Dictionary, Extension):
        for item in self.Children:
            if item.IsDir:
                item.FindExtension(Dictionary, Extension)
            else:
                result = False
                for Current in Extension:
                    if f'.{Current}' in item.Name:
                        result = True
                        break
                if result:
                    if self in Dictionary.keys():
                        Dictionary[self].append(item)
                    else:
                        Dictionary[self] = [item]

    def FindDirectory(self, Keywords, DepthLimit, CurrentDepth=0):
        if self.IsDir:
            for Keyword in Keywords:
                if self.Name.upper() == Keyword.upper():
                    return self
                elif CurrentDepth + 1 <= DepthLimit:
                    for Child in self.Children:
                        Result = Child.FindDirectory([Keyword], DepthLimit, CurrentDepth + 1)
                        if Result is not None:
                            return Result


class DirectoryTree:
    def __init__(self, RootPath):
        self.Head = DirectoryTreeNode(Name=os.path.basename(RootPath), Path=RootPath)
        self.Head.SetTree()

    def FindExtension(self, Result, Extension):
        self.Head.FindExtension(Result, Extension)
        
    def FindDirectory(self, Keywords, DepthLimit):
        return self.Head.FindDirectory(Keywords, DepthLimit)
