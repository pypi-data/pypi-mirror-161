import configparser

def ReadINIConfig(Path=''):
    Result = {}
    iniSections = GetINISections(Path)
    for Section in iniSections:
        Result[Section] = {}
        iniOptions = GetINIOptions(Path, Section)
        for Option in iniOptions:
            _, temp = GetINIValue(Path, Section, Option)
            if ',' in temp:
                temp = temp.replace(" ", "")
                temp = temp.split(",")
            Result[Section][Option] = temp
    return Result


def GetINIValue(Path="", Section="", Key=""):
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


def GetINISections(Path):
    config = configparser.ConfigParser()
    config.read(Path)
    return config.sections()


def GetINIOptions(Path, Section=""):
    config = configparser.ConfigParser()
    config.optionxform = str
    Options = []
    try:
        config.read(Path)
        Options = config.options(Section)
    except configparser.NoSectionError:
        print('Error : Section is not correct')
    return Options

