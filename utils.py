import codecs
import copy
try:
        from lxml import etree
except ImportError:
        import xml.etree.cElementTree as etree
        
MANUALLY_POS_TAGGED=["1007.xml", "1048.xml", "1063.xml", "1198_1.xml", \
"1198_2.xml", "1270.xml"]

MANUALLY_NORMALISED=["1007.xml", "1048.xml", "1063.xml", "1143.xml", \
"1198_1.xml", "1198_2.xml", "1270.xml", "1142.xml", "1212.xml", "1261.xml"\
]
def get_namespace(tree):
        return tree.getroot().nsmap[None]
def get_word_elements(element_tree):
        namespace=element_tree.getroot().nsmap[None]
        return element_tree.findall(".//{"+namespace+"}w")
        
def get_utterance_elements(element_tree):
        namespace=element_tree.getroot().nsmap[None]
        return element_tree.findall(".//{"+namespace+"}u")
        
def find_word(elem_id,element_tree):
        """find a word element by its id"""
        namespace=element_tree.getroot().nsmap[None]
        return element_tree.find(".//{"+namespace+"}w[@{http://www.w3.org/XML/1998/namespace}id='"+elem_id+"']")

def find_utterance(elem_id,element_tree):
        """find an utterance element by its id"""
        namespace=element_tree.getroot().nsmap[None]
        return element_tree.find(".//{"+namespace+"}u[@{http://www.w3.org/XML/1998/namespace}id='"+elem_id+"']")

def get_id(elem):
        """get the id of an archimob xml element"""
        return elem.attrib["{http://www.w3.org/XML/1998/namespace}id"]
        
def replace_content(xml_doc, ref_xml_doc):
        """replace all utterances in a document with utterances from another document"""
        new_doc = copy.deepcopy(xml_doc)
        d_ids = []
        body = new_doc.find(".//{"+get_namespace(xml_doc)+"}body")
        for utterance in new_doc.iter("{"+get_namespace(new_doc)+"}u"):
                d_ids.append( get_id(utterance))
                body.remove(utterance)
         
        for d_id in d_ids:
            body.append(copy.deepcopy(find_utterance(d_id,ref_xml_doc)))
        return new_doc

def make_empty_doc(title,release="1.0"):
        skeleton="""<TEI xmlns="http://www.tei-c.org/ns/1.0">
<teiHeader>
<fileDesc>
  <titleStmt>
    <title>{}</title>
  </titleStmt>
  <publicationStmt>
    <publisher>University of Zurich</publisher>
    <distributor>CorpusLab @ UFSP Sprache und Raum</distributor>
    <pubPlace>Zurich, Switzerland</pubPlace>
    <date>June 2016, Release {}</date>
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
<body/>
</text>
</TEI>""".format(title,release)
        return etree.fromstring(skeleton)


def save_file(tree,filename):
        s = etree.tostring(tree, pretty_print=True, encoding='UTF-8', xml_declaration=True)                
        with codecs.open(filename,"w") as out_xml:
                out_xml.write(s)
        print "saved to:",filename
