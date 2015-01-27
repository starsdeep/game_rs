#!/usr/bin/env python
# -*- coding: utf8 -*-
import os
import sys
import re
import sets
import MySQLdb

rootPath = os.path.dirname(os.path.abspath(os.path.split(os.path.realpath(__file__))[0]))
sys.path.append(rootPath + "/common/")
sys.path.append(rootPath + "/filter/")
import Common
from Logger import Logger
from StringTool import StringTool
from FileTool import FileTool
reload(sys)
sys.setdefaultencoding('UTF8')

def cleanData(datalist):
    name = datalist[0]
    if name.endswith('...'):
        utf_list = StringTool.getUtfTokensList(name)
        for index in range(len(utf_list)):
            item = utf_list[index]
            if len(item) == 3:
                if not isinstance(item, unicode):
                    item = item.decode("utf-8")
                if not StringTool.is_chinese(item):
                    break
            else:
                break
            name = "".join(utf_list[0:index])
    if name == "":
        return False

    for idx in range(1, len(datalist)):
        datalist[idx] = datalist[idx].strip()
    return True



def process():

    try:
        conn = MySQLdb.connect(host='10.99.20.92', user='root', passwd='shenma123', db='mobile_game', charset='utf8')
        cur = conn.cursor()
        cur.execute("TRUNCATE TABLE wandoujia_data_new")
        for game in open('./data/seged_wdj').readlines():
            fields = game.split('\001')
            if len(fields) != 11:
                continue
            if not cleanData(fields):
                continue
                print '[Warning]:' + str(fields)

            #sqlcmd = "insert into wandoujia_data_new(nam,size, download_num, like_num, comment_num, url, key_tag, category, tag, description) select %s as `size`, %s as `download_num`, %s as `like_num`, %s as `comment_num`, %s as `url`, %s as `key_tag`, %s as `category`, %s as `tag`, %s as `description`, " + str1
            sqlcmd = "insert into wandoujia_data_new(pkgname,title,key_tag,category,tag,description,download_num,like_num,comment_num,size,url) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) "

            try:
                cur.execute(sqlcmd, tuple(fields))
            except Exception, e:
                print "[Error]:", e
                print fields[0]
        #print len(to_add)
        #for item in to_add:
            #print item
        conn.commit()

    except Exception, e:
        print "[Error]:", e
    finally:
        cur.close()
        conn.close()


def clean():
    content = open('./data/wdj_game_data').read()
    of = open('./data/cleaned_wdj_game_data','w')
    games = content.split('\003')
    for game in games:
        game = game.strip()
        if game:        
            game = game.replace('\n',"")
            game = game.replace('\\n',"")
            of.write(game+"\n")
    of.close()


if __name__ == '__main__':
    #clean()
    process()

