#encoding=utf8
import sys,os,math
import MySQLdb
from WriteTool import WriteTool
from GetFromFile import GetFromFile
from AppInfoFromRecords import AppInfoFromRecords
from GetFromDB import GetFromDB
reload(sys)
sys.setdefaultencoding('UTF8')





def blend_list(list1,list2):
    # list1 : list2  =  2 : 1
    list3 = []
    while list1 and list2:
        list3.append(list1.pop(0))
        list3.append(list2.pop(0))
        if list1:
            list3.append(list1.pop(0))
        else:
            break
   
    if list1:
        list3 += list1
    if list2:
        list3 += list2

    return list3


if __name__ == '__main__':
    
    if len(sys.argv) != 4:
        print "<discountedSim><cfFile><outFile>"
        sys.exit()
     
    outFile = sys.argv[3]
    discountedSim = WriteTool.load_nested_dict(sys.argv[1])
    discountedSimList = WriteTool.nested_dict2list(discountedSim)
    sim_rank = {game:[p[0] for p in sim_list] for game,sim_list in discountedSimList.items() if game and sim_list}
    cf_rank = WriteTool.load_list_dict(sys.argv[2])
   
    

    
    overall_rank = {}
    for game,cf_list in cf_rank.items():
        if game not in sim_rank and len(cf_list) >= 50:
            overall_rank[game] = cf_list
        if game in sim_rank:
            overall_rank[game] = blend_list(cf_list,sim_rank[game])
    
    mobile_db = GetFromDB("10.99.20.92","root",'shenma123','mobile_game')
    online_db = GetFromDB("10.99.48.85","rw_yulin",'xakX7VmPk7Ef8','app_vertical',3308)
    mobile_records = mobile_db.getRecords("select pkg_name,title,download_count from all_game order by download_count desc")
    online_records = online_db.getRecords("select package_name,title,download_count,count(distinct title) from all_app group by title order by download_count DESC")
    
    MGI = AppInfoFromRecords(mobile_records)
    OGI = AppInfoFromRecords(online_records)

    pkg_list = OGI.get_pkg_list()
    online_pkg_titlename_dict = OGI.get_pkg_titlename_dict() 
    pkg_titlename_dict = MGI.get_pkg_titlename_dict()
    for pkg,title in online_pkg_titlename_dict.items():
        if not pkg in pkg_titlename_dict:
            pkg_titlename_dict[pkg] = title
    
    WriteTool.write_list_dict(overall_rank,outFile,pkg_titlename_dict,pkg_list) 
