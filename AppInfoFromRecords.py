#encoding=utf8
import sys
from collections import defaultdict
from WriteTool import WriteTool
from TitleClean import TitleClean
from GetFromDB import GetFromDB
from TitleClean import TitleClean

class AppInfoFromRecords:
    def __init__(self,records):
        
        print "records is [pkgname,title,download_count]"
        self.pkg_list = []
        self.pkg_titlename_dict = {}
        self.pkg_dlcount_dict = {}
        self.records = records

    def dump_cleaned_title(self):
        TC = TitleClean()
        s = set()
        of = open('data/all_game_cleaned_title','w')
        n = 0
        for line in self.records:
            if line and line[1].strip():
                t = TC.clean(line[1].strip().encode('utf-8'))
                if t not in s:
                    n += 1
                    of.write(t.strip() + '\n')
                    s.add(t)
        print "dump cleaned_title okay,len is " + str(n) + ", location is data/all_game_clean_title"


    def dump_title(self):
        for line in self.records:
            if line and line[1].strip():
                of.write(line[1].strip() + '\n')
        of.close()

    def get_pkg_list(self):
        for line in self.records:
            self.pkg_list.append(line[0].strip())
        return self.pkg_list

        
    def get_pkg_titlename_dict(self):
        for line in self.records:
            self.pkg_titlename_dict[line[0].strip()] = line[1].strip()
        return self.pkg_titlename_dict

    def get_pkg_dlcount_dict(self):
        for line in self.records:
            self.pkg_dlcount_dict[line[0].strip()] = int(line[3])
        return self.pkg_dlcount_dict


    def get_title_pkg_dict(self):
        if not self.pkg_dlcount_dict:
            self.get_pkg_dlcount_dict()
        title_pkgs_dict = defaultdict(list)
        TC = TitleClean()
        for line in self.records:
            title_pkgs_dict[TC.clean(line[1].encode('utf-8'))].append(line[0].strip())

        title_pkg_dict = {}
        for title,pkgs in title_pkgs_dict.items():
            pkg = max(pkgs,key = lambda pkg:self.pkg_dlcount_dict[pkg])
            title_pkg_dict[title] = pkg
       
        
        #WriteTool.write_dict(self.pkg_dlcount_dict,"data/pkg_dlcount_dict")
        #WriteTool.write_dict(title_pkg_dict,"data/title_pkg_dict")
        WriteTool.write_list_dict(title_pkgs_dict,"data/title_pkgs_dict")
        return title_pkg_dict


    def get_cate_pkg_dict(self):
        title_cate_dict = {}
        for line in self.records:
            title_cate_dict[line[1].encode('utf-8')] = line[2]
        return title_cate_dict
            
    
