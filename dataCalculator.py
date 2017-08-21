# -*- coding: utf-8 -*-

from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import os
import re
import globalVar
import htmlMaker
from fn import iters
from time import strftime, localtime
import pathMsgMaker
import StringIO
from base_function import *
import getMap


class stripMsg:
    guessUidNotMatch = ""
    guessUidRepeat = 0
    testCount = 0
    usefulChipNum = 0
    num = 0
    testTime = ""
    file = ""
    name = ""
    firstTestFail = 0
    failNum = 0
    finalYieldRate = "%"
    siteDifferent = ""
    packagingSkip = 0


class skipFile:
    fileName = ""
    pathFileName = ""
    errorReason = ""


def addSkipFile(pathFile, errorReason, file=""):
    sf = skipFile()
    sf.pathFileName = pathFile
    if len(file) == 0:
        sf.fileName = str(sf.pathFileName).split('/')[-1]
    else:
        sf.fileName = file
    sf.errorReason = errorReason
    globalVar.SkipList.append(sf)


def unifyFilesName(fileList):
    if fileList == []:
        return
    pathList = list(map(lambda x: "/".join(re.split("/", x)[:-1]), fileList))
    nameList = list(map(lambda x: re.split("/", x)[-1], fileList))
    log(str(nameList))

    lengthList = map(lambda x: len(x), nameList)
    maxLength = max(lengthList)
    minLength = min(lengthList)
    maxLengthFile = list(filter(lambda x: len(x) == maxLength, nameList))[0]
    minLengthFile = list(filter(lambda x: len(x) == minLength, nameList))[0]
    log("maxLengthFile" + maxLengthFile)
    log("minLengthFile" + minLengthFile)
    if len(minLengthFile) == len(maxLengthFile):
        return

    samePartLength = -1
    leftPart = ""
    for i in range(minLength):
        leftPart = str(minLengthFile)[0:i + 1]
        if leftPart[-1] not in map(lambda x: str(x), range(10)):
            if leftPart == maxLengthFile[0:i + 1]:
                samePartLength = i + 1

    leftSamePart = minLengthFile[0:samePartLength]
    diffNum_max = re.findall("(\d+).*", maxLengthFile[samePartLength:])
    if diffNum_max == []:
        return

    diffNum_max = diffNum_max[0]
    retNameList = []
    for i in range(len(nameList)):
        retNameList.append(pathList[i] + '/' + nameList[i][0:samePartLength])
        currentNumLength = re.findall("(\d+).*",
                                      nameList[i][samePartLength:])[0]
        fillLength = len(diffNum_max) - len(currentNumLength)
        retNameList[-1] += '0' * fillLength + nameList[i][samePartLength:]

    for i in range(len(fileList)):
        if pathList[i] + '/' + nameList[i] != retNameList[i]:
            log("rename " + fileList[i] + "to " + retNameList[i])
            os.renames(fileList[i], retNameList[i])


def getAndRenamefile(path, needRecursion=True):

    dcPathList, excelFileType = getDcPathAndType(
        globalVar.PATH1, globalVar.KEY_WORD, "", needRecursion)
    for i in dcPathList:
        pathDcFiles = getFile(globalVar.PATH1, globalVar.KEY_WORD, "",
                              needRecursion)
        pathDcFiles = filter(lambda x: excelFileType in x, pathDcFiles)
        unifyFilesName(pathDcFiles)
    retFileList = getFile(globalVar.PATH1, globalVar.KEY_WORD, "",
                          needRecursion)
    retFileList = filter(lambda x: excelFileType in x, retFileList)

    return retFileList, excelFileType


def renameHeaderName(l):
    left = []
    ret = []
    for i in l:
        j = i
        if i in left:
            if i[-1] in map(lambda x: str(x), range(10)) and i[-2] == '_':
                i = i[:-1]
                i += str(int(i[-1]) + 1)[0]
            else:
                i += '_2'
        ret.append(i)
        left.append(j)
    return ret


class rawExcelToFinalTestInit(object):
    def __init__(self, needRecursion=True):
        self.finalTestContext = ""
        self.firstTestContext = ""
        self.fileLength = {}
        self.ELEM_NUM = -1

        self.excelFileList, self.excelFileType = getAndRenamefile(
            globalVar.PATH1, needRecursion)

        self.STRIPS_MSG = []
        self.allUidList = []
        if len(self.excelFileList) == 0:
            raiseError(4, u"匹配不到任何文件")
        self.excelFileList = map(lambda x: x.replace('\\', '/'),
                                 self.excelFileList)
        self.excelFileList = filter(lambda x: not x.startswith("RT"),
                                    self.excelFileList)
        log("raw file num:" + str(len(self.excelFileList)))
        log("excel file list :")
        for i in self.excelFileList:
            log("\t" + i.split('/')[-1])

        globalVar.firstFail = 0
        globalVar.finalFail = 0

    def fuzzHeaderMatch(self, name, headerArray):
        retName = retIndex = 0
        if len(filter(lambda x: x not in "0123456789", name)) == 0:
            retIndex = int(name) - 1
            retName = headerArray[retIndex]
            if retIndex >= self.ELEM_NUM:
                raiseError(5, u"数字匹配" + name + u"超出范围")
        else:
            temp = process.extractOne(name, headerArray)
            log(name + u" 模糊匹配率:" + str(temp[1]) + u"%, 匹配到的内容为:" + temp[0])
            if temp[1] < 95:
                warning(name + u"模糊匹配率:" + str(temp[1]) + u"%, 匹配到的内容为:" +
                        temp[0])
                raiseError(6, u"匹配" + name + u" 列还需要再试一试")

            retName = temp[0]
            retIndex = headerArray.index(retName) % self.ELEM_NUM

        log(name + u" 模糊匹配为：" + retName + u"，匹配到表格的列为:" + str(retIndex))
        return retName, retIndex

    def getTable2D(self, fileName):
        context2D = []
        fileContextList = openFileAsLineList(fileName)
        self.fileLength[fileName] = len(fileContextList)
        for i in fileContextList:
            l = []
            if self.excelFileType.lower() == 'xls':
                l = i.rstrip().split("\t")
            elif self.excelFileType.lower() == 'csv':
                l = i.rstrip().split(",")
            if len(l) > 0 and len(l[-1]) == 0:
                l.pop()
            if len(filter(lambda x: len(x) != 0, l)) == 0:
                continue
            if "HSKey" in l[0]:
                raiseError(0, u"加密")

            if (len(l) > 1):
                context2D.append(l)

        log("len(context2D)" + str(len(context2D)))
        if len(context2D) < 10:
            raiseError(7, u"行数太少")

        if self.ELEM_NUM == -1:
            self.ELEM_NUM = len(context2D[-1])
            log("self.ELEM_NUM :" + str(self.ELEM_NUM))
        else:
            log("self.ELEM_NUM :" + str(len(context2D[-1])))
            if self.ELEM_NUM != len(context2D[-1]):
                raiseError(8, u"列数不同")

        return context2D

    def saveCurStripMsg(self, fileName, testTime, usefulChipNum,
                        guessUidRepeat, lineNum, firstTestSiteList,
                        finalTestSiteList, uidErrorLineList, fileFirstFailNum,
                        fileFinalFailNum, siteDifferent):
        CurStripMsg = stripMsg()
        CurStripMsg.num = len(self.STRIPS_MSG)
        CurStripMsg.file = fileName
        CurStripMsg.name = str(fileName).split('/')[-1].split('.')
        CurStripMsg.name = ".".join(CurStripMsg.name[:-1])
        CurStripMsg.testTime = testTime
        if len(CurStripMsg.testTime) < 5:
            CurStripMsg.testTime = ""
        CurStripMsg.usefulChipNum = usefulChipNum
        CurStripMsg.packagingSkip = globalVar.CHIP_NUM - CurStripMsg.usefulChipNum

        if CurStripMsg.packagingSkip > 7:
            CurStripMsg.packagingSkip = '<font color=red>' + str(
                CurStripMsg.packagingSkip) + '</font>'
        CurStripMsg.firstTestFail = fileFirstFailNum
        CurStripMsg.failNum = fileFinalFailNum
        CurStripMsg.siteDifferent = (u'<font color=red>是</font>').encode(
            'GB2312') if firstTestSiteList != finalTestSiteList else ""
        if siteDifferent == False:
            CurStripMsg.siteDifferent = ""
        if CurStripMsg.firstTestFail > CurStripMsg.failNum * 1.5 + 6 or CurStripMsg.firstTestFail < CurStripMsg.failNum:
            CurStripMsg.firstTestFail = '<font color=red>' + str(
                CurStripMsg.firstTestFail) + '</font>'
        if len(uidErrorLineList) != 0:
            CurStripMsg.guessUidNotMatch = (
                '<font color=red>' + str(len(uidErrorLineList)) +
                '</font>') if len(uidErrorLineList) != 0 else " "
        CurStripMsg.guessUidRepeat = (
            '<font color=red>' + str(guessUidRepeat) +
            '</font>') if guessUidRepeat != 0 else " "
        CurStripMsg.testCount = str(lineNum)

        if int(CurStripMsg.testCount) > float(
                CurStripMsg.usefulChipNum) * 1.35:
            CurStripMsg.testCount = '<font color=red>' + CurStripMsg.testCount + '</font>'

        CurStripMsg.finalYieldRate = str(100 * (
            1 - float(fileFinalFailNum) / CurStripMsg.usefulChipNum))[:5] + '%'
        if 100 * (
                1 - float(fileFinalFailNum) / CurStripMsg.usefulChipNum) < 96:
            CurStripMsg.finalYieldRate = '<font color=red>' + CurStripMsg.finalYieldRate + '</font>'
        self.STRIPS_MSG[-1] = CurStripMsg

    def scanFileBaseMsg(self, fileName):
        curFileName = fileName.split('/')[-1]
        log("\n\n\nscan File Base Msg" + curFileName + "}")
        context2D = self.getTable2D(fileName)
        fuzzGuessItem = self.ELEM_NUM * 3
        contexts2D = filter(
            lambda x: self.ELEM_NUM == len(x) and len(str(x[-1])) >= 1,
            context2D)

        context1D = list([y for x in contexts2D for y in x])  #将多维数据化为一维数

        globalVar.header = contexts2D[0]
        globalVar.SITE_NAME, globalVar.SITE_ROW_INDEX = self.fuzzHeaderMatch(
            globalVar.SITE_NAME, context1D[0:fuzzGuessItem])
        globalVar.BIN_NAME, globalVar.BIN_ROW_INDEX = self.fuzzHeaderMatch(
            globalVar.BIN_NAME, context1D[0:fuzzGuessItem])
        if globalVar.UID_NAME != "":
            globalVar.UID_NAME, globalVar.UID_ROW_INDEX = self.fuzzHeaderMatch(
                globalVar.UID_NAME, context1D[0:fuzzGuessItem])
        if globalVar.TEST_TIME != "":
            ignore_time, globalVar.TIME_ROW_INDEX = self.fuzzHeaderMatch(
                globalVar.TEST_TIME, context1D[0:fuzzGuessItem])
        globalVar.FIRST_DC_DATA_LABEL, globalVar.FIRST_DC_ROW_INDEX = self.fuzzHeaderMatch(
            globalVar.FIRST_DC_DATA_LABEL, globalVar.header)
        coordNameList = globalVar.X_COORD_NAME
        globalVar.X_COORD_NAME = ""
        for i in coordNameList:
            try:
                globalVar.X_COORD_NAME, globalVar.X_ROW_INDEX = self.fuzzHeaderMatch(
                    i, context1D[0:fuzzGuessItem])
                break
            except:
                pass

    def getTestTimeList(self, context2D):
        testTimeList = []
        if globalVar.TEST_TIME != "":
            timeRow = map(lambda x: x[globalVar.TIME_ROW_INDEX], context2D)
            testTimeList = map(lambda x: pathMsgMaker.getFormatTestTime(x),
                               timeRow)
        else:
            testTimeList = ['0'] * len(context2D)
        return testTimeList

    def uidCheck(self, uid1, uid2, uidErrorLineList, firstIndex):
        if len(filter(lambda x: x != '0', uid1)) == 0:
            uid1 = '0'
        if globalVar.UID_NAME != "" and (uid1 != uid2) and len(uid1) > 5:
            uidErrorLineList.append(firstIndex + 1)
            log("different=>uid1:" + uid1 + ",uid2:" + uid2)

    def getStripMsgAndSetHtml(self, contexts2D, curFileName):
        lineNum = len(contexts2D)
        log("testCount(lineNum):" + str(lineNum))

        testTimeList = self.getTestTimeList(contexts2D)
        #如果存在"RT"文件则按"RT"文件，存在坐标就按照site试图运行，如果数目较少，则按堆叠方法
        usefulChipNum = 0
        uidErrorLineList = []
        firstContexts2D, finalContexts2D = [], []
        siteDifferent = None

        curPath = "/".join(curFileName.split('/')[:-1])
        curPathFiles = os.listdir(curPath)
        retestFile = list(filter(
            lambda x: x.startswith("RT") and x.endswith(self.excelFileType),
            curPathFiles))
        retestFile.sort()
        if len(retestFile) != 0:
            siteDifferent = False
            firstContexts2D = contexts2D[:]
            finalContexts2D = list(filter(
                lambda x: x[globalVar.BIN_ROW_INDEX].strip() == str(globalVar.PASS_BIN),
                firstContexts2D))
            retestFileLen = len(retestFile)
            for i in range(retestFileLen):
                newContext = self.getContexts2D(curPath + '/' + retestFile[i])
                newPassContext = filter(
                    lambda x: x[globalVar.BIN_ROW_INDEX].strip() == str(globalVar.PASS_BIN),
                    newContext)
                finalContexts2D.extend(newPassContext)
            lastContext = self.getContexts2D(curPath + '/' + retestFile[-1])
            lastFailContext = filter(
                lambda x: x[globalVar.BIN_ROW_INDEX].strip() != str(globalVar.PASS_BIN),
                lastContext)
            finalContexts2D.extend(lastFailContext)
            usefulChipNum = len(finalContexts2D)
            siteDifferent = False
        else:
            try:
                assert globalVar.X_COORD_NAME != "", changeStrEncode(u"无坐标",
                                                                     "GB2312")
                xCoordList = []
                yCoordList = []
                usefulXyCoordList = []
                usefulSiteList = []
                usefulBinList = []
                usefulTestContexts = []

                siteDifferent = False

                for i in range(len(contexts2D)):
                    tempXStr = contexts2D[i][globalVar.X_ROW_INDEX].strip()
                    tempYStr = contexts2D[i][globalVar.X_ROW_INDEX + 1].strip()
                    if int(tempXStr) >= -999 and int(tempYStr) >= -999:
                        usefulTestContexts.append(contexts2D[i])

                        usefulXyCoordList.append(tempXStr + " " + tempYStr)
                        usefulSiteList.append(contexts2D[i][
                            globalVar.SITE_ROW_INDEX].strip())
                        usefulBinList.append(int(contexts2D[i][
                            globalVar.BIN_ROW_INDEX].strip()))

                leftPartOfXyCoordList = []
                for i in xrange(len(usefulXyCoordList)):
                    if usefulXyCoordList[i] in leftPartOfXyCoordList:
                        firstIndex = leftPartOfXyCoordList.index(
                            usefulXyCoordList[i])
                        # assert usefulSiteList[i] == finalContexts2D[firstIndex][globalVar.SITE_ROW_INDEX].strip()
                        if usefulSiteList[i] != finalContexts2D[firstIndex][
                                globalVar.SITE_ROW_INDEX].strip():
                            siteDifferent = True
                        uid1 = finalContexts2D[firstIndex][
                            globalVar.UID_ROW_INDEX].strip()
                        uid2 = usefulTestContexts[i][
                            globalVar.UID_ROW_INDEX].strip()
                        self.uidCheck(uid1, uid2, uidErrorLineList, firstIndex)
                        if usefulBinList[firstIndex] != int(
                                globalVar.PASS_BIN):
                            finalContexts2D[firstIndex] = usefulTestContexts[i]
                    else:
                        usefulChipNum += 1
                        firstContexts2D.append(usefulTestContexts[i])
                        finalContexts2D.append(usefulTestContexts[i])
                        leftPartOfXyCoordList.append(usefulXyCoordList[i])
                assert globalVar.CHIP_NUM / 1.25 <= usefulChipNum <= globalVar.CHIP_NUM

            except Exception, e:
                warning(u"坐标无效！！！")
                usefulChipNum = 0
                uidErrorLineList = []
                firstContexts2D, finalContexts2D = [], []
                siteDifferent = None

                maxSite = 0
                siteList = []
                for i in range(len(contexts2D)):
                    tempSiteStr = contexts2D[i][
                        globalVar.SITE_ROW_INDEX].strip()
                    if len(filter(lambda x: x not in "0123456789",
                                  tempSiteStr)) > 0:
                        raiseError(9, u"Site列匹配到错误值")
                    tempSite = int(tempSiteStr)
                    siteList.append(tempSite)
                    if tempSite > maxSite:
                        maxSite = tempSite
                maxSite += 1
                allGroupNum = globalVar.CHIP_NUM / maxSite
                log(u"TOUCH_DOWN组数:" + str(allGroupNum))
                log(u"SITE_LIST:" + str(siteList))
                lastSite = -1
                curGroupNum = 0
                curLine = 0
                lastGurGroup = []
                for i in siteList:
                    if i <= lastSite:
                        curGroupNum += 1
                        if curGroupNum == allGroupNum:
                            break
                    if curGroupNum == allGroupNum - 1:
                        lastGurGroup.append(curLine)
                    curLine += 1
                    lastSite = i

                if len(lastGurGroup) == 0:
                    raiseError(10, u"首测数据匹配不完全")

                #最后一组数据要减去时间不一致的部分
                wrongNum = 0
                lastTime = ""
                curTime = ""
                for i in lastGurGroup:
                    if wrongNum > 0:
                        wrongNum += 1
                    else:
                        curTime = testTimeList[i]
                        if lastTime != "" and lastTime != curTime:
                            wrongNum = 1
                        lastTime = curTime
                usefulChipNum = curLine - wrongNum
                if usefulChipNum > globalVar.CHIP_NUM:
                    raiseError(11, u"封装良品数错误")
                if usefulChipNum < globalVar.CHIP_NUM / 1.5:
                    raiseError(12, u"封装良品太少了")
                reTestContexts2D = list(contexts2D[usefulChipNum:])
                contexts2D = list(contexts2D[0:usefulChipNum])

                firstContexts2D = contexts2D[:]
                uidErrorLineList = self.repeatReplaceFirst(contexts2D,
                                                           reTestContexts2D)
                finalContexts2D = contexts2D[:]

        # 汇总部分
        uidErrorLineList = list(set(uidErrorLineList))
        guessUidRepeat = self.getUidRepeatNum(finalContexts2D)
        firstTestSiteList, fileFirstFailNum = self.getSiteListAndFailNum(
            firstContexts2D)
        finalTestSiteList, fileFinalFailNum = self.getSiteListAndFailNum(
            finalContexts2D)
        firstContexts1D, finalContexts1D = [], []
        for i in range(usefulChipNum):
            firstContexts1D.append(",".join(firstContexts2D[i]) + ',' +
                                   curFileName + "\n")
            finalContexts1D.append(",".join(finalContexts2D[i]) + ',' +
                                   curFileName + "\n")

        log("first test fail :" + str(fileFirstFailNum))
        log("final test fail :" + str(fileFinalFailNum))

        if globalVar.UID_NAME != "":
            if len(uidErrorLineList) != 0:
                warning(u"这些行复测UID不匹配: " + str(uidErrorLineList))
            if len(uidErrorLineList) > 4:
                raiseError(13, u"UID错误太多了")
            if guessUidRepeat > 5:
                raiseError(13, u"UID重复太多了")

        if fileFinalFailNum > usefulChipNum / 2:
            raiseError(14, u"良率太低")
        if fileFirstFailNum < fileFinalFailNum:
            raiseError(15, u"复测后不良品变多")

        self.saveCurStripMsg(curFileName, testTimeList[0], usefulChipNum,
                             guessUidRepeat, lineNum, firstTestSiteList,
                             finalTestSiteList, uidErrorLineList,
                             fileFirstFailNum, fileFinalFailNum, siteDifferent)
        return firstContexts1D, finalContexts1D, fileFirstFailNum, fileFinalFailNum

    def getUidRepeatNum(self, contexts2D):
        guessUidRepeat = 0
        if globalVar.UID_NAME != "":
            uidList = []
            for i in range(len(contexts2D)):
                tempUid = contexts2D[i][globalVar.UID_ROW_INDEX]
                if len(tempUid) > 4 and len(filter(lambda x: x != '0',
                                                   tempUid)) > 0:
                    uidList.append(tempUid)
            uidSet = set(uidList)
            guessUidRepeat = len(uidList) - len(uidSet)
            self.allUidList.extend(uidList)
            log("guessUidRepeat:" + str(guessUidRepeat))
        return guessUidRepeat

    def repeatReplaceFirst(self, contexts2D, reTestContexts):
        uidErrorLineList = []
        loopTime = 0
        while len(reTestContexts) > 0:
            for i in range(len(contexts2D)):
                if contexts2D[i][globalVar.BIN_ROW_INDEX].strip() != str(
                        globalVar.PASS_BIN):
                    if int(globalVar.MAX_RETEST_TIME) != 0:
                        if len(reTestContexts) > 0 and len(reTestContexts[
                                0]) == self.ELEM_NUM:
                            if globalVar.UID_NAME != "":
                                uid1 = contexts2D[i][
                                    globalVar.UID_ROW_INDEX].strip()
                                uid2 = reTestContexts[0][
                                    globalVar.UID_ROW_INDEX].strip()
                                self.uidCheck(uid1, uid2, uidErrorLineList,
                                              i + 1)
                            contexts2D[i] = reTestContexts[0]
                            reTestContexts = reTestContexts[1:]
                        else:
                            loopTime += 1
                            break
            loopTime += 1
            if loopTime >= int(globalVar.MAX_RETEST_TIME):
                if len(reTestContexts) > 0:
                    warning(",Retest loop time " + " > " + str(
                        globalVar.MAX_RETEST_TIME) + "!")
                break
        return uidErrorLineList

    def getSiteListAndFailNum(self, con):
        siteList = map(lambda x: int(x[globalVar.SITE_ROW_INDEX]), con)
        failNum = len(filter(
            lambda x: x[globalVar.BIN_ROW_INDEX].strip() != str(globalVar.PASS_BIN),
            con))

        return siteList, failNum

    def getContexts2D(self, file):
        print "current file:", changeStrEncode(file, "GB2312")
        log("\n\n\nCurrent file name{" + file + "}")
        contexts2D = self.getTable2D(file)
        fuzzGuessItem = self.ELEM_NUM * 3
        contexts2D = filter(
            lambda x: self.ELEM_NUM == len(x) and len(str(x[-1])) >= 1,
            contexts2D)

        if 80 < fuzz.ratio("".join(globalVar.header),
                           "".join(contexts2D[0])) < 99:
            raiseError(16, u"行标题不同")
        elif fuzz.ratio("".join(globalVar.header),
                        "".join(contexts2D[0])) < 50:
            warning("assume this file have no header,first line is " + "".join(
                contexts2D[0]) + "!")
        else:
            contexts2D = contexts2D[1:]

        while len(filter(lambda x: x not in "0123456789", contexts2D[0][
                globalVar.BIN_ROW_INDEX].split())) or len(contexts2D[0][
                    globalVar.BIN_ROW_INDEX].split()) == 0:
            contexts2D = contexts2D[1:]  # 跳过单位行
        return contexts2D

    def getFileFinalTestMsg(self, curFileName):
        contexts2D = self.getContexts2D(curFileName)

        firstContexts2D, contexts2D, fileFirstFailNum, fileFinalFailNum = self.getStripMsgAndSetHtml(
            contexts2D, curFileName)

        return "".join(firstContexts2D), "".join(
            contexts2D), fileFirstFailNum, fileFinalFailNum

    def getALLFileFinalTest(self):
        before_uid_list = []
        # scan one file and match user setting string
        for i in range(len(self.excelFileList)):
            try:
                self.scanFileBaseMsg(self.excelFileList[i])
                break
            except Exception, e:
                log(u"无法匹配必要标题头！")

        #calculator files
        calculatorFileFail = 0
        for f in self.excelFileList:
            try:
                before_uid_list = self.allUidList[:]
                self.STRIPS_MSG.append(0)
                firstContext, finalContext, fileFirstFailNum, fileFinalFailNum = self.getFileFinalTestMsg(
                    f)
                if len(self.STRIPS_MSG) >= 2:
                    if (self.STRIPS_MSG[-1].name ==
                            self.STRIPS_MSG[-2].name):
                        raiseError(17, u"数据疑似测试两次")
                self.firstTestContext += firstContext
                self.finalTestContext += finalContext
                globalVar.firstFail += fileFirstFailNum
                globalVar.finalFail += fileFinalFailNum

            except Exception, e:
                calculatorFileFail += 1
                warning("File catch a wrong!!!!")
                self.STRIPS_MSG.pop()
                self.ELEM_NUM = -1
                self.allUidList = before_uid_list[:]
                addSkipFile(f, e)

        if len(self.excelFileList) == calculatorFileFail:
            raiseError(18,u"数据全部无法使用")

    def saveExcelFile(self):
        globalVar.header = renameHeaderName(globalVar.header)
        globalVar.FINAL_TABLE_FILE_CONTEXT = StringIO.StringIO(re.sub(
            '[\"\t]', '', ",".join(
                globalVar.header)) + ",fileName\n" + self.finalTestContext)
        globalVar.FIRST_TABLE_FILE_CONTEXT = StringIO.StringIO(re.sub(
            '[\"\t]', '', ",".join(
                globalVar.header)) + ",fileName\n" + self.firstTestContext)
        globalVar.BIN_NAME = re.sub('[\"\t]', '', globalVar.BIN_NAME)
        globalVar.SITE_NAME = re.sub('[\"\t]', '', globalVar.SITE_NAME)
        globalVar.UID_NAME = re.sub('[\"\t]', '', globalVar.UID_NAME)
        globalVar.FIRST_DC_DATA_LABEL = re.sub('[\"\t]', '',
                                               globalVar.FIRST_DC_DATA_LABEL)

    def addHtml_baseAndStripMsg(self):
        htmlMaker.htmlMsg['icType'] = globalVar.IC_TYPE
        htmlMaker.htmlMsg['name'] = globalVar.PATH1.split("/")[-1]
        htmlMaker.htmlMsg['folderName'] = globalVar.PATH1 + '/'
        allUidSet = set(self.allUidList)
        htmlMaker.htmlMsg['diffFileRepeatUid'] = list(filter(
            lambda x: self.allUidList.count(x) > 1, list(allUidSet)))
        if htmlMaker.htmlMsg['diffFileRepeatUid'] == []:
            htmlMaker.htmlMsg['diffFileRepeatUid'] = u"无".encode('GB2312')
        else:
            htmlMaker.htmlMsg['diffFileRepeatUid'] = '<font color=red>' + str(htmlMaker.htmlMsg['diffFileRepeatUid'][0:3]) +\
                                                    u"共%d个".encode('GB2312')%(len(htmlMaker.htmlMsg['diffFileRepeatUid'])) + '</font>'
        htmlMaker.htmlMsg['haveUid'] = (globalVar.UID_NAME != "")
        htmlMaker.htmlMsg['skipPackageFail'] = True
        htmlMaker.htmlMsg['testPackageFail'] = False
        htmlMaker.htmlMsg['retestTime'] = globalVar.MAX_RETEST_TIME
        htmlMaker.htmlMsg['exportTime'] = strftime('%Y-%m-%d %H:%M:%S',
                                                   localtime())
        htmlMaker.htmlMsg['stripNum'] = len(self.excelFileList) - len(
            globalVar.SkipList)
        if len(globalVar.SkipList) == 0:
            addSkipFile(u"无".encode('GB2312'), u"无".encode('GB2312'),
                        u"无".encode('GB2312'))
        htmlMaker.htmlMsg['skipFileList'] = globalVar.SkipList
        htmlMaker.htmlMsg['icNum'] = sum(map(lambda x: x.usefulChipNum,
                                             self.STRIPS_MSG))
        htmlMaker.htmlMsg['icNumofStrip'] = globalVar.CHIP_NUM
        htmlMaker.htmlMsg['firstYieldRate'] = str(
            100 * (1 - float(globalVar.firstFail) /
                   htmlMaker.htmlMsg['icNum']))[:5] + '%'
        htmlMaker.htmlMsg['finalYieldRate'] = str(
            100 * (1 - float(globalVar.finalFail) /
                   htmlMaker.htmlMsg['icNum']))[:5] + '%'
        htmlMaker.htmlMsg['strips'] = self.STRIPS_MSG[:]

    def drawAllMap(self):
        textList = self.finalTestContext.split("\n")
        context2D = map(lambda x: x.split(','), textList)
        avgCoordValList = []
        for i in context2D:
            if len(i) > 1:
                x, y = int(i[globalVar.X_ROW_INDEX]), int(i[
                    globalVar.X_ROW_INDEX + 1])
                if x > -999 and y > -999:
                    avgCoordValList.append([x, y, int(i[
                        globalVar.BIN_ROW_INDEX]), i[-1]])

        valListLen = len(avgCoordValList)
        print "len(avgCoordValList)", valListLen

        if 1 == intInput(u"是否进行修改？ 0.不需要， 1.需要"):
            x = y = 0
            xChange = rawInput(u"请输入x的转换关系，如(100-x)*2").lower()
            yChange = rawInput(u"请输入y的转换关系，如(100-y)*2").lower()
            for i in range(valListLen):
                x = avgCoordValList[i][0]
                y = avgCoordValList[i][1]
                cx = eval(xChange)
                cy = eval(yChange)
                avgCoordValList[i][0] = cx
                avgCoordValList[i][1] = cy

        for strip in self.STRIPS_MSG:
            curMapMsg2D = filter(lambda x: x[-1] == strip.file,
                                 avgCoordValList)
            getMap.drawMapPic(strip, curMapMsg2D)

    def overlayCoord(self, table2D, addone1_add2_avg3, binSelect="True"):
        #均值合并、累加和并
        avgCoordValList = []
        coordValDict = {}

        for i in table2D:
            if len(i) > 1:
                x, y = str(i[0]).strip(), str(i[1]).strip()
                coord = x + " " + y
                b = int(str(i[3]).strip())
                val = float(str(i[2]).strip())
                if int(x) > -999 and int(y) > -999:
                    if eval(binSelect) and coordValDict.has_key(coord):
                        if addone1_add2_avg3 == 1:
                            coordValDict[coord] += 1
                        elif addone1_add2_avg3 == 2:
                            coordValDict[coord] += val
                        elif addone1_add2_avg3 == 3:
                            coordValDict[coord].append(val)
                    if eval(binSelect) and not coordValDict.has_key(coord):
                        if addone1_add2_avg3 == 1:
                            coordValDict[coord] = 1
                        elif addone1_add2_avg3 == 2:
                            coordValDict[coord] = val
                        elif addone1_add2_avg3 == 3:
                            coordValDict[coord] = [val]
                    if not eval(binSelect) and not coordValDict.has_key(coord):
                        if addone1_add2_avg3 != 3:
                            coordValDict[coord] = 0
                    if not eval(binSelect) and coordValDict.has_key(coord):
                        pass

        for i in coordValDict:
            if addone1_add2_avg3 in (1, 2):
                avgCoordValList.append([int(i.split(' ')[0]), int(i.split(' ')[
                    1]), coordValDict[i], -1])
            elif addone1_add2_avg3 == 3:
                if len(coordValDict[i]) != 0:
                    val = sum(coordValDict[i]) / len(coordValDict[i])
                    avgCoordValList.append([int(i.split(' ')[0]), int(i.split(
                        ' ')[1]), val, -1])
        return avgCoordValList

    def drawOverlayMap(self,rootPath):
        binSelect = rawInput(
u"请输入需要进行统计的BIN项，\n\
Example=> b == 1 \n\
Example=> b in (1,2,3,4,5)\n\
Example=> 8<=b<=20 and b!= 10\n").lower()
        header = renameHeaderName(globalVar.header)

        binName, binRow = self.fuzzHeaderMatch(globalVar.BIN_NAME, header)

        textList = self.finalTestContext.split("\n")
        context2D = map(lambda x: x.split(','), textList)

        avgCoordValList = []
        for i in context2D:
            if len(i) > 1:
                avgCoordValList.append([i[globalVar.X_ROW_INDEX], i[
                    globalVar.X_ROW_INDEX + 1], i[globalVar.BIN_ROW_INDEX], i[
                        globalVar.BIN_ROW_INDEX]])
        avgCoordValList = self.overlayCoord(avgCoordValList,
                                            addone1_add2_avg3=1,
                                            binSelect=binSelect)

        valListLen = len(avgCoordValList)
        print "len(avgCoordValList)", valListLen

        if 1 == intInput(u"是否进行修改？ 0.不需要， 1.需要\n"):
            xChange = rawInput(u"请输入x的转换关系，如(100-x)*2\n").lower()
            yChange = rawInput(u"请输入y的转换关系，如(100-y)*2\n").lower()
            for i in range(valListLen):
                x = avgCoordValList[i][0]
                y = avgCoordValList[i][1]
                cx = eval(xChange)
                cy = eval(yChange)
                avgCoordValList[i][0] = cx
                avgCoordValList[i][1] = cy
            avgCoordValList = self.overlayCoord(avgCoordValList,
                                                addone1_add2_avg3=2,
                                                binSelect="True")
        
        strip = self.STRIPS_MSG[0]
        stripNum = len(self.STRIPS_MSG)
        getMap.drawOverlayMapPic(strip, stripNum, binSelect, avgCoordValList,rootPath)

    def drawDcValView3D(self, dcValView):
        header = renameHeaderName(globalVar.header)

        dcName, dcRow = self.fuzzHeaderMatch(dcValView, header)

        textList = self.finalTestContext.split("\n")
        context2D = map(lambda x: x.split(','), textList)
        avgCoordValList = []
        for i in context2D:
            if len(i) > 1:
                avgCoordValList.append([i[globalVar.X_ROW_INDEX], i[
                    globalVar.X_ROW_INDEX + 1], i[dcRow], i[
                        globalVar.BIN_ROW_INDEX]])
        avgCoordValList = self.overlayCoord(avgCoordValList,
                                            addone1_add2_avg3=3,
                                            binSelect="b == 1")
        valListLen = len(avgCoordValList)
        print "len(avgCoordValList)", valListLen

        if 1 == intInput(u"是否进行修改？ 0.不需要， 1.需要\n"):
            xChange = rawInput(u"请输入x的转换关系，如(100-x)*2\n").lower()
            yChange = rawInput(u"请输入y的转换关系，如(100-y)*2\n").lower()
            valChange = rawInput(u"请输入val的转换关系，如(100-val)*2\n").lower()
            for i in range(valListLen):
                x = avgCoordValList[i][0]
                y = avgCoordValList[i][1]
                val = avgCoordValList[i][2]
                cx = eval(xChange)
                cy = eval(yChange)
                cval = eval(valChange)
                avgCoordValList[i][0] = cx
                avgCoordValList[i][1] = cy
                avgCoordValList[i][2] = cval
            avgCoordValList = self.overlayCoord(avgCoordValList,
                                                addone1_add2_avg3=3,
                                                binSelect="True")
            dcValView = changeStrEncode(
                changeStrDecode(
                    rawInput(u"请重新命名标题："), "GB2312"), "unicode")
        getMap.drawDcVal3D(dcValView, avgCoordValList)
