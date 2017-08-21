# -*- coding: utf-8 -*-
from watchdog.observers import Observer
from watchdog.events import *
import time
from base_function import *
import globalVar

# 由于我的程序会改变Dc文件的名称和解压和生成文件，所以不要被这里捕获


class FileEventHandler(FileSystemEventHandler):
    def __init__(self):
        FileSystemEventHandler.__init__(self)

    def on_moved(self, event):
        # if event.is_directory:
        #     log("directory moved from {0} to {1}".format(event.src_path,
        #                                                    event.dest_path))
        # else:
        #     log("file moved from {0} to {1}".format(event.src_path,
        #                                               event.dest_path))
        globalVar.ChangePathList.append(unifyPath(event.dest_path))
        print "on_moved", changeStrEncode(event.dest_path, "GB2312")

    def on_created(self, event):
        # if event.is_directory:
        #     log("directory created:{0}".format(event.src_path))
        # else:
        #     log("file created:{0}".format(event.src_path))
        globalVar.ChangePathList.append(unifyPath(event.src_path))
        print "on_created", changeStrEncode(event.src_path, "GB2312")

    def on_deleted(self, event):
        # if event.is_directory:
        #     log("directory deleted:{0}".format(event.src_path))
        # else:
        #     log("file deleted:{0}".format(event.src_path))
        globalVar.ChangePathList.append(unifyPath(event.src_path))
        globalVar.ChangePathList.append(unifyPath(event.src_path))
        print "on_deleted", changeStrEncode(event.src_path, "GB2312")

    def on_modified(self, event):
        # if event.is_directory:
        #     log("directory modified:{0}".format(event.src_path))
        # else:
        #     log("file modified:{0}".format(event.src_path))
        globalVar.ChangePathList.append(unifyPath(event.src_path))
        print "on_modified", changeStrEncode(event.src_path, "GB2312")


def watchChangePath(path):
    globalVar.ChangePathList = []
    observer = Observer()
    event_handler = FileEventHandler()
    observer.schedule(event_handler, path, True)
    observer.start()

    # t ry:
    #     while True:
    #         time.sleep(1)
    # except KeyboardInterrupt:
    #     observer.stop()
    # observer.join()


def changingFileOrPath():
    ret = globalVar.ChangePathList[:]
    globalVar.ChangePathList = []
    ret = filter(lambda x: "logger.log" not in x, ret)
    ret = filter(lambda x: "pathMsg" not in x, ret)
    ret = filter(lambda x: ".html" not in x, ret)
    ret = filter(lambda x: "FAIL.csv" not in x, ret)
    ret = filter(lambda x: "SITE_SUMMY.csv" not in x, ret)
    ret = filter(lambda x: "TOTAL_SUMMY.csv" not in x, ret)
    # ret = filter(lambda x: globalVar.KEY_WORD in x, ret) wrong
    ret = map(lambda x: unifyPath(x), ret)

    return ret
