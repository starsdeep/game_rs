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
import xml.dom.minidom
import sys
from collections import defaultdict
reload(sys)
sys.setdefaultencoding('UTF8')


alignNum = 0
MatchNumList = [0] * 11
oldLineNum = 0
uniqueLineNum = 0
finalLineNum = 0
patternList = [r"\(.*\)", r"-.*", r"（.*）", r"\[.*\]", r"【.*】",r"（.*）",r"【.*】", r"\(.*", r"（.*", r"（.*", r"[ -!&].*版"]


def isLenOK(my_string):
    my_string = my_string.decode('utf-8')
    len_ch = len([l for l in list(my_string) if 19968<=ord(l)<=40869])
    len_en = len([l for l in list(my_string) if 65<=ord(l)<=90 or 97<=ord(l)<=112 ])

    if len_ch > 8 or len_en > 20 or (len_ch+len_en) < 2:
        return False
    return True


def inputdata(infname):
    n = 0
    datalist = []
    for line in open(infname,'r').readlines():
        temp_list = line.split('\t')
        if len(temp_list) != 4:
            n += 1
            continue
        datalist.append(temp_list)
    print r"\t split failed : " + str(n)
    return datalist



def aligndb(datalist):
    global alignNum

    sqlcmd1 = '''  SELECT  ios_pkg,app  FROM app_annotation WHERE ios_pkg !=""  AND app !="" '''
    sqlcmd2 = '''  SELECT  android_pkg,app  FROM app_annotation WHERE android_pkg != ""  AND app !="" '''

    entries1 = db.query(sqlcmd1)
    entries2 = db.query(sqlcmd2)

    db_dict1 = {entry.ios_pkg:entry.app for entry in entries1}
    db_dict2 = {entry.android_pkg:entry.app for entry in entries2}

    db_dict = dict(db_dict1,**db_dict2)
    #datalist = [ l[0] = db_dict[l[1]] for l in datalist if l[1] in db_dict ] 问 晓希
    for l in datalist:
        if l[0] in db_dict:
            if l[1] != db_dict[ l[0] ]:
                alignNum += 1
                l[1] = db_dict[ l[0] ].encode('utf-8')



def patternMatch(datalist):

    global patternList
    pObjectList = []

    for pattern in patternList:
        p = re.compile(pattern)
        pObjectList.append(p)


    for l in datalist:
        for idx, p in enumerate(pObjectList):
            (l[1],n) = p.subn('',l[1])
            MatchNumList[idx] += n

    return datalist


def writeResult(datalist,outfname):
    of = open(outfname, 'w')
    for line in datalist:
        if not is_list_ok(line):
            continue
        for idx,field in enumerate(line):
            of.write(field.strip() + '\t')
        of.write('\n')
    of.close()


def is_list_ok(temp_list):
    for item in temp_list:
        if not item:
            return False
    return True



def printStatistics():
    global finalLineNum, oldLineNum, uniqueLineNum, alignNum, MatchNumList
    finalLineNum = len(datalist)
    print "Orginal file line number: " + str(oldLineNum)
    print "line number after doing unique: " + str(uniqueLineNum)
    print "Number of lines being replaced using our database:" + str(alignNum)
    print "Number of lines being processed using patters:"
    for idx, n in enumerate(MatchNumList):
        print "Pattern" + str(idx+1) + ": " + patternList[idx] + ", " + str(n)
    print "final line number" + str(finalLineNum)




def removeSuffix(datalist):
    doc = xml.dom.minidom.parse('./data/suffixWord.xml')
    root = doc.documentElement
    nodeList = root.getElementsByTagName('suffix')
    suffixList = []

    for node in nodeList:
        nodeValue = str(node.childNodes[0].nodeValue)
        suffixList = suffixList + nodeValue.split('|')

    for l in datalist:
        l[1] = StringTool.normalizedStr(l[1])
        for s in suffixList:
            l[1] = l[1].replace(s, '')

    return datalist


if __name__ == '__main__':

    if len(sys.argv) < 3 or len(sys.argv[1]) <= 0 or len(sys.argv[2]) <= 0:
        print 'please enter valid input filename and output filename'
        sys.exit()

    infname = sys.argv[1]
    outfname = sys.argv[2]

    datalist = inputdata(infname)
    datalist = patternMatch(datalist)
    removeSuffix(datalist)
    writeResult(datalist, outfname)

