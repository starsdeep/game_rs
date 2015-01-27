#encoding=utf8
import sys,os
import MySQLdb
curPath = os.path.abspath(os.path.split(os.path.realpath(__file__))[0])
sys.path.append(curPath + "/../common/")
sys.path.append(curPath + "/../filter/")
from LanguageModel import LanguageModel
from StringTool import StringTool
from collections import defaultdict,Counter
from WriteTool import WriteTool
import math
import heapq
reload(sys)
sys.setdefaultencoding('UTF8')
import cPickle as p


def load_pkg():
    try:
        conn = MySQLdb.connect(host='10.99.20.92', user='root', passwd='shenma123', db='mobile_game', charset='utf8')
        cur = conn.cursor()
        n = cur.execute("select pkg_name from all_game where title!='' and pkg_name!='' and description!='' and business_type='1' ORDER BY download_count DESC LIMIT 11000") 
        self.pkg_dlcount_dict = {item[0] for item in cur.fetchall() if item[0].strip() }
    except Exception, e:
        print "[Error]:", e
    finally:
        cur.close()
        conn.close()
    print "load business pkg: " + str(n)

def load_discounted_sim(filename): 
    if os.path.exists(filename):
        discount_dict_dict = WriteTool.load_nested_dict(filename)
        return discount_dict_dict


def boost_business(original_pkg_sim_list,pkg_set):
    pkg_sim_list = original_pkg_sim_list
    for pkg,sim_list in pkg_sim_list.items():
        top_pos = 0
        for idx,temp_tuple in enumerate(sim_list):
            if temp_tuple[0] in pkg_set:
                increased_pos = get_increased_pos(idx,top_pos)
                del pkg_sim_list[pkg][idx]
                pkg_sim_list.insert(increased_pos,temp_tuple)
                top_pos = increased_pos + 1
    return pkg_sim_list 



def get_increased_pos(pos,top_pos):
    result = pos
    if 0 <= pos < 5:
        result -= 2
    elif 6 <= pos < 11:
        result -= 3
    elif 11 <= pos < 20:
        result -= 5
    else:
        result = max(20,top_pos)
    return max(result,top_pos)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print "<discounted_sim><outFile>"

    pkg_set = load_pkg()
    pkg_sim_dict = load_discounted_sim(sys.argv[1])
    pkg_sim_list = WriteTool.nested_dict2list(pkg_sim_dict)
    boosted_pkg_sim_list = boost_business(pkg_sim_list,pkg_set)
    WriteTool.write_nested_dict(boosted_pkg_sim_list,sys.argv[2])
    
    of = open('data/business_boosted_game.txt','w')
    for pkg in pkg_set:
        of.write(pkg + '\n')


