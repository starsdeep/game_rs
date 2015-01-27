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


def inputData():
    db = GetFromDB("10.99.20.92","root",'shenma123',"app_platform")
    sqlcmd = "select app,actor,scene,style,background,play from game_app where app!='' "
    game_list = [ list(t) for t in db.getRecords(sqlcmd) ]
    print ",".join(game_list[0])
    return game_list 


def align(game_list,titlename_pkg_dict):
    aligned_game_list = []
    aligned_pkgs = set()
    for idx,game in enumerate(game_list):
        titlename = game[0].strip().encode('utf-8')
        if not titlename in titlename_pkg_dict:
            continue
        for pkg in titlename_pkg_dict[titlename]: 
            if pkg in aligned_pkgs:
                continue
            temp_game = list(game)
            temp_game.insert(0,pkg)
            aligned_game_list.append(temp_game)
            aligned_pkgs.add(pkg)    

    print "align game_list okay, len is " + str(len(aligned_game_list)) 
    return aligned_game_list

def write(game_list,outFile):
    print "write result to outFile"
    of = open(outFile,'w')
    for game in game_list:
        of.write('\001'.join(game) + '\n')

def get_cleanedTitlename_pkg_dict(titlename_pkg_dict):
    
    print "testing titlename_pkg_dict: 捕鱼达人"
    for pkg in titlename_pkg_dict['捕鱼达人']:
        print pkg
    
    TC = TitleClean()
    cleanedTitlename_pkg_dict = defaultdict(list)
    for title,pkg_list in titlename_pkg_dict.items():
        cleanedTitlename_pkg_dict[TC.clean(title)] += pkg_list
    
    print "after clened" 
    for pkg in cleanedTitlename_pkg_dict['捕鱼达人']:
        print pkg
    
    return cleanedTitlename_pkg_dict

def get_titleCleaned_game_list(game_list):
    cleaned_game_list = []
    TC = TitleClean()
    for game in game_list:
        temp = list(game)
        temp[0] = TC.clean(temp[0].encode('utf-8'))
        cleaned_game_list.append(list(temp))
    print "in get_titleCleaned_game_list"
    for game in game_list:
        if game[0].encode('utf-8') == '捕鱼达人':
            print ",".join(game)
    print "after cleaned"
    for game in cleaned_game_list:
        if game[0].encode('utf-8') == '捕鱼达人':
            print ",".join(game)
    return cleaned_game_list


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "<outFile>"
        sys.exit()
    g = GetFromFile()
    titlename_pkg_dict = g.get_titlename_pkg_dict()
    cleanedTitlename_pkg_dict = get_cleanedTitlename_pkg_dict(titlename_pkg_dict)
    
    game_list = inputData()
    cleaned_game_list = get_titleCleaned_game_list(game_list)
    #alianed_game_list = align(game_list,titlename_pkg_dict)
    alianed_game_list = align(cleaned_game_list,cleanedTitlename_pkg_dict)
    write(alianed_game_list,sys.argv[1])
