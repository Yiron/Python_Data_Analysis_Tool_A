#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import cProfile
# import pdfMaker
import FileDialog
import json
import os
import shutil
import tarfile
import zipfile
from shutil import copyfile
from time import ctime, localtime, sleep, strftime
# import affirm
import rarfile
import fileState
import getChart
import dataCalculator
import getMap
import getMessage
import globalVar
import htmlMaker
import pathMsgMaker
from base_function import *
import thread

from __future__ import print_function

def formatUserUid(uid):
    if uid[0:2].lower() == "0x":
        uid = uid[2:]
    if uid[-6:].upper() == "FFFFFF":
        uid = uid[:-6]
    uid = uid.lower()
    uid = "0x" + uid + "FFFFFF"
    return uid


def dcDataFiles(members):
    retList = []
    for fileInfo in members:
        fileInfo = changeStrEncode(fileInfo, "GB2312")
        if str.lower(os.path.splitext(fileInfo)[1]) in [".csv", ".xls"]:
            retList.append(fileInfo)
    # mPrint(str(retList))
    return retList


def tarDcDataFiles(members):
    for tarinfo in members:
        if str.lower(os.path.splitext(tarinfo.name)[1]) in [".csv", ".xls"]:
            yield tarinfo


def saveHtml():
    saveHtmlFile = changeStrDecode(globalVar.PATH1,"GB2312") + '/' + changeStrDecode(globalVar.PATH1.split("/")[
        -1],"GB2312") + u"_高级测报.html"
    saveHtmlFile = changeStrEncode(saveHtmlFile,"GB2312")
    copyHtmlFile = changeStrDecode(globalVar.HTML_SAVE_PATH,"GB2312")  + '/'+changeStrDecode(globalVar.PATH1.split("/")[-1],"GB2312")+u"_高级测报.html"
    copyHtmlFile = changeStrEncode(copyHtmlFile,"GB2312")
    htmlMaker.htmlViewSave(saveHtmlFile)
    copyfile(saveHtmlFile, copyHtmlFile)
    return saveHtmlFile


def deCompress(file):
    subDecompressPath = ".".join(file.split('.')[:-1])
    if not os.path.exists(subDecompressPath) and (
            str.lower(os.path.splitext(file)[1]) in
        [".zip", ".rar", ".tar", ".7z", ".bz2", ".gz"]):
        try:
            if file.lower().endswith(".zip"):
                z = zipfile.ZipFile(file)
                # z.extractall(subDecompressPath)
                z.extractall(members=dcDataFiles(z.namelist()),
                                path=subDecompressPath)
                deCompressPath(subDecompressPath)
                z.close()
            elif file.lower().endswith(".rar"):
                r = rarfile.RarFile(file)
                # r.extractall(subDecompressPath)
                r.extractall(members=dcDataFiles(r.namelist()),
                                path=subDecompressPath)
                deCompressPath(subDecompressPath)
                r.close()
            elif file.lower().endswith(".tar"):
                t = tarfile.TarFile(file)
                # t.extractall(subDecompressPath)
                t.extractall(members=tarDcDataFiles(t), path=subDecompressPath)
                deCompressPath(subDecompressPath)
                t.close()
            # 不删除文件，防止目录更新
        except Exception as e:
            try:
                warning("skip uncompress file:")
                warning(file)
                shutil.rmtree(subDecompressPath)
            except:
                warning("rmtree unable to remove path!")


def deCompressPath(path):
    files = getCompressFiles(path)
    for i in files:
        deCompress(i)


def analysisPathProcess(_needDeepAnalysis, rootPath, needRecursion, mapModeList):
    dataOper = dataCalculator.rawExcelToFinalTestInit(needRecursion)
    dataOper.getALLFileFinalTest()
    dataOper.addHtml_baseAndStripMsg()
    try:
        if 1 in mapModeList:
            mPrint(u"\n\n准备绘制正常MAP。")
            dataOper.drawAllMap()
        if 2 in mapModeList:
            mPrint(u"\n\n准备绘制叠加MAP。")
            dataOper.drawOverlayMap(rootPath)
        if 3 in mapModeList:
            mPrint(u"\n\n准备绘制DC参数均值MAP（3D）。")
            dcValView = rawInput(u"请输入需要观察的DC参数）：\n").strip()
            dataOper.drawDcValView3D(dcValView)
    except:
        pass

    dataOper.saveExcelFile()
    getMessage.messageInit()
    getMessage.addHtmlAndLogAndPathMsg()
    saveHtml()
    closeAndHideLog()  # or may cause  re-analysis
    pathMsgMaker.saveAndHidePathMsg(rootPath)

    if _needDeepAnalysis:
        # os.system(r'start " " ""' + saveHtmlFile + r'"')
        globalVar.FINAL_TABLE_FILE_CONTEXT.seek(0)
        globalVar.FIRST_TABLE_FILE_CONTEXT.seek(0)
        finalTestFile = globalVar.PATH1 + "/_FINAL_" + globalVar.PATH1.split(
            '/')[-1] + ".csv"
        f = open(finalTestFile, "w")
        f.write(globalVar.FINAL_TABLE_FILE_CONTEXT.getvalue())
        f.close()
        firstTestFile = globalVar.PATH1 + "/_FIRST_" + globalVar.PATH1.split(
            '/')[-1] + ".csv"
        f = open(firstTestFile, "w")
        f.write(globalVar.FIRST_TABLE_FILE_CONTEXT.getvalue())
        f.close()
        try:
            if 4 in mapModeList:
                mPrint(u"\n\n准备DC分布和各SITE均值图。")
                getChart.saveHistogramDC()
                getChart.saveSiteDC()  
                getChart.closeAll()
        except:
            pass


def comparePathProcess(_needDeepAnalysis):
    getMessage.messageInit()
    copyfile(globalVar.FINAL_TABLE_FILE1, globalVar.COMPARE_PATH + '/' +
             globalVar.FINAL_TABLE_FILE1.split("/")[-1])
    copyfile(globalVar.FINAL_TABLE_FILE2, globalVar.COMPARE_PATH + '/' +
             globalVar.FINAL_TABLE_FILE2.split("/")[-1])
    if _needDeepAnalysis:
        getChart.saveCmpHistogramDC()
        getChart.saveCmpSiteDC()
        getChart.closeAll()


def searchPathProcess():
    searchPath = rawInput(u"请输入需要搜索的目录")
    selectSearch = intInput(u"1.搜索UID（输入UID全内容，OSWEGO） 2.搜索时间 3.搜索时间段 \n")
    msgFile = pathMsgMaker.getAllMsgPathFile(searchPath)
    print "getAllMsgPathFile", map(lambda x: changeStrEncode(x, "GB2312"),
                                   msgFile)
    getResult = []
    if selectSearch == 1:
        uid = rawInput(u"请输入UID: ")
        uid = formatUserUid(uid)
        getResult = map(lambda x: pathMsgMaker.findUidAtPath(uid, x), msgFile)
    elif selectSearch == 2:
        time = rawInput(u"请输入时间点(如2010-10-10 10:10:10):")
        getResult = map(lambda x: pathMsgMaker.findTimeAtPath(time, x),
                        msgFile)
    elif selectSearch == 3:
        timeBeg = rawInput(u"请输入起始时间(如2010-10-10):")
        timeEnd = rawInput(u"请输入结束时间(如2010-10-10):")
        getResult = map(
            lambda x: pathMsgMaker.findTimeBetweenPath(timeBeg, timeEnd, x),
            msgFile)
    mPrint(u"搜索到的目录为：")
    getResult = filter(lambda x: len(x) != 0, getResult)
    for i in getResult:
        mPrint(i)
    mPrint(u"以上为搜索结果，如果搜索不正确，请“递归分析”更新总目录，或确认数据是否异常。")


def single_process(_needDeepAnalysis, rootPath, needRecursion=True):
    print "\n\n\n\n\n\n\n\n\n\n\n\n"
    print strftime('%Y-%m-%d %H:%M:%S', localtime())
    print "Analysis Start<<<"

    if globalVar.SELECT_MODE == ANALYSIS_MODE:
        mapModeList = []
        if _needDeepAnalysis == True:
            mapModeList = listInput(
u"请选择需要生成的图像类型？回车Enter继续 \n1.正常MAP 2.BIN叠加MAP 3.DC参数均值MAP（3D） 4.各SITE均值图和简易分布直方图\n\
Example=> 1,3,4\n")
        analysisPathProcess(_needDeepAnalysis, rootPath, needRecursion,
                            mapModeList)
    elif globalVar.SELECT_MODE == COMPARE_MODE:
        mPrint(u"此功能仅可以用于已经分析的目录！")
        comparePathProcess(_needDeepAnalysis)
    print "\n\n\n\n>>>Analysis End"
    print strftime('%Y-%m-%d %H:%M:%S', localtime())
    return map(lambda x: x.pathFileName, globalVar.SkipList)


def getCfgAndPath():
    path1 = path2 = ""
    pathList = []
    pathCfgList = []
    if globalVar.SELECT_MODE in [ANALYSIS_MODE, AUTO_ANALYSIS_MODE]:
        path1 = rawInput(u"请输入对应DC目录\n")
    elif globalVar.SELECT_MODE == COMPARE_MODE:
        path1 = rawInput(u"对照组 DC目录\n")
        path2 = rawInput(u"实验组 DC目录\n")
    elif globalVar.SELECT_MODE == MULTIPLE_AUTO_ANALYSIS_MODE:
        while (1):
            path1 = rawInput(
                u"请输入需要分析的DC目录，每一个工作目录应该有默认配置文件(default_CFG.JSON)，输入回车结束\n")
            if path1 != "\n":
                pathList.append(path1)
            else:
                break

    path1, path2 = unifyPath(path1), unifyPath(path2)
    pathList = map(lambda x: unifyPath(x), pathList)

    cfgFile = ""
    cfg = ""
    if globalVar.SELECT_MODE == MULTIPLE_AUTO_ANALYSIS_MODE:
        pathCfgList = map(lambda x: x + '/default_CFG.JSON', pathList)
        for i in range(len(pathCfgList)):
            if not os.path.exists(pathCfgList[i]):
                raiseError(u"默认配置文件不存在！期望的配置文件为：" + changeStrDecode(
                    pathCfgList[i], "GB2312"))
            with codecs.open(pathCfgList[i], 'r', 'GB2312') as f:
                pathCfgList[i] = json.loads(f.read().replace("\\", "\\/"))
    elif globalVar.SELECT_MODE in [ANALYSIS_MODE,COMPARE_MODE,AUTO_ANALYSIS_MODE]:
        if os.path.exists(path1 + '/default_CFG.JSON'):
            cfgFile = path1 + '/default_CFG.JSON'
        else:
            print u"请选择一个配置文件：\n".encode("GB2312")
            cfgJsonList = filter(lambda x: str(x[-8:]).upper() == "CFG.JSON",
                                 os.listdir("./"))
            if len(cfgJsonList) == 0:
                print u"没有找到配置文件！".encode("GB2312")
                exit(1)
            cfgSelectStr = ""
            for index, cfgName in enumerate(cfgJsonList):
                cfgSelectStr += str(index + 1) + "." + cfgName + "\t"
                if index % 2 == 1:
                    cfgSelectStr += '\n'
            cfgFile = cfgJsonList[intInput(cfgSelectStr + "\n") - 1]
        with codecs.open(cfgFile, 'r') as f:
            cfg = json.loads(f.read().replace("\\", "\\/"))

    return cfg, path1, path2, pathList, pathCfgList


def batchAnalysisPath(path, cfg, rootPath, needRecursion=True):
    dcPathList = list(getDcPathAndType(path, globalVar.KEY_WORD, "",
                                       needRecursion)[0])
    dcPathList.sort()
    #init_log(rootPath)
    globalVar.TopFailSummy = summyInfoBase(
        rootPath, "FAIL",
        changeStrEncode(u"目录,型号,总数,BIN,BIN含义,首测不良,复测不良,最终不良率", "GB2312"))
    globalVar.TotalSummy = summyInfoBase(
        rootPath, "TOTAL_SUMMY", changeStrEncode(
            u"目录,型号,扫描基板数,单片芯片数,芯片总数,首测不良率,复测不良率,各SITE良率差", "GB2312"))
    globalVar.SiteSummy = summyInfoBase(
        rootPath, "SITE_SUMMY",
        changeStrEncode(u"目录,型号,SITE,终测芯片数目,首测良率,最终良率,首测、终测良率差", "GB2312"))
    for i in dcPathList:
        try:
            log("\n\n\n\n\n\ncurrent path")
            log(i)
            curPathMsg = pathMsgMaker.getPathMsg(path, i)
            pdthChangeTime = ctime(os.path.getmtime(i))
            if curPathMsg == "" or (
                    curPathMsg['lastChangeTime'] != pdthChangeTime and
                    curPathMsg['pathMd5'] != getPathMd5(i)):
                setCfgAndMkLog(cfg, i, "")
                single_process(False, rootPath, needRecursion)
            else:
                closeAndHideLog()
                warning(u"跳过目录" + changeStrDecode(i,"GB2312"))
        except Exception, e:
            closeAndHideLog()
            warning(u"分析出现异常的目录" + changeStrDecode(i,"GB2312"))
            warning(str(e))


def watchPath(path):
    mPrint(u"正在进行自动分析，任何目录变动都将尝试自动进行分析。。。。。。（如果不需要动态监控，请关闭窗口）")
    lastAnalyPath = set([])
    fileState.watchChangePath(path)
    while 1:
        analyPath = set(fileState.changingFileOrPath())
        changePath = list(lastAnalyPath - analyPath)
        for i in changePath:
            log("change file(Path):")
            log(i)
        lastAnalyPath = analyPath
        time.sleep(5)
    return


def watchPathAndProcess(path, cfg):
    mPrint(u"正在进行自动分析，任何目录变动都将尝试自动进行分析（如果不需要动态监控，请关闭窗口）。。。。。。")
    lastAnalyObj = set([])
    fileState.watchChangePath(path)
    while 1:
        analyObj = set(fileState.changingFileOrPath())
        changeObj = list(lastAnalyObj - analyObj)
        changePath = []
        for i in changeObj:
            if os.path.isfile(i) or (globalVar.KEY_WORD in i and str(i).split('.')[-1].lower() in ("csv","xls")):
                deCompress(i)
                if globalVar.KEY_WORD in i:
                    changePath.append("/".join(i.split('/')[:-1]))
        changePath = set(changePath)
        for i in changePath:
            batchAnalysisPath(changeStrEncode(i, "GB2312"), cfg, path, False)

        lastAnalyObj = analyObj
        time.sleep(3)
    return


# def clearnSplitDataProcess():
#     mPrint(u"此功能仅可以用于已经分析的目录！")
#     mPrint(u"功能说明：挑选具有某种特征的单行数据或整个文件数据。")
#     formula = rawInput(u"请输入对应筛选公式，如data['SW_BIN'] == 3")
#     numberSelect = rawInput(u"筛选后")
#     outputDataChoose = rawInput(u"请输入需保存的类型：\n1.单行数据 2.整个文件")
    

    
#     pass

def setCfgAndMkLog(cfg, path1, path2):
    globalVar.SkipList = []
    globalVar.PATH1 = path1
    globalVar.PATH2 = path2
    globalVar.IC_TYPE = cfg["IC_TYPE"]
    globalVar.KEY_WORD = changeStrEncode(
        changeStrDecode(cfg["KEY_WORD"], "GB2312"), "ascii")
    globalVar.CHIP_NUM = cfg["CHIP_NUM"]  #120
    globalVar.BIN_NAME = cfg["BIN_NAME"]  # 'SWBIN'
    globalVar.UID_NAME = cfg["UID_NAME"]  # 'UID'
    globalVar.X_COORD_NAME = str(cfg["X_COORD"]).split(',')  # "X,X_POS"
    globalVar.MAX_RETEST_TIME = cfg["MAX_RETEST_TIME"]  # 10
    globalVar.PASS_BIN = cfg["PASS_BIN"]  # 1
    globalVar.FIRST_DC_DATA_LABEL = cfg["FIRST_DC_DATA_LABEL"]  # 'SVDDF/V'
    globalVar.SITE_NAME = cfg["SITE"]
    globalVar.TEST_TIME = cfg["TEST_TIME"]  #'Date='
    globalVar.WORNG_BIN_LIST = changeStrEncode(cfg["WORNG_BIN_LIST"], "GB2312")

    globalVar.TOP_N = 999
    globalVar.IGNORE_BIn = []
    if globalVar.SELECT_MODE == ANALYSIS_MODE:
        init_log(globalVar.PATH1)
    if globalVar.SELECT_MODE == COMPARE_MODE:
        globalVar.COMPARE_PATH = "./compare/" + path1.split("/")[
            -1] + "_" + path2.split("/")[-1]
        if not os.path.exists(globalVar.COMPARE_PATH):
            os.makedirs(globalVar.COMPARE_PATH)
        init_log(globalVar.COMPARE_PATH)


def process():
    if globalVar.SELECT_MODE == HELPER_MODE:
        os.system(changeStrEncode(u"start DcHelper使用说明.docx", "GB2312"))
        return
    elif globalVar.SELECT_MODE == EXTRACT_MODE:
        decompPath = unifyPath(rawInput(u"请输入需要解压的目录\n"))
        deCompressPath(decompPath)
        return
    elif globalVar.SELECT_MODE == SEARCH_MODE:
        searchPathProcess()
        return

        
    cfg, path1, path2, pathList, cfgList = getCfgAndPath()
    setCfgAndMkLog(cfg, path1, path2)
    if globalVar.SELECT_MODE == CLEAN_SPLIT_DATA_MODE:
        # clearnSplitDataProcess()
        return
    elif globalVar.SELECT_MODE in [ANALYSIS_MODE, COMPARE_MODE]:
        single_process(True, path1)
    elif globalVar.SELECT_MODE == AUTO_ANALYSIS_MODE:
        globalVar.SELECT_MODE = ANALYSIS_MODE  # dummy
        analyOldFile = intInput(u"是否分析存在的目录（不会进行解压操作）？ \n输入0或回车Enter不分析，输入1分析")
        if analyOldFile == 1:
            mPrint(u"正在分析已经存在的目录")
            batchAnalysisPath(path1, cfg, path1, True)
        mPrint(u"现在开始监控目录")
        watchPathAndProcess(changeStrDecode(path1, "GB2312"), cfg)
    elif globalVar.SELECT_MODE == MULTIPLE_AUTO_ANALYSIS_MODE:
        globalVar.SELECT_MODE = ANALYSIS_MODE  # dummy
        while True:
            for i in len(range(pathList)):
                batchAnalysisPath(i, cfgList[i], path1, True)


if __name__ == '__main__':
    try:
        globalVar.HTML_SAVE_PATH = './htmlSave'
        if not os.path.exists(globalVar.HTML_SAVE_PATH):
            os.makedirs(globalVar.HTML_SAVE_PATH)
        globalVar.NEED_LOG = False
        globalVar.SELECT_MODE = None
        globalVar.IGNORE_ERROR = ()
        while globalVar.SELECT_MODE in[SAVE_LOG_MODE,IGNORE_ERROR_MODE] or globalVar.SELECT_MODE == None:
            os.system('cls')
            if globalVar.NEED_LOG == True:
                warning(u"需要保存LOG")
            if globalVar.IGNORE_ERROR != ():
                warning(u"忽略错误：" + str(globalVar.IGNORE_ERROR))
            globalVar.SELECT_MODE = intInput(u"\
    欢迎使用Dc_Helper\n\n\
    0.打开说明\n\
    1.分析DC目录\t2.对比DC目录\n\
    3.解压数据文件\t4.自动递归(分析、监控)\n\
    5.多目录递归\t6.搜索已分析的目录\n\
    7.需要LOG,可选 \t8.取消错误代码,可选\n")
            if globalVar.SELECT_MODE == None: continue
            if globalVar.SELECT_MODE == SAVE_LOG_MODE:
                globalVar.NEED_LOG = True
            if globalVar.SELECT_MODE == IGNORE_ERROR_MODE:
                globalVar.IGNORE_ERROR = listInput(u"请输入需要屏蔽的数字编号,如\nExample=>1,2,3\n")

        process()
        rawInput(u"正常结束，按回车退出\n")
            # #cProfile.run("main()")
            # cProfile.runctx("process()",
            #                 globals(),
            #                 locals(),
            #                 filename="OpenGLContext.profile")
    except:
        warning(u"运行中遇到错误")
        rawInput(u"按回车退出\n")
