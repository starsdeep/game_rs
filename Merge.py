#encoding=utf8
import sys,os,heapq
from WriteTool import WriteTool
from collections import Counter
from LanguageModel import LanguageModel
from ComputeJacardSim import ComputeJacardSim
from GetFromFile import GetFromFile
reload(sys)
sys.setdefaultencoding('UTF8')



def merge(pkg_titleTagSim_dict,pkg_despSim_dict,topn=200):
    print "in merge titleTag_sim and desp_sim"
    print "len of pkg_titleTagSim_dict " +  str(len(pkg_titleTagSim_dict))
    print "len of pkg_despSim_dict " +  str(len(pkg_despSim_dict))
    pkg_mergedSim_dict = {}
    for pkg,sim_dict in pkg_despSim_dict.items():
        if pkg in pkg_titleTagSim_dict: 
            single = Counter(sim_dict) + Counter(pkg_titleTagSim_dict[pkg])
            single = dict(single)
            single = heapq.nlargest(topn, single.items(), key=lambda e:e[1])
            pkg_mergedSim_dict[pkg] = {v[0]:v[1] for v in single}
        else:
            pass
            #print "[error in merge tag] pkg is " + pkg
    
    return pkg_mergedSim_dict



if __name__ == '__main__':
    if len(sys.argv) != 5:
        print "<tagTitleSim><despSim><inFile><outFile>"
        sys.exit()

    titleTagSim = sys.argv[1]
    despSim = sys.argv[2]
    inFile = sys.argv[3]
    outFile = sys.argv[4]

    g = GetFromFile(inFile)
    pkg_list = g.get_pkg_list()
    pkg_titlename_dict = g.get_pkg_titlename_dict()  

    if os.path.exists(titleTagSim):
        pkg_titleTagSim_dict = WriteTool.load_nested_dict(titleTagSim)
    
    if os.path.exists(despSim):
        pkg_despSim_dict = WriteTool.load_nested_dict(despSim)

    merged_sim = merge(pkg_titleTagSim_dict,pkg_despSim_dict)
    WriteTool.write_nested_dict(merged_sim,outFile,pkg_titlename_dict,pkg_list) 
