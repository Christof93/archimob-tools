#!/usr/bin/python
# -*- coding: utf-8 -*-

import codecs,re
from lxml import etree as ET
import json
    
class XML_mod:
	"""Class to handle modifications in xml files of the Archimob corpus"""
	def __init__(self,xmlfile,verbose=False):
		self.filename=xmlfile
		self.verbose=verbose
		self.tree=ET.parse(xmlfile)
		self.namespace=self.tree.getroot().nsmap[None]
		self.filenum= re.search(r'\d{4}', xmlfile.split("/")[-1]).group(0)
		self.manual_pos_tagged=["1007.xml", "1048.xml", "1063.xml", "1198_1.xml","1198_2.xml", "1270.xml"]
		self.manual_norm=["1007.xml", "1048.xml", "1063.xml", "1143.xml", "1198_1.xml","1198_2.xml", "1270.xml"]
		self.manual_norm_corrected=["1212.xml","1261.xml","1142.xml"]
	
		
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
    
	def _align_normalizations_manual(self, before, after):
		for index in range(max[len(before),len(after)]):
			userinput=raw_input()
			if userinput=="":
				continue
			else:
				return
				
		return
	def _align_lists(self,original,from_segm_transl,xml_words):
		"""After the segment level character translation system run, 
		the list of words can have a different length than the original.
		There are some unclear cases normally denoted by a blank line in the output.
		These are normally very few and the function just deletes the blank line
		leaving at most one incorrect normalization."""
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
					if self.verbose:
						print getid(orig)
						print ET.tostring(orig),"changed to:", ET.tostring(update)
			else:
				print getid(orig), "not found in new file!"

	def get_updates_from_json(self,json_file):
		"""read a json file in archimob change format and apply the changes to the tree."""
		changes=[]
		with codecs.open(json_file,"r","utf-8") as change_file:
			changes=json.load(change_file)
		for change in changes:
			if change["doc"]==self.filename.split("/")[-1]:
				node = self.find_word(change["id"])
				if node is None:
					print "WARNING couldn't find", change["id"],"in",change["doc"]
					continue
				if self.verbose:
					print "-"*100
					print ET.tostring(node).encode("utf-8")
					print "changed to:"
				for key in change["changes"]:
					if key=="text":
						node.text=change["changes"]["text"]
					elif key=="delete" and change["changes"]["delete"]==True:
						parent = node.find("..")
						parent.remove(node)
						### enumerate the words new (also pauses and stuff). Not a good idea to change unique ids IMO.
						#~ for num, child in enumerate(parent):
							#~ try:
								#~ curr_id = child.attrib["{http://www.w3.org/XML/1998/namespace}id"]
								#~ new_id = "-".join(curr_id.split("-")[:-1]+["w"+str(num+1)])
								#~ child.attrib["{http://www.w3.org/XML/1998/namespace}id"] = new_id
							#~ except KeyError:
								#~ for child2 in child:
									#~ curr_id = child2.attrib["{http://www.w3.org/XML/1998/namespace}id"]
									#~ new_id = "-".join(curr_id.split("-")[:-1]+["w"+str(num+1)])
									#~ child2.attrib["{http://www.w3.org/XML/1998/namespace}id"] = new_id
						if len(list(parent))==0:
							parent.find("..").remove(parent)
					else:
						node.attrib[key]=change["changes"][key]
				if self.verbose:
					print ET.tostring(node).encode("utf-8")
		
	def replace_all(self, old_new_list):
		"""replace characters or strings in all elements text. 
		Input: a dictionary with the strings to replace and the new strings
		{old:new,old:new,...}"""
		for word in self.get_word_elements():
			for occurence,new_string in old_new_list:
				if occurence in word.text:
					if self.verbose:
						print "-"*100
						print word.attrib["{http://www.w3.org/XML/1998/namespace}id"],word.text.encode("utf-8"),"\nchanged to:"
					word.text = word.text.replace(occurence,new_string)
					if self.verbose:
						print word.attrib["{http://www.w3.org/XML/1998/namespace}id"],word.text.encode("utf-8")

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
		if self.verbose:
			print "-"*100
			print "added transcriptor tag:"
			print metainfodict[self.filenum]["Transcriptor"].encode("utf-8")
		transcr.text=metainfodict[self.filenum]["Transcriptor"]
	
	def add_normalizations_raw(self,orig_file_path,norm_file_path,\
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
			
	def add_normalizations_from_vertical(self, vertical_file_path,\
		replace_uniq=True, unique_filepath="unique_normalizations.tsv"):
		""""""
		normalizations=[]
		original=[]
		with codecs.open(vertical_file_path,"r","utf-8") as normalized_file:
			for line in normalized_file:
				if not line =="\n":
					try:
						norm = line.strip().split()[1]
					except IndexError:
						norm = "" 
					try:
						orig = line.strip().split()[0]
					except IndexError:
						orig = ""
					finally:
						original.append(orig)
						normalizations.append(norm)

		normalized_unique=[]
		original_unique=[]
		if replace_uniq:
			with codecs.open(unique_filepath,"r","utf-8") as uniques_file:
				for line in uniques_file:
					line=line.strip().split("\t")
					o,n=line[0],line[1]
					original_unique.append(o)
					normalized_unique.append(n)
				
		# replace normalizations that are uniquely found in training material
		if replace_uniq:
			normalizations=self._replace_uniques(original_unique, normalized_unique, original, normalizations)

		assert len(original)==len(normalizations)
	
		# all words in xml file
		words=self.get_word_elements()
		
		if len(words)!=len(normalizations):
			original,normalizations=self._align_lists(original,normalizations,words)
			for i in range(len(normalizations)):
				xml_window = [w.text for w in words[i:i+10]]
				norm_window = [o for o in original[i:i+10]]
				test = [w==o for w,o in zip(xml_window, norm_window)] 
				if not any(test):
					print "verticalized normalization out of alignment on line:",i
					print "orig xml:",xml_window
					print "orig verticalized output:",norm_window
					break
		try:
			assert len(words)==len(normalizations)
		except AssertionError:
			print "could not merge normalizations into file!"
			print "number of words in xml:", len(words)
			print "number of words in normalized file:", len(normalizations)
			print [w.text for w in words[-10:]]
			print normalizations[-10:]
			print "no normalisations added!"
			return
		
		for w,norm in zip(words,normalizations):
			w.attrib["normalised"]=norm
			
		if self.verbose:
			print "added new normalisations from: "+vertical_file_path
				
	def add_pos_tags(self, pos_tag_file):
		"""add the pos attribute to <w> tags. """

		predict_tree=ET.parse(pos_tag_file)
		actual_words=self.tree.findall(".//{http://www.tei-c.org/ns/1.0}w")
		pred_words=predict_tree.findall(".//{http://www.tei-c.org/ns/1.0}w")
		try:
			assert len(actual_words)==len(pred_words)
		except AssertionError:
			print "Couldn't add pos-tags from file: "+pos_tag_file
			return
		for w_act,w_pred in zip(actual_words,pred_words):
			w_act.attrib["tag"]=w_pred.attrib["pred_tag"]
	
		if self.verbose:
			print "added new pos-tags from: "+pos_tag_file
			
	def save_file(self,filename=None):
		
		s = ET.tostring(self.tree, pretty_print=True, encoding='UTF-8', xml_declaration=True)
		if filename==None:
			filename=self.filename
			
		with codecs.open(filename,"w") as out_xml:
			out_xml.write(s)
		if self.verbose:
			print "#"*100
			print "file saved to:",filename
			print "#"*100

if __name__=="__main__":
    mod=XML_mod("Archimob_Release_2/1205.xml",verbose=True)
    print mod.namespace
    #~ mod.add_transcriptor("../archimob_stuff/20170419_overview_corpus.csv")
    #~ mod.add_normalizations_from_vertical("new_normalised/1205.vert")
    mod.add_pos_tags("pos_predictions/1205.xml")
    #~ mod.save_file()
