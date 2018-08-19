#!/usr/bin/python
# -*- coding: utf-8 -*-

import codecs,re
from lxml import etree as ET
import json

    
class XML_mod:
	"""Class to handle modifications in xml files of the Archimob corpus"""
	def __init__(self,xmlfile):
		self.filename=xmlfile
		self.tree=ET.parse(xmlfile)
		self.namespace=self.tree.getroot().nsmap[None]
		self.filenum= re.search(r'\d{4}', self.filename.split("/")[-1]).group(0)
		self.manual_pos_tagging=["1007.xml", "1048.xml", "1063.xml", "1198.xml", "1270.xml"]
		self.manual_norm=["1007.xml", "1048.xml", "1063.xml", "1143.xml", "1198.xml", "1270.xml"]

	def get_word_elements(self,element_tree=None):
		if not element_tree:
			element_tree = self.tree
		return element_tree.findall(".//{"+self.namespace+"}w")
		
	def get_utterance_elements(self,element_tree=None):
		if not element_tree:
			element_tree = self.tree
		return element_tree.findall(".//{"+self.namespace+"}u")
	def find_word(self,elem_id,element_tree=None):
		if not element_tree:
			element_tree = self.tree
		return element_tree.find(".//{"+self.namespace+"}w[@{http://www.w3.org/XML/1998/namespace}id='"+elem_id+"']")
	
	def find_utterance(self,elem_id,element_tree=None):
		if not element_tree:
			element_tree = self.tree
		return element_tree.find(".//u[@{"+self.namespace+"}id='"+elem_id+"']")
	

	def _replace_uniques(self,uniq_origs,uniq_norms,original,mt_normalized):
		"""replace automatic normalizations which were found with a unique normalization
		 in the trainingdata """
		try:
			assert len(uniq_origs)==len(uniq_norms)
			assert len(original)==len(mt_normalized)
		except AssertionError:
			print len(uniq_origs),"=?",len(uniq_norms)    
			print len(original),"=?",len(mt_normalized)
			return False
			
		for i,o in enumerate(original):
			if o in uniq_origs:
				mt_normalized[i]=uniq_norms[uniq_origs.index(o)]
			
		return mt_normalized
        
	def _align_lists(self,original,from_segm_transl,xml_words):
		"""After the segment level character translation system run, 
		the list of words can have a different length than the original.
		There are some unclear cases normally denoted by a blank line in the output.
		These are normally very few and the function just deletes the blank line
		leaving at least one incorrect normalization."""
		corrected=0
		for i,w in enumerate(original):
			if w=="":
				if len(original[i-1].split())==2 and len(original[i+1].split())==2:
					pass
					
				elif len(original[i-1].split())==1 and len(original[i+1].split())==1:
					del from_segm_transl[i]
					del original[i]
					corrected+=1
	
				elif len(original[i-1].split())==2 or len(original[i+1].split())==2:
					#~ original[i-1]=original[i-1].split()[0]
					del from_segm_transl[i]
					del original[i]
					corrected+=1
				
				if [unicode(xml_words[j].text) for j in range(i-3,i+4)][-1]!=original[i-3:i+4][-1]:
					print
					print "after adjustment:"
					print "mt_out:"
					print original[i-3:i+4]
					print "xml:"
					print [unicode(xml_words[j].text) for j in range(i-3,i+4)]
					print from_segm_transl[i-3:i+4]
					print
		
		print "adjusted",corrected,"positions."
		return original,from_segm_transl

# update content iteratively going trough both files
	#~ def update_content(self,other_xml):
		#~ def getid(elem):
			#~ return elem.attrib["{http://www.w3.org/XML/1998/namespace}id"]
		#~ update_tree=ET.parse(other_xml)
		#~ assert len(self.get_word_elements(self.tree))==len(self.get_word_elements(update_tree))
		#~ for orig,update in zip(self.get_word_elements(self.tree),self.get_word_elements(update_tree)):
			
			#~ try:
				#~ assert getid(orig)==getid(update)
			#~ except AssertionError:
				#~ print getid(orig),getid(update)
				#~ print "id mismatch!"
				#~ return None
			#~ if orig.text != update.text or orig.attrib != update.attrib:
				#~ print getid(orig)
				#~ print ET.tostring(orig),"changed to:", ET.tostring(update)

# update based on id
	def update_content(self,other_xml):
		def getid(elem):
			return elem.attrib["{http://www.w3.org/XML/1998/namespace}id"]
		update_tree=ET.parse(other_xml)
		for orig in self.get_word_elements():
			update= self.find_word(getid(orig),update_tree)
			if update!=None:
				if orig.text != update.text or orig.attrib != update.attrib:
					print getid(orig)
					print ET.tostring(orig),"changed to:", ET.tostring(update)
			else:
				print getid(orig), "not found in new file!"

	def get_updates_from_json(self,json_file):
		changes=[]
		with codecs.open(json_file,"r","utf-8") as change_file:
			changes=json.load(change_file)
		for change in changes:
			if change["doc"]==self.filename.split("/")[-1]:
				node = self.find_word(change["id"])
				print ET.tostring(node)
				print "changed to:"
				for key in change["changes"]:
					if key=="text":
						node.text=change["changes"]["text"]
					else:
						node.attrib[key]=change["changes"][key]
				print ET.tostring(node)
		

	def add_transcriptor(self,metafile):
		"""add a transcriptor tag under <publicationStmt> to the file"""
		metainfodict={}
		with codecs.open(metafile,"r","utf-8") as meta:
			lines = meta.readlines()
			descript=lines[0].split("\t")
			for line in lines[1:]:
				values=line.split("\t")
				ID=values[0]
				metainfodict[ID]={descript[i].replace(" ",""):v for i,v in enumerate(values)}
		pub=self.tree.find(".//{"+self.namespace+"}publicationStmt")
		transcr=ET.SubElement(pub,"transcriptor")
		print metainfodict[self.filenum]["Transcriptor"]
		transcr.text=metainfodict[self.filenum]["Transcriptor"]
	
	def add_normalizations(self,orig_file_path,norm_file_path,\
							replace_uniq=True,unique_filepath="unique_normalizations.tsv"):
		"""add the normalization attribute to <w> tags. """
		normalized_unique=[]
		original_unique=[]
		original=[]
		mt_normalized=[]
		if replace_uniq:
			with codecs.open(unique_filepath,"r","utf-8") as uniques_file:
				for line in uniques_file:
					line=line.strip().split("\t")
					o,n=line[0],line[1]
					original_unique.append(o)
					normalized_unique.append(n)
				
		with codecs.open(orig_file_path,"r","utf-8") as original_file:
			original=[l.replace(" ","").replace("_"," ").strip() for l in original_file]
		with codecs.open(norm_file_path,"r","utf-8") as normalized_file:
			mt_normalized=[l.strip() for l in normalized_file]
		
		# replace normalizations that are uniquely found in training material
		if replace_uniq:
			normalizations=self._replace_uniques(original_unique,normalized_unique,original,mt_normalized)
		assert len(original)==len(normalizations)
	
		# all words in xml file
		words=self.tree.findall(".//{http://www.tei-c.org/ns/1.0}w")
		
		if len(words)!=len(normalizations):
			original,normalizations=self._align_lists(original,normalizations,words)
				
		try:
			assert len(words)==len(normalizations)
		except AssertionError:
			print "could not merge normalizations into file!"
			print "number of words in xml:",len(words)
			print "number of words in normalized file:",len(normalizations)
			print [w.text for w in words[-10:]]
			print normalizations[-10:]
				
		for w,norm in zip(words,normalizations):
			w.attrib["normalised"]=norm
			
	def add_pos_tags(self,pos_tag_file):
		"""add the pos attribute to <w> tags. """
		predict_tree=ET.parse(pos_tag_file)
		actual_words=self.tree.findall(".//{http://www.tei-c.org/ns/1.0}w")
		pred_words=predict_tree.findall(".//{http://www.tei-c.org/ns/1.0}w")
		assert len(actual_words)==len(pred_words)
		
		for w_act,w_pred in zip(actual_words,pred_words):
			w_act.attrib["tag"]=w_pred.attrib["pred_tag"]
	
		
	def save_file(self,filename=None):
		
		s = ET.tostring(self.tree, pretty_print=True, encoding='UTF-8', xml_declaration=True)
		if filename==None:
			filename=self.filename
			
		with codecs.open(filename,"w") as out_xml:
			out_xml.write(s)
			
		print "saved to:",filename

if __name__=="__main__":
    mod=XML_mod("ArchiMob_Release1_new/XML/Content/1055.xml")
    print mod.namespace
    #~ mod.add_transcriptor("../archimob_stuff/20170419_overview_corpus.csv")
    mod.add_normalizations("../archimob_stuff/addition_release/normalized/1055_orig.txt","../archimob_stuff/addition_release/normalized/1055_normalized2.txt")
    mod.save_file()
