import sys, os
curPath = os.path.abspath(os.path.split(os.path.realpath(__file__))[0])

sys.path.append(curPath + "/../common/")
sys.path.append(curPath + "/../filter/")
from StringTool import StringTool

of = open('ndesp','w')

for line in open('seged_game_desp.txt','r').readlines():
    for word in line.strip().split('\t'):
        nword = StringTool.normalizedStr(word.strip())
        if len(nword.strip())>0:
            of.write(nword.strip()+'\t')
    of.write('\n')
