#encoding=utf8
import sys
from collections import defaultdict
from WriteTool import WriteTool
from GetFromFile import GetFromFile
reload(sys)
sys.setdefaultencoding('UTF8')


def load():
    sim_dict = defaultdict(list)
    line_num = 0
    for line in open('data/final_result','r').readlines():
        line_num += 1
        if line.find('\001') >= 0:
            pkg = line.strip().strip('\001').strip()
        elif line.find('\002') >= 0:
            other = line.strip().strip('\002').strip()
            sim_dict[pkg].append(other)
        else:
            print "error in line:" + str(line_num)
    print "load dict okay,len is " + str(len(sim_dict))
    return sim_dict



if __name__ == '__main__':
    if len(sys.argv) != 4:
        print "<discountedSim><inFile><outFile>"
        sys.exit()

    #discountedSim = WriteTool.load_nested_dict(sys.argv[1])
    #discountedSim_list = WriteTool.nested_dict2list(discountedSim)
    g = GetFromFile(sys.argv[2]) 
    pkg_list = g.get_pkg_list()
    pkg_titlename_dict = g.get_pkg_titlename_dict()
    
    sim_dict = load()
    of = open(sys.argv[3],'w')
    for pkg in pkg_list:
        if pkg not in sim_dict:
            continue
        of.write(pkg + '\001')
        for t in sim_dict[pkg]:
            of.write(t + '\002')
        of.write('\n')
    of.close
    
    
    ''' 
    of = open('data/pkg_list','w')
    for pkg in pkg_list:
        if pkg not in discountedSim or not pkg  in pkg_titlename_dict:
            continue
        of.write(pkg + '\t' + pkg_titlename_dict[pkg] + '\n')
    of.close()
    '''
