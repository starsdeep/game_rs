#encoding=utf8
import sys,os,heapq
from collections import defaultdict
from LanguageModel import LanguageModel
from WriteTool import WriteTool
from ComputeJacardSim import ComputeJacardSim
from GetFromFile import GetFromFile
from GetFromDB import GetFromDB
reload(sys)
sys.setdefaultencoding('UTF8')



topCat_secondCat_dict = {
    'actor':['勇士','萌物','忍者','僵尸','战士','侠盗','英雄','海盗','魔法师','火柴人','Null'],
    'scene':['3D','炫彩','Q萌','水墨','唯美','血腥','手绘','像素','Null'],
    'style':['休闲','简单','智力','节奏','重口','暗黑','Null'],
    'background':['魔幻','都市','战争','仙侠','星际','历史','空战','Null'],
    'play':['角色','射击','竞速','卡牌','体育','消除','重力','横版','物理','模拟','塔防','Null']}

topCat_index_dict = {'actor':0,'scene':1,'style':2,'background':3,'play':4}
index_topCat_dict = {0:'actor',1:'scene',2:'style',3:'background',4:'play'}

ch_py_dict = {'Null':'Null', '勇士':'yongshi', '萌物':'mengwu', '忍者':'renzhe', '僵尸':'jiangshi', '战士':'zhanshi', '侠盗':'xiadao', '英雄':'yingxiong', '海盗':'haidao', '魔法师':'mofashi', '火柴人':'huochairen', '3D':'3D','炫彩':'xuancai', 'Q萌':'Qmeng', '水墨':'shuimo', '唯美':'weimei', '血腥':'xuexing', '手绘':'shouhui', '像素':'xiangsu', '休闲':'xiuxian', '简单':'jiandan', '智力':'zhili', '节奏':'jiezou', '重口':'zhongkou', '暗黑':'anhei', '魔幻':'mohuan', '都市':'dushi', '战争':'zhanzheng', '仙侠':'xianxia', '星际':'xingji', '历史':'lishi', '空战':'kongzhan', '角色':'juese', '射击':'sheji', '竞速':'jingsu', '卡牌':'kapai', '体育':'tiyu', '消除':'xiaochu', '重力':'zhongli', '横版':'hengban', '物理':'wuli', '模拟':'moni', '塔防':'tangfang'}

def inputGame(inFile):
    pkg_tag_dict = {}
    for line in open(inFile,'r').readlines():
        game = [field.strip() for field in line.split('\001')]
        pkg_tag_dict[game[0]] = game[2:] 

    return pkg_tag_dict

def get_write_games(pkg_game_dict,topCat,secondCat):
    global topCat_index_dict
    pkgs = set()
    idx = topCat_index_dict[topCat]
    for pkg,game in pkg_game_dict.items():
        if secondCat == 'Null' and not game[idx]:
            pkgs.add(pkg)
        if game[idx] == secondCat:
            pkgs.add(pkg)
    if pkgs:
        writePkgs(pkgs,get_filename(topCat,secondCat))
    return pkgs

def writePkgs(pkgs,filename):
    of = open(filename,'w')
    for pkg in pkgs:
        of.write(pkg + '\t')

def get_filename(topCat,secondCat):
    global ch_py_dict
    return 'data/GameClassify/' + str(topCat) + '_' + ch_py_dict[secondCat] + '.txt'


def classifyGames(pkg_game_dict):
    global index_topCat_dict 
    for i in range(5):
        topCat = index_topCat_dict[i]
        total = 0
        print topCat + "======================"
        for secondCat in topCat_secondCat_dict[topCat]:
            pkgs = get_write_games(pkg_game_dict,topCat,secondCat)
            total += len(pkgs)
            print secondCat + ":" + str(len(pkgs)) 
        print "total:" + str(total)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print '<inFile data/GameClassify/game_ano.txt>'
        sys.exit()
    pkg_game_dict = inputGame(sys.argv[1])
    classifyGames(pkg_game_dict)
   
    print "test style:简单"
    pkgs =  get_write_games(pkg_game_dict,'style','简单')
    for pkg in pkgs:
        print pkg





