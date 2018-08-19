#!/usr/bin/python
# -*- coding: utf-8 -*-

from lxml import etree
import codecs
import os
import re
import random
import copy

class Train_test_gen:
    def __init__(self,archi_path="ArchiMob_Release1_new/XML/Content",noah_path="NOAHsCorpusOfSwissGermanDialects_Release2.1/"):
        self.archi_path=archi_path
        self.noah_path=noah_path
        self.manual_archi=["1048","1063","1198","1270","1007"]
        self.noah_files=['blick.xml',"blogs.xml",'schobinger.xml','swatch.xml','wiki.xml']
        self.utterances=[]
        self.namespace="http://www.tei-c.org/ns/1.0"
        skeleton="""<TEI xmlns="http://www.tei-c.org/ns/1.0">
<teiHeader>
<fileDesc>
  <titleStmt>
    <title>Transcription 1270</title>
  </titleStmt>
  <publicationStmt>
    <publisher>University of Zurich</publisher>
    <distributor>CorpusLab @ UFSP Sprache und Raum</distributor>
    <pubPlace>Zurich, Switzerland</pubPlace>
    <date>June 2016, Release 1.0</date>
  </publicationStmt>
  <sourceDesc>
    <recordingStmt>
      <recording type="video" xml:id="d1270">
        <respStmt>
          <name>Archimob Association</name>
          <resp>www.archimob.ch/d/archimob.html</resp>
        </respStmt>
      </recording>
    </recordingStmt>
  </sourceDesc>
</fileDesc>
</teiHeader>
<text>
<body/></text>
</TEI>"""
        self.base_tree=etree.fromstring(skeleton)

        
    def add_archi_files(self,filter=None):
        for archi_file in os.listdir(self.archi_path):
            if re.match(r"\d{4}.*\.xml",archi_file):
                file_num=re.search(r"(\d{4}).*\.xml",archi_file).group(1)
                
                if file_num in self.manual_archi and filter=="manual":
                    print "added file number:",file_num
                    tree=etree.parse(self.archi_path+"/"+archi_file)
                    self.namespace=tree.getroot().nsmap[None]
                    self.utterances+=tree.findall(".//{"+self.namespace+"}u")
                elif file_num not in self.manual_archi and filter=="not manual":
                    print "added file number:",file_num
                    tree=etree.parse(self.archi_path+"/"+archi_file)
                    self.namespace=tree.getroot().nsmap[None]
                    self.utterances+=tree.findall(".//{"+self.namespace+"}u")
                elif file_num and not filter:
                    print "added file number:",file_num
                    tree=etree.parse(self.archi_path+"/"+archi_file)
                    self.namespace=tree.getroot().nsmap[None]
                    self.utterances+=tree.findall(".//{"+self.namespace+"}u")
     
    def add_noah_files(self):
        docnum=0
        for noah_file in os.listdir(self.noah_path):
            if noah_file in self.noah_files:
                print "added document:",noah_file
                docnum+=1
                noah_tree=etree.parse(self.noah_path+"/"+noah_file)
                noah_sents=noah_tree.findall(".//s")
                for sent in noah_sents:
                    sent.tag="u"
                    sent.attrib["{http://www.w3.org/XML/1998/namespace}id"]="d"+str(docnum)+"-"+sent.attrib["n"]
                    sent.attrib["start"]="xxx"
                    sent.attrib["who"]="xxx"
                    del sent.attrib["n"]
                    for w in sent:
                        if w.text==None:
                            print "found empty element. deleted."
                            print etree.tostring(w)
                            sent.remove(w)
                            continue
                        w.attrib["tag"]=w.attrib["pos"]
                        w.attrib["normalised"]="xxx"
                        w.attrib["{http://www.w3.org/XML/1998/namespace}id"]="d"+str(docnum)+"-"+w.attrib["n"]
                        del w.attrib["pos"]
                        del w.attrib["n"]
                self.utterances+=noah_sents
                
    def split(self,train_len=None,test_len=None,rate=0.9):
        if train_len:
            self.train_len= train_len
            self.test_len=len(self.utterances)-train_len
            if self.test_len<0:
                self.test_len=0
        elif test_len:
            self.train_len= len(self.utterances)-test_len
            self.test_len= test_len
            if self.train_len<0:
                self.train_len=0
        else:
            self.train_len=int(len(self.utterances)*rate)
            self.test_len=len(self.utterances)-self.train_len
            
        print "total number of sentences:",len(self.utterances)
        print "trainset number of sentences:",self.train_len
        print "testset number of sentences:",self.test_len
        
    def pick_traintest(self):
        self.train_set=self.utterances
        self.test_set=[]
        
        if not (self.train_len or self.test_len):
            self.split()
        
        for i in range(self.test_len):
            choice=random.randint(0,len(self.train_set)-1)
            test_spec=self.train_set.pop(choice)
            self.test_set.append(test_spec)
        
    def build_train(self):
        self.train_doc=copy.deepcopy(self.base_tree)
        
        self.train_doc.find(".//{"+self.namespace+"}title").text="training file from manually annotated corpus files 1248, 1063, 1198 and 1270 as well as the five NOAH corpus files 'blick.xml','blogs.xml,'schobinger.xml','swatch.xml','wiki.xml'"
        train_body=self.train_doc.find(".//{"+self.namespace+"}body")
        for elem in self.train_set:
            train_body.append(elem)
            
    def build_test(self):
        self.test_doc=copy.deepcopy(self.base_tree)
        
        self.test_doc.find(".//{"+self.namespace+"}title").text="testing file randomly picked from manually annotated corpus files 1248, 1063, 1198 and 1270 as well as the five NOAH corpus files 'blick.xml','blogs.xml,'schobinger.xml','swatch.xml','wiki.xml'"
        test_body=self.test_doc.find(".//{"+self.namespace+"}body")
        for elem in self.test_set:
            test_body.append(elem)
    
    def save(self,train_filename="crf_train.xml",test_filename="crf_test.xml"):
        if self.train_doc is not None:
            with codecs.open(train_filename,"w") as train_file:
                train_file.write(etree.tostring(self.train_doc,pretty_print=True,encoding="utf-8"))
        if self.test_doc is not None:
            with codecs.open(test_filename,"w") as test_file:
                test_file.write(etree.tostring(self.test_doc,pretty_print=True,encoding="utf-8"))
    
if __name__=="__main__":
    ## train and test from manually annotated archimob files
    #~ tta=Train_test_gen()
    #~ tta.add_archi_files(filter="manual")
    
    #~ tta.split()
    #~ tta.pick_traintest()
    #~ tta.build_train()
    #~ tta.build_test()
    #~ tta.save(train_filename="crf_train_archimob.xml",test_filename="crf_test_archimob.xml")
    
    ## train and test from manually annotated noah corpus files

    #~ ttn=Train_test_gen()
    #~ ttn.add_noah_files()
    
    #~ ttn.split()
    #~ ttn.pick_traintest()
    #~ ttn.build_train()
    #~ ttn.build_test()
    #~ ttn.save(train_filename="crf_train_noah.xml",test_filename="crf_test_noah.xml")

    ## pool and not yet annotated test from newest transcribed files

    #~ ttm=Train_test_gen(archi_path="normalized_xml/")
    #~ ttm.add_archi_files()
    
    #~ ttm.split(test_len=300)
    #~ ttm.pick_traintest()
    #~ ttm.build_train()
    #~ ttm.build_test()
    #~ ttm.save(train_filename="crf_pool_archimob.xml",test_filename="new_files_test_archimob.xml")

    ## pool and not yet annotated test from all files that are not manually annotated

    #~ ttm=Train_test_gen(archi_path="/Users/chrble/Downloads/ArchiMob_Release1_160812/XML/Content")
    #~ ttm.add_archi_files(filter="not manual")
    #~ 
    #~ ttm.split(test_len=600)
    #~ ttm.pick_traintest()
    #~ ttm.build_train()
    #~ ttm.build_test()
    #~ ttm.save(train_filename="crf_pool_old_archimob.xml",test_filename="old_files_test_archimob.xml")

## train and test from manually annotated archimob files
    tta=Train_test_gen()
    tta.add_archi_files(filter="manual")
    #~ 
    tta.split(train_len=1000,test_len=0)
    tta.pick_traintest()
    tta.build_train()
    tta.build_test()
    tta.save(train_filename="crf_train_small.xml",test_filename="crf_test_small.xml")
