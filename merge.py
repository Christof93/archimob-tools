from lxml import etree

from utils import make_empty_doc, MANUALLY_NORMALISED, get_id, save_file
import codecs

def merge_into_one(outfile, files_to_merge):
        """merge a number of archimob files into one."""
        all_trees=[]
        for filename in files_to_merge:
                all_trees.append(etree.parse(filename))
        # set up the header and base of document
        base_tree=make_empty_doc("merged archimob corpus:"+", ".join(files_to_merge))
        namespace=base_tree.nsmap[None]
        # find the body to attach utterances
        body = base_tree.find(".//{"+namespace+"}body")
        for tree in all_trees:
                for elem in tree.iter("{"+namespace+"}u"):
                        body.append(elem)
        # write the new file
        save_file(base_tree, outfile)


if __name__=="__main__":
        #~ base_path="Archimob_Release_2"
        #~ merge_into_one("archimob_norm_goldstandard.xml",[base_path+"/"+p for p in MANUALLY_NORMALISED])
        
        import sys
        merge_into_one(sys.argv[1],sys.argv[2:])
        
