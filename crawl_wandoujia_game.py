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


def strConvert(number):
    if number.isdigit():
        return int(number)
    elif u"万" in number:
        number = number.replace(u'万','')
        number = int(float(number) * 10000)
    elif u"亿" in number:
        number = number.replace(u'亿','')
        number = int(float(number) * 100000000)
    else:
        return -1
    return number

class GameCrawler():
    def __init__(self):
        self.driver = webdriver.PhantomJS(executable_path='/usr/local/bin/phantomjs')

    def __del__(self):
        self.driver.quit()

    def process(self, url):
        #try:
        num = 0
        if True:
            self.driver.get(url)
            try:
                self.driver.find_element_by_partial_link_text("更多").click()
                #for i in driver.find_elements_by_css_selector("a.more-link"):
                    #i.click()
                    #time.sleep(1)
            except Exception, ex:
                print "在" + str(url) + '''中不能找到“更多”按钮'''
                #print ex
            #for i in driver.find_elements_by_css_selector("dd.tag-box"):
            name = u"None"
            try:
                i = self.driver.find_element_by_css_selector('p.app-name>span')
                name = i.text
            except:
                name = u"None"
            desp = u"None"
            try:
                i = self.driver.find_element_by_css_selector('div[itemprop="description"]')
                desp = i.text
            except:
                desp = u"None"
            #print desp
            install_number = -1
            try:
                i = self.driver.find_element_by_css_selector('i[itemprop="interactionCount"]')
                install_number = i.text
                install_number = strConvert(install_number)
            except:
                install_number = -1
            #print install_number
            like_number = -1
            try:
                i = self.driver.find_element_by_css_selector('span.love>i')
                like_number = i.text
                #like_number = i.find_element_by_tag_name('i').text
                like_number = strConvert(like_number)
                #print like_number
            except:
                like_number = -1
            comment_number = -1
            try:
                i = self.driver.find_element_by_css_selector('a.comment-open>i')
                comment_number = i.text
                comment_number = strConvert(comment_number)
                #print comment_number
            except:
                comment_number = -1
            tag = []
            try:
                for i in self.driver.find_elements_by_css_selector("dd.tag-box>a"):
                    tag.append(i.text.encode('utf-8'))
                    #print i.text
            except:
                tag = []
            file_size = -1
            try:
                i = self.driver.find_element_by_css_selector('meta[itemprop="fileSize"]')
                file_size = int(i.get_attribute("content"))
                #print comment_number
            except:
                file_size = -1


            
            '''
            for i in driver.find_elements_by_css_selector('div.change-info'):
                for j in i.find_elements_by_css_selector('div.con'):
                    app_name = j.text
                    print app_name
            '''
            return name.encode('utf-8'), desp.encode('utf-8'), install_number, like_number, comment_number, file_size, tag
        #except Exception, e:
            #print e

    def crawl(self, inFileName, outFileName):
        outFile = open(outFileName, 'w')
        for line in open(inFileName):
            items = line.split('\t')
            if len(items) == 5:
                pkgname = items[0].strip()
                name = items[1].strip()
                child_cate = items[2].strip()
                cate = items[3].strip()
                url = items[4].strip()
                get_name, desp, install, like, comment, file_size, tag = self.process(url)
                if len(tag) > 0:
                    tagStr = '\002'.join(tag)
                else:
                    tagStr = "None"
                outFile.write(pkgname+'\001'+ name + '\001' + child_cate + '\001' + cate + '\001' + tagStr + '\001' + desp + '\001' + str(install) + '\001' + str(like) + '\001' + str(comment) + '\001' + str(file_size) + '\001' + url + '\n\003\n')
        outFile.close()
        #desp, install, like, comment, tag = self.process("http://www.wandoujia.com/apps/com.kiloo.subwaysurf")
        #print desp

if __name__ == '__main__':

    if len(sys.argv) != 3:
        print '<wandoujia_game_url_list><output_file_name>'
        sys.exit()
    g = GameCrawler()
    g.crawl(sys.argv[1], sys.argv[2])
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
