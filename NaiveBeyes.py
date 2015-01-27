#encoding=utf8
import sys,os,heapq,math
from collections import defaultdict,Counter
from LanguageModel import LanguageModel
from WriteTool import WriteTool
from ComputeJacardSim import ComputeJacardSim
from GetFromFile import GetFromFile
from GetFromDB import GetFromDB
import ClassifyGame
reload(sys)
sys.setdefaultencoding('UTF8')

class NaiveBeyes():

    total = 0
    cate_num_dict = {}
    anoed_pkgs = set()
    pkg_cate_dict = {}
    pkg_desp_dict = {}
    notCate_desp_dict = {}
    pkg_titlename_dict = {}
    all_pkg_desp_dict = {}
    vocabulary = {}
    bagOfWords = {}
    not_bagOfWords = {}
    logLikelihoodOfWords = {}
    not_logLikelihoodOfWords = {}
    cat_distinctValue_dict = {}
    game2classify = {}
    titleTag2classify = {}

    cate_pkgs_dict = {}
    cate_desp_dict = {}
    topCat = ""
    secondCat = []

    def __init__(self,topCat):
        self.topCat = topCat
        self.secondCat = ClassifyGame.topCat_secondCat_dict[self.topCat]

    def _input_classified_game(self):
        print "in input_classified_game"
        cat2remove = []
        for cat in self.secondCat:
            pkgs = self._input_pkgs(ClassifyGame.get_filename(self.topCat,cat)) 
            if pkgs:
                self.cate_pkgs_dict[cat] = pkgs
                self.cate_num_dict[cat] = len(pkgs)
                self.total += self.cate_num_dict[cat]
                print cat + ':' + str(len(self.cate_pkgs_dict[cat])) + ", ",
            else:
                print cat + "0!!!",
                cat2remove.append(cat)
        print "total:" + str(self.total)
        for cat in cat2remove:
            self.secondCat.remove(cat)

    def _input_pkgs(self,inFile):
        pkgs = []
        if os.path.isfile(inFile): 
            content = open(inFile).read().strip()
            pkgs = [pkg.strip() for pkg in content.split('\t') if pkg.strip()]
        else:
            print inFile + " not exist"
        return pkgs

    def _input_game_ano(self,inFile):
        for line in open(inFile,'r').readlines():
            game = [field.strip() for field in line.split('\001')]
            self.anoed_pkgs.add(game[0])

    def _input_game_desp(self,inFile):
        g = GetFromFile(inFile)
        self.pkg_titlename_dict = g.get_pkg_titlename_dict()
        pkg_titletag_dict = g.get_pkg_title_dict()
        pkg_unigram_dict = g.get_pkg_unigram_dict()

        self.all_pkg_desp_dict = WriteTool.merge_nested_list(pkg_titletag_dict,pkg_unigram_dict)
        self.pkg_desp_dict = {pkg:desp for pkg,desp in self.all_pkg_desp_dict.items() if pkg and desp and pkg in self.anoed_pkgs}
        self.game2classify = {pkg:desp for pkg,desp in self.all_pkg_desp_dict.items() if pkg and desp and pkg not in self.anoed_pkgs} 
        self.titleTag2classify = {pkg:desp for pkg,desp in pkg_titletag_dict.items() if pkg and desp and pkg not in self.anoed_pkgs}

    def _get_despOfCate(self,cate):
        desp = [] 
        pkgs = self.cate_pkgs_dict[cate]
        for pkg in pkgs:
            if pkg == '' or pkg not in self.pkg_desp_dict:
                print cate
                sys.exit()
            desp += self.pkg_desp_dict[pkg]
        return desp

    def _get_despOfNotCate(self,cate):
        desp = []
        if cate == 'Null':
            for cat in self.secondCat:
                if cat == cate:
                    continue
                desp += self._get_despOfCate(cat)
        else:
            for cat in self.secondCat:
                if cat == cate or cat == 'Null':
                    continue
                desp += self._get_despOfCate(cat)
        return desp

    def _getSmallestCat(self,cate_list):
        cate_dict = {k:v for k,v in self.cate_num_dict.items() if k in cate_list}
        return min(cate_dict.iterkeys(),key = lambda k:cate_dict[k])


    def inputData(self):
        self._input_game_ano(sys.argv[1])
        self._input_game_desp(sys.argv[2])
        self._input_classified_game()
        
        self.vocabulary = LanguageModel.getVocabulary(self.pkg_desp_dict)
        self.vocabulary = {word:1 for word in self.vocabulary if word}
        for cat in self.secondCat:
            self.cate_desp_dict[cat] = self._get_despOfCate(cat)
            self.notCate_desp_dict[cat] = self._get_despOfNotCate(cat)

        print "get desp okay,info of self.cate_desp_dict",
        WriteTool.get_nested_data_info(self.cate_desp_dict)
        print "info of self.notCate_desp_dict",
        WriteTool.get_nested_data_info(self.notCate_desp_dict)
    
    def train_phrase1(self):
        
        self.bagOfWords = LanguageModel.getBagOfWords(self.cate_desp_dict)
        self.not_bagOfWords = LanguageModel.getBagOfWords(self.notCate_desp_dict)
        

        for doc in self.bagOfWords:
            self.bagOfWords[doc] = Counter(self.bagOfWords[doc]) + Counter(self.vocabulary)
        for doc in self.not_bagOfWords:
            self.not_bagOfWords[doc] = Counter(self.not_bagOfWords[doc]) + Counter(self.vocabulary)

        self.bagOfWords = LanguageModel.getTrimedDocTermDict(self.bagOfWords,5)
        self.not_bagOfWords = LanguageModel.getTrimedDocTermDict(self.not_bagOfWords,5)
        
        print "compute log likelihood"
        for doc,temp_dict in self.bagOfWords.items():
            doc_len = sum(temp_dict.values())
            self.logLikelihoodOfWords[doc] = {word:math.log(1.0*value / doc_len) for word,value in temp_dict.items() }
        print 
        for doc,temp_dict in self.not_bagOfWords.items():
            doc_len = sum(temp_dict.values())
            self.not_logLikelihoodOfWords[doc] = {word:math.log(1.0*value / doc_len) for word,value in temp_dict.items() }

        for cat in self.secondCat:
            single = WriteTool.merge_single_dict(self.logLikelihoodOfWords[cat],self.not_logLikelihoodOfWords[cat],"minus" )        
            self.cat_distinctValue_dict[cat] = {t[0]:t[1] for t in heapq.nlargest(100,single.items(),key = lambda e:e[1])}
            
        WriteTool.write_nested_dict(self.cat_distinctValue_dict,'data/GameClassify/NB_distinct_words_' + self.topCat)
        WriteTool.write_nested_dict(self.bagOfWords,'data/GameClassify/NB_bagOfWords_' + self.topCat)
        WriteTool.write_nested_dict(self.not_bagOfWords,'data/GameClassify/NB_not_bagOfWords_' + self.topCat)
        WriteTool.write_nested_dict(self.logLikelihoodOfWords,'data/GameClassify/NB_logLikelihood_' + self.topCat)
        WriteTool.write_nested_dict(self.not_logLikelihoodOfWords,'data/GameClassify/NB_not_logLikelihood_' + self.topCat)
        WriteTool.write_dict(NB.vocabulary,'data/vocabulary_anoedGame.txt')
       

    def train_phrase2(self):
        self.cat_distinctValue_dict = WriteTool.load_nested_dict('data/GameClassify/NB_distinct_words_' + self.topCat)
        vocabulary = set()
        for cat,temp_dict in self.cat_distinctValue_dict.items():
            vocabulary = vocabulary | set(temp_dict.keys())
        
        bagOfWords = LanguageModel.getBagOfWords(self.cate_desp_dict,vocabulary)
        print "compute log likelihood"
        logLikelihoodOfWords = {}
        for doc,temp_dict in bagOfWords.items():
            doc_len = sum(temp_dict.values())
            logLikelihoodOfWords[doc] = {word:math.log(1.0*value / doc_len) for word,value in temp_dict.items() }
        WriteTool.write_nested_dict(logLikelihoodOfWords,'data/GameClassify/NB_logLikelihood_' + self.topCat + '_2')

    
    def classify_1(self):
        self.logLikehoodOfWords = WriteTool.load_nested_dict('data/GameClassify/NB_logLikelihood_' + self.topCat)
        self.bagOfWords2classify = LanguageModel.getBagOfWords(self.game2classify)
        print "bagOfWords2classify:" + str(len(self.bagOfWords2classify))
        num = 0
        for pkg,temp_dict in self.bagOfWords2classify.items():
            num += 1
            if num%1000 == 0:
                print str(num)
            cat_posterior_dict = {}
            for cat in self.secondCat:
                cat_posterior_dict[cat] = self._logPosterior(cat,temp_dict)
            max_cat = max(cat_posterior_dict.iterkeys(),key = lambda k:cat_posterior_dict[k])
            self.pkg_cate_dict[pkg] = max_cat 
            if pkg == 'skt.board.single':
                print "skt.board.single : "
                for cat,value in cat_posterior_dict.items():
                    print "cat:" + str(value)
    
    
    def classify_2(self):
        self.logLikehoodOfWords = WriteTool.load_nested_dict('data/GameClassify/NB_logLikelihood_' + self.topCat + '_2')
        self.cat_distinctValue_dict = WriteTool.load_nested_dict('data/GameClassify/NB_distinct_words_' + self.topCat)
        vocabulary = set()
        for cat,temp_dict in self.cat_distinctValue_dict.items():
            vocabulary = vocabulary | set(temp_dict.keys())
        
        self.bagOfWords2classify = LanguageModel.getBagOfWords(self.game2classify,vocabulary)
        print "bagOfWords2classify:" + str(len(self.bagOfWords2classify))
        num = 0
        for pkg,temp_dict in self.bagOfWords2classify.items():
            num += 1
            if num%1000 == 0:
                print str(num)
            cat_posterior_dict = {}
            for cat in self.secondCat:
                cat_posterior_dict[cat] = self._logPosterior(cat,temp_dict)
            max_cat = max(cat_posterior_dict.iterkeys(),key = lambda k:cat_posterior_dict[k])
            self.pkg_cate_dict[pkg] = max_cat 
            if pkg == 'skt.board.single':
                print "skt.board.single : "
                for cat,value in cat_posterior_dict.items():
                    print "cat:" + str(value)

    def _logPosterior(self,cate,temp_dict):
        logLikelihood = self.logLikehoodOfWords[cate]
        sum_of_logLikelihood  = sum([1.0 * value * logLikelihood[word] for word,value in temp_dict.items() if  word in logLikelihood])
        sum_of_logPosterior = sum_of_logLikelihood + math.log(1.0 * self.cate_num_dict[cate] / self.total)
        return sum_of_logPosterior 


    def classifyByTitleTag(self):  
        setOfWords = LanguageModel.getSetOfWords(self.titleTag2classify)
        #print "in classifyByTitleTag"
        #print "len of titleTag2classify:" + str(len(self.titleTag2classify))
        #print "len of setOfWords:" + str(len(setOfWords))
        #print "len of pkg_cate_dict:" + str(len(self.pkg_cate_dict))
        for pkg in self.pkg_cate_dict:
            cat_list = []
            if pkg not in setOfWords:
                continue
            for cat in self.secondCat:
                if cat in setOfWords[pkg]:
                    cat_list.append(cat)
                if cat in self.pkg_titlename_dict[pkg]:
                    cat_list.append(cat)
                if cat_list:
                    self.pkg_cate_dict[pkg] = self._getSmallestCat(cat_list)
        
        #print "testing,炫彩艺术,com.natenai.artofglow"
        #print "titleTag"
        #for word in self.titleTag2classify['com.natenai.artofglow']:
        #    print word,
        #print "\nsetOfWords"
        #for word in setOfWords['com.natenai.artofglow']:
        #    print word,
        #print "testing,火柴人战争2,com.gamevil.cartoonwars.gunner.cn"
        #print "titleTag"
        #for word in self.titleTag2classify['com.gamevil.cartoonwars.gunner.cn']:
        #    print word,
        #print "\nsetOfWords"
        #for word in setOfWords['com.gamevil.cartoonwars.gunner.cn']:
        #    print word,

    def writeResult(self,suffix=""):
        WriteTool.write_dict(NB.pkg_cate_dict,'data/GameClassify/classify_by_' + self.topCat + suffix)
        of = open('data/GameClassify/classify_by_' + self.topCat + '_view' + suffix,'w')
        for pkg,cate in NB.pkg_cate_dict.items():
            of.write(pkg + '\t' + NB.pkg_titlename_dict[pkg] + '\t' + cate + '\n')


def mergeResult(suffix):
    dic = {}
    for topCat in ClassifyGame.topCat_secondCat_dict:
        dic[topCat] = WriteTool.load_dict('data/GameClassify/classify_by_' + topCat + suffix)
    pkgs = dic[topCat].keys()
    g = GetFromFile()
    pkg_titlename_dict = g.get_pkg_titlename_dict()
    
    print "saving merged result in " + 'data/GameClassify/classify_by_all' + '_view' + suffix
    of = open('data/GameClassify/classify_by_all' + '_view' + suffix,'w')
    of.write('pkgname\001title\001')
    for topCat in dic:
        of.write(topCat + '\001')
    of.write('\n')
    for pkg in pkgs:
        of.write(pkg + '\001' )
        of.write(pkg_titlename_dict[pkg] + '\001')
        for topCat in dic:
            of.write(dic[topCat][pkg] + '\001')
        of.write('\n')
    of.close()

    print "saving classify_info in " +  'data/GameClassify/classify_info' + suffix
    #write statistics
    of = open('data/GameClassify/classify_info' + suffix,'w')
    cat_num_dict = {}
    cat_persentage_dict = {}
    for topCat in dic:
        cat_num_dict = getInfo(topCat,dic[topCat])
        s = sum(cat_num_dict.values())
        cat_persentage_dict = {cat:1.0*num/s for cat,num in cat_num_dict.items() if cat and num}
        hitNum = s - cat_num_dict['Null']
        recall = 1 - cat_persentage_dict['Null']
        
        cat_num_dict = {cat:str(num) for cat,num in cat_num_dict.items()}
        cat_persentage_dict = {cat:'%.2f'%num for cat,num in cat_persentage_dict.items()}
        
        of.write(topCat + '\n')
        of.write('recall' + '\t' + '\t'.join(cat_num_dict.keys()) + '\n')
        of.write(str(hitNum) + '\t' + '\t'.join(cat_num_dict.values()) + '\n')
        of.write('%.2f'%recall + '\t' + '\t'.join(cat_persentage_dict.values()) + '\n')
        of.write('\n')
        

def getInfo(topCat,pkg_cat_dict):
    cat_num_dict = defaultdict(lambda :0)
    for pkg,cat in pkg_cat_dict.items():
        cat_num_dict[cat] += 1
    return cat_num_dict



if __name__ == '__main__':
    if len(sys.argv) != 3:
        print "<inFile1, data/game_ano.txt><inFile2,data/game_input_all>"
        sys.exit()
     
    for topCat in ClassifyGame.topCat_secondCat_dict:
        print "\ntraining " + topCat + " ======================"
        NB = NaiveBeyes(topCat)    
        NB.inputData()
        NB.train_phrase1()
        NB.classify_1()
        NB.classifyByTitleTag()
        NB.writeResult("_1")
    
    
    ''' 
    NB = NaiveBeyes('scene')    
    NB.inputData()
    #NB.train_phrase1()
    #NB.classify_1()
    NB.classifyByTitleTag()
    #NB.train_phrase2()
    #NB.classify_1()
    #NB.classifyByTitleTag()
    #NB.writeResult("_1")
    '''
    
    mergeResult("_1")







