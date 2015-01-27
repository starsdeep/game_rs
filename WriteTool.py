#encoding=utf8
import sys,os
from collections import defaultdict,Counter
import math
import heapq
reload(sys)
sys.setdefaultencoding('UTF8')
import cPickle as p



class WriteTool():

    @staticmethod
    def dump_data(d,f):
        print "dump to " + f
        f = file(f, 'w')
        p.dump(self.pkg_tfidf_dict, f) # dump the object to a file
        f.close()


    @staticmethod
    def get_nested_data_info(d):
        num_key = len(d)
        total_len = 0
        average_len = 0
        for k,temp_dict in d.items():
            total_len += len(temp_dict)
        average_len = 1.0*total_len / num_key
        print "print info of dict"
        print "num of key:" + str(num_key) + ", total len:" + str(total_len) + ", average len:" + str(average_len)
        return num_key,total_len,average_len

    @staticmethod
    def write_dict(d,f,first_line=''):
        d = sorted(d.items(),key=lambda e:e[1],reverse=True)
        of = open(f,'w')
        if first_line:
            of.write(first_line + '\n')
        for t in d:
            of.write(str(t[0]) + '\t' + str(t[1]) + '\n')
        of.close()

    @staticmethod
    def load_dict(f):
        dic = {}
        for line in open(f,'r').readlines():
            if not line.strip():
                continue
            temp_list = line.strip().split('\t')
            if len(temp_list) == 2:
                dic[temp_list[0].strip()] = temp_list[1].strip()
        return dic     

    @staticmethod
    def write_list_dict(dic,outFile,key_title_dict = {},sorted_list = []):
        print "write list_dict to " + outFile
        of = open(outFile,'w')
        if not sorted_list:
            sorted_list = dic.keys()
        for k in sorted_list:
            if k in dic:
                of.write(k + '\001')
                of.write('\002'.join(dic[k]) + '\n')

        if not key_title_dict:
            return 
        of.close()
        of = open(outFile+"_view",'w')
        for k in sorted_list:
            if k in dic:
                of.write(k)
                if k in key_title_dict:
                    of.write('\t' + key_title_dict[k])
                of.write('\001\n')
                for pkg in dic[k]:
                    of.write(pkg)
                    if pkg in key_title_dict:
                        of.write('\t' + key_title_dict[pkg])
                    of.write('\002\n')
        of.close() 



    @staticmethod
    def load_list_dict(inFile,sep1='\001',sep2='\002'):
        print "load list_dict from: " + inFile
        list_dict = {}
        num = 0;
        for line in open(inFile,'r'):
            num += 1
            key_value_list = line.strip().split(sep1)
            if len(key_value_list) != 2:
                print str(num) + ":" + line
                sys.exit()
            
            key = key_value_list[0].strip()
            value = key_value_list[1].strip()
            temp_list = value.split(sep2)
            list_dict[key] = list(temp_list)
        print "load okay, len is:" + str(len(list_dict))
        return  list_dict


    @staticmethod
    def write_nested_dict(d,f,key_title_dict = {},sorted_key_list=[]):
        print "write nested_dict to " + f
        of = open(f,'w')
        if not sorted_key_list:
            sorted_key_list = d.keys()

        for k in sorted_key_list:
            if not k or not k in d:
                continue
            temp_dict = d[k]
            of.write(str(k)+'\001\n')
            sorted_list = sorted(temp_dict.items(),key=lambda e:e[1],reverse=True)
            for t in sorted_list:
                if t[0]:
                    of.write(str(t[0]) + "\004"+ str(t[1]) + "\003")
            of.write('\002\n')
        of.close()

        if not key_title_dict:
            return 
        of = open(f+"_view",'w')
        for k in sorted_key_list:
            if not k or not k in d:
                continue
            temp_dict = d[k]
            of.write(str(k) + "\t" + str(key_title_dict[k]) +'\001\n')
            sorted_list = sorted(temp_dict.items(),key=lambda e:e[1],reverse=True)
            if k =='com.ea.game.realracing2_na':
                t = sorted_list[0]
                print t[0] + ":" + str(t[1])
                
            for t in sorted_list:
                if t[0]:
                    of.write(str(t[0]) + "\t" + str(key_title_dict[t[0]]) + "\t"+ str(t[1]) + "\002\n")
        of.close() 


    @staticmethod 
    def load_nested_dict(inputfile):
        print "load old result from " + inputfile 
        pkg = ''
        nested_dict = {}
        line_num = 0
        for line in open(inputfile):
            if line.strip():
                line_num += 1
                if line.find('\001')>0:
                    pkg=line.strip().strip('\001').strip()
                if line.find('\002')>0:
                    line = line.strip().strip('\002').strip()
                    single_dict = {}
                    #single_dict  ={t[0].strip():float(t[1]) for t in item.split('\004') if t and t[0] (for item in line.split('\003') if item.strip() ) }  
                    for item in line.split('\003'):
                        t = item.split('\004') 
                        if t and t[0]:
                            single_dict.update({t[0].strip():float(t[1])})
                    nested_dict[pkg] = single_dict
        
        print "loading nested_dict okay,size is " + str(len(nested_dict))
        return nested_dict



    @staticmethod
    def boost_nested_dict(nested_dict,weight_dict):
        boost_dict = {} 
        if weight_dict:
            for key,temp_dict in nested_dict.items():
                boost_dict[key] = {k:v * weight_dict[k] for k,v in temp_dict.items() if k and k in weight_dict}
        return boost_dict

    @staticmethod
    def nested_dict2list(nested_dict):
        nested_list_dict = {}
        for key,temp_dict in nested_dict.items():
            nested_list_dict[key] = sorted(temp_dict.items(),key = lambda e:e[1],reverse = True)
        return nested_list_dict 
    
    @staticmethod
    def nested_list2dict(nested_list):
        nested_dict_dict = {}
        for k,temp_list in nested_list.items():
            nested_dict_dict[k] = {t[0]:t[1] for t in temp_list}
        return nested_dict_dict


    @staticmethod
    def merge_single_dict(d1,d2,mode="sum"):
        d3 = {}
        if mode=="sum":
            d3 =  dict(Counter(d1)+ Counter(d2))
        elif mode=="max":
            s = set(d1.keys()) | set(d2.keys())
            for k in s:
                if k in d1 and k in d2:
                    d3[k] = max(d1[k],d2[k])   
                elif k in d1:
                    d3[k] = d1[k]
                else:
                    d3[k] = d2[k]
        elif mode=="min":
            s = set(d1.keys()) | set(d2.keys())
            for k in s:
                if k in d1 and k in d2:
                    d3[k] = min(d1[k],d2[k])   
                elif e in d1:
                    d3[k] = d1[k]
                else:
                    d3[k] = d2[k]
        elif mode =="minus":
            s = set(d1.keys()) | set(d2.keys())
            for k in s:
                if k in d1 and k in d2:
                    d3[k] = d1[k] - d2[k]  
                elif k in d1:
                    d3[k] = d1[k]
                else:
                    d3[k] = d2[k]
        else:
            print "[error]:wrong operation. only suppor sum,max,min,minus"
        return d3


    @staticmethod
    def filter_nested_dict(sim_dict_dict,topn,threshold):
        filtered_sim_dict = {}
        for pkg,sim_dict in sim_dict_dict.items():
            single= {other:value for other,value in sim_dict.items() if other and value >= threshold }
            filtered_sim_dict[pkg]  = {t[0]:t[1] for t in heapq.nlargest(topn,single.items(),key=lambda e:e[1] )} 
        return filtered_sim_dict

    @staticmethod
    def merge_nested_list(doc_term_dict1, doc_term_dict2):
        print "in WriteTool.merged_nested_list"
        pkgs = set(doc_term_dict1.keys()) | set(doc_term_dict2.keys())
        merged_doc_term_dict = {}
        for pkg in pkgs:
            if pkg in doc_term_dict1 and pkg in doc_term_dict2:
                merged_doc_term_dict[pkg] = list(set(doc_term_dict1[pkg]) | set(doc_term_dict2[pkg]))
            elif pkg in doc_term_dict1:
                merged_doc_term_dict[pkg] = list(set(doc_term_dict1[pkg]))
            else:
                merged_doc_term_dict[pkg] = list(set(doc_term_dict2[pkg]))
        print "testing com.imangi.templerun2 after merge"
        for word in merged_doc_term_dict['com.imangi.templerun2']:
            print word,
        print ""
        return merged_doc_term_dict




    @staticmethod
    def print_dict_sample():
        pass        




