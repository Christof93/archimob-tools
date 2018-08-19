#!/usr/bin/python
#coding: utf-8
import xml.etree.cElementTree as ET
import codecs
import os

files = sorted(os.listdir("Archimob_Release_1/XML/Content") )
loeschliste = []
neuedatei = open('anonymization_deletion.txt', 'w')

for file in files:
        if file.endswith(".xml"):
                arbeitsdatei = ET.parse("Archimob_Release_1/XML/Content/" + file)
                root = arbeitsdatei.getroot()
                for utterance in root.iter('{http://www.tei-c.org/ns/1.0}u'):
                        ut_id = (utterance.attrib['start'].split("#")[1]+".wav").replace("-","_")
                        for w in utterance.iter('{http://www.tei-c.org/ns/1.0}w'):
                                if '***' in w.text:
                                        loeschliste.append(ut_id)
print(len(loeschliste))

for utteranceid in loeschliste:
    neuedatei.write(utteranceid + "\n")

neuedatei.close()
