#encoding=utf8
import sys
from GetFromDB import GetFromDB
reload(sys)
sys.setdefaultencoding('UTF8')





def Join_keyword(inFile,pkg_tag_dict):
    for line in open(inFile,'r'):
        items = line.strip().split('\t')
        pkg = items[0]
        tags = "、".join(items[1:])
        if pkg and tags and pkg in pkg_tag_dict:
            pkg_tag_dict[pkg]+= "、" + tags
        return pkg_tag_dict


if __name__ == '__main__':

    if len(sys.argv) != 2:
        print "<keywords.txt>"
        sys.exit()

    db = GetFromDB("10.99.20.92","root",'shenma123',"mobile_game")
    sqlcmd = "select pkg_name, tags from all_game"
    records = db.getRecords(sqlcmd)
    pkg_tag_dict = {item[0]:item[1] for item in records if item[0].strip()}

    pkg_tag_dict = Join_keyword('data/keywords.txt',pkg_tag_dict)

    for pkg,tag in pkg_tag_dict.items():
        if pkg and tag:
            sqlcmd = r"UPDATE all_game SET tags = '%s' WHERE pkg_name = '%s'" % (tag,pkg)
            db.ExecuteSQL(sqlcmd)



