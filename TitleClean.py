#!/bin/env python
#encoding=utf-8
#anthor: yikang.liao@shenma-inc.com
''' This file is used to remove noisy text in the title field of app_db_dump '''


import os,sys
import re
curPath = os.path.abspath(os.path.split(os.path.realpath(__file__))[0])
sys.path.append(curPath + "/../common/")
sys.path.append(curPath + "/../filter/")
from StringTool import StringTool
import string
import xml.dom.minidom
import sys
from collections import defaultdict
reload(sys)
sys.setdefaultencoding('UTF8')

class TitleClean():

    suffixList = []
    pObjectList = []
    char2strip = "1234 " + ''.join(set(string.punctuation))

    def __init__(self):
        print "the codec of the string must be utf-8"
        self._prepare_pObject()
        self._prepare_suffix()
    
    def _prepare_suffix(self):
        global curPath
        doc = xml.dom.minidom.parse(curPath +  '/data/suffixWord.xml')
        root = doc.documentElement
        nodeList = root.getElementsByTagName('suffix')

        for node in nodeList:
            nodeValue = str(node.childNodes[0].nodeValue)
            self.suffixList = self.suffixList + nodeValue.split('|')

    def _prepare_pObject(self):
        patternList = [r"\(.*\)", r"-.*", r"（.*）", r"\[.*\]", r"【.*】",r"（.*）",r"【.*】", r"\(.*", r"（.*", r"（.*", r"[ -!&].*版"]
        for pattern in patternList:
            p = re.compile(pattern)
            self.pObjectList.append(p)


    def patternMatch(self,title):
        for idx, p in enumerate(self.pObjectList):
            title = p.sub('',title)

        return title

    def removeSuffix(self,title):

        for s in self.suffixList:
            title  = title.replace(s, '')

        return title

    def stripDigit_Punc(self,title):
        if not title.isdigit():
            title = title.strip().strip(self.char2strip)
        return title

    def clean(self,title):
       
        title = StringTool.normalizedStr(title)
        title = self.patternMatch(title)
        title = self.removeSuffix(title)
        title = self.stripDigit_Punc(title) 
        return title

if __name__ == '__main__':
    
    c = TitleClean()
    test_list = ['割绳子','捕鱼达人3','捕鱼达人（高清版）怎么下载' ,'捕鱼达人（高清版）','捕鱼达人中文版','捕鱼达人--中文版','捕鱼达人!','捕鱼达人！']
    for title in test_list:
        print title + " -> " + c.clean(title)

