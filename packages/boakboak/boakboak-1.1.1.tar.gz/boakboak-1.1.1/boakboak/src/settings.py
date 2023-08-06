# settings.py
import os, re, sys
from contextlib import contextmanager
from pathlib import Path
import inspect


def prep_path(checkPath: str, filePrefix=None) -> str:
    checkPath = checkPath.replace("~", os.path.expanduser("~"))
    if checkPath.startswith("."):
        checkPath = os.path.join(os.getcwd(), checkPath[2:])
    if checkPath.startswith("_"):
        checkPath = os.path.join(appBaseDir, checkPath[2:])
    if filePrefix:
        checkPath = f"{filePrefix}_{checkPath}"
    checkPath = checkPath.replace("/", os.sep).replace("\\", os.sep)
    if not (os.path.isfile(checkPath) or os.path.isdir(checkPath)):
        print(f"Not a valid Path: {checkPath}")
        return False
    return checkPath


# takes the current module and runs function with funcName
settingsPath = os.path.split(__file__)[0]
srcPath = os.path.split(settingsPath)[0]
appBasePath = os.path.split(srcPath)[0]
appBaseDir = os.path.split(appBasePath)[0]


# messages
sysArgsException = f"\nProvide a program alias to be run, see list below:"

# runntime parrameters for running apps
if r".venv\Scripts" in sys.executable:
    # testing uses boakboak internal apps folder
    appsParamsDir = prep_path(os.path.join(srcPath, "apps"))
else:
    appsParamsDir = prep_path("~/boaks")


appPathAliass = [".", ""]
allApps = "*"
pFileExt = ".yml"
exceptionMsg = f"Runntime args, kwargs not found: NOTE: use '*' to run all"
fatal = f"found nothing, check your parameters app !"


# if param file does not exist in params directory it might be inside the package itself
# package param file search parameters

# if param file is held inside the target package it needs to be prefixed to be identified
pgParamPrefix = "boak"
searchTimeout = 1.0
minD, maxD = 2, 6
# start dir for params.py.find_package_params_file search is defined here
_sl = os.getcwd().split(os.sep)
# search begins one level below cwd unless path len is smaller than 3
searchBase = os.sep.join(_sl if len(_sl) <= 2 else _sl[:-1])


# signal parameters to indicate venv location
activators = [".venv", "Pipfile"]
packageIndicator = "__init__.py"
venvsPaths = {
    "nt": [".virtualenvs", "Scripts/python.exe"],
    "posix": [".local/share/virtualenvs", "bin/python"],
}

# test
testPath = os.path.join(srcPath, "test")

# Path function settings
# os seperator correction
os_sep = lambda x: os.path.abspath(x)


@contextmanager
def temp_chdir(path: Path) -> None:
    """Sets the cwd within the context

    Args:
        path (Path): The path to the cwd

    Yields:
        None
    """

    origin = Path().absolute()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(origin)
