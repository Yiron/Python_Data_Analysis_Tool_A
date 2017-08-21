# -*- coding: utf-8 -*-
# 用户输入或配置部分全大写加下划线，固定匹配的变量也可以这么命名，但需要将相应变量靠拢
# 文件或图片相关的列表用首字母大写
# 关键字用首字母大写
# 其余均用小写，用大写字母分割
import globalVar
from base_function import *
import json
import os
import time

pathMsg = {'folderFileName': u"中文测试".encode('gb2312'),
           'pathMd5': "",
           'uidSectionTable': [],
           'timeBeg': "",
           'timeEnd': "",
           "lastChangeTime": "",
           'paraListMd5': "", }


def pathMsgPath(rootPath):
    msgPath = unifyPath(rootPath) + "/pathMsg"
    if not os.path.exists(msgPath):
        os.makedirs(msgPath)
    return msgPath


def getAllMsgPathFile(rootPath):
    msgPath = pathMsgPath(rootPath)
    fileList = os.listdir(msgPath)
    fileList = filter(lambda x: "_pathMsg.json" in x, fileList)
    fileList = map(lambda x: msgPath + '/' + unifyPath(x), fileList)
    return fileList


def getPathMsg(rootPath, path):
    pathMsgFile = pathMsgPath(rootPath) + '/' + path.split('/')[
        -1] + '_pathMsg.json'
    pathMsgJson = ""
    if os.path.isfile(pathMsgFile):
        try:
            with codecs.open(pathMsgFile, 'r', 'GB2312') as f:
                pathMsgJson = json.loads(f.read())
        except Exception, e:
            log("getPathMsg fail")
    return pathMsgJson


def saveAndHidePathMsg(rootPath):
    pathMsg['lastChangeTime'] = time.ctime(os.path.getmtime(globalVar.PATH1))
    pathMsgFile = pathMsgPath(rootPath) + '/' + globalVar.PATH1.split('/')[
        -1] + '_pathMsg.json'
    try:
        with codecs.open(pathMsgFile, 'w', 'GB2312') as f:
            f.write(json.dumps(pathMsg))
    except Exception, e:
        mPrint(u"保存PATH_MESSEGE失败:"+changeStrDecode(pathMsgFile,"GB2312"))
    try:
        hideFile(changeStrDecode(pathMsgPath(rootPath),"GB2312"))
    except Exception, e:
        mPrint(u"隐藏PATH_MESSEGE失败:"+changeStrDecode(pathMsgPath(rootPath),"GB2312"))


def getPathMsgFromFile(file):
    pathMsgFile = changeStrEncode(file, "GB2312")
    pathMsgJson = ""
    if os.path.isfile(pathMsgFile):
        try:
            with codecs.open(pathMsgFile, 'r', 'GB2312') as f:
                pathMsgJson = json.loads(f.read())
        except Exception, e:
            log("getPathMsg fail")
    return pathMsgJson


def __isUidInSectionList(searchUid, l):
    if searchUid.startswith('0x') and searchUid.endswith('FFFFFF'):
        searchUid = searchUid[:-6]
        for i in xrange(len(l)):
            left = l[i][0]
            right = l[i][1]
            if int(right, 16) >= int(searchUid, 16) >= int(left, 16):
                return True
    return False


def getUidSectionList(rawUidList):
    uidList = filter(lambda x: x.startswith("0x") and x.endswith("FFFFFF"),
                     rawUidList)
    if len(uidList) == 0:
        return []
    uidSet = set(uidList)
    uidList = list(uidSet)
    uidList.sort()
    simpleUidList = map(lambda x: x[:-6], uidList)

    gapLeft = [simpleUidList[0]]
    gapRight = []
    for i in xrange(len(simpleUidList) - 1):
        if int(simpleUidList[i + 1], 16) - int(simpleUidList[i], 16) > 10:
            gapLeft.append(simpleUidList[i + 1])
            gapRight.append(simpleUidList[i])
    gapRight.append(simpleUidList[-1])

    assert len(gapLeft) == len(gapRight)
    uidSection = []
    for i in xrange(len(gapLeft)):
        if int(gapRight[i], 16) - int(gapLeft[i], 16) >= 0:
            uidSection.append([gapLeft[i], gapRight[i]])
        else:
            log("gap elem" + gapRight[i])
    return uidSection


def getFormatTestTime(testTime, isEndDate=False):
    testTime = "".join(map(lambda x: x if x in "0123456789" else '-',
                           testTime))
    timeSplit = testTime.split('-')
    testTime = ""
    for i in timeSplit:
        if len(i) > 0:
            if len(i) == 1:
                i = '0' + i
            testTime += i + '-'
    testTime = testTime[:-1]
    if isEndDate:
        while len(testTime) < 19:  #len("0000-00-00-00-00-00")
            testTime += '-99'
    else:
        while len(testTime) < 19:  #len("0000-00-00-00-00-00")
            testTime += '-00'

    return testTime


def __isTimeInSection(searchTime, saveTimeBeg, saveTimeEnd):
    if saveTimeBeg <= searchTime <= saveTimeEnd:
        return True
    return False


def isTimeIncludeSection(searchTimeBeg, searchTimeEnd, saveTimeBeg,
                         saveTimeEnd):
    retBool = False
    if searchTimeBeg > searchTimeEnd or saveTimeBeg > saveTimeEnd:
        raiseError(19, u"起始时间比结束时间晚")
    if saveTimeBeg <= searchTimeBeg <= saveTimeEnd or saveTimeBeg <= searchTimeEnd <= saveTimeEnd:
        retBool = True
    if searchTimeBeg <= saveTimeBeg <= searchTimeEnd <= saveTimeEnd:
        retBool = True
    return retBool


def getTimeSection(rawTimeList):
    rawTimeList = filter(lambda x: len(x) > 5, rawTimeList)
    rawTimeList = map(lambda x: getFormatTestTime(x), rawTimeList)
    return min(rawTimeList), max(rawTimeList)


def findUidAtPath(searchUid, file):
    ret = ""
    try:
        msg = getPathMsgFromFile(file)
        uidSectionTable = msg['uidSectionTable']
        if __isUidInSectionList(searchUid, uidSectionTable):
            ret = msg['folderFileName']
    except:
        pass
    return ret


def findTimeAtPath(searchTime, file):
    ret = ""
    try:
        searchTime = getFormatTestTime(searchTime)
        msg = getPathMsgFromFile(file)
        timeBeg = msg['timeBeg']
        timeEnd = msg['timeEnd']
        if __isTimeInSection(searchTime, timeBeg, timeEnd):
            ret = msg['folderFileName']
    except:
        pass
    return ret


def findTimeBetweenPath(searchTimeBeg, searchTimeEnd, file):
    ret = ""
    try:
        searchTimeBeg, searchTimeEnd = getFormatTestTime(
            searchTimeBeg), getFormatTestTime(searchTimeEnd, True)
        msg = getPathMsgFromFile(file)
        timeBeg = msg['timeBeg']
        timeEnd = msg['timeEnd']
        if isTimeIncludeSection(searchTimeBeg, searchTimeEnd, timeBeg,
                                timeEnd):
            ret = msg['folderFileName']
    except:
        pass
    return ret
