# -*- coding: utf-8 -*-
import os
import pandas as pd
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import globalVar
import htmlMaker
import json
import codecs
import pathMsgMaker
import time
import StringIO
from base_function import *


class topMsg:
    bin = -1
    name = ""
    firstNum = -1
    num = -1
    rate = -1
    rateOfFail = '%'


class siteMsg:
    name = ""
    subFinalFirstNum = -1
    num = -1
    firstRate = "%"
    finalRate = "%"
    subRate = "%"


def messageInit():

    if globalVar.SELECT_MODE == ANALYSIS_MODE:
        with codecs.open(globalVar.WORNG_BIN_LIST, 'r', 'GB2312') as f:
            globalVar.binToTestItem = json.loads(f.read())
        globalVar.FINAL_TABLE_FILE_CONTEXT.seek(0)
        globalVar.header = globalVar.FINAL_TABLE_FILE_CONTEXT.readline().split(
            ',')

    elif globalVar.SELECT_MODE == COMPARE_MODE:
        globalVar.FINAL_TABLE_FILE1 = globalVar.PATH1 + "/_FINAL_" + globalVar.PATH1.split(
            "/")[-1] + ".csv"
        globalVar.FINAL_TABLE_FILE2 = globalVar.PATH2 + "/_FINAL_" + globalVar.PATH2.split(
            "/")[-1] + ".csv"
        header1 = header2 = ""
        with open(globalVar.FINAL_TABLE_FILE1) as f:
            header1 = f.readline().split(',')
        with open(globalVar.FINAL_TABLE_FILE2) as f:
            header2 = f.readline().split(',')
        globalVar.header = filter(lambda x: x in header1, header2)
        warning("some dc data, only in " + globalVar.PATH1.split("/")[-1] + ":"
                + str(filter(lambda x: x not in globalVar.header, header1)))
        warning("some dc data, only in " + globalVar.PATH2.split("/")[-1] + ":"
                + str(filter(lambda x: x not in globalVar.header, header2)))


def addTotalLogMsg():
    if globalVar.TotalSummy != None:
        globalVar.TotalSummy.addSummyLog(
            globalVar.PATH1.split("/")[-1] + ',' + changeStrEncode(
                htmlMaker.htmlMsg['icType'], "GB2312") + ',' +
            str(htmlMaker.htmlMsg['stripNum']) + ',' + str(htmlMaker.htmlMsg[
                'icNumofStrip']) + ',' + str(htmlMaker.htmlMsg['icNum']) + ','
            + str(htmlMaker.htmlMsg['firstYieldRate']) + ',' + str(
                htmlMaker.htmlMsg['finalYieldRate']) + ',' + str(
                    htmlMaker.htmlMsg['siteRateSub']) + ',')
        # changeStrEncode("目录,型号,扫描基板数,单片芯片数,芯片总数,首测不良率,复测不良率，各SITE良率差"),"GB2312")


def addFailSortLogMsg(top_num, firstDataFrame):
    tops_msg = []
    for i in xrange(top_num):
        curr_top_msg = topMsg()
        if globalVar.binToTestItem.has_key(globalVar.binNumDict[i][0]):
            curr_top_msg.name = globalVar.binToTestItem[globalVar.binNumDict[
                i][0]].encode('GB2312')
        curr_top_msg.bin = globalVar.binNumDict[i][0]
        curr_top_msg.firstNum = len(firstDataFrame[firstDataFrame[
            globalVar.BIN_NAME] == int(globalVar.binNumDict[i][0])])
        curr_top_msg.num = globalVar.binNumDict[i][1]
        curr_top_msg.rate = str(100 * float(curr_top_msg.num) /
                                globalVar.workedLineNum)[:5] + '%'
        curr_top_msg.rateOfFail = str(100 * float(curr_top_msg.num) /
                                      globalVar.totalFailNum)[:5] + '%'
        tops_msg.append(curr_top_msg)
        #changeStrEncode("目录,型号,总数,BIN,BIN含义,首测不良,复测不良,最终不良率"),"GB2312")
        if globalVar.TopFailSummy != None:
            globalVar.TopFailSummy.addSummyLog(
                globalVar.PATH1.split("/")[
                    -1] + ',' + changeStrEncode(globalVar.IC_TYPE, "GB2312") +
                ',' + str(globalVar.workedLineNum) + ',' + str(
                    curr_top_msg.bin) + ',' + curr_top_msg.name + ',' + str(
                        curr_top_msg.firstNum) + ',' + str(
                            curr_top_msg.num) + ',' + curr_top_msg.rate)

    return tops_msg


def addSiteLogMsg(sites_msg, tops_msg, siteNum, finalDataFrame, firstDataFrame,
                  finalPassCsv, firstPassCsv):
    maxRate = -1
    minRate = 100
    siteRateSub = 0
    for i in range(siteNum):
        cur_site_msg = siteMsg()
        cur_site_msg.name = "SITE_" + str(i)
        cur_site_first_num = len(firstDataFrame[firstDataFrame[
            globalVar.SITE_NAME] == i])
        cur_site_msg.num = len(finalDataFrame[finalDataFrame[
            globalVar.SITE_NAME] == i])
        cur_site_msg.subFinalFirstNum = cur_site_msg.num - cur_site_first_num

        finalSitePassNum = len(finalPassCsv[finalPassCsv[globalVar.SITE_NAME]
                                            == i])
        firstSitePassNum = len(firstPassCsv[firstPassCsv[globalVar.SITE_NAME]
                                            == i])
        if cur_site_msg.num == 0 or cur_site_first_num == 0:
            cur_site_msg.firstRate = '?'
            cur_site_msg.finalRate = '?'
            cur_site_msg.subRate = '?'
        else: 
            cur_site_msg.firstRate = str(100 * float(firstSitePassNum) /
                                         cur_site_first_num)[:5] + '%'
            cur_site_msg.finalRate = str(100 * float(finalSitePassNum) /
                                         cur_site_msg.num)[:5] + '%'
            cur_site_msg.subRate = str(
                100 * float(finalSitePassNum - firstSitePassNum) /
                cur_site_msg.num)[:5] + '%'
        sites_msg.append(cur_site_msg)

        if cur_site_msg.num == 0:
            siteRateSub = '?'
        else:
            if maxRate < float(finalSitePassNum) / cur_site_msg.num:
                maxRate = float(finalSitePassNum) / cur_site_msg.num
            if minRate > float(finalSitePassNum) / cur_site_msg.num:
                minRate = float(finalSitePassNum) / cur_site_msg.num
            siteRateSub = maxRate - minRate
            # changeStrEncode("目录,型号,SITE,终测芯片数目,首测良率,最终良率, 首测、终测良率差"),"GB2312")
        if globalVar.SiteSummy != None:
            globalVar.SiteSummy.addSummyLog(
                globalVar.PATH1.split("/")[
                    -1] + ',' + changeStrEncode(globalVar.IC_TYPE, "GB2312") +
                ',' + str(cur_site_msg.name) + ',' + str(cur_site_msg.num) +
                ',' + str(cur_site_msg.firstRate) + ',' + str(
                    cur_site_msg.finalRate) + ',' + str(cur_site_msg.subRate))

    htmlMaker.htmlMsg['tops'] = tops_msg[:]
    htmlMaker.htmlMsg['sites'] = sites_msg[:]
    htmlMaker.htmlMsg['siteRateSub'] = str(100 * (siteRateSub))[:5] + '%'


def addPathMsg(finalDataFrame):
    pathMsgMaker.pathMsg['folderFileName'] = changeStrEncode(
        changeStrDecode(globalVar.PATH1, "GB2312"), "ascii")
    pathMsgMaker.pathMsg['pathMd5'] = getPathMd5(globalVar.PATH1)

    pathMsgMaker.pathMsg['uidSectionTable'] = []
    if globalVar.UID_NAME != "":
        pathMsgMaker.pathMsg[
            'uidSectionTable'] = pathMsgMaker.getUidSectionList(finalDataFrame[
                globalVar.UID_NAME])
    timeList = finalDataFrame.iloc[:, globalVar.TIME_ROW_INDEX]
    pathMsgMaker.pathMsg['timeBeg'], pathMsgMaker.pathMsg[
        'timeEnd'] = pathMsgMaker.getTimeSection(timeList)
    pathMsgMaker.pathMsg['headerListMd5'] = getHeaderMd5()


def addHtmlAndLogAndPathMsg():

    globalVar.FINAL_TABLE_FILE_CONTEXT.seek(0)
    globalVar.FIRST_TABLE_FILE_CONTEXT.seek(0)
    finalDataFrame = pd.read_csv(globalVar.FINAL_TABLE_FILE_CONTEXT,
                                 low_memory=False)
    firstDataFrame = pd.read_csv(globalVar.FIRST_TABLE_FILE_CONTEXT,
                                 low_memory=False)
    binlist = list(finalDataFrame[globalVar.BIN_NAME])

    globalVar.workedLineNum = len(filter(
        lambda x: x not in globalVar.IGNORE_BIN, binlist))
    # log("all ic num：" + str(globalVar.workedLineNum))
    globalVar.binNumDict = {}

    for i in binlist:
        binStr = str(i)
        if i not in globalVar.IGNORE_BIN and i != globalVar.PASS_BIN:
            if globalVar.binNumDict.has_key(binStr):
                globalVar.binNumDict[binStr] += 1
            else:
                globalVar.binNumDict[binStr] = 1

    globalVar.binNumDict = sorted(globalVar.binNumDict.iteritems(),
                                  key=lambda d: d[1],
                                  reverse=True)
    log("globalVar.binNumDict" + str(globalVar.binNumDict))

    globalVar.totalFailNum = 0
    top_num = min(len(globalVar.binNumDict), globalVar.TOP_N)
    for i in xrange(len(globalVar.binNumDict)):
        globalVar.totalFailNum += globalVar.binNumDict[i][1]

    tops_msg = addFailSortLogMsg(top_num, firstDataFrame)

    sites_msg = []
    finalPassCsv = finalDataFrame[finalDataFrame[globalVar.BIN_NAME] ==
                                  globalVar.PASS_BIN]
    firstPassCsv = firstDataFrame[firstDataFrame[globalVar.BIN_NAME] ==
                                  globalVar.PASS_BIN]
    siteNum = max(list(finalDataFrame[globalVar.SITE_NAME])) + 1
    log("SITE NUM :" + str(siteNum))

    addSiteLogMsg(sites_msg, tops_msg, siteNum, finalDataFrame, firstDataFrame,
                  finalPassCsv, firstPassCsv)
    addTotalLogMsg()

    addPathMsg(finalDataFrame)
