# -*- coding: utf-8 -*-
# 用户输入或配置部分全大写加下划线，固定匹配的变量也可以这么命名，但需要将相应变量靠拢
# 文件或图片相关的列表用首字母大写
# 关键字用首字母大写
# 其余均用小写，用大写字母分割
import templite

htmlMsg = {'folderName': u"中文测试".encode('gb2312'),
           'name': u"中文测试".encode('gb2312'),
           'exportTime': "exportTime",
           'stripNum': -1,
           'icNum': -1,
           'icNumofStrip': -1,
           'finalYieldRate': -1,
           'firstYieldRate': -1,
           'strips': [],
           'diffFileRepeatUid': [],
           'ignoreBin': [],
           'tops': [],
           'sites': [],
           'siteRateSub': "%", }


def htmlViewSave(name):
    htmlFile = open("template.html")
    t = templite.Templite(htmlFile.read())
    htmlFile.close()
    text = t.render(htmlMsg)

    outputHtml = open(name, mode='w+')
    outputHtml.write(text)
    outputHtml.close()


def htmlAllViewSave(name):
    htmlFile = open("combineTemplate.html")
    t = templite.Templite(htmlFile.read())
    htmlFile.close()
    text = t.render(htmlMsg)

    outputHtml = open(name, mode='w+')
    outputHtml.write(text)
    outputHtml.close()
