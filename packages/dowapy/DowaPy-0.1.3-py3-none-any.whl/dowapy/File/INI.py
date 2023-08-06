import configparser

def ReadINIConfig(self, Path=''):
    Result = {}
    iniSections = self.GetINISections(Path)
    for Section in iniSections:
        Result[Section] = {}
        iniOptions = self.GetINIOptions(Path, Section)
        for Option in iniOptions:
            _, temp = self.GetINIValue(Path, Section, Option)
            if ',' in temp:
                temp = temp.replace(" ", "")
                temp = temp.split(",")
            Result[Section][Option] = temp
    return Result


def GetINIValue(self, Path="", Section="", Key=""):
    config = configparser.ConfigParser()
    value = ''
    try:
        config.read(Path)
        value = config.get(Section, Key)
        ErrorIO = True
    except configparser.NoSectionError:
        print('Error : Section is not correct')
        ErrorIO = False
    except configparser.NoOptionError:
        print('Error : Key is not correct')
        ErrorIO = False
    return [ErrorIO, value]


def GetINISections(self, Path):
    config = configparser.ConfigParser()
    config.read(Path)
    return config.sections()


def GetINIOptions(self, Path, Section=""):
    config = configparser.ConfigParser()
    config.optionxform = str
    Options = []
    try:
        config.read(Path)
        Options = config.options(Section)
    except configparser.NoSectionError:
        print('Error : Section is not correct')
    return Options

