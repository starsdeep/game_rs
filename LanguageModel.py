#encoding=utf8
import sys,os
import MySQLdb
curPath = os.path.abspath(os.path.split(os.path.realpath(__file__))[0])
sys.path.append(curPath + "/../common/")
sys.path.append(curPath + "/../filter/")
from StringTool import StringTool
from collections import defaultdict
import math
import heapq
reload(sys)
sys.setdefaultencoding('UTF8')
import cPickle as p

class LanguageModel():

    @staticmethod
    def getTermCount(doc_term_dict,write=0):
        print "in get term count"
        term_count_dict = defaultdict(lambda:0)
        for doc, terms in doc_term_dict.items():
            for term in set(terms):
                term_count_dict[term] += 1
        if write:
            LanguageModel.write_dict(term_count_dict,'data/word_list'+str(write))
        return term_count_dict


    @staticmethod
    def getStopWordSet(term_count_dict,min=1,max=0):
        if max:
            return {k for k,v in term_count_dict.items() if k and (v<=min or v>max) }
        else:
            return {k for k,v in term_count_dict.items() if k and v <= min}

    @staticmethod
    def getVocabulary(doc_term_dict,stopSet={}):
        setOfWords = set()
        for doc,terms in doc_term_dict.items():
            setOfWords = setOfWords | set(terms)
        if stopSet:
            setOfWords = {word for word in setOfWords if word and word not in stopSet} 
        return setOfWords

    @staticmethod
    def getTrimedDocTermDict(doc_term_dict,stopSet):
        doc_count_dict = LanguageModel.getTermCount(doc_term_dict,1)
        stopSet = LanguageModel.getStopWordSet(doc_count_dict,5)
        
        for line in open('data/idf_let5').readlines():
            temp_list = line.strip().split('\t')
            
            if len(temp_list)<2:
                continue
            word = temp_list[0]
            value = int(temp_list[1])
            if value<=3 or len(word)==3 and value<=5:
                stopSet.add(word)
        for line in open('./data/stop_word_list600'):
            if line.strip():
                stopSet.add(line.strip())
        print "test stop_word_list600:"
        print str('了' in stopSet)

        trimed_doc_term_dict = {}
        for doc,temp_dict in doc_term_dict.items():
            single = {k:v for k,v in temp_dict.items() if k and k not in stopSet}
            if doc == "com.android.girlfriends":
                print doc + ":" + str(single)
            if single:
                trimed_doc_term_dict[doc] = single
        print "original word number:" + str(len(doc_term_dict)) + " after trimmed:" + str(len(trimed_doc_term_dict))


        return trimed_doc_term_dict    





    @staticmethod
    def get_idf(doc_term_dict):
        print "in get idf"
        term_count_dict = defaultdict(lambda:0)
        for doc, terms in doc_term_dict.items():
            for term in set(terms):
                term_count_dict[term] += 1
      
        num_doc = len(doc_term_dict)
        term_idf_dict = {k:math.log(1.0* num_doc / v ) for k,v in term_count_dict.items() if k}
        LanguageModel.write_dict(term_idf_dict,'./data/word_idf_list') 
        return term_idf_dict


    @staticmethod
    def write_dict(d,f):
        d = sorted(d.items(),key=lambda e:e[1],reverse=True)
        of = open(f,'w')
        for t in d:
            of.write(str(t[0]) + "\t" + str(t[1]) + "\n")
        of.close()

    '''
    @staticmethod
    def getBagOfWords(doc_term_dict):
        bagOfWords = {}
        for doc,terms in doc_term_dict.items():
            termSet = set(terms)
            term_count_dict = { term:terms.count(term) for term in termSet if term.strip()!='' }
            bagOfWords[doc] = term_count_dict
    
        return bagOfWords
    '''
    @staticmethod
    def getBagOfWords(doc_term_dict,vocabulary={} ):
        bagOfWords = {}
        for doc,terms in doc_term_dict.items():
            single = defaultdict(lambda :0)
            for term in terms:
                if vocabulary and term not in vocabulary:
                    continue
                single[term] += 1
            bagOfWords[doc] = dict(single)
            single.clear()
        return bagOfWords

    @staticmethod
    def getSetOfWords(doc_term_dict):
        print "in get setOfWords"
        stopSet = {'的','大','游戏','休闲','益智','单机','网游','1','2','3','4','5','6'}
        for word in open('./data/stop_suffix.txt','r'):
            stopSet.add(word.strip())
        
        setOfWords = {}
        for doc,terms in doc_term_dict.items():
            termSet = {t.strip() for t in set(terms) if t.strip() and t.strip() not in stopSet}
            if termSet:
                setOfWords[doc] = termSet
        print "orginal length of doc_term_dict:" + str(len(doc_term_dict)) + " setOfWords length:" + str(len(setOfWords))
        print "testing set of words:"
        if 'com.mobirate.officegamebox' in setOfWords:
            print "com.mobirate.officegamebox: ",
            for word in setOfWords['com.mobirate.officegamebox']:
                print word,
        if 'com.digiplex.game' in setOfWords:
            print "\ncom.digiplex.game: ",
            for word in setOfWords['com.digiplex.game']:
                print word
                
        return setOfWords

    @staticmethod
    def get_single_jacard_sim(set1,set2):
        if set1 and set2:
            return 1.0 * len(set1 & set2) / len(set1 |  set2)


    @staticmethod
    def get_jacard_sim(setOfWords,doc_weight={},topn=200):
        print "in get jacard sim"
        jacard_sim_dict = {}
        jacard_sim_list = {}
        num = 0
        if not doc_weight: 
            for doc in setOfWords:
                num +=1;
                if num%500 == 0:
                    print str(num)
                single = {other.strip():LanguageModel.get_single_jacard_sim(setOfWords[doc],setOfWords[other]) for other in setOfWords if other.strip() and doc!=other } 
                jacard_sim_list[doc] = heapq.nlargest(topn,single.items(),key = lambda e:e[1])
                jacard_sim_dict[doc] = {t[0]:t[1] for t in jacard_sim_list[doc] if t} 
        else: 
            for doc in setOfWords:
                num +=1;
                if num%500 == 0:
                    print str(num)
                single = {other.strip():LanguageModel.get_single_jacard_sim(setOfWords[doc],setOfWords[other]) for other in setOfWords if other.strip() and doc!=other } 
                single = heapq.nlargest(200,single.items(),key = lambda e:e[1])
                if doc in doc_weight:
                    jacard_sim_list[doc] = [(t[0],t[1] * doc_weight[t[0]]) for t in single if t[0] ]
                    jacard_sim_dict[doc] = {t[0]:t[1] for t in jacard_sim_list[doc] if t} 
        print "testing jacard sim," + " com.imangi.templerun and com.imangi.templerun2 is:" + str(jacard_sim_dict['com.imangi.templerun']['com.imangi.templerun2']) 
        print 'com.imangi.templerun2:' 
        for word in setOfWords['com.imangi.templerun2']:
            print word,
        print '\ncom.imangi.templerun:'
        for word in setOfWords['com.imangi.templerun']:
            print word,
        #print "com.BifrostStudios.ZombieJuice and com.ggnes.contra3:" + str(jacard_sim_dict['com.BifrostStudios.ZombieJuice']['com.ggnes.contra3'])
        
        return jacard_sim_dict


    @staticmethod
    def getTfOfWords(doc_term_dict,doc_length_dict={},minDocLength=0):
        tfOfWords = {}
       
        for doc,terms in doc_term_dict.items():
            doclen = doc_length_dict[doc] if doc_length_dict else len(terms)
            if minDocLength:
                doclen = max(minDocLength,doclen)
            termSet = set(terms)
            term_count_dict = { term:1.0*terms.count(term)/doclen for term in termSet if term.strip()!='' }
            tfOfWords[doc] = term_count_dict
        
        #print "testing getTfOfWords: count of '捕鱼':" + str(doc_term_dict['org.cocos2dx.FishGame'].count('捕鱼'))+",total is:"+str(len(doc_term_dict['org.cocos2dx.FishGame']))
        #print "tf:" + str(tfOfWords['org.cocos2dx.FishGame']['捕鱼'])
        return tfOfWords

    
    @staticmethod
    def getWeightedTfOfWords(doc_term_dict,minDocLength=0):
        tfOfWords = {}
       
        for doc,term_dict in doc_term_dict.items():
            doclen = minDocLength if minDocLength else sum(term_dict.values())
            term_count_dict = {k:1.0*v/doclen for k,v in term_dict.items() if k }
            tfOfWords[doc] = term_count_dict
        
        #print "testing getTfOfWords: count of '捕鱼':" + str(doc_term_dict['org.cocos2dx.FishGame'].count('捕鱼'))+",total is:"+str(len(doc_term_dict['org.cocos2dx.FishGame']))
        #print "tf:" + str(tfOfWords['org.cocos2dx.FishGame']['捕鱼'])
        return tfOfWords

    @staticmethod
    def getTfidf(doc_term_dict,doc_length_dict={},minDocLength=0):
        print "in get Tfidf"
        tfidfOfWords = {}
        term_count = LanguageModel.getTermCount(doc_term_dict)
        
        tfOfWords = LanguageModel.getTfOfWords(doc_term_dict,doc_length_dict)
        num_doc = len(tfOfWords)
        for doc,tfs in tfOfWords.items():
            tfidfOfWords[doc] = {term:1.0 * tf * math.log(num_doc / term_count[term]) for term,tf in tfs.items() }    
        
        if '捕鱼' in term_count:
            print "get tfidf ok,testing '捕鱼'" 
            print "testing getTfOfWords: count of '捕鱼':" + str(doc_term_dict['org.cocos2dx.FishGame'].count('捕鱼'))+",total is:"+str(len(doc_term_dict['org.cocos2dx.FishGame']))
            print "total doc:"+str(len(doc_term_dict)) + "  doc count:" + str(term_count['捕鱼'])
            if '捕鱼' in tfOfWords['org.cocos2dx.FishGame']:   
                print "tf:" + str(tfOfWords['org.cocos2dx.FishGame']['捕鱼'])
                print "tfidf:" + str(tfidfOfWords['org.cocos2dx.FishGame']['捕鱼'])
            print "\n\n"

        return tfidfOfWords
    
    @staticmethod
    def getWeightedTfidf(doc_term_dict,minDocLength=0):
        print "in get weighted Tfidf"
        tfidfOfWords = {}
        doc_term_dict0 = {k:v.keys() for k,v in doc_term_dict.items()}
        term_count = LanguageModel.getTermCount(doc_term_dict0,2)
        t = LanguageModel.get_idf(doc_term_dict0)
        
        tfOfWords = LanguageModel.getWeightedTfOfWords(doc_term_dict,minDocLength)
        num_doc = len(tfOfWords)
        for doc,tfs in tfOfWords.items():
            tfidfOfWords[doc] = {term:1.0 * tf * math.log(num_doc / term_count[term]) for term,tf in tfs.items() }    
        
        if '捕鱼' in term_count:
            print "get tfidf ok,testing '捕鱼' in org.cocos2dx.FishGame " 
            print "testing getTfOfWords: count of '捕鱼':" + str(doc_term_dict['org.cocos2dx.FishGame']['捕鱼'])+",total is:"+str(len(doc_term_dict['org.cocos2dx.FishGame']))
            print "total doc:"+str(len(doc_term_dict)) + "  doc count:" + str(term_count['捕鱼'])
            if '捕鱼' in tfOfWords['org.cocos2dx.FishGame']:   
                print "tf:" + str(tfOfWords['org.cocos2dx.FishGame']['捕鱼'])
                print "tfidf:" + str(tfidfOfWords['org.cocos2dx.FishGame']['捕鱼'])
            print "\n\n"
        
        print "getWeighted tfidf okay,pkg_ifidf_dict : " + str(len(tfidfOfWords))
        return tfidfOfWords


    @staticmethod
    def normalize(tfidfOfWords,minDocLength=0):
        print "in normalize "
        normalized_tfidfOfWords = {}
        num =0
        for doc,temp_dict in tfidfOfWords.items() :
            num +=1;
            if num%5000 == 0:
                print num
            
            sum_of_squares = math.sqrt(sum([pow(value, 2) for value in temp_dict.values()]))
            if sum_of_squares==0:
                print "sum sqluqre is 0, doc is " + doc 
                continue
            weight = 1.0 * len(temp_dict) / minDocLength
            if weight>1:
                weight = 1.0
            normalized_tfidfOfWords[doc] = {k:weight * v / sum_of_squares for k,v in temp_dict.items() if k}

        print "normalized okay, pkg_ifidf_dict : " + str(len(normalized_tfidfOfWords))
        return normalized_tfidfOfWords




    def computeWordWeight(self):

        self.buildWordList()
        
        print "dumping okay!"
        
        self.word_weight_dict = {word: math.log(self.num_all_game * 1.0 / count) for word, count in self.Fword_count_dict.items() }

        for pkg in self.pkg_desp_dict:
            single1 = {word:self.word_weight_dict[word] for word in self.pkg_desp_dict[pkg] if word in self.Fword_count_dict}
            sum_of_squares = math.sqrt(sum([pow(value, 2) for value in single1.values() ]))
            single2 = {word:value/sum_of_squares for word,value in single1.items()}
            self.per_pkg_word_weight_dict[pkg] = single2
        
        #normalize
        print "鬼屋魅影2"
        for k,v in self.per_pkg_word_weight_dict['com.furiousapps.haunt2'].items():
            print "key:"+k +" value:"+str(v)

        print "鬼屋魅影2"
        print "original len:" + str(len(self.pkg_desp_dict['com.furiousapps.haunt2']))
        print "after filtering:" + str(len(self.per_pkg_word_weight_dict['com.furiousapps.haunt2']))
        for k,v in self.per_pkg_word_weight_dict['com.furiousapps.haunt2'].items():
            print k+' ',
            
    @staticmethod
    def getInvertedIndex(doc_tfidf_dict):
        print "in get inverted index"
        term_doc_dict = defaultdict(dict)
        for doc,d in doc_tfidf_dict.items():
            for word, weight in d.items():
                term_doc_dict[word][doc] = weight
        return term_doc_dict


    @staticmethod
    def getInvertedIndex_list(doc_term_dict):
        print "in get inverted index list version"
        term_doc_dict = defaultdict(set)
        for doc,temp_list in doc_term_dict.items():
            for word in temp_list:
                term_doc_dict[word].add(doc)
        return term_doc_dict



if __name__ == '__main__':

    print "this is language model"
