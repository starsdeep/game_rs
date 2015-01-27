#encoding=utf8
import sys
reload(sys)
sys.setdefaultencoding('UTF8')
import pexpect

def doScp(user,password, host, path, files):
    fNames = ' '.join(files)
    print fNames
    child = pexpect.spawn('scp %s %s@%s:%s' % (fNames, user, host,path))
    print 'scp %s %s@%s:%s' % (fNames, user, host,path)
    i = child.expect(['password:', r"yes/no"], timeout=30)
    if i == 0:
        child.sendline(password)
    elif i == 1:
        child.sendline("yes")
        child.expect("password:", timeout=30)
        child.sendline(password)
    data = child.read()
    print data
    child.close()


if __name__ == '__main__':
    user = 'yikang.liao'
    password = '123456'
    host = '10.99.20.92'
    path = '~/game_rds'
    files = ['data/title_sim','data/titleTag_sim','data/desp_sim','data/merged_sim','data/boosted_sim','data/discounted_sim']
    doScp(user,password,host,path,files)

