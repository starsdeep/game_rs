#encoding=utf8
import sys,os
from collections import defaultdict,Counter
from LanguageModel import LanguageModel
from StringTool import StringTool
from WriteTool import WriteTool
from TitleClean import TitleClean
reload(sys)
sys.setdefaultencoding('UTF8')



class GetFromFile():
    pkg_list = []
    pkg_titlename_dict = {}
    titlename_pkg_dict = defaultdict(list)
    pkg_title_dict = {}
    pkg_tag_dict = {}
    pkg_unigram_dict = {}
    pkg_bigram_dict = {}
    pkg_desp_dict = {}
    pkg_doclen_dict = {}

    def __init__(self,inFile = './data/game_input_all' ):
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
            
            self.pkg_list.append(pkgname)
            self.pkg_titlename_dict[pkgname] = title_list[0] 
            self.pkg_title_dict[pkgname] = title_list if len(title_list) < 3 else title_list[1:]
            self.pkg_tag_dict[pkgname] = tag_list
            self.pkg_desp_dict[pkgname] = desp_list
            self.pkg_unigram_dict[pkgname] = unigram_list
            self.pkg_bigram_dict[pkgname] = bigram_list
            #self.pkg_trigram_dict[pkgname] = trigram_list
            
            self.pkg_doclen_dict[pkgname] = len(self.pkg_title_dict[pkgname]) + len(self.pkg_tag_dict[pkgname])+len(self.pkg_unigram_dict[pkgname])+len(self.pkg_bigram_dict[pkgname]) # + len(self.pkg_trigram_dict[pkgname])
        
        print "game input:" + str(len(self.pkg_title_dict))



    def get_pkg_desp_dict(self):
        print "in get_merge_model"
        weight_title = 1.0
        weight_tag = 1.0
        weight_desp = 1.0

        weight_unigram = (1.0/1.4)*weight_desp
        weight_bigram = (0.4/1.4)*weight_desp
        #weight_trigram = (0.16/1.56)*weight_desp
        
        #pkg_title_count_dict = {}
        #pkg_tag_count_dict = {}
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

        pkg_desp_dict = {}
        for pkg in self.pkg_title_dict:
            #single = Counter(pkg_title_count_dict[pkg]) + Counter(pkg_tag_count_dict[pkg]) + Counter(pkg_unigram_count_dict[pkg]) + Counter(pkg_bigram_count_dict[pkg]) #+ Counter(pkg_trigram_count_dict[pkg])
            single = Counter(pkg_unigram_count_dict[pkg]) + Counter(pkg_bigram_count_dict[pkg]) #+ Counter(pkg_trigram_count_dict[pkg])
            pkg_desp_dict[pkg] = single
        
        print "get desp okay,pkg_desp_dict" + str(len(pkg_desp_dict))
        return pkg_desp_dict

    def get_pkg_list(self):
        return self.pkg_list

    def get_pkg_title_dict(self):
        return self.pkg_title_dict
    
    def get_pkg_titlename_dict(self):
        return self.pkg_titlename_dict

    def get_pkg_cleanedTitlename_dict(self):
        TC = TitleClean()
        return {pkg.strip():TC.clean(titlename.strip()) for pkg,titlename in self.pkg_titlename_dict.items() if pkg.strip() and titlename.strip()}

    def get_pkg_unigram_dict(self):
        return self.pkg_unigram_dict

    def get_pkg_bigram_dict(self):
        return self.pkg_bigram_dict

    def get_pkg_titletag_dict(self):
        return WriteTool.merge_nested_list(self.pkg_title_dict,self.pkg_tag_dict)


    def get_titlename_pkg_dict(self):
        for pkg,titlename in self.pkg_titlename_dict.items():
            self.titlename_pkg_dict[titlename].append(pkg)
        print "test get_titlename_pkg_dict '神庙逃亡'"
        print ','.join(self.titlename_pkg_dict['神庙逃亡'])
        return self.titlename_pkg_dict
