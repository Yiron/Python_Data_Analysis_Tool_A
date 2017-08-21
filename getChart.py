# -*- coding: utf-8 -*-
import numpy as np
import os
import pandas
from matplotlib.font_manager import FontProperties
import matplotlib.pyplot as plt
import globalVar
import StringIO
import thread
from base_function import *


def initPlt(width, height):
    plt.figure(figsize=(width, height))


def closeAll():
    plt.close('all')


def savePlt(name):
    if os.path.isfile(name):
        os.remove(name)
    plt.savefig(name)
    closeAll()


def nameAndTitleSave(dcName, isSite, num1, num2=0):
    s = ""
    if isSite == 0:
        s = "HIST"
    else:
        s = "SITE"
    if globalVar.SELECT_MODE == ANALYSIS_MODE:
        picName = s + '-' + dcName.replace(
            '/',
            '_') + '(' + globalVar.PATH1.split("/")[-1] + "-pass)" + ".png"
        title = dcName.replace(
            '/',
            '_') + '(' + globalVar.PATH1.split("/")[-1] + ":" + str(num1) + ")"
    elif globalVar.SELECT_MODE == COMPARE_MODE:
        picName = s + '-' + dcName.replace(
            '/', '_') + '(' + globalVar.PATH1.split("/")[
                -1] + "," + globalVar.PATH2.split("/")[-1] + "-pass)" + ".png"
        title = dcName.replace(
            '/', '_') + '[Red:' + str(num1) + ',Blue:' + str(num2) + "]"
    title = changeStrDecode(title, "GB2312")
    font = FontProperties(fname=r"wqy.ttc", size=15)
    plt.title(title,
              bbox={'facecolor': '0.8',
                    'pad': 5},
              fontproperties=font,
              loc='left',
              fontsize=15)
    if isSite == 0:
        globalVar.HIST_IMAGES_DC.append(picName)
        globalVar.HIST_STR.append(picName)
    else:
        globalVar.HIST_SITE_DC.append(picName)
        globalVar.SITE_STR.append(picName)
    return picName, title


def getPassFinalCsvAndLength(file):
    finalCsv = pandas.read_csv(file, low_memory=False)
    finalCsv = finalCsv[finalCsv[globalVar.BIN_NAME] == int(
        globalVar.PASS_BIN)]
    lenFinalCsv = len(finalCsv)
    log("pass finalCsv length :" + str(lenFinalCsv))
    if lenFinalCsv == 0:
        raiseError(1, u"文件：" + file + u"，数据只有一行")
    return finalCsv, lenFinalCsv


def getDcDataAndAvg(finalCsv, dcName):
    dcData = finalCsv[dcName]
    oneData = str(list(dcData)[0])
    nextLabel = 0
    if oneData == "":
        return dcData, ""
    for i in oneData:
        if i not in ".-+0123456789":
            return dcData, ""
    log("current dcName " + dcName)
    return dcData, dcData.mean()


def getSitesDataAndNum(finalCsv):
    siteNum = max(list(finalCsv[globalVar.SITE_NAME])) + 1
    log("SITE NUM :" + str(siteNum))
    if siteNum == 0:
        raiseError(2, u"一个Site都没有")
    finalCsv_Site = []
    for i in range(siteNum):
        finalCsv_Site.append(finalCsv[finalCsv[globalVar.SITE_NAME] == i])
        if len(finalCsv_Site) == 0:
            warning("Site " + i + u"未匹配任何数据行")
    return finalCsv_Site, siteNum


def getSiteLabelAndAvg(finalCsv_Site, dcName, siteNum):
    siteLabel = []
    siteAvgNum = []
    for i in range(siteNum):
        data = list(finalCsv_Site[i][dcName])
        siteLabel.append("SITE_" + str(i))
        if len(data) != 0:
            siteAvgNum.append(float(sum(data)) / len(data))
        else:
            siteAvgNum.append(0)
    if siteAvgNum == []:
        raiseError(3, u"无法截取SITE均值")
    log("siteAvgNum" + str(siteAvgNum))
    return siteLabel, siteAvgNum


def sortAmdMatchDCLabel():
    firstDcIndex = globalVar.header.index(globalVar.FIRST_DC_DATA_LABEL)
    retHeader = globalVar.header[firstDcIndex:]
    retHeader.sort()
    return retHeader


def saveHistogramDC():
    globalVar.HIST_IMAGES_DC = []
    globalVar.HIST_STR = []
    globalVar.FINAL_TABLE_FILE_CONTEXT.seek(0)
    finalCsv, lenFinalCsv = getPassFinalCsvAndLength(
        globalVar.FINAL_TABLE_FILE_CONTEXT)
    plt.style.use("ggplot")
    sortedHeader = sortAmdMatchDCLabel()
    for label in sortedHeader:
        try:
            dcName = label.strip()
            dcData, avg1 = getDcDataAndAvg(finalCsv, dcName)
            if avg1 == "":
                continue
            initPlt(9, 9)
            dcData.plot.hist(bins=10, color='red', alpha=0.5)
            picName, title = nameAndTitleSave(dcName, 0, lenFinalCsv)
            savePlt(globalVar.PATH1 + '/' + picName)
        except:
            warning(label + u"  generate fail!")
            closeAll()
    


def saveSiteDC():
    globalVar.HIST_SITE_DC = []
    globalVar.SITE_STR = []
    globalVar.FINAL_TABLE_FILE_CONTEXT.seek(0)
    finalCsv, lenFinalCsv = getPassFinalCsvAndLength(
        globalVar.FINAL_TABLE_FILE_CONTEXT)
    finalCsv_Site, siteNum = getSitesDataAndNum(finalCsv)
    plt.style.use("ggplot")
    sortedHeader = sortAmdMatchDCLabel()
    for label in sortedHeader:
        dcName = label.strip()
        try:
            log("current dcName " + dcName)
            xLabel, avgNum = getSiteLabelAndAvg(finalCsv_Site, dcName, siteNum)
            idx = np.arange(len(xLabel))
            width = 0.5
            if siteNum < 10:
                initPlt(9, 9)
            else:
                initPlt(int((siteNum -10)*0.85), 9)

            plt.bar(idx,
                    avgNum,
                    width,
                    color='red',
                    label=u'average',
                    alpha=0.5)
            font = FontProperties(fname=r"wqy.ttc", size=15)
            plt.xlabel(u'各Site良品均值', fontproperties=font)
            plt.ylabel(u'数值分布', fontproperties=font)
            plt.xticks(idx + width / 2, xLabel, rotation=40)

            picName, title = nameAndTitleSave(dcName, 1, lenFinalCsv)
            savePlt(globalVar.PATH1 + '/' + picName)
        except:
            warning(label + u"  generate fail!")
            closeAll()
    


def saveCmpHistogramDC():
    globalVar.HIST_IMAGES_DC = []
    globalVar.HIST_STR = []
    finalCsv1, lenFinalCsv1 = getPassFinalCsvAndLength(
        globalVar.FINAL_TABLE_FILE1)
    finalCsv2, lenFinalCsv2 = getPassFinalCsvAndLength(
        globalVar.FINAL_TABLE_FILE2)
    plt.style.use("ggplot")
    sortedHeader = sortAmdMatchDCLabel()
    for label in sortedHeader:
        dcName = label.strip()
        try:
            dcData1, avg1 = getDcDataAndAvg(finalCsv1, dcName)
            dcData2, avg2 = getDcDataAndAvg(finalCsv2, dcName)
            dcData3 = pandas.read_csv(StringIO.StringIO("a\n-99999999999"))[
                'a']
            if avg1 == "" or avg2 == "":
                continue
            _min = min(list(dcData1) + list(dcData2))
            _max = max(list(dcData1) + list(dcData2))

            initPlt(9, 9)

            dcData1.plot.hist(bins=20,
                              color='red',
                              alpha=0.5,
                              range=(_min, _max),
                              label=changeStrEncode(
                                  changeStrDecode(
                                      globalVar.PATH1.split('/')[
                                          -1], "GB2312"), "unicode"),
                              normed=True)
            dcData2.plot.hist(bins=20,
                              color='blue',
                              alpha=0.5,
                              label=changeStrEncode(
                                  changeStrDecode(
                                      globalVar.PATH2.split('/')[
                                          -1], "GB2312"), "unicode"),
                              range=(_min, _max),
                              normed=True)
            dcData3.plot.hist(
                bins=20,
                color='#800080',
                alpha=1,
                range=(_min, _max),
                label=changeStrEncode(
                    changeStrDecode(u"重合区域", "GB2312"), "unicode"),
                normed=True)

            picName, title = nameAndTitleSave(dcName, 0, lenFinalCsv1,
                                              lenFinalCsv2)

            # if avg1 > 0:
            #     plt.legend(bbox_to_anchor=(1, 0.1128), prop=font)
            # else:
            font = FontProperties(fname=r"wqy.ttc", size=15)
            plt.legend(bbox_to_anchor=(1, 1.14), prop=font)
            savePlt(globalVar.COMPARE_PATH + '/' + picName)
        except:
            warning(label + u"  generate fail!")
            closeAll()
    

def saveCmpSiteDC():
    globalVar.HIST_SITE_DC = []
    globalVar.SITE_STR = []
    finalCsv1, lenFinalCsv1 = getPassFinalCsvAndLength(
        globalVar.FINAL_TABLE_FILE1)
    finalCsv2, lenFinalCsv2 = getPassFinalCsvAndLength(
        globalVar.FINAL_TABLE_FILE2)
    finalCsv_Site1, siteNum1 = getSitesDataAndNum(finalCsv1)
    finalCsv_Site2, siteNum2 = getSitesDataAndNum(finalCsv2)

    siteNum = max(siteNum1, siteNum2)
    log("SITE NUM :" + str(siteNum))

    plt.style.use("ggplot")
    sortedHeader = sortAmdMatchDCLabel()
    for label in sortedHeader:
        dcName = label.strip()
        try:
            log("current dcName " + dcName)
            xLabel1, avgNum1 = getSiteLabelAndAvg(finalCsv_Site1, dcName,
                                                  siteNum1)
            xLabel2, avgNum2 = getSiteLabelAndAvg(finalCsv_Site2, dcName,
                                                  siteNum2)
            while len(avgNum1) < len(avgNum2):
                avgNum1.append(0)
            while len(avgNum1) > len(avgNum2):
                avgNum2.append(0)

            xLable = xLabel1 if siteNum1 > siteNum2 else xLabel2
            idx = np.arange(len(xLable))

            width = 0.4
            if siteNum < 10:
                initPlt(9, 9)
            else:
                initPlt(int((siteNum -10)*0.85), 9)

            plt.bar(idx + 0.1,
                    avgNum1,
                    width,
                    color='red',
                    label=changeStrEncode(
                        changeStrDecode(
                            globalVar.PATH1.split('/')[
                                -1], "GB2312"), "unicode"),
                    alpha=0.4)
            plt.bar(idx + 0.5,
                    avgNum2,
                    width,
                    color='blue',
                    label=changeStrEncode(
                        changeStrDecode(
                            globalVar.PATH2.split('/')[
                                -1], "GB2312"), "unicode"),
                    alpha=0.5)
            font = FontProperties(fname=r"wqy.ttc", size=15)
            plt.xlabel(u'各Site良品均值', fontproperties=font)
            plt.ylabel(u'数值分布', fontproperties=font)
            plt.xticks(idx + width, xLable, rotation=40)
            # if avgNum1[0] > 0:
            #     plt.legend(bbox_to_anchor=(1, 0.1128), prop=font)
            # else:
            plt.legend(bbox_to_anchor=(1, 1.13), prop=font)

            picName, title = nameAndTitleSave(dcName, 1, lenFinalCsv1,
                                              lenFinalCsv2)
            savePlt(globalVar.COMPARE_PATH + '/' + picName)
        except:
            warning(label + u"  generate fail!")
            closeAll()
    