#encoding=utf8
import sys,os,math
import MySQLdb
from WriteTool import WriteTool
from GetFromFile import GetFromFile
reload(sys)
sys.setdefaultencoding('UTF8')

class BoostProcessor:
    max_dlcount = 0.0
    min_dlcount = 0.0
    log_max_dlcount = 0.0 
    log_min_dlcount = 0.0
    sorted_pkg_list = []
    pkg_dlcount_dict = {}

    def __init__(self):
        self._inputData()

    def boost(self,nested_dict,offset):
        print "in boost"
        print "len of mergedSim" + str(len(nested_dict))
        weight_dict = {}
        if offset + self.log_min_dlcount > 0:
            weight_dict = {pkg: (offset+math.log(value)) / (offset+self.log_max_dlcount)  for pkg,value in self.pkg_dlcount_dict.items() }
        
        boostedSim = WriteTool.boost_nested_dict(nested_dict,weight_dict)
        
        return boostedSim



    def _inputData(self):
        #input download count,used to sort game when save result 
        try:
            conn = MySQLdb.connect(host='10.99.20.92', user='root', passwd='shenma123', db='mobile_game', charset='utf8')
            cur = conn.cursor()
            n = cur.execute("select pkg_name, download_count from all_game where title!='' and pkg_name!='' and description!='' ORDER BY download_count DESC LIMIT 11000") 
            self.pkg_dlcount_dict = {item[0]:item[1] for item in cur.fetchall() if item[0].strip() }
            #used to boost by download count
            slist = sorted(self.pkg_dlcount_dict.items(),key=lambda e:e[1],reverse=True)
            self.sorted_pkg_list = [ t[0] for t in slist if t[0] ]
            self.max_dlcount = slist[0][1]
            self.min_dlcount = slist[-1][1]
            self.log_max_dlcount = math.log(self.max_dlcount)
            self.log_min_dlcount = math.log(self.min_dlcount)
        except Exception, e:
            print "[Error]:", e
        finally:
            cur.close()
            conn.close()
        
        offset = 0.0
        print "input download from db:" + str(len(self.pkg_dlcount_dict))
        print str(self.max_dlcount) + "," + str(self.min_dlcount) + "," + str(self.log_max_dlcount) + "," + str(self.log_min_dlcount) + "," + str((offset+self.log_min_dlcount) / (offset+self.log_max_dlcount))
        



if __name__ == '__main__':
    if len(sys.argv) != 4:
        print "<mergedSim><inFile><outFile>"
        sys.exit()
    
    inFile = sys.argv[2]
    outFile = sys.argv[3]
    g = GetFromFile(inFile)
    pkg_list = g.get_pkg_list()
    pkg_titlename_dict = g.get_pkg_titlename_dict()

    mergedSim = WriteTool.load_nested_dict(sys.argv[1])
    b = BoostProcessor()
    boostedSim = b.boost(mergedSim,0)
    WriteTool.write_nested_dict(boostedSim,outFile,pkg_titlename_dict,pkg_list) 
