#encoding=utf8
import sys,os,re
import MySQLdb
curPath = os.path.abspath(os.path.split(os.path.realpath(__file__))[0])
sys.path.append(curPath + "/../common/")
sys.path.append(curPath + "/../filter/")
from StringTool import StringTool
from collections import defaultdict,Counter
from WriteTool import WriteTool
import math
import heapq
reload(sys)
sys.setdefaultencoding('UTF8')



def input_data():
    try:
        conn = MySQLdb.connect(host='10.99.48.85', port=3308,user='app_vertical', passwd='CKD2agk2TBU3m', db='app_vertical', charset='utf8')
        cur = conn.cursor()
        num_online = cur.execute("select package_name,description from all_app where resource_type=1 and  title!='' and package_name!='' and download_url!='' and description!='' ORDER BY download_count DESC LIMIT 12000")
        pkg_desp_dict = {item[0].strip():item[1].strip() for item in cur.fetchall() if item[0].strip() and item[1].strip()}
    except Exception, e:
        print "[Error]:", e
    finally:
        cur.close()
        conn.close()
    
    return pkg_desp_dict 

def sentence_extraction(sentence):

    result_list = re.findall(r"(?<=一款)[^!.。！]*?(?=游戏)".decode('utf-8'), sentence)
    result_list += re.findall(r"(?<=这款)[^!.。！]*?(?=游戏)".decode('utf-8'), sentence)
    
    return result_list

    

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "<output file,data/key_sentence.txt>"
        sys.exit()
    
    sentence_extraction("八戒咖喱结果这是一款坑爹的游戏发了几个垃圾")
     
    pkg_desp_dict = input_data()
    pkg_key_dict = {} 
    for pkg,desp in pkg_desp_dict.items():
        key = sentence_extraction(desp)
        if key:
            pkg_key_dict[pkg] = key
    
    of = open(sys.argv[1],'w')
    for pkg,key_list in pkg_key_dict.items():
        key_str = "".join(key_list)
        of.write(pkg + "\t" +  key_str + "\n")
    of.close()
    
