#encoding=utf8
import sys,os,heapq
from collections import defaultdict
from LanguageModel import LanguageModel
from WriteTool import WriteTool
from ComputeJacardSim import ComputeJacardSim
from GetFromFile import GetFromFile
import cPickle as p
reload(sys)
sys.setdefaultencoding('UTF8')



def getTopSingleSimilarity(invertedIndex,pkg_tfidf_dict,pkg,topn=200):
    single_sim = defaultdict(lambda : 0)
    for word,weight0 in pkg_tfidf_dict[pkg].items():
        for other,weight1 in invertedIndex[word].items():
            if pkg == other:
                continue
            single_sim[other] += weight0*weight1
    sim_dict = {t[0]:t[1] for t in heapq.nlargest(topn, single_sim.items(), key=lambda e:e[1])}
    return sim_dict


def computeDespSim(invertedIndex,pkg_tfidf_dict,outFile,topn=200):
    print "in computer desp sim,len of pkg_tfidf_dict " + str(len(pkg_tfidf_dict))
    pkg_despSim_dict = {}
    num = 0
    for pkg in pkg_tfidf_dict:
        num+=1
        if num%1000==0:
            print num
        pkg_despSim_dict[pkg] = getTopSingleSimilarity(invertedIndex,pkg_tfidf_dict,pkg,topn)
     
    
    return pkg_despSim_dict


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print "<inFile><outFile>"
        sys.exit()
    
    inFile = sys.argv[1]
    outFile = sys.argv[2]
    g = GetFromFile(inFile)
    pkg_list = g.get_pkg_list()
    pkg_titlename_dict = g.get_pkg_titlename_dict()  
    pkg_desp_dict = g.get_pkg_desp_dict()
    pkg_desp_dict= LanguageModel.getTrimedDocTermDict(pkg_desp_dict,5)
    pkg_tfidf_dict = LanguageModel.getWeightedTfidf(pkg_desp_dict)
    pkg_tfidf_dict = LanguageModel.normalize(pkg_tfidf_dict,100)
    invertedIndex = LanguageModel.getInvertedIndex(pkg_tfidf_dict)
    despSim = computeDespSim(invertedIndex,pkg_tfidf_dict,200)

    WriteTool.write_nested_dict(despSim,outFile,pkg_titlename_dict,pkg_list)

    print "dumping pkg_tfidf_dict.data"
    f = file('./data/pkg_tfidf_dict.data', 'w')
    p.dump(pkg_tfidf_dict, f) # dump the object to a file
    f.close()



