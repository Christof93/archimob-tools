#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import os

from archimob_tools.archimob_xml import XML_mod

####In my case order was crucial!!!
## python transform_release_1_to_release_2.py -d Archimob_Release_1/XML/Content > changelog.txt
## python transform_release_1_to_release_2.py -d stage1_xml >> changelog.txt
parser = argparse.ArgumentParser()

parser.add_argument('-d', help='path to to data folder')
args = parser.parse_args()

data_folder=vars(args)["d"]

target_folder = "./Archimob_Release_2"

#add transcriptors

for xml_filename in os.listdir(data_folder):
	if xml_filename.endswith(".xml"):
		mod=XML_mod(data_folder+"/"+xml_filename, verbose=True)
		print "now processing:",mod.filenum
	
		mod.add_transcriptor("./20170419_overview_corpus.tsv")
		if not mod.filename.split("/")[-1] in mod.manual_norm+mod.manual_norm_corrected:
			mod.add_normalizations_from_vertical("./new_normalised/"+mod.filename.split("/")[-1][:-4]+".vert")
		if mod.filenum=="1261":
			mod.add_normalizations_from_vertical("./new_normalised/1261.vert")
			
		for json_change_filename in sorted(os.listdir("change_files")):
			if json_change_filename.endswith(".json"):
				mod.get_updates_from_json("change_files/"+json_change_filename)
		mod.get_updates_from_json("./fatima_changes.json")
		mod.get_updates_from_json("./larissa_changes_st.json")
		mod.get_updates_from_json("./larissa_changes_sp.json")
		mod.get_updates_from_json("./varDial_corrections.json")
		mod.replace_all([
			# remove punctuation signs as they are not part of the transcription guidelines
			# use of - is very transcriber-specific, maybe keep
			#(u"'",u""),(u",",u""),(u".",u""),
			(u"-",u""),
			# q, x and y should not appear according to guidelines
			("x","ggs"),("qu","kw"),(u"psy",u"psü"),(u"typ",u"tüp"),
			# uneasyness => aniisiness???
			("mayer","maier"),("uneasyness","aniisiness"),
			(u"einparteiensystem",u"einparteiensüstem"), 
			# ô is not part of the guidelines - could be õ or o, we choose o; ̆  is an obvious transcription mistake
			(u"ô",u"o"),
			# replace base letter + combining diacritic by diacriticized letter (2 glyphs => 1 glyph)
			(u"ẽ",u"ẽ"),(u"ǜ",u"ǜ"),
			# replace combined diacritics for nasalisation by simple diacritics: ò~ => õ, è~ => ẽ
			# this might be useful to generalize, as close vowel nasals are next to impossible...
			(u"ò̃",u"õ"),(u"è̃",u"ẽ"),(u"é̃",u"ẽ")
			])
		if not mod.filename.split("/")[-1] in mod.manual_pos_tagged:
			mod.add_pos_tags("./pos_predictions/"+mod.filename.split("/")[-1])
			
		mod.save_file(target_folder+"/"+xml_filename)
