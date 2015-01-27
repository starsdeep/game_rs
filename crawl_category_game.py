#!/usr/bin/env python
#encoding=utf-8
import urllib2, re, urllib
from bs4 import BeautifulSoup
import time
import sys, os

curPath = os.path.abspath(os.path.split(os.path.realpath(__file__))[0])

sys.path.append(curPath + "/../common/")
sys.path.append(curPath + "/../filter/")
from Logger import Logger
from StringTool import StringTool
import Common
from filter_entity_game_new import *
from selenium import webdriver

def process(outFileName, click_times):
    #try:
    game_dict = {}
    num = 0
    if True:
        driver = webdriver.PhantomJS(executable_path='/usr/local/bin/phantomjs')
        category_dict = {}
        url = 'http://www.wandoujia.com/tag/game'
        req = urllib2.Request(url)
        res_html = urllib2.urlopen(req, timeout=60).read().decode('utf-8', 'ignore')
        soup = BeautifulSoup(res_html)
        i = soup.find('ul', 'tag-box')
        for j in i.findAll('li', recursive=False):
            cate = j.find('span', 'cate-name').text
            print '------',cate
            if cate != None:
                category_dict[cate] = []
                k = j.find('div', 'child-cate')
                for l in k.findAll('a', recursive=False):
                    print l.text
                    category_dict[cate].append(l.text)
        outFile = open(outFileName, 'w')
        for cate,cate_list in category_dict.iteritems():
            print "crawling:" + cate
            for child_cate in cate_list:
                num += 1
                cateurl = urllib.quote(child_cate.encode('utf-8'))
                url = 'http://www.wandoujia.com/tag/' + cateurl
                
                driver.get(url)
                try:
                    for i in range(click_times):
                        driver.find_element_by_id("j-refresh-btn").click()
                        time.sleep(1)
                except Exception, ex:
                    print 'http://www.wandoujia.com/tag/'+child_cate + ': refresh time is ' + str(i)
                    #print ex
                for i in driver.find_elements_by_css_selector("div.app-desc"):
                    j = i.find_element_by_tag_name("a")
                    site = j.get_attribute('href')
                    if site is None:
                        site = u"None"
                        pkgname = u"None"
                    else:
                        pkgname = site.split(r'/')[-1]
                        subpkg = pkgname.split('.')
                        suffix = subpkg[-1]
                        if suffix == 'wdj':
                            pkgname = '.'.join(subpkg[0:-1])
                    app_name = j.text
                    game_dict[site] = (pkgname,app_name, child_cate, cate)

        for site, value in game_dict.iteritems():
            outFile.write(value[0].encode('utf-8') + '\t' + value[1].encode('utf-8') + '\t' + value[2].encode('utf-8') + '\t' + value[3].encode('utf-8') + '\t'  + site.encode('utf-8') + '\n')

        outFile.close()
        driver.quit
    #except Exception, e:
        #print e

if __name__ == '__main__':
    if len(sys.argv) != 3 or (len(sys.argv) == 3 and not sys.argv[2].isdigit()):
        print '<out_file><click_times>'
        sys.exit()
    process(sys.argv[1], int(sys.argv[2]))
#for i in soup.findAll('li', {'class': 'parent-cate '}):
    #print i.find('span', 'cate-name').text
'''
driver = webdriver.PhantomJS(executable_path='/usr/local/bin/phantomjs')
driver.get("http://www.wandoujia.com/top/app")
for i in range(10):
    driver.find_element_by_id("j-refresh-btn").click()
    time.sleep(1)
for i in driver.find_elements_by_css_selector("div.app-desc"):
    print i.text.encode('utf-8')
    print i.find_element_by_tag_name("a").text
print driver.current_url
driver.quit
'''
