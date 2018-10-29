from archimob_tools.utils import *
from archimob_tools.merge import merge_into_one
from lxml import etree

def correct_pos_train_test():
    """replacing all utterances in the crf_train and test files with newest content"""
    pos_train_tree = etree.parse("pos_sets/crf_train_archimob.xml")
    pos_test_tree = etree.parse("pos_sets/crf_test_archimob.xml")
    
    ref_tree = etree.parse("manually_normalised/archimob_norm_goldstandard.xml")
    
    new_pos_train = replace_content(pos_train_tree,ref_tree)
    print "training file replaced!"
    new_pos_test = replace_content(pos_test_tree,ref_tree)
    print "testing file replaced!"
    
    save_file(new_pos_train,"pos_sets/crf_train_corrected_archimob.xml")
    save_file(new_pos_test,"pos_sets/crf_test_corrected_archimob.xml")

def merge_1048_and_al_into_train():
    """add 1048 and active learning contributions"""
    merge_into_one("crf_train_new_archimob.xml",["pos_sets/crf_train_corrected_archimob.xml","Archimob_Release_2/1048.xml"])

if __name__=="__main__":
    merge_1048_and_al_into_train()
