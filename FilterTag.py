#encoding=utf-8

import os,sys
import re
curPath = os.path.abspath(os.path.split(os.path.realpath(__file__))[0])
sys.path.append(curPath + "/../common/")
sys.path.append(curPath + "/../filter/") 

    

def get_filtered_set(tag_set, single_list):
    return {tag.strip() for tag in single_list if tag.strip() and tag.strip() in tag_set}

    
       


if __name__ == '__main__':
    
    if len(sys.argv) != 4:
        print "<tagFile><inFile><outFile>"
        sys.exit()

    tag_set = {line.strip() for line in open(sys.argv[1],'r') if line.strip()}
    sentence_list = [ line.strip().split('\t') for line in open(sys.argv[2],'r') ]
    keywords_list = [ temp_list[0:1] + list(get_filtered_set(tag_set,temp_list))  for temp_list in sentence_list if temp_list and temp_list[0] ]

    of = open(sys.argv[3],'w')
    for temp_list in keywords_list:
        of.write("\t".join(temp_list) + "\n")


