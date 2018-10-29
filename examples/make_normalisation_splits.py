#!/usr/bin/python
# -*- coding: utf-8 -*-

from archimob_tools.utils import *

from lxml import etree

if __name__=="__main__":
        print "load old splits..."
        all_man_norm=etree.parse("archimob_norm_goldstandard.xml")
        
        trainset = etree.parse("../Programmierprojekt Normalization/archimob-split/train_g.xml").getroot().findall(".//u")
        devset = etree.parse("../Programmierprojekt Normalization/archimob-split/dev_g.xml").getroot().findall(".//u")
        testset = etree.parse("../Programmierprojekt Normalization/archimob-split/test_g.xml").getroot().findall(".//u")
        
        train_tree = make_empty_doc("train set consisting of words from documents 1007, 1048, 1063, 1143, 1198,1270, 1142, 1212, 1261")
        dev_tree = make_empty_doc("dev set consisting of words from documents 1007, 1048, 1063, 1143, 1198,1270, 1142, 1212, 1261")
        test_tree = make_empty_doc("test set consisting of words from documents 1007, 1048, 1063, 1143, 1198,1270")
        
        trainbody = train_tree.find(".//{"+get_namespace(all_man_norm)+"}body")
        devbody = dev_tree.find(".//{"+get_namespace(all_man_norm)+"}body")
        testbody = test_tree.find(".//{"+get_namespace(all_man_norm)+"}body")
        
        print "replace with newest..."
        for utterance in trainset:
                try:
                        trainbody.append(find_utterance(get_id(utterance),all_man_norm))
                except:
                        print "not found!:",utterance.attrib
        
        for utterance in devset:
                devbody.append(find_utterance(get_id(utterance),all_man_norm))
                
        for utterance in testset:
                testbody.append(find_utterance(get_id(utterance),all_man_norm))
        
        
        print "add new documents..."
        additional_elems_train = []
        additional_elems_dev = []
        for add_file in ["Archimob_Release_2/1142.xml","Archimob_Release_2/1212.xml","Archimob_Release_2/1261.xml"]:
                add_stuff = get_utterance_elements(etree.parse(add_file))
                additional_elems_train += add_stuff[:int(len(add_stuff)*0.9)]
                additional_elems_dev += add_stuff[-int(len(add_stuff)*0.1):]
                
        print (train_tree)
        for u in additional_elems_train:
                trainbody.append(u)
        save_file(train_tree,"manually_normalised/train_norm.xml")
        
        for u in additional_elems_dev:
                devbody.append(u)
        save_file(dev_tree,"manually_normalised/dev_norm.xml")
        
        save_file(test_tree,"manually_normalised/test_norm.xml")
        
        
        
        
