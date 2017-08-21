# -*- coding: utf-8 -*-
# 用户输入或配置部分全大写加下划线，固定匹配的变量也可以这么命名，但需要将相应变量靠拢
# 文件或图片相关的列表用首字母大写，或Log句柄用首字母大写
# 关键字用首字母大写
# 其余均用小写，用大写字母分割

SkipWord = "_SKIP_"
SkipList = []
TopFailSummy = None
TotalSummy = None
SiteSummy = None

ChangePathList = []


IGNORE_ERROR = ()
NEED_LOG = False
CHIP_NUM = 0
KEY_WORD = ""
IC_TYPE = ""
WORNG_BIN_LIST = ""
PATH1 = ""
PATH2 = ""
MAX_RETEST_TIME = 0
X_COORD_NAME = ""
X_ROW_INDEX = -1
UID_NAME = ""
UID_ROW_INDEX = -1
BIN_NAME = ""
BIN_ROW_INDEX = -1
TEST_TIME = ""
TIME_ROW_INDEX = -1
SITE_NAME = ""
SITE_ROW_INDEX = -1
FIRST_TABLE_FILE_CONTEXT = ""
FINAL_TABLE_FILE_CONTEXT = ""
FINAL_TABLE_FILE1 = ""
FINAL_TABLE_FILE2 = ""
PASS_BIN = 0
FIRST_DC_DATA_LABEL = 0
FIRST_DC_ROW_INDEX = -1
TOP_N = 0
COMPARE_PATH = 0
HTML_SAVE_PATH = 0
SELECT_MODE = None
IGNORE_BIN = []

header = ""

binNumDict = {}
totalFailNum = 0
workedLineNum = 0

firstFail = 0
finalFail = 0
binToTestItem = {}

#暂无用
HIST_IMAGES_DC = []
HIST_SITE_DC = []
HIST_STR = []
SITE_STR = []
