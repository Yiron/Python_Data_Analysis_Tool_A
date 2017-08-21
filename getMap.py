# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw, ImageFont
import globalVar
from base_function import *
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
from mpl_toolkits.mplot3d.art3d import Line3DCollection

font = ImageFont.truetype("wqy.ttc", 20)

colorBinLimit = 16

binMsgList = [
    # ("BIN0",(20,20,20)),
    ("PASS", (0, 255, 0)),
    ("BIN2", (255, 0, 0)),
    ("BIN3", (255, 255, 0)),
    ("BIN4", (0, 0, 255)),
    ("BIN5", (255, 0, 255)),
    ("BIN6", (255, 143, 31)),
    ("BIN7", (0, 255, 255)),
    ("BIN8", (132, 66, 0)),
    ("BIN9", (170, 170, 170)),
    ("BIN10", (153, 204, 255)),
    ("BIN11", (102, 102, 51)),
    ("BIN12", (153, 204, 51)),
    ("BIN13", (174, 0, 174)),
    ("BIN14", (0, 75, 151)),
    ("BIN15", (255, 204, 255)),
    ("BIN16", (187, 255, 187)),
    ("BIN>=17", (213, 213, 37)),
    ("Skip Chip", (255, 255, 255)),
    ("Ugly Edge Chip", (0, 0, 0)),
    # ("#Poor Package",(255,218,185))
]

# countMsgList = [
#     # ("BIN0",(20,20,20)),
#     ("1 time", (0, 255, 0)),
#     ("2 times", (255, 0, 0)),
#     ("3 times", (255, 255, 0)),
#     ("4 times", (0, 0, 255)),
#     ("5 times", (255, 0, 255)),
#     ("6 times", (255, 143, 31)),
#     ("7 times", (0, 255, 255)),
#     ("8 times", (132, 66, 0)),
#     ("9 times", (170, 170, 170)),
#     ("10 times", (153, 204, 255)),
#     ("11 times", (102, 102, 51)),
#     ("12 times", (153, 204, 51)),
#     ("13 times", (174, 0, 174)),
#     ("14 times", (0, 75, 151)),
#     ("15 times", (255, 204, 255)),
#     ("16 times", (187, 255, 187)),
#     (">=17times", (213, 213, 37)),
#     ("Skip Chip", (255, 255, 255)),
#     ("Ugly Edge Chip", (0, 0, 0)),
#     # ("#Poor Package",(255,218,185))
# ]


def getColor(binNum):
    if binNum < 1:
        return (100, 100, 100)
    elif binNum <= colorBinLimit:
        return binMsgList[binNum - 1][1]
    elif binNum == int(globalVar.PASS_BIN):
        return binMsgList[0][1]
    else: 
        return binMsgList[colorBinLimit][1]


def newImg(w, h):
    img = Image.new("RGB", (w, h), color=(120, 150, 170))
    draw = ImageDraw.Draw(img)
    return [img, draw]


def drawFont(offsetX, offsetY, txt, imgDraw):
    # draw.ink = 0 + 255*256 + 0*255*256
    imgDraw[1].text((offsetX, offsetY), txt, font=font, fill=(0, 75, 151))
    return imgDraw


def drawExampleIcon(offsetX, offsetY, textColorList, imgDraw):
    xPosSave = []
    recW = 15
    recH = 25

    for i in range(colorBinLimit):
        baseX = i % 4 * 130 + offsetX
        baseY = i / 4 * recH + offsetY
        # fontSize = font.getsize(font) - font.getoffset()
        text = textColorList[i][0]
        if len(text) < 5: text += (5 - len(text)) * "  "
        fontX = font.getsize(text)[0] - font.getoffset(text)[0]
        imgDraw[1].text((baseX, baseY + 2), text, font=font)
        imgDraw[1].rectangle(
            ((baseX + fontX + 5, baseY),
             (baseX + fontX + recW + 5, baseY + recH)),
            fill=textColorList[i][1])
        if i == 1 or i == 3:
            xPosSave.append(baseX + fontX + 5)

    for i in range(colorBinLimit, len(textColorList)):
        baseX = (i - colorBinLimit) % 2 * 260 + offsetX
        baseY = (i - colorBinLimit) / 2 * recH + 100 + offsetY
        text = textColorList[i][0]
        fontX = font.getsize(text)[0] - font.getoffset(text)[0]
        imgDraw[1].text((baseX, baseY + 2), text, font=font)
        imgDraw[1].rectangle(
            ((xPosSave[i % 2] + 1, baseY),
             (xPosSave[i % 2] + recW + 1, baseY + recH)),
            fill=textColorList[i][1])

    return imgDraw


def drawIconAndText(x, y, binRec_W_H, context2D, imgDraw, isDrawBin):
    binRec_W_H = int(binRec_W_H)
    f = ImageFont.truetype("wqy.ttc", int(binRec_W_H / 1.3))
    valList = map(lambda x: int(x[2]),context2D)
    valLen =max(map(lambda x:len(str(x)), valList))
    if valLen < 2: valLen = 2
    minVal = min(valList)
    maxVal = max(valList)
    if minVal == maxVal:
        minVal = 0
        maxVal = 1
    for i in context2D:
        xDraw = int(i[0] * int(binRec_W_H*valLen/2) + x)
        yDraw = int(i[1] * binRec_W_H + y)
        val = int(i[2])

        colorDraw = 0
        if isDrawBin:
            colorDraw = getColor(val)
        else:
            colorDraw = int(float(val-minVal) / (maxVal-minVal) * 256)
            if colorDraw > 255:
                colorDraw = 255
            if colorDraw < 1:
                colorDraw = 1
            colorDraw = (colorDraw,65,65)

        imgDraw[1].rectangle(
            ((xDraw + 3, yDraw + 3),
             (xDraw + int(binRec_W_H*valLen/2) - 3, yDraw + binRec_W_H - 3)),
            fill=colorDraw)
        if val != int(globalVar.PASS_BIN) or not isDrawBin:
            text = str(val)
            if len(text) == 1: text = " " + text + " "
            imgDraw[1].text(
                (xDraw + 3, yDraw + 3),
                text,
                fill=(0, 0, 0),
                font=f)
    return imgDraw


def savePic(fname, imgDraw):
    imgDraw[0].save(fname)
    return imgDraw


def drawMapPic(strip, context2D):
    mapName = '.'.join(strip.file.split('.')[:-1]) + "_map.jpg"
    try:
        xList = map(lambda x: x[0], context2D)
        yList = map(lambda x: x[1], context2D)
        xLen = len(set(xList))
        yLen = len(set(yList))
        xMin = min(xList)
        yMin = min(yList)
        for i in range(len(context2D)):
            context2D[i][0] -= xMin
            context2D[i][1] -= yMin

        textList = [u"型号：", u"文件名：", u"总数：", u"不测：", u"FAIL：", u"良率：",
                    u"说明：本MAP由DC数据生成，仅供参考！"]
        textAns = [
            globalVar.IC_TYPE, changeStrDecode(
                str(strip.file).split('/')[-1],
                "gbk"), str(globalVar.CHIP_NUM),
            str(globalVar.CHIP_NUM - strip.usefulChipNum), str(strip.failNum),
            str(100 *
                (1 - float(strip.failNum) / strip.usefulChipNum))[:5] + '%',
            ""
        ]
        text = ""
        for i in range(len(textList)):
            text += textList[i] + textAns[i] + "\n"
        titleW = 1100
        titleH = 400
        binRec_W_H = 70 - max(xLen, yLen)
        if binRec_W_H < 25:
            binRec_W_H = 25

        w = binRec_W_H * xLen * 1.1
        if w < titleW: w = titleW
        h = titleH + binRec_W_H * yLen * 1.1

        imgDraw = drawExampleIcon(600, 5, binMsgList,
                                  drawFont(5, 5, text, newImg(
                                      int(w) + 50, int(h) + 50)))
            
        imgDraw = drawIconAndText(
            (w - binRec_W_H * xLen) / 2, titleH, binRec_W_H, context2D,
            imgDraw, True)
        savePic(mapName, imgDraw)
    except:
        warning("mapFail:" + mapName)


def drawOverlayMapPic(strip, stripNum, binSelect, context2D ,rootPath):
    mapName = rootPath + "/OverlayMAP.jpg"
    log(mapName)
    try:
        xList = map(lambda x: x[0], context2D)
        yList = map(lambda x: x[1], context2D)
        xLen = len(set(xList))
        yLen = len(set(yList))
        xMin = min(xList)
        yMin = min(yList)
        valList = map(lambda x: int(x[2]),context2D)
        valLen =max(map(lambda x:len(str(x)), valList))
        if valLen < 2: valLen = 2
        for i in range(len(context2D)):
            context2D[i][0] -= xMin
            context2D[i][1] -= yMin

        textList = [u"型号：", u"目录名：", u"文件数：", u"叠加BIN筛选规则：",
                    u"说明：本MAP由DC数据生成，仅供参考！"]
        textAns = [
            globalVar.IC_TYPE,
            changeStrDecode('/'.join(str(strip.file).split('/')[:-1]), "gbk"),
            str(stripNum), binSelect, ""
        ]
        text = ""
        for i in range(len(textList)):
            text += textList[i] + textAns[i] + "\n"

        titleW = 1100
        titleH = 400
        binRec_W_H = 70 - max(xLen, yLen)
        if binRec_W_H < 25:
            binRec_W_H = 25

        w = binRec_W_H * xLen * 1.1 * valLen / 2
        if w < titleW: w = titleW
        h = titleH + binRec_W_H * yLen * 1.1

        imgDraw = drawFont(5, 5, text, newImg(
                                        int(w) + 50, int(h) + 50))
        imgDraw = drawIconAndText(
            (w - binRec_W_H * xLen* valLen / 2) / 2, titleH, binRec_W_H, context2D,
            imgDraw, False)
        savePic(mapName, imgDraw)
    except:
        warning("mapFail:" + mapName)


def getRectangleData(x, y, z, dx=1, dy=1, dz=1):
    verts = [(x, y, z), (x, y + dy, z), (x + dx, y + dy, z), (x + dx, y, z),
             (x, y, z + dz), (x, y + dy, z + dz), (x + dx, y + dy, z + dz),
             (x + dx, y, z + dz)]
    faces = [
        [0, 1, 2, 3], [4, 5, 6, 7], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6],
        [0, 3, 7, 4]
    ]

    # 获得每个面的顶点
    poly3d = [[verts[vert_id] for vert_id in face] for face in faces]
    return poly3d, verts


def drawDcVal3D(dcName, coordValList):
    try:
        plt.style.use("ggplot")
        fig = plt.figure()
        ax = fig.gca(projection='3d')
        xSet, ySet = set(), set()
        # 正文体顶点和面
        valList = []
        coordValList.sort(key=lambda x: x[1])
        coordValList.sort(key=lambda x: x[0])
        for i in coordValList:
            print "x", i[0], "  y", i[1], "  val", i[2]
            xSet.add(i[0])
            ySet.add(i[1])
            valList.append(i[2])

        valMin, valMax = min(valList), max(valList)
        yWid = len(ySet) / len(xSet)
        if yWid < 0.2: yWid = 0.2
        if yWid > 1: yWid = 1

        poly3dAll = []
        # colorAll = []
        for i in coordValList:
            poly3d, verts = getRectangleData(i[0], i[1], 0, 1, yWid, i[2])
            poly3dAll.extend(poly3d)
            # # 绘制顶点
            x, y, z = zip(*verts)
            ax.scatter(x, y, z, alpha=0.0)
            # 绘制多边形面
            color = 0.5
            if valMax - valMin != 0:
                color = 1 - (i[2] - valMin) / (valMax - valMin)
                if color > 1: color = 1
                if color < 0: color = 0
            # colorAll.append([0.2, 0.5 - 0.5*color, color, 1])
            # ax.add_collection3d(Line3DCollection(poly3d, colors='k', linewidths=0.5, linestyles=':'))
            ax.add_collection3d(Poly3DCollection(poly3d,
                                                 facecolor=[[0.2, 0.5 - color /
                                                             2, color, 1]],
                                                 linewidths=0.5))
        # ax.add_collection3d(Poly3DCollection(poly3dAll,
        #                                     facecolor=[[0.2,0.45,0.08,1]],
        #                                     linewidths=0.5))

        xmajorLocator = MultipleLocator(1)  #将x主刻度标签设置为1的倍数
        xmajorFormatter = FormatStrFormatter('%d')  #设置x轴标签文本的格式
        xminorLocator = MultipleLocator(1)  #将x轴次刻度标签设置为1的倍数
        ymajorLocator = MultipleLocator(1)  #将y轴主刻度标签设置为1的倍数
        ymajorFormatter = FormatStrFormatter('%d')  #设置y轴标签文本的格式
        yminorLocator = MultipleLocator(1)  #将此y轴次刻度标签设置为1的倍数

        #设置主刻度标签的位置,标签文本的格式
        ax.xaxis.set_major_locator(xmajorLocator)
        ax.xaxis.set_major_formatter(xmajorFormatter)
        ax.yaxis.set_major_locator(ymajorLocator)
        ax.yaxis.set_major_formatter(ymajorFormatter)
        #显示次刻度标签的位置,没有标签文本
        ax.xaxis.set_minor_locator(xminorLocator)
        ax.yaxis.set_minor_locator(yminorLocator)

        ax.set_xlim(min(xSet), max(xSet))
        ax.set_ylim(min(ySet), max(ySet))
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel(dcName.replace('/', '_'))
        valMinStr = str(int(valMin)) + '.' + str(int((valMin - int(valMin)) *
                                                     100))
        valMaxStr = str(int(valMax)) + '.' + str(int((valMax - int(valMax)) *
                                                     100))
        plt.title(dcName.replace('/', '_') + '=>>[' + valMinStr + '~' +
                  valMaxStr + ']')
        plt.show()
    except:
        warning("dc map fail!")

