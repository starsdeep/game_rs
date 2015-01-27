#encoding=utf8
import sys,os
from LanguageModel import LanguageModel
from WriteTool import WriteTool
from ComputeJacardSim import ComputeJacardSim
from GetFromFile import GetFromFile
reload(sys)
sys.setdefaultencoding('UTF8')
import cPickle as p


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print "<inFile><outFile>"
        sys.exit()
    
    inFile = sys.argv[1]
    outFile = sys.argv[2]
    g = GetFromFile(inFile)
    pkg_list = g.get_pkg_list()
    pkg_titlename_dict = g.get_pkg_titlename_dict()  
    pkg_title_dict = g.get_pkg_title_dict()
    titleSim = ComputeJacardSim(pkg_title_dict)
    WriteTool.write_nested_dict(titleSim,outFile,pkg_titlename_dict,pkg_list)
    print "dumping pkg_segtitle_dict.data"
    f = file('./data/pkg_segtitle_dict.data', 'w')
    p.dump(pkg_title_dict, f) # dump the object to a file
    f.close()
