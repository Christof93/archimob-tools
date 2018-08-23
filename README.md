# Archimob corpus handling tools
In this repository you can find some of the scripts that were used to build, transform and update the Archimob text corpus of Swiss-German interview transcriptions.

### utils.py
Contains various useful functions to work with the Archimob corpus. 

functions:
 - **get_namespace(tree)**
  get the default namespace of the archimob tree, parsed from archimob xml file. (Should be http://www.tei-c.org/ns/1.0)
  
  
 - **get_word_elements(tree)**
 
 
 - **get_utterance_elements(tree)**
 
 
 - **find_word(elem_id,element_tree)**
 
 
 - **find_utterance(elem_id,element_tree)**
 
 
 - **get_id(elem)**
 
 
 - **replace_content(xml_doc, ref_xml_doc)**
 
    replace all utterances in a document with utterances from another document. Takes element trees as input.
    
    
 - **make_empty_doc(title,release="1.0")**
 
   make an archimob document, but only an empty xml body with the tei header. arguments are title of the file and release number. Returns the empty element tree.
   
   
 - **save_file(tree,filename)**
 
    save the tree to an outputfile
    
    
usage:
```
from archimob_tools.utils import *
base_tree = make_empty_doc("1007.xml")
save_file(base_tree, "new_empty_1007.xml")
```

### transc_to_xml_na.py (by Noëmi Aepli and Phillip Ströbel)
Script to transform .exb transcription files into archimob xml files.

usage: `transcr_to_xml_na.py -d \<path to the folder with exb files\> -o \<path to the output folder\> (-m \<OPTIONAL path to a csv file with meta information\>)`

### archi_xml_to_text.py
A very simple script that takes as input argument a file or folder of files from the archimob corpus. It writes the contents of all the utterances in the transcription(s) to STDOUT. One utterance per line.

usage:
`python archi_xml_to_text.py 1007.xml > output.txt`

### archimob_xml.py
Contains the class xml_mod. Instances of this class can be used to change various things in an archimob file and save them to a new version.
Initialize with an xml filename.

functions:

 - **update_content(other_xml)**
 
    go trough all words and if the same word (id) can be found in the other file, replace text and attributes with the ones from the other file.
    
    
 - **update_from_json(json_file)**
 
    Go through an archimob-change json file and if the id can be found in the document, make the specified changes.
 
 
 - **add_transcriptor(metafile)**
 
    Given a csv with metainformation about exb transcription-files, retrieve the name of the transcriber based on the filename and add a transcriptor tag to the file under \<publicationStmt\> .


- **add_normalizations()**

    Add normalisations that were created using Yves Scherrers Character Based Translation approach.


- **add_pos_tags()**

    Add POS tags from a active learning CRF tagger output file
 
 
- **save_file(outputfile_name)**

    Save the changed xml tree to an outputfile


usage:
```
mod=XML_mod("1007.xml")
print "now processing:",mod.filenum
mod.add_transcriptor("./20170419_overview_corpus.tsv")
mod.get_updates_from_json("./fatima_changes.json")
mod.save_file("1007_new.xml")
  ```
### delete_wavs.py (by Larissa Schmidt)
Go through all the files in the Archimob Release folder and write the utterance id to a file if the utterance contains an anonymized person name.

usage: `python delete_wavs.py`

### merge.py
Contains function merge_into_one(outfile, files_to_merge) which takes an outputfile name and a list of Archimob xml files as parameters. It writes a new file which consists of all the utterances in all of the files_to_merge.

usage:
  `merge_into_one("archimob_norm_goldstandard.xml",["1007.xml", "1048.xml", "1063.xml", "1143.xml", "1198.xml", "1270.xml"])`

### split_train_test_pos.py
Can be used to split a new set of training and testing files for POS tagging. Randomly shuffles utterances.

usage:
```
tta=Train_test_gen()
tta.add_archi_files(filter="manual")
tta.split()
tta.pick_traintest()
tta.build_train()
tta.build_test()
tta.save(train_filename="crf_train_small.xml",test_filename="crf_test_small.xml")
```
