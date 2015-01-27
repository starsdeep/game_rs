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

def discount(sim_dict_dict,title_sim_dict,threshold=0.3,stop_value = 0.1):
    print "in discount"
    discountedSim = sim_dict_dict

    sqlcmd = "select pkg_name, download_count from all_game where title!='' and pkg_name!='' and description!='' ORDER BY download_count DESC LIMIT 11000"
    db = GetFromDB("10.99.20.92","root",'shenma123',"mobile_game")
    records = db.getRecords(sqlcmd)
    pkg_dlcount_dict = {item[0]:item[1] for item in records if item[0].strip()}

    total_match = 0
    for pkg,sim_dict in sim_dict_dict.items():
        if pkg not in title_sim_dict:
            continue
        
        match_num = 0
        sim_list = sorted(sim_dict.items(),key=lambda e:e[1],reverse=True)
        for idx,t in enumerate(sim_list):
            
            i = min(idx,11)
            discount = 1
            other = t[0]
            top_sim_list = [title_sim_dict[other][sim_list[j][0]]  for j in xrange(i) if other in title_sim_dict and sim_list[j][0] in title_sim_dict[other]]
            if top_sim_list:
                max_sim = max(top_sim_list)
            else:
                max_sim = 0
            if max_sim > threshold:
                discount = max(discount * (1-max_sim)  ,stop_value)
                discountedSim[pkg][t[0]] = t[1] * discount
                #match_num += 1
                total_match +=1

            if other in title_sim_dict[pkg]: 
                discount = max(discount*num_value_map(match_num) * (1-title_sim_dict[pkg][t[0]]  )  ,stop_value)
                discountedSim[pkg][t[0]] = t[1] * discount
                match_num += 1
                total_match+=1
                if title_sim_dict[pkg][other] >= 0.75 and pkg in pkg_dlcount_dict and other in pkg_dlcount_dict and  pkg_dlcount_dict[pkg] >= pkg_dlcount_dict[other]:
                    del discountedSim[pkg][other]

    print "discountedSim :" + str(len(discountedSim)) + "total match " + str(total_match) 
    return discountedSim


def num_value_map(num):
    if num==1:
        return 0.6
    elif num==2:
        return 0.85
    else:
        return 0.95


if __name__ == '__main__':
    if len(sys.argv) != 5:
        print "<boostedSim><titleSim><inFile><outFile>"
        sys.exit()

    boostedSim = WriteTool.load_nested_dict(sys.argv[1])
    titleSim = WriteTool.load_nested_dict(sys.argv[2])
    inFile = sys.argv[3]
    outFile = sys.argv[4]
    g = GetFromFile(inFile)
    pkg_list = g.get_pkg_list()
    pkg_titlename_dict = g.get_pkg_titlename_dict()  
    discountedSim = discount(boostedSim,titleSim)
    discountedSim = WriteTool.filter_nested_dict(discountedSim,100,0.001) 
    WriteTool.write_nested_dict(discountedSim,outFile,pkg_titlename_dict,pkg_list) 
