#encoding=utf8
import sys,os
from LanguageModel import LanguageModel
from WriteTool import WriteTool
reload(sys)
sys.setdefaultencoding('UTF8')



def ComputeJacardSim(doc_term_matrix):
    print "in get_jacard_sim"

    setOfWords = LanguageModel.getSetOfWords(doc_term_matrix)
    jacard_sim_dict = LanguageModel.get_jacard_sim(setOfWords)
    
    print "get tag sim okay,length is:" + str(len(jacard_sim_dict))
    return jacard_sim_dict




