#encoding=utf8
import sys,os
import cPickle as p
import socket
import MySQLdb
from collections import defaultdict
from LanguageModel import LanguageModel
curPath = os.path.abspath(os.path.split(os.path.realpath(__file__))[0])
sys.path.append(curPath + "/../common/")
sys.path.append(curPath + "/../filter/")
sys.path.append(curPath + "/../")

from qp_accessor import QPAccessor

reload(sys)
sys.setdefaultencoding("UTF8")


class Server():

    word_pkgSet_dict=defaultdict(set)
    pkg_game_dict = {}
    title_pkg_dict = {}
    pkg_list = []
    title_list = []
    topSim_dict = {}

    def inputGame(self):
        game = None
    
        try:
            conn = MySQLdb.connect(host='10.99.20.92', user='root', passwd='shenma123', db='mobile_game', charset='utf8')
            cur = conn.cursor()
            num= cur.execute("select pkg_name,title,tags,description,detail_info_url from all_game")
            items = cur.fetchall()
            self.pkg_game_dict = {item[0].strip():item for item in items if len(item[0].strip()) > 0 and len(item[1].strip())>0 }            
            #self.title_pkg_dict = {item[1].strip().encode('utf-8'):item[0] for item in items if len(item[0].strip()) > 0 and len(item[1].strip())>0 }            
            #self.pkg_list = [item[0].strip() for item in items if len(item[0].strip()) > 0 and len(item[1].strip())>0 ]
            #self.title_list = [title.strip() for title in open('seged_game_title.txt').readlines() ]
            print "pkg_game_dict:" + str(len(self.pkg_game_dict))
            #print "title_pkg_dict:" + str(len(self.title_pkg_dict))
            #print "pkg_list:" + str(len(self.pkg_list))
            #print "title_list:" + str(len(self.title_list))              

            print "test input Game,print a sample"
            print "title for com.furiousapps.haunt2:" + self.pkg_game_dict['com.furiousapps.haunt2'][1]
            #print "seged title for " + self.pkg_list[0] + self.title_list[0]
            #print "pkgname for 捕鱼达人2:" + self.title_pkg_dict['鬼屋魅影2']

        except Exception, e:
            print "[Error]:", e
            sys.exit()
        finally:
            cur.close()
            conn.close() 
        return game


    def buildWordPkgSet(self):
        print "building WordPkgSet"
        print "num of title:" + str(len(self.title_list))
        
        num = 0
        for idx,title in enumerate(self.title_list):         
            num+=1
            if num%10000 == 0:
                print str(num)+',',
            for word in title.split('\t'):
                self.word_pkgSet_dict[word].add(self.pkg_list[idx])
        print "building ok"
        print "total words:"+str(len(self.word_pkgSet_dict))
        print "test a sample,pkgs of 魅影"
    
    ''' 
    def buildWordPkgSet(self):
        self.word_pkgSet_dict = LanguageModel.getInvertedIndex(self.pkg_segtitle.dict)
    '''


    def getPkgname(self,title):
        print "in get Pkgname,query :" + title
        if isinstance(title,unicode):
            title = title.encode('utf-8')
        retArr = QPAccessor.getQPSegQuery(title)
        pkgSet = set(self.word_pkgSet_dict[retArr[0]])
        pkg_titleLen_dict = {}
        for word in retArr:
                pkgSet = pkgSet & self.word_pkgSet_dict[word]
        if len(pkgSet)>0:
            for pkg in pkgSet:
                pkg_titleLen_dict[pkg] = len(self.pkg_game_dict[pkg][1])
                print pkg,
            pkg_titleLen_list = sorted(pkg_titleLen_dict.items(),key=lambda e:e[1],reverse=False)
            print "\n"+str(len(pkgSet)) + "matches for "+ title
            print "length for " + pkg_titleLen_list[0][0] + ":" +  str(pkg_titleLen_list[0][1])
            return pkg_titleLen_list[0][0]
        
        
        
        print "title:"+title+" does not match any title"
        return "None"


    def buildResponse(self,type,query):
        response = ""
        if type=='0':
            pkgname = self.getPkgname(query)
        else:
            pkgname = query
        if isinstance(pkgname,unicode):
            pkgname = pkgname.decode('utf8')
        print "pkgname for"+query+":"+pkgname 
        #build query itself
        if pkgname not in self.pkg_game_dict:
            return "None"
        
        response+='\003'.join(self.pkg_game_dict[pkgname])
        response+='\003'
        bagOfwords = sorted(self.per_pkg_word_weight_dict[pkgname].items(),key=lambda e:e[1],reverse=True)
        for t in bagOfwords:
            response += t[0] + ":" + str("%.3f"%t[1]) +'   ' 
        response+='\001'
        #build top 50
        num=0
        if pkgname in self.topSim_dict:
            print "length for " + pkgname + ":" + str(len(self.topSim_dict[pkgname]))
            for other,sim in self.topSim_dict[pkgname].items():
                if other not in self.pkg_game_dict:
                    continue;
                #num+=1
                #print str(num)+":"+ str(len(response))
                response+='\003'.join(self.pkg_game_dict[other])
                #bagOfwords
                response+='\003'
                if other in self.per_pkg_word_weight_dict:
                    #sort
                    bagOfwords = sorted(self.per_pkg_word_weight_dict[other].items(),key=lambda e:e[1],reverse=True)
                    for t in bagOfwords:
                        response += t[0] + ":" + str("%.3f"%t[1]) +'   ' 
                #sim
                response += '\003'
                if pkgname in self.topSim_dict and other in self.topSim_dict[pkgname]:
                    response+=str("%.3f"%self.topSim_dict[pkgname][other])+'\003'
                else:
                    response+='None'+'\003'
                
                response+='\002'
        return response.strip('\002')


    def loadData(self):
        print 'load data'     
        f = file('./data/pkg_ntopSimilarity_dict.data')
        self.topSim_dict = p.load(f)
        f.close()
        
        f = file('./data/pkg_ntfidf_dict.data')
        self.per_pkg_word_weight_dict = p.load(f)
        f.close()
        
        f = file('./data/pkg_segtitle_dict.data')
        self.pkg_segtitle_dict.data = p.load(f)
        f.close()
        print "load data testing"
        #print "top sim for com.furiousapps.haunt2 and air.mgg1beautifulteendressup"  + str(self.topSim_dict['com.furiousapps.haunt2']['air.mgg1beautifulteendressup'])



if __name__ == '__main__':
    print "test QPAccessor"
    retArr = QPAccessor.getQPSegQuery('愤怒的小鸟')
    for item in retArr:
        print item

    s = Server() 
    s.loadData()
    s.inputGame() 
    s.buildWordPkgSet()
    print s.getPkgname('愤怒的小鸟')
    

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('10.99.20.96', 8851))
    sock.listen(5)
    print "\n socket start"
    while True:
       
        try:
            of=open('./data/serverlog','w')
            connection,address = sock.accept()
            connection.settimeout(8000)
            queryStr = connection.recv(1024)
            print "query is :"+queryStr
            type=queryStr.split('\001')[0]
            query=queryStr.split('\001')[1]
            print "the seged query is:",
            for word in QPAccessor.getQPSegQuery(query):
                print word,
            print "build response"
            response = s.buildResponse(type,query)
            print "build okay,response length:" + str(len(response))
            print "writing response"
            of.write(response+'\n\n\n\n')
            of.close()
            connection.sendall(response)
        except socket.timeout:
            print 'time out'
        finally:
            connection.close()
