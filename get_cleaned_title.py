#encoding=utf8
import sys,os,heapq
from collections import defaultdict
from LanguageModel import LanguageModel
from WriteTool import WriteTool
from ComputeJacardSim import ComputeJacardSim
from TitleClean import TitleClean
from GetFromFile import GetFromFile
from GetFromDB import GetFromDB
reload(sys)
sys.setdefaultencoding('UTF8')


def get_titles():
    db = GetFromDB('10.99.20.92','root','shenma123','mobile_game')
    sqlcmd = "select title from all_game where title!='' and pkg_name!=''"
    records = db.getRecords(sqlcmd)
    titles = [item[0].strip().encode('utf-8') for item in records if item and item[0].strip()]
    return titles


if __name__ == '__main__':

    if len(sys.argv) != 2:
        print "<outFile:data/cleaned_title_list.txt>"
        sys.exit()

    titles = get_titles()
    TC = TitleClean()
    cleaned_titles = {TC.clean(title) for title in titles}

    of = open(sys.argv[1],'w')
    for title in cleaned_titles:
      of.write(title + "\n")


