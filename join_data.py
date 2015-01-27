#encoding=utf-8
__author__ = 'starsdeep'
import os
import sys
reload(sys)
sys.setdefaultencoding('UTF8')
import MySQLdb


class DataJoinProcessor():

    online_pkg_dict = {}
    online_title_dict = {}
    ano_pkg_dict = {}
    wandoujia_pkg_dict = {}

    num_online = 0
    num_ano = 0
    num_wandoujia = 0
    
    num_wdj_joined = 0
    num_pp_joined = 0
    num_ano_joined = 0
    num_keyword_joined = 0
    
    num_final_added = 0

    def __init__(self):
        pass


    def Strip(self,fields):
        for field in fields:
            if isinstance(field,unicode):
                field = field.strip()
        if len(fields[2]) <= 2:
            fields[2] =''
        
        if fields[1] == 'hjf.game.ncgy10':
            print 'title:' + fields[0]
            print 'pkgname:' + fields[1]
            print 'tag:'  + fields[2]
            print 'len of tag:' + str(len(fields[2]))

        return fields

    def Has_tags_and_description(self,fields):
        return len(fields[2].strip()) > 0  or len(fields[3].strip()) > 0


    def Has_description(self,fields):
        return len(fields[3].strip()) > 0


    def Input_online_data(self):
        try:
            conn = MySQLdb.connect(host='10.99.48.85', port=3308,user='app_vertical', passwd='CKD2agk2TBU3m', db='app_vertical', charset='utf8')
            cur = conn.cursor()
            self.num_online = cur.execute("select title,package_name,tags,description,download_count,comment_count,size,business_type,download_url,detail_info_url from all_app where resource_type=1 and  title!='' and package_name!='' and download_url!='' ")
            self.online_pkg_dict = {item[1].strip(): self.Strip(list(item)) for item in cur.fetchall()}
        except Exception, e:
            print "[Error]:", e
        finally:
            cur.close()
            conn.close()
 

    def Input_annotation_data(self):
        try:
            conn = MySQLdb.connect(host='10.99.48.85', user='app_platform', passwd='QsF21iJOgp3HX', db='app_platform', port=3308, charset='utf8')
            cur = conn.cursor()
            self.num_ano = cur.execute("select app,android_pkg,tags from app_annotation  where app!='' and android_pkg!='' and tags!='' ")
            self.ano_pkg_dict = {item[1].strip(): self.Strip(list(item)) for item in cur.fetchall()}
        except Exception, e:
            print "[Error]:", e
        finally:
            cur.close()
            conn.close()
        print "a sample from ano_pkg_dict : " + str(self.ano_pkg_dict['org.cocos2d.fishingjoy3.uc'.decode('utf-8')])

    def Input_wandoujia_data(self):
        try:
            conn = MySQLdb.connect(host='10.99.20.92', user='root', passwd='shenma123', db='mobile_game', charset='utf8')
            cur = conn.cursor()
            self.num_wandoujia = cur.execute("select pkgname,title,tag,description,download_num,comment_num,size,url from wandoujia_data_new")
            self.wandoujia_pkg_dict = {item[0].strip(): list(item) for item in cur.fetchall()}
        except Exception, e:
            print "[Error]:", e
        finally:
            cur.close()
            conn.close()

    
    

    def Join_online_pp(self):
        print "in join pp"
        for item in open('./data/seged_pp'):
            fields = item.split('\t')
            pkg = fields[1].strip()
            if pkg in self.online_pkg_dict:
                tag1 = fields[2].split(',')
                tag2 = fields[3].split(',')
                tags = tag1 +tag2
                tags = [t.strip() for t in tags if t.strip()]
                if self.online_pkg_dict[pkg][2]:
                   self.online_pkg_dict[pkg][2] += '、' + '、'.join(tags)
                else:
                   self.online_pkg_dict[pkg][2] += '、'.join(tags)
                self.num_pp_joined +=1


    def Join_online_ano(self):
        for pkg,game in self.online_pkg_dict.items():
            if pkg in self.ano_pkg_dict:
                game[2] += '' + self.ano_pkg_dict[pkg][2]
                self.num_ano_joined += 1
            #else:
            #    print pkg
            #    print 'pkg of online data:' + str(type(pkg))
            #    print 'pkg of ano data:' + str(type(pkg))
        #self.online_title_dict = {item[0]: list(item) for item in self.online_pkg_dict.values()}


    def Join_online_wandoujia(self):
        for pkg,game in self.online_pkg_dict.items():
            temp_list = pkg.split('.')
            if temp_list[-1] == 'uc':
                temp_list = temp_list[0:-1]
            pkg = '.'.join(temp_list)
            
            if pkg == "com.soulgame.bubble":
                print "online has:" + pkg
                if pkg in self.wandoujia_pkg_dict:
                    print "in !!!!!!!!"
            
            if pkg in self.wandoujia_pkg_dict:
                tags = self.wandoujia_pkg_dict[pkg][2].replace('\002','、').strip()
                game[2] += '、' + tags
                self.num_wdj_joined += 1

    def Join_online_keyword(self,inFile):
        for line in open(inFile,'r'):
            items = line.strip().split('\t')
            pkg = items[0]
            tags = "、".join(items[1:])
            if pkg and tags and pkg in self.online_pkg_dict:
                self.online_pkg_dict[pkg][2] += "、" + tags
                self.num_keyword_joined += 1

    def Add_data_to_DB(self):
        try:
            conn = MySQLdb.connect(host='10.99.20.92', user='root', passwd='shenma123', db='mobile_game', charset='utf8')
            cur = conn.cursor()
            cur.execute("TRUNCATE TABLE all_game")
            sqlcmd = "insert into all_game(title,pkg_name,tags,description,download_count,comment_count,size,business_type,download_url,detail_info_url) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            for game in self.online_pkg_dict.values():
                try:
                    if self.Has_description(game):
                        self.num_final_added += 1
                        cur.execute(sqlcmd,tuple(game))
                except Exception, e:
                    print "[Error]:", e
                    print game[0]
                    sys.exit()
            conn.commit()
        except Exception, e:
            print "[Error]:", e
            sys.exit()
        finally:
            cur.close()
            conn.close()

    def PrintResult(self):
        print "Data input from online database:" + str(self.num_online)
        print "Data input from annotation database:" + str(self.num_ano)
        print "Data joined annotation data:" + str(self.num_ano_joined)
        print "Data joined pp data:" + str(self.num_pp_joined)
        print "Data joined wdj data:" + str(self.num_wdj_joined)
        print "Data joined keyword data:" + str(self.num_keyword_joined)
        print "Data Added to dabase:" + str(self.num_final_added)


    def SegmentWord(self):
        tmp_of = open('temp_desp','w')
        try:
            conn = MySQLdb.connect(host='10.99.20.92', user='root', passwd='shenma123', db='mobile_game', charset='utf8')
            cur = conn.cursor()
            num_all_game = cur.execute("select description from all_game")
            print "num of all game:" + str(num_all_game)
            for d in cur.fetchall():
                if len(d) < 1:
                    print "[Error]:description should not be empty!!!"
                    sys.exit()
                tmp_of.write(d[0].strip()+'\n')
            tmp_of.close()
        except Exception, e:
            print "[Error]:", e
        finally:
            cur.close()
            conn.close()

        os.system('/apsarapangu/disk5/yikang.liao/workspace/SegmentationProject/build/release64/bin/segment_word_rwc temp desp.txt')


if __name__ == '__main__':

    s = DataJoinProcessor()
    s.Input_online_data()
    s.Input_annotation_data()
    s.Input_wandoujia_data()
    s.Join_online_ano()
    s.Join_online_wandoujia()
    s.Join_online_pp()
    s.Join_online_keyword('data/keywords.txt')
    s.Add_data_to_DB()
    #s.SegmentWord()
    s.PrintResult()
    

