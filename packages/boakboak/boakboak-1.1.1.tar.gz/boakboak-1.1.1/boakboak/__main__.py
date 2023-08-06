# __main__.py

import os, re, sys
from datetime import datetime as dt
import boakboak.src.settings as sts
from boakboak.src.executable import Executable
from boakboak.src.params import Params
from boakboak.src.clean_params import cleaner
import boakboak.src.boakboak as boakboak
import boakboak.src.logger as logger

global timeStamp
timeStamp = re.sub(r"([:. ])", r"-", str(dt.now()))


def run(*args, params, **kwargs):
    # running the called python module
    for app, pars in params.items():
        log = logger.mk_logger(pars.get("logDir"), f"{timeStamp}_{app}.log", __name__)
        pars["executable"], isPackage = Executable(*args, **pars).get_executable(app, **pars)
        out = boakboak.crow(*args[1:], isPackage=isPackage, **pars)
        out = "\n".join([l for l in out.replace("\r", "").replace("\n\n", "\n").split("\n")])
        log.info(f"\n{out}")
        for l in out.split("\n"):
            print(l)


def main(*args, **kwargs):
    # when installed, args have to come via sys.argv not from main(*sys.argv)
    if not args:
        args = sys.argv[1:]
    if not args:
        print(f"{sts.sysArgsException}: \n\n\tPath:\t\t\t{sts.os_sep(sts.appsParamsDir)}")
        print(f"\tavailable apps: \t{os.listdir(sts.appsParamsDir)}\n")
        exit()
    p = Params()
    apps = p.get_all_apps(*args)
    params = p.get_params(apps, *args)
    params = cleaner(params)
    if params:
        run(*args, params=params)


if __name__ == "__main__":
    main(*sys.argv[1:])
