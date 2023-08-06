# logger.py
import os, re
import logging

import boakboak.src.settings as sts


def mk_logger(logDir, fileName, loggerName, *args, **kwargs):
    # logging config to put somewhere before calling functions
    # call like: logger.debug(f"logtext: {anyvar}")
    if logDir is None:
        return type("NoLogger", (), {"info": lambda self: "logging-not-active"})
    if not os.path.isdir(logDir):
        raise Exception(f"The logDir you specified does not exist: {logDir}")
    logger = logging.getLogger(loggerName)
    logger.setLevel(logging.INFO)
    logformat = "%(asctime)s %(levelname)s %(module)s - %(funcName)s: %(message)s"
    datefmt = "%m-%d %H:%M"
    logForm = logging.Formatter(fmt=logformat, datefmt=datefmt)
    logPath = os.path.join(logDir, fileName)
    logHandler = logging.FileHandler(logPath, mode="a")
    logHandler.setFormatter(logForm)
    logger.addHandler(logHandler)
    return logger
