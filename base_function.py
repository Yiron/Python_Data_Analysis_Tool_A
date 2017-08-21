# -*- coding: utf-8 -*-
import time
import os
import codecs
import logging
import logging.handlers
import hashlib
import globalVar
import platform, locale, shutil
import cmdColor


HELPER_MODE = 0 
ANALYSIS_MODE = 1
COMPARE_MODE = 2
EXTRACT_MODE = 3
AUTO_ANALYSIS_MODE = 4
MULTIPLE_AUTO_ANALYSIS_MODE = 5
SEARCH_MODE = 6
SAVE_LOG_MODE = 7
IGNORE_ERROR_MODE = 8
CLEAN_SPLIT_DATA_MODE = 9

def hideFile(filePath):
    if 'Windows' in platform.system():
        cmd = 'attrib +h "' + filePath + '"'
        cmd = cmd.encode(locale.getdefaultlocale()[1])
        os.popen(cmd).close()


class summyInfoBase:
    def __init__(self, path, name, s):
        LOG_FILE = path + '/' + name + '.csv'
        handler = logging.handlers.RotatingFileHandler(
            LOG_FILE,
            maxBytes=1 * 256 * 1024,
            backupCount=5)  # 实例化handler
        fmt = '%(message)s'
        formatter = logging.Formatter(fmt)  # 实例化formatter
        handler.setFormatter(formatter)  # 为handler添加formatter
        self.log = logging.getLogger(name)  # 获取名为tst的logger
        self.log.addHandler(handler)  # 为logger添加handler
        self.log.setLevel(logging.INFO)
        self.log.info(s)

    def addSummyLog(self, s):
        self.log.info(s)


def getAlnum(s):
    return str(filter(lambda x: str(x).isalnum(), s))


def getHeaderMd5():
    return hashlib.md5("".join(globalVar.header)).hexdigest()


def getFileMd5(file):
    md5file = open(file, 'rb')
    md5 = hashlib.md5(md5file.read()).hexdigest()
    md5file.close()
    return md5


def getPathMd5(path):
    dcFile = recursionGetFile(path, globalVar.KEY_WORD)
    dcFile = filter(lambda x: '.' + dcFile[0][-3:] == x[-4:], dcFile)
    md5List = []
    for i in dcFile:
        md5List.append(getFileMd5(i))
    md5List.sort()
    md5Str = str(md5List)
    md5 = hashlib.md5(md5Str).hexdigest()
    return md5


def changeStrDecode(str, code):
    ret = ""
    try:
        ret = str.decode(code)
    except:
        ret = str
    return ret


def changeStrEncode(str, code):
    ret = ""
    try:
        ret = str.encode(code)
    except:
        ret = str
    return ret


def rawInput(s, defaultValue=None):
    s = changeStrEncode(s, "GB2312")
    cmdColor.printYellow(s)
    print "=>",
    return raw_input("").strip()


def intInput(s, defaultValue=None):
    try:
        return int(rawInput(s))
    except:
        return defaultValue

def listInput(s, defaultValue=None):
    try:
        return eval("[" + rawInput(s) + "]")
    except:
        return defaultValue

logger = ""
log_handler = ""


def closeAndHideLog():
    global logger, log_handler
    if logger != "" and log_handler != "":
        logger.removeHandler(log_handler)
    logger = ""
    log_handler = ""


def init_log(path):
    global logger, log_handler
    if not globalVar.NEED_LOG:
        return

    closeAndHideLog()

    LOG_FILE = path + '/' + 'logger.log'
    log_handler = logging.handlers.RotatingFileHandler(
        LOG_FILE,
        maxBytes=1024 * 1024,
        backupCount=1)  # 实例化handler
    fmt = '%(asctime)s & %(filename)s & %(lineno)s & %(name)s & %(message)s'

    formatter = logging.Formatter(fmt)  # 实例化formatter
    log_handler.setFormatter(formatter)  # 为log_handler添加formatter

    logger = logging.getLogger('logger')  # 获取名为tst的logger
    logger.addHandler(log_handler)  # 为logger添加log_handler
    logger.setLevel(logging.DEBUG)


def mPrint(s):
    s = changeStrEncode(s, "GB2312")
    cmdColor.printYellow(s)
    print ""


def log(s):
    global logger
    logStr = changeStrEncode(s, "GB2312")
    if logger != "" and globalVar.NEED_LOG:
        logger.info(logStr)
    if globalVar.NEED_LOG:
        cmdColor.printDarkGreen("LOG: ")
        cmdColor.printDarkGreen(logStr)
        print ""


def warning(s):
    global logger

    warnStr = changeStrEncode(s, "GB2312")
    if logger != "" and globalVar.NEED_LOG:
        logger.info(warnStr)
    cmdColor.printRed("WARN: ")
    cmdColor.printRed(warnStr)
    print ""


def raiseError(code, s):
    global logger
    if code in  globalVar.IGNORE_ERROR:
        return
    s =  str(code) + "-" + changeStrDecode(s,"GB2312")
    raiseStr = changeStrEncode(s, "GB2312")
    if logger != "" and globalVar.NEED_LOG:
        logger.info(raiseStr)
    cmdColor.printYellowRed("ERROR(" + str(code) + "): ")
    cmdColor.printYellowRed(raiseStr)
    print ""
    raise Exception(raiseStr)


def openFileAsLineList(fileName):
    tableLines = ""
    aTableFile = open(fileName, "r")
    try:
        tableLines = aTableFile.readlines()
    finally:
        aTableFile.close()
    return tableLines


def unifyPath(path):
    path = changeStrEncode(path, "GB2312").replace('\\', '/')
    if path.endswith('/'):
        path = path[:-1]
    if path.endswith('"'):
        path = path[:-1]
    if path.startswith('"'):
        path = path[1:]

    return path


def getCompressFiles(path):
    retFileList = []
    generator = os.walk(path)
    for (now_dir, _t, file_list) in generator:
        rawFileList = map(lambda x: os.path.join(now_dir, x), file_list)
        rawFileList = map(lambda x: unifyPath(x), rawFileList)
        rawFileList = filter(
            lambda x: str.lower(os.path.splitext(x)[1]) in [".zip", ".rar", ".tar", ".7z", ".bz2", ".gz"],
            rawFileList)
        retFileList.extend(rawFileList)
    return retFileList

# keyword also include pathStr, bug


def recursionGetFile(path, getKeyWord="", skipKeyWord=""):
    retFileList = []
    generator = os.walk(path)
    for (now_dir, _t, file_list) in generator:
        rawFileList = map(lambda x: os.path.join(now_dir, x), file_list)
        rawFileList = map(lambda x: unifyPath(x), rawFileList)
        rawFileList = filter(lambda x: getKeyWord in x.split('/')[-1],
                             rawFileList)
        if skipKeyWord != "":
            rawFileList = filter(lambda x: skipKeyWord not in x, rawFileList)
        retFileList.extend(rawFileList)
    return retFileList


def listDirGetFile(path, getKeyWord="", skipKeyWord=""):
    rawFileList = map(lambda x: os.path.join(path, x), os.listdir(path))
    rawFileList = map(lambda x: unifyPath(x), rawFileList)
    rawFileList = filter(lambda x: getKeyWord in x.split('/')[-1], rawFileList)
    if skipKeyWord != "":
        rawFileList = filter(lambda x: skipKeyWord not in x, rawFileList)
    return rawFileList


def getFile(path, getKeyWord="", skipKeyWord="", needRecursion=True):
    fileList = []
    if needRecursion:
        fileList = recursionGetFile(path, getKeyWord, skipKeyWord)
    else:
        fileList = listDirGetFile(path, getKeyWord, skipKeyWord)
    return fileList


def getDcPathAndType(path, getKeyWord="", skipKeyWord="", needRecursion=True):
    fileList = getFile(path, getKeyWord, skipKeyWord, needRecursion)
    if len(fileList) == 0:
        return [], ""

    fileList = filter(lambda x: x[-4:] == '.' + fileList[0][-3:], fileList)

    if len(fileList) == 0:
        return [], ""
    fileList = map(lambda x: unifyPath(x), fileList)
    pathList = set(map(lambda x: "/".join(x.split('/')[:-1]), fileList))
    return pathList, str(fileList[0][-3:])
