#encoding=utf8
import sys,os
curPath = os.path.abspath(os.path.split(os.path.realpath(__file__))[0])
sys.path.append(curPath + "/../common/")
sys.path.append(curPath + "/../filter/")
sys.path.append(curPath + "/../")
from qp_accessor import QPAccessor
reload(sys)
sys.setdefaultencoding("UTF8")

if __name__ == '__main__':
    
    print "test QPAccessor"
    retArr = QPAccessor.getQPSegQuery('炫彩泡泡龙')
    
    for item in retArr:
        print item
