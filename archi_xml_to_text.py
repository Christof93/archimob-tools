#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys,os
from lxml import etree as ET

def print_text(xml_tree,ns):
    for u in tree.getroot().iter("{"+ns+"}u"):
        utterance=[w.text for w in u.findall("{"+ns+"}w")]
        output_u=" ".join(utterance)
        print output_u.encode("utf-8")

inp = sys.argv[1]

if inp.endswith(".xml"):
    tree=ET.parse(inp)
    namespace=tree.getroot().nsmap[None]
    print_text(tree,namespace)
    

else:
    for f in os.listdir(inp):
        if f.endswith(".xml"):
            tree=ET.parse(inp+"/"+f)
            namespace=tree.getroot().nsmap[None]
            print_text(tree,namespace)

