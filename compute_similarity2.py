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

class DespSimilarityProcessor():

    stopWordSet = set()
    pkg_game_dict = {}  #pkg->[title,tags,desp ]
    num_all_game = 0
    word_weight_dict = {}
    per_pkg_word_weight_dict={}  #pkg->dict(word:weight)
    pkg_similarity_dict={}
    pkg_topSimilarity_dict={}
    pkg_topSimilarity_list={}

    tag_sim_dict = {}
    title_sim_dict = {}
    desp_sim_dict = {} 
    blend_sim_dict = defaultdict(dict)

    tag_sim_list = {}
    title_sim_list = {}
    desp_sim_list = {} 
    blend_sim_list = {} 
    word_game_dict=defaultdict(dict)
    count=0
    #有意义的word,2<count<....
    wordlist=set() 
    Oword_count_dict={}
    Fword_count_dict={}
    pkg_segtitle_dict = {} 
    pkg_title_dict={}
    pkg_tag_dict = {}
    pkg_desp_dict = {}
    pkg_unigram_dict ={}
    pkg_bigram_dict={}
    pkg_trigram_dict = {}
    pkg_title_tfidf_dict = {}
    pkg_tag_tfidf_dict = {}
    pkg_unigram_tfidf_dict = {}
    pkg_bigram_tfidf_dict = {}
    pkg_trigram_tfidf_dict = {}
    pkg_merged_model_dict = {}
    pkg_tfidf_dict = {}    
    pkg_setOfWords = {}
    jacard_sim_dict = {}
    invertedIndex = {}   
    pkg_dlcount_dict = {}    
    pkg_doclen_dict = {}
    pkg_titlename_dict = {}


    count = 0
    sorted_pkg_list = []
    final_model = {}
    word_intersect = defaultdict(dict)

    max_dlcount = 0
    min_dlcount = 0
    log_max_dlcount = 1
    log_min_dlcount = 1

    def printGame(self,pkgname):
        print "print game " + pkgname
        game = self.pkg_game_dict[pkgname]
        
        print "title:\t", 
        for word in game[0]:
            print word,
        print "\ntag:\t",
        for word in game[1]:
            print word,
        print "\ndesp:"
        print "unigram:\t",
        for word in game[2][0]:
            print word,
        print "\n\nbigram:\t",
        for word in game[2][1]:
            print word,
        print "\n\ntrigram:\t",
        for word in game[2][2]:
            print word,
        
        print "\n"

    def inputData(self,inFile):
        #input download count,used to sort game when save result 
        try:
            conn = MySQLdb.connect(host='10.99.20.92', user='root', passwd='shenma123', db='mobile_game', charset='utf8')
            cur = conn.cursor()
            n = cur.execute("select pkg_name, download_count from all_game where title!='' and pkg_name!='' and description!='' ORDER BY download_count DESC LIMIT 11000") 
            self.pkg_dlcount_dict = {item[0]:item[1] for item in cur.fetchall() if item[0].strip() }
            # used to sort data
            slist = sorted(self.pkg_dlcount_dict.items(),key=lambda e:e[1],reverse=True)
            self.sorted_pkg_list = [ t[0] for t in slist if t[0] ]
            #used to boost by download count
            self.max_dlcount = slist[0][1]
            self.min_dlcount = slist[-1][1]
            self.log_max_dlcount = math.log(self.max_dlcount)
            self.log_min_dlcount = math.log(self.min_dlcount)
            offset = 0.0
        except Exception, e:
            print "[Error]:", e
        finally:
            cur.close()
            conn.close()

        print "input download from db:" + str(len(self.pkg_dlcount_dict))
        print str(self.max_dlcount) + "," + str(self.min_dlcount) + "," + str(self.log_max_dlcount) + "," + str(self.log_min_dlcount) + "," + str((offset+self.log_min_dlcount) / (offset+self.log_max_dlcount))
        
        #input useless punctuation
        for punc in open('StopPunc.txt', 'r').readlines():
            self.stopWordSet.add(punc.decode('utf-8').strip().strip('\"').encode('utf-8')) #去除开头结尾引号
        for word in open('StopWord.txt','r').readlines():
            self.stopWordSet.add(word.strip())
        
        #input game data
        for item in open(inFile, 'r').readlines():
            game_list = []
            fields = item.strip().split('\001')
            pkgname = fields[0];
            title_list = [t.strip().lower() for t in fields[1].strip().split('\t') if t.strip()]
            tag_list = [t.strip().lower() for t in  fields[2].strip().split('\t') if t.strip()]
            desp_list = fields[3].split('\002')
            unigram_list = [t.strip().lower() for t in  desp_list[0].split('\t') if t.strip()]
            bigram_list = [t.strip().lower() for t in desp_list[1].split('\t') if t.strip()]
            #trigram_list = [t.strip().lower() for t in desp_list[2].split('\t') if t .strip()]
            desp_list=[]
            desp_list+=unigram_list
            desp_list+=bigram_list
            #desp_list.append(trigram_list)

            game_list.append(title_list)
            game_list.append(tag_list)
            game_list.append(desp_list) 
            
            self.pkg_titlename_dict[pkgname] = title_list[0] 
            self.pkg_title_dict[pkgname] = title_list if len(title_list) < 3 else title_list[1:]
            self.pkg_tag_dict[pkgname] = tag_list
            self.pkg_desp_dict[pkgname] = desp_list
            self.pkg_unigram_dict[pkgname] = unigram_list
            self.pkg_bigram_dict[pkgname] = bigram_list
            #self.pkg_trigram_dict[pkgname] = trigram_list
            
            self.pkg_game_dict[pkgname] = game_list
            self.pkg_doclen_dict[pkgname] = len(self.pkg_title_dict[pkgname]) + len(self.pkg_tag_dict[pkgname])+len(self.pkg_unigram_dict[pkgname])+len(self.pkg_bigram_dict[pkgname]) # + len(self.pkg_trigram_dict[pkgname])

        
        
        print "input num:" + str(len(self.pkg_game_dict))
        
        
        #self.printGame('org.cocos2dx.FishGame') 


    def dumpWordCount(self,word_pkgCount_dict,outfile):
        sortedWordList = sorted(word_pkgCount_dict.items(),key=lambda e:e[1],reverse=True)
        of = open(outfile,'w')
        for item in sortedWordList:
            of.write(item[0]+'\t'+str(item[1])+'\n')
        of.close()

    def getTopSingleSimilarity(self,pkg,topn=200):
        single_sim={}
        for word,weight0 in self.pkg_tfidf_dict[pkg].items():
            for other,weight1 in self.invertedIndex[word].items():
                if pkg == other:
                    continue
                single_sim[other] = weight0*weight1
        sim_list = heapq.nlargest(topn, single_sim.items(), key=lambda e:e[1])
        sim_dict = {t[0]:t[1] for t in sim_list}
            
        return sim_list,sim_dict


    '''
    def getTopSingleSimilarity2(self,pkg):
        single_sim = defaultdict(lambda:0)
        match_count_dict = defaultdict(lambda :0)
        match_wordweight_dict = defaultdict(list)
        for word,weight0 in self.pkg_tfidf_dict.items():
            for other,weight1 in self.invertedIndex[word].items():
                match_count_dict[other]+=1;
                match_word_dict[other].append(word)
        sorted_match_list = sorted(match_count_dict.items(), key=lambda e:e[1],reverse=True)
        i = min(300,len(match_count_dict)) 
        for i in xrange(300):
            for tup in sorted_match_list:
                other = tup[0]
                for word in match_word_dict[other]:
                    single_sim[other] += self.pkg_tfidf_dict[pkg][word]*self.pkg_tfidf_dict[other][word]
        
        sim_list = heapq.nlargest(200, single_sim.items(), key=lambda e:e[1])
        sim_dict = {t[0]:t[1] for t in sim_list}
        return sim_list,sim_dict
    '''



    def computerAllSimilarity2(self,filename,topn=200):
        print "in computer all similarity"
        if os.path.exists(filename):
            self.pkg_topSimilarity_dict = WriteTool.load_nested_dict(filename)
            self.pkg_topSimilarity_list = WriteTool.nested_dict2list(self.pkg_topSimilarity_dict)
            return 
        
        print "in computer all similaritiy,len of pkg_tfidf_dict " + str(len(self.pkg_tfidf_dict))
        num = 0
        for pkg in self.sorted_pkg_list:
            if pkg in self.pkg_tfidf_dict:
                num+=1
                if num%1000==0:
                    print num
                if num>10000:
                    break;
                self.pkg_topSimilarity_list[pkg],self.pkg_topSimilarity_dict[pkg] = self.getTopSingleSimilarity(pkg,topn)
                self.pkg_segtitle_dict[pkg] = self.pkg_title_dict[pkg]
         
        if filename:
            WriteTool.write_nested_dict(self.pkg_topSimilarity_dict,filename,self.pkg_titlename_dict) 


    def get_word_intersect(self):
        print "int get word intersect"
        for pkg in self.pkg_merged_model_dict:
            for other in self.pkg_topSimilarity_dict[pkg]:
                self.word_intersect[pkg][other] = self.pkg_merged_model_dict[pkg].keys() & self.pkg_merged_model_dict[other].keys() 
        print "testing word intersect"
        #print "com.imangi.templerun and" 



    def saveResult(self,sim_dict,outfile1,outfile2):
        
        print "saving result,len of sim_dict " + str(len(sim_dict))
        of1 = open(outfile1, 'w')
        
        for pkg in self.sorted_pkg_list:
            if pkg in sim_dict and pkg in self.pkg_game_dict:
                of1.write(pkg + '\t' +self.pkg_game_dict[pkg][0][0]+ '\002' +  '\n')
                for other in sim_dict[pkg]:
                    of1.write(other[0]+'\t' + self.pkg_game_dict[other[0]][0][0] +'\t'+ str(other[1]) + '\003' + '\n')
        of1.close()
        
        of2 = open(outfile2, 'w')
        for pkg, sim_list in sim_dict.items():
            of2.write(pkg + '\002' + '\n')
            for other in sim_list:
                of2.write(other[0]+'\t' + str(other[1]) + '\003' + '\n')
        of2.close()



    def dumpData(self):
        print "dumping pkg_tfidf_dict.data"
        f = file('./data/pkg_ntfidf_dict.data', 'w')
        p.dump(self.pkg_tfidf_dict, f) # dump the object to a file
        f.close()
        

        print "dumping pkg_topSimilarity_dict.data"
        f = file('./data/pkg_ntopSimilarity_dict.data', 'w')
        print str(self.pkg_topSimilarity_dict['com.imangi.templerun2']['com.notdoppler.earntodie'])
        p.dump(self.pkg_topSimilarity_dict, f) # dump the object to a file
        f.close()


        print "dumping pkg_segtitle_dict.data"
        f = file('./data/pkg_segtitle_dict.data', 'w')
        p.dump(self.pkg_segtitle_dict, f) # dump the object to a file
        f.close()

        
        f = file('./data/word_intersect.data', 'w')
        p.dump(self.word_intersect, f) # dump the object to a file
        f.close()



    '''def merge_model(self,topn):
        weight_title = 2
        weight_tag = 2
        weight_desp = 1

        weight_unigram = (1/1.56)*weight_desp
        weight_bigram = (0.4/1.56)*weight_desp
        weight_trigram = (0.16/1.56)*weight_desp
        for pkg in self.pkg_title_dict:
            title =Counter({k:weight_title*v for k,v in self.pkg_title_tfidf_dict[pkg].items()})
            tag = Counter({k:weight_tag*v for k,v in self.pkg_tag_tfidf_dict[pkg].items()})
            unigram = Counter({k:weight_unigram*v for k,v in self.pkg_unigram_tfidf_dict[pkg].items()})
            bigram = Counter({k:weight_bigram*v for k,v in self.pkg_bigram_tfidf_dict[pkg].items()})
            trigram = Counter({k:weight_trigram*v for k,v in self.pkg_trigram_tfidf_dict[pkg].items()})
            desp = unigram + bigram + trigram
            #print str(len(unigram)) + "," + str(len(bigram)) + ","+str(len(trigram))+","+str(len(desp))
            n = min(len(desp),topn) if topn!=0 else len(desp)
            desp = Counter({l[0]:l[1] for l in sorted(desp.items(),key=lambda e:e[1],reverse=True)[0:n] })
            tmp = title+tag+desp
            #print str(len(tmp))
            s.pkg_tfidf_dict[pkg] = dict(tmp)'''

    def get_merge_model(self):
        print "in get_merge_model"
        weight_title = 1.0
        weight_tag = 1.0
        weight_desp = 1.0

        weight_unigram = (1.0/1.4)*weight_desp
        weight_bigram = (0.4/1.4)*weight_desp
        #weight_trigram = (0.16/1.56)*weight_desp
        
        pkg_title_count_dict = {}
        pkg_tag_count_dict = {}
        pkg_unigram_count_dict = {}
        pkg_bigram_count_dict = {}
        #pkg_trigram_count_dict = {}

        #for pkg,temp_list in self.pkg_title_dict.items():
            #pkg_title_count_dict[pkg] = {k:weight_title for k in set(temp_list) if k.strip()} 
        #for pkg,temp_list in self.pkg_tag_dict.items():
            #pkg_tag_count_dict[pkg] = {k:weight_tag for k in set(temp_list) if k.strip()} 
        for pkg,temp_dict in LanguageModel.getBagOfWords(self.pkg_unigram_dict).items():
            pkg_unigram_count_dict[pkg] = {k:weight_unigram*v for k,v in temp_dict.items() if k.strip()} 
        for pkg,temp_dict in LanguageModel.getBagOfWords(self.pkg_bigram_dict,).items():
            pkg_bigram_count_dict[pkg] = {k:weight_bigram*v for k,v in temp_dict.items() if k.strip()} 
        #for pkg,temp_dict in LanguageModel.getBagOfWords(self.pkg_trigram_dict).items():
            #pkg_trigram_count_dict[pkg] = {k:weight_trigram*v for k,v in temp_dict.items() if k.strip()} 

        merged_model = {}
        for pkg in self.pkg_title_dict:
            #single = Counter(pkg_title_count_dict[pkg]) + Counter(pkg_tag_count_dict[pkg]) + Counter(pkg_unigram_count_dict[pkg]) + Counter(pkg_bigram_count_dict[pkg]) #+ Counter(pkg_trigram_count_dict[pkg])
            single = Counter(pkg_unigram_count_dict[pkg]) + Counter(pkg_bigram_count_dict[pkg]) #+ Counter(pkg_trigram_count_dict[pkg])
            merged_model[pkg] = single
        return merged_model


    def merge_tag(self,filename,topn=200):
        print "in merge tag_sim and desp_sim"
        if os.path.exists(filename):
            self.pkg_topSimilarity_dict = WriteTool.load_nested_dict(filename)
            return self.pkg_topSimilarity_dict 
        
        print "len of top_sim " +  str(len(self.pkg_topSimilarity_dict))
        for pkg,sim_dict in self.pkg_topSimilarity_dict.items():
            if pkg in self.jacard_sim_dict: 
                single = Counter(sim_dict) + Counter(self.jacard_sim_dict[pkg])
                single = dict(single)
                single = heapq.nlargest(200, single.items(), key=lambda e:e[1])
                self.pkg_topSimilarity_list[pkg] = single
                self.pkg_topSimilarity_dict[pkg] = {v[0]:v[1] for v in single}
            else:
                pass
                #print "[error in merge tag] pkg is " + pkg
        
        if filename:
            WriteTool.write_nested_dict(self.pkg_topSimilarity_dict,filename,self.pkg_titlename_dict) 


    def save_language_model(self,outFile):
        
        if outFile:
            of = open(outFile,'w')
            saveout = sys.stdout
            sys.stdout = of
       
        slist = sorted(self.pkg_dlcount_dict.items(),key=lambda e:e[1],reverse=True)
        #print "len of pkg_dlcount_dict:" + str(len(self.pkg_dlcount_dict))
        #print "len of slist:" + str(len(slist))
        for t in slist:
            self.print_language_model(t[0],outFile)
        
        if outFile:
            of.close()
            sys.stdout = saveout

    @staticmethod
    def print_single_model(d,pkgname):
        if pkgname not in d:
            return 
        sorted_list = sorted(d[pkgname].items(),key=lambda e:e[1],reverse=True)
        for t in sorted_list:
            print t[0]+":"+str("%.3f"%t[1])+", ",
        print ""


    def print_language_model(self,pkgname,outFile):
        if pkgname not in self.pkg_game_dict:
            return 
        self.count+=1
        print str(self.count) + ", " + pkgname+", "+ self.pkg_game_dict[pkgname][0][0]
        print "\ntitle:",
        self.print_single_model(self.pkg_title_tfidf_dict,pkgname)
        print "\ntag:",
        self.print_single_model(self.pkg_tag_tfidf_dict,pkgname)
        print "\nunigram:",
        self.print_single_model(self.pkg_unigram_tfidf_dict,pkgname)
        print "\nbigram:",
        self.print_single_model(self.pkg_bigram_tfidf_dict,pkgname)
        print "\ntrigram:",
        self.print_single_model(self.pkg_trigram_tfidf_dict,pkgname)
        print "\nafter merge:",
        self.print_single_model(self.pkg_tfidf_dict,pkgname)
    
    @staticmethod
    def write_dict(d,f):
        d = sorted(d.items(),key=lambda e:e[1],reverse=True)
        of = open(f,'w')
        for t in d:
            of.write(str(t[0]) + "\t" + str(t[1]) + "\n")
        of.close()

    def write_info(self):
        DespSimilarityProcessor.write_dict(LanguageModel.getTermCount(self.pkg_tag_dict),'./data/tag_list')
        DespSimilarityProcessor.write_dict(LanguageModel.getTermCount(self.pkg_merged_model_dict),'./data/term_list')
        
    @staticmethod
    def merged_doc_term_dict(doc_term_dict1, doc_term_dict2):
        print "in merge doc term dict"
        pkgs = set(doc_term_dict1.keys()) | set(doc_term_dict2.keys())
        merged_doc_term_dict = {}
        for pkg in pkgs:
            if pkg in doc_term_dict1 and pkg in doc_term_dict2:
                merged_doc_term_dict[pkg] = list(set(doc_term_dict1[pkg]) | set(doc_term_dict2[pkg]))
            elif pkg in doc_term_dict1:
                merged_doc_term_dict[pkg] = list(set(doc_term_dict1[pkg]))
            else:
                merged_doc_term_dict[pkg] = list(set(doc_term_dict2[pkg]))
        print "testing com.imangi.templerun2:"
        for word in merged_doc_term_dict['com.imangi.templerun2']:
            print word,
        print ""
        return merged_doc_term_dict



    def write_for_xiaoxi(self):
        temp_dict = {}
        sekf.pkg_unigram_tfidf_dict = LanguageModel.getTfidf(s.pkg_unigram_dict)
        for pkg,tempSet in s.pkg_setOfWords.items():
            if pkg in s.pkg_unigram_tfidf_dict:
                single = {word.strip():1.0 for word in tempSet if word.strip()}
                single = WriteTool.merge_dict(single , s.pkg_unigram_tfidf_dict[pkg],"max")
                temp_dict[pkg] = dict(single) 
        WriteTool.write_nested_dict(temp_dict,'data/blend_word_list_max1')

    
    def compute_field_jacardsim(self,doc_term_dict,filename="",offset=0):
        '''input dict is key:term_list '''
        print "in compute_field_jacardsim"
        if os.path.exists(filename):
            jacard_sim_dict = WriteTool.load_nested_dict(filename)
            return jacard_sim_dict

        weight_dict = {}
        if offset + s.log_min_dlcount > 0:
            weight_dict = {pkg: (offset+math.log(value)) / (offset+self.log_max_dlcount)  for pkg,value in self.pkg_dlcount_dict.items() }
        field_setOfWords = LanguageModel.getSetOfWords(doc_term_dict)
        jacard_sim_dict = LanguageModel.get_jacard_sim(field_setOfWords,weight_dict)
        
        if filename:
            WriteTool.write_nested_dict(jacard_sim_dict,filename,self.pkg_titlename_dict) 
        
        print str(len(jacard_sim_dict))
        return jacard_sim_dict


    def boost(self,nested_dict,offset,filename):
        print "in boost"
        if os.path.exists(filename):
            self.pkg_topSimilarity_dict = WriteTool.load_nested_dict(filename)
            return self.pkg_topSimilarity_dict 
        
        print "len of pkg_topSimilarity_dict " + str(len(s.pkg_topSimilarity_dict))
        weight_dict = {}
        if offset + s.log_min_dlcount > 0:
            weight_dict = {pkg: (offset+math.log(value)) / (offset+self.log_max_dlcount)  for pkg,value in self.pkg_dlcount_dict.items() }
        
        s.pkg_topSimilarity_dict = WriteTool.boost_nested_dict(s.pkg_topSimilarity_dict,weight_dict)
        
        if filename:
            WriteTool.write_nested_dict(s.pkg_topSimilarity_dict,filename,self.pkg_titlename_dict) 
        
        return self.pkg_topSimilarity_dict

    def blend(self):
        print "in blending,"+str(len(self.pkg_topSimilarity_list)) + "," + str(len(self.tag_sim_list)) + "," + str(len(self.desp_sim_list))
        for pkg in self.pkg_topSimilarity_dict:
            if pkg in self.tag_sim_list and pkg in self.desp_sim_list:
                i = 0
                i_top=0
                i_tag=0
                i_desp=0
                while i<100 and i<len(self.pkg_topSimilarity_list[pkg]):
                    #single = self.pkg_topSimilarity_list[pkg][i_top]
                    #print single[1]
                    self.blend_sim_dict[pkg][self.pkg_topSimilarity_list[pkg][i_top][0]] = self.pkg_topSimilarity_list[pkg][i_top][1]
                    i_top+=1
                    self.blend_sim_dict[pkg][self.tag_sim_list[pkg][i_tag][0]] = self.tag_sim_list[pkg][i_tag][1]
                    i_tag+=1
                    self.blend_sim_dict[pkg][self.pkg_topSimilarity_list[pkg][i_top][0]] = self.pkg_topSimilarity_list[pkg][i_top][1]
                    i_top+=1
                    self.blend_sim_dict[pkg][self.desp_sim_list[pkg][i_desp][0]] = self.desp_sim_list[pkg][i_desp][1]
                    i_desp+=1
                    i += 4
            elif pkg in self.tag_sim_dict:
                i = 0
                i_top=0
                i_tag=0
                while i<100 and i<len(self.pkg_topSimilarity_list[pkg]):
                    self.blend_sim_dict[pkg][self.pkg_topSimilarity_list[pkg][i_top][0]] = self.pkg_topSimilarity_list[pkg][i_top][1]
                    i_top += 1
                    self.blend_sim_dict[pkg][self.tag_sim_list[pkg][i_tag][0]] = self.tag_sim_list[pkg][i_tag][1]
                    i_tag +=1
                    i += 2

            elif pkg in self.desp_sim_dict:
                i = 0
                i_top=0
                i_desp=0
                
                while i<100 and i<len(self.pkg_topSimilarity_list[pkg]):
                    self.blend_sim_dict[pkg][self.pkg_topSimilarity_list[pkg][i_top][0]] = self.pkg_topSimilarity_list[pkg][i_top][1]
                    i_top += 1
                    self.blend_sim_dict[pkg][self.desp_sim_list[pkg][i_desp][0]] = self.desp_sim_list[pkg][i_desp][1]
                    i_desp += 1
                    i+=2
            else:
                while i<100:
                    self.blend_sim_dict[pkg][self.pkg_topSimilarity_list[pkg][i][0]] = self.pkg_topSimilarity_list[pkg][i][1]
                    i += 1

        print "in blending,len of blend_sim_dict is" + str(len(self.blend_sim_dict))
        for pkg in self.blend_sim_dict:
            self.blend_sim_list[pkg] = [(k,v) for k,v in self.blend_sim_dict[pkg].items()]


    def discount_title(self,sim_dict_dict,threshold=0.3,stop_value = 0.4,filename=""):
        print "in discount"
        discount_dict_dict = sim_dict_dict
        '''
        if os.path.exists(filename):
            discount_dict_dict = WriteTool.load_nested_dict(filename)
            return discount_dict_dict 
        print "len of dict to discount " + str(len(sim_dict_dict))
        '''
        total_match = 0
        
        for pkg,sim_dict in sim_dict_dict.items():
          
            if pkg not in self.title_sim_dict:
                continue
            match_num = 0
             
            sim_list = sorted(sim_dict.items(),key=lambda e:e[1],reverse=True)
            for idx,t in enumerate(sim_list):
                
                i = min(idx,11)
                discount = 1
                other = t[0]
                top_sim_list = [self.title_sim_dict[other][sim_list[j][0]]  for j in xrange(i) if other in self.title_sim_dict and sim_list[j][0] in self.title_sim_dict[other]]
                if top_sim_list:
                    max_sim = max(top_sim_list)
                else:
                    max_sim = 0
                if max_sim > threshold:
                    discount = max(discount * (1-max_sim)  ,stop_value)
                    discount_dict_dict[pkg][t[0]] = t[1] * discount
                    #match_num += 1
                    total_match +=1
                

                if other in self.title_sim_dict[pkg]: 
                    
                    
                    discount = max(discount*self.num_value_map(match_num) * (1-self.title_sim_dict[pkg][t[0]]  )  ,stop_value)
                    discount_dict_dict[pkg][t[0]] = t[1] * discount
                    match_num += 1
                    total_match+=1
                    if self.title_sim_dict[pkg][other] >= 0.75 and self.pkg_dlcount_dict[pkg] >= self.pkg_dlcount_dict[other]:
                        del discount_dict_dict[pkg][other]

        if filename:
            WriteTool.write_nested_dict(discount_dict_dict,filename,self.pkg_titlename_dict) 
        print "discount_dict_dict :" + str(len(discount_dict_dict)) + "total match " + str(total_match) 
        return discount_dict_dict



    def topn_rerank(self,n,threshhold):
        for pkg in self.pkg_topSimilarity_list:
            pos = n + 1
            for i in xrange(1,n):
                t = self.pkg_topSimilarity_list[pkg][i]
                other = t[0]
                sim_list = [self.title_sim_dict[other][self.pkg_topSimilarity_list[pkg][j][0]]  for j in xrange(i) if other in self.title_sim_dict and self.pkg_topSimilarity_list[pkg][j][0] in self.title_sim_dict[other]]
                if not sim_list:
                    continue
                max_sim = max(sim_list)
                if max_sim >= threshhold:
                   self.pkg_topSimilarity_list[pkg].remove(t)
                   self.pkg_topSimilarity_list[pkg].insert(pos,t)
                   pos += 1
            


    
    def num_value_map(self,num):
        if num==1:
            return 0.6
        elif num==2:
            return 0.85
        else:
            return 0.95
       


    @staticmethod
    def filter_nested_dict(sim_dict_dict,topn,threshold):
        filtered_sim_dict = {}
        for pkg,sim_dict in sim_dict_dict.items():
            single= {other:value for other,value in sim_dict.items() if other and value >= threshold }
            filtered_sim_dict[pkg]  = {t[0]:t[1] for t in heapq.nlargest(topn,single.items(),key=lambda e:e[1] )} 
        return filtered_sim_dict



if __name__ == '__main__':
    if len(sys.argv) != 4:
        print "<inFile><view_#verion><resut_#version>"
        sys.exit()
    
    version_num = filter(str.isdigit, sys.argv[2])
    if version_num != filter(str.isdigit, sys.argv[3]):
        print "<inFile><view_#verion><resut_#version> view version and result version should be the same, since I will use the version num to generate some data file"
        sys.exit
     
    s = DespSimilarityProcessor()
    
    s.inputData(sys.argv[1])
    s.title_sim_dict = s.compute_field_jacardsim(s.pkg_title_dict,"./data/title_sim"+str(version_num),-101)
    print s.title_sim_dict['com.ea.game.realracing2_na']['com.ea.games.r3_row']
    s.title_sim_dict = s.filter_nested_dict(s.title_sim_dict,50,0.09) 
    print "len of s.title_sim_dict " + str(len(s.title_sim_dict))
    print s.title_sim_dict['com.ea.game.realracing2_na']['com.ea.games.r3_row']
   
    s.jacard_sim_dict = s.compute_field_jacardsim(s.merged_doc_term_dict(s.pkg_title_dict,s.pkg_tag_dict),"./data/jacard_sim"+str(version_num),-101)
    

    # pkg_merged_model_dict is bag of words
    s.pkg_merged_model_dict = s.get_merge_model()
    s.pkg_merged_model_dict = LanguageModel.getTrimedDocTermDict(s.pkg_merged_model_dict,5)
    print "pkg_merged_model_dict : " + str(len(s.pkg_merged_model_dict))
    s.pkg_tfidf_dict = LanguageModel.getWeightedTfidf(s.pkg_merged_model_dict)
    print "pkg_ifidf_dict : " + str(len(s.pkg_tfidf_dict))
    s.pkg_tfidf_dict = LanguageModel.normalize(s.pkg_tfidf_dict,100)
    print "normalized pkg_ifidf_dict : " + str(len(s.pkg_tfidf_dict))
    #s.save_language_model('./data/language_model')
    s.invertedIndex = LanguageModel.getInvertedIndex(s.pkg_tfidf_dict)
    
    s.computerAllSimilarity2("./data/desp_sim"+str(version_num),200)
    s.merge_tag("./data/standard_sim"+str(version_num),200)
    s.boost(s.pkg_topSimilarity_dict,0,"./data/boosted_sim"+str(version_num))
    s.pkg_topSimilarity_dict = s.discount_title(s.pkg_topSimilarity_dict, 0.3 ,0.1,"./data/discounted_sim"+str(version_num))
    s.pkg_topSimilarity_dict = s.filter_nested_dict(s.pkg_topSimilarity_dict,100,0.001)
    
    print str(s.pkg_topSimilarity_dict['com.imangi.templerun2']['com.notdoppler.earntodie'])
    s.pkg_topSimilarity_list = WriteTool.nested_dict2list(s.pkg_topSimilarity_dict)
    #s.topn_rerank(11,0.3) 
    #s.pkg_topSimilarity_dict = WriteTool.nested_list2dict(s.pkg_topSimilarity_list)
    s.dumpData() 
    s.write_info()
    s.saveResult(s.pkg_topSimilarity_list,sys.argv[2],sys.argv[3])
