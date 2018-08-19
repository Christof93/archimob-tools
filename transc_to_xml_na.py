#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This script converts a transcription xml produced by Exmeralda (.exb) to a
corpus xml.
The structure of the output looks like described in the following (Please also
check the documentation for more detailed commments on the XML structure):

<TEI xmlns="http://www.tei-c.org/ns/1.0">
    <teiHeader>
        <fileDesc>
            <titleStmt>
                <title/>
            </titleStmt>
            <publicationStmt>
                <publisher/>
                <distributor/>
                <pubPlace/>
                <date/>
            </publicationStmt>
            <sourceDesc>
                <recordingStmt>
                    <recording>
                        <respStmt>
                            <name/>
                            <resp/>
                        </respStmt>
                    </recording>
                </recordingStmt>
            </sourceDesc>
        </fileDesc>
    </teiHeader>
    <text>
        <body>
            <u>
                <w/>
                <del/>
                <gap/>
                <pause/>
                <unclear>
                    <w/>
                    <del/>
                    <gap/>
                    <pause/>
                </unclear>
                <vocal>
                    <desc>
                </vocal>
                <kinesic>
                    <desc>
                </kinesic>
                <incident>
                    <desc>
                </incident>
                <other>
                    <desc>
                </other>
            <u/>
        </body>
    </text>
        

Attributes:

<recording> --> type, xml:id
<u> --> xml:id, start, who
<w> --> xml:id, tag, normalised
<desc> --> xml:id
<pause> --> xml:id
<del> --> type, xml:id
<gap> --> reason, xml_id

"""


#__author__ = 'Noëmi Aepli'/'Phillip Ströbel'
#__email__ = 'noemi.aepli@uzh.ch'/'phillip.stroebel@gmx.ch'
#__organisation__ = 'University of Zurich'
#__copyright__ = '2016, UZH'

import argparse
import os
import re
import pickle
import codecs
import itertools
from collections import defaultdict
from xml.etree import cElementTree as cET
from lxml import etree 

    
    

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', help='path to to data folder')
    parser.add_argument('-o', help='path to output folder')
    parser.add_argument('-m', help='path to metainformation csv file')
    args = parser.parse_args()

    data_folder = vars(args)['d']
    output_folder = vars(args)['o']
    metafile = vars(args)['m']

    person_db_file = open('person_db', 'rb')
    person_db = pickle.load(person_db_file)
    
    metainfodict={}
    if metafile:
        with codecs.open(metafile,"r","utf-8") as meta:
            lines = meta.readlines()
            descript=lines[0].split("\t")
            for line in lines[1:]:
                values=line.split("\t")
                ID=values[0]
                metainfodict[ID]={descript[i].replace(" ",""):v for i,v in enumerate(values)}
            
    #~ print metainfo_dict
    
    # transcription of hesitations, laughter, "throat-clearing", etc.
    hesitation_list = [u'ehm', u'eh', u'hh', u'ää', u'ääm', u'äämm', u'ämm', u'mm', u'üü', u'ee', u'ff', u'ss', u'eeh', u'/ä/', u'/ää/',    u'/ääm/', u'/aa/', u'/ä/' , u'/äh/', u'äh', u'/ähm/', u'/äw/', u'/äwr/', u'/e/', u'/eh/', u'/ehm/', u'/ehm/ ', u'/hä/', u'/hm/', u'/hmm/', u'/k/', u'/mpf/', u'/pff/', u'/ww/', u'/m/', u'/w/', u'/eh/', u'/ehm/', u'/eh', u'eh/', u'/ehm', u'ehm/']
    laughter_list = [u'haha', u'hahah', u'hahaha', u'hahahaa', u'hahahaha', u'hahahahaha', u'hahahahahaha', u'heh', u'hehe', u'heheh']
    throatclear_list = [u'hkm', u'hkmhkm',u'hkmhkmhkm',]
    incident_list = [u'[auto im hintergrund]', u'[Bellen eines Hundes]', u'[Fehler in Aufnahme]', u'[Gemurmel]', u'[Hundegebell]', u'[Kamerawechsel]', u'[Kassettenwechsel]', u'[kein Ton respektive Pfeifen]', u'[kein Ton]', u'[Klingeln]', u'[Klopfen]', u'[ohne sprache]', u'[Pfeifton; offenbar ist hier ein Teil des Interviews verloren gegangen, inhaltlicher Bruch]', u'[Pfeifton]', u'[Schluss; Anschliessend Kommentierung von Fotos]', u'[schreiendes Kind]', u'[switched cd]', u'[Tassenklappern]', u'[telefon klingelt]', u'[Uhr im Hintergrund]', u'[Unterbruch von etwa acht Sekunden, Grund unbekannt]', u'[Unterbruch: Kassettenwechsel?]', u'[Unterbruch: Kassettenwechsel]', u'[Unterbruch]', u'[wohl Anweisungen des Assistenten zum Interviewer]', u'[zeigt auf den Sohn]', u'[hintergrundgeräsusche]', u'[hintergrundgeräusch]', u'[Hintergrundgeräusche, bellender Hund]', u'[Hintergrundgeräusche]', u'[Metallgeräusch, Rauschen]', u'[motorrad fährt vorbei]', u'[türe schliesst sich]', u'[unverständliche Stimme der Lichttechnikerin im Hintergrund]', u'[wanduhr schlägt]']
    incidents = [x.lower() for x in incident_list]
    kinesic_list = [u'[ liest ]', u'[ zeigt ein Buch ]', u'[ zeigt eine Karte ]', u'[ zeigt Karte ]', u'[liest]', u'[zeigt ein Buch]', u'[zeigt eine Karte]', u'[zeigt Karte]', u'[bewegt sich]', u'[bewegt sich ]', u'[bewegt sich, knistert]', u'[bewegt sich]', u'[deutet auf die Waage]', u'[deutet mit der Hand an]', u'[G streckt sich nach einem Dokument, das auf dem Tisch neben ihr steht]', u'[schmunzelt]', u'[steht auf]', u'[streckt den Arm nach oben]', u'[Blättern im Dienstbüchlein]', u'[Blättern]', u'[blättert weiter]', u'[blättert]', u'[deutet Höhe an]', u'[hält die Hand auf]', u'[macht eine Bewegung mit den Händen]', u'[schaut Lebensmittelkarten an]', u'[schlägt die Hände zusammen]', u'[zeigt auf Kopfhöhe]', u'[zeigt in entsprechende Richtung]', u'[ zur Kamera ]', u'[zur Kamera]', u'[zu Assistentin]', u'[zu einer anderen Person]', u'[zu seiner Frau]', u'[zum Hund]', u'[zum Sohn]', u'[zur Katze]', u'[zu Kameramann]', u'[zur Kamera]']
    kinesics = [x.lower() for x in kinesic_list]    
    other_list = [u'[bejahend]', u'[imitiert Ostschweizer Dialekt]', u'[meint ev. Collines de L\'Artois]', u'[meint vermutlich sin]', u'[verneint]', u'[zustimmend]', u'[ahmt ein Geräusch nach]', u'[ahmt Geräusch nach]', u'[ahmt Motorengeräusch nach]', u'[andere qualität]', u'[Fehler in Aufnahme, daher unverständliche Passage]', u'[Fehler in Aufnahme?]', u'[Geräuschillustration]', u'[macht Geräusch für Ausdruck hoher Geschwindigkeit]', u'[vermutlich Kassettenwechsel, da Wiederholung von \"(iksaal) häts vil ggää\", vgl. auch das Folgende]', u'[Vorgeschpräch mit Lichttechnikerin aus Basel]', u'[Vorstellen der Bilder von F. Pümpin durch dessen Sohn]']
    others = [x.lower() for x in other_list]    
    vocal_list = [u'[Husten]', u'[hustet]', u'[lacht]', u'[Niesen]', u'[räuspert sich]', u'[räuspet sich]', u'[schnäuzt sich]']
    vocals = [x.lower() for x in vocal_list]
    normal_word_list = [u'/mhm/', u'/aha/', u'/ähä/', u'/jo/', u'/hmhm/', u'/mhmh/', u'/ah/',]  
    
 
    for folder in os.listdir(data_folder):
        # in order to avoid hidden folders throwing an error
        if not folder.startswith('.') :
            for corpus_file in os.listdir(os.path.join(data_folder, folder)):
                print(corpus_file)
                if not corpus_file.startswith('.'):
                    corpus = os.path.join(data_folder, folder) + '/' + corpus_file

                    filename = re.match(r'\d{4}(\_\d)?', corpus_file)

                    person_db_key = re.match(r'\d{4}', filename.group(0))

                    for key in person_db.keys():
                        if person_db_key.group(0) in key:
                            interviewee = key
                            break

                    out_xml = codecs.open(os.path.join(output_folder, filename.group(0) + '.xml'), 'w')
                    out_txt = codecs.open(os.path.join(output_folder, filename.group(0) + '.txt'), 'w', 'utf-8')
                                        
                    parsed = etree.parse(corpus) # parse xml
                    
                    # remove empty event elements (that appear due to an EXMARALDA-bug)
                    for e in parsed.xpath("//event"):
                        if e.text == None:
                            e.getparent().remove(e)
                    

                    root = parsed.getroot() # get the root
                    
            
                    turn_ids = []   # ids of turns
                    # turns dict to capture whole text from turn, where key equals event
                    turns_dict = defaultdict(tuple)


                    # get time line to identify turns
                    for turn in root.findall('.//tli'):
                        turn_ids.append(turn.get('id'))

                    speakers = [tier.get('speaker') for tier in root.findall('.//tier')]

                    turn_index = 1
                    # find turns in chronological order and replicate xml structure in dictionary
                    for turn_id in turn_ids:
                        for tier in root.findall('.//tier'):
                            for event in tier.findall('.//event'):
                                if turn_id == event.get('start'):
                                    for speaker in speakers:
                                        if tier.get('speaker') == speaker:
                                            turns_dict[turn_index] = (speaker, event.text, event.get('start'))
                                            turn_index += 1
                                            break

                    total_events = 0
                    for speaker in speakers:
                        total_events += len(turns_dict[speaker])

                    sorted_turns = sorted(turns_dict.items())


                    # write to XML file according to the specifications above
                    out_xml.write('<?xml version="1.0" encoding="UTF-8"?>' + '\n')
                    out_root = etree.Element('TEI', xmlns='http://www.tei-c.org/ns/1.0')
                    header = etree.SubElement(out_root, 'teiHeader')
                    file_desc = etree.SubElement(header, 'fileDesc')
                    title_stmt = etree.SubElement(file_desc, 'titleStmt')
                    title = etree.SubElement(title_stmt, 'title')
                    title.text = 'Transcription {0}'.format(filename.group(0))
                    
                    pub_stmt = etree.SubElement(file_desc, 'publicationStmt')
                    publisher = etree.SubElement(pub_stmt, 'publisher')
                    publisher.text = "University of Zurich"
                    distributor = etree.SubElement(pub_stmt, 'distributor')
                    distributor.text = "CorpusLab @ UFSP Sprache und Raum"
                    pub_place = etree.SubElement(pub_stmt, 'pubPlace')
                    pub_place.text = "Zurich, Switzerland"
                    date = etree.SubElement(pub_stmt, 'date')
                    date.text = "December 2016" #"June 2016, Release 1.0"
                    
                    ## add the transcriber information if possible
                    if metafile:
                        transcr=etree.SubElement(pub_stmt,"transcriptor")
                        print metainfodict[person_db_key.group(0)]["Transcriptor"]
                        transcr.text=metainfodict[person_db_key.group(0)]["Transcriptor"]
                        
                    source_desc = etree.SubElement(file_desc, 'sourceDesc')
                    recording_stmt = etree.SubElement(source_desc, 'recordingStmt')
                    recording = etree.SubElement(recording_stmt, 'recording',
                                                 attrib={'type': 'video',
                                                         '{http://www.w3.org/XML/1998/namespace}id': 'd{0}'.format(filename.group(0))})
                    resp_stmt = etree.SubElement(recording, 'respStmt')
                    name = etree.SubElement(resp_stmt, 'name')
                    name.text = 'Archimob Association'
                    resp = etree.SubElement(resp_stmt, 'resp')
                    resp.text = 'www.archimob.ch/d/archimob.html'
                    text = etree.SubElement(out_root, 'text')
                    body = etree.SubElement(text, 'body')

                    for i, u in enumerate(sorted_turns):
                        try:
                            utterance = etree.SubElement(body,
                                                     'u', attrib={
                                '{http://www.w3.org/XML/1998/namespace}id': 'd{0}-u{1}'.format(filename.group(0), i + 1),
                                'start': 'media_pointers#d{0}-{1}'.format(filename.group(0),u[1][2])})
                            out_txt.write("\n")
                        except IndexError:
                            continue

                        # exb file should contain only G for interviewee & I for interviewer, A and any others will be "otherPerson"
                        try:
                            #print(u[1][0])
                            if u[1][0] == 'G':
                                utterance.attrib['who'] = 'person_db#{0}'.format(key)
                            elif u[1][0] == 'I':
                                utterance.attrib['who'] = 'interviewer'
                            else:
                                utterance.attrib['who'] = 'otherPerson'
                        except IndexError:
                            continue

                        # remove white spaces around parentheses & brackets 
                        try:
                            line = u[1][1]
                            substituteDict = {'( ':'(', ' )':')', '[ ':'[', ' ]':']'}
                            for old, new in substituteDict.iteritems():
                                line = line.replace(old, new)                       
                        except:
                            continue                        
                        
                        # merge comments so they don't get split during tokenising
                        try:
                            if "[" in line:         
                                comments = re.finditer("\[.*?\]", line)
                                for comm in comments:
                                    new = re.sub(" ","_" , comm.group())
                                    line = line[:comm.span()[0]]+ new +line[comm.span()[1]:]

                            if "(" in line:
                                unclears = re.finditer("\(.*?\)", line)
                                for case in unclears:
                                    case_new = re.sub(" ","_" , case.group())
                                    line = line[:case.span()[0]]+ case_new +line[case.span()[1]:]

                            if "{" in line:
                                metacomments = re.finditer("\{.*?\}", line)
                                for meta in metacomments:
                                    meta_new = re.sub(" ","_" , meta.group())
                                    line = line[:meta.span()[0]]+ meta_new +line[meta.span()[1]:]



                        except:
                            continue


                        # slash problem (because they're ambiguous)
                        try:
                            if "/" in line:
                                
                                # replace double slash with single slash
                                #line = re.sub('//',u'/' , line)
                            
                                # find old hesitation annotations & convert to new ones, so they can be found later
                                #line = re.sub('/ eh /',u'/eh/' , line)
                                #line = re.sub('/ ehm /',u'/ehm/' , line)
                                
                                # if / in the middle of an event: replace with £ as placeholder for <pause/>
                                line = re.sub('^ */ *$',u'£' , line)
                                # if / at the end of an event: delete
                                line = re.sub(' / ?$','' , line)
                                # if / in the beginning of an event: delete
                                line = re.sub('^ ?/ ','' , line)    
                        except:
                            continue

                        
                        
                        
                        # get words
                        try:
                            try:
                                words = line.split(' ')
                            except IndexError:
                                continue
                        except AttributeError:
                            continue
            
                        
                        index = 0
                        for word in words:
                            if word != '':
                                # replace multiple characters with 2 characters
                                word = ''.join(''.join(s)[:2] for _, s in itertools.groupby(word))
                                
                                # chch --> ch, schsch --> sch
                                word = re.sub('chch', 'ch', word)
                                word = re.sub('schsch', 'sch', word)
                                
                                # everything lowercase
                                word = word.lower()
                                

                                # pause-node: replace place holder that was set before with pause tag
                                if word == u'£' or word == "/":
                                    pause_node = etree.SubElement(utterance, 'pause', attrib={'{http://www.w3.org/XML/1998/namespace}id': 'd{0}-u{1}-w{2}'.format(
                                                                    filename.group(0),
                                                                    i + 1,
                                                                    index + 1)})
                                    index += 1
        
                                # new: if $ in word -> hesitation node
                                elif '$' in word:
                                    vocal_node = etree.SubElement(utterance, 'vocal')
                                    desc_node = etree.SubElement(vocal_node, 'desc', attrib={
                                                                '{http://www.w3.org/XML/1998/namespace}id': 'd{0}-u{1}-w{2}'.format(
                                                                    filename.group(0),
                                                                    i + 1,
                                                                    index + 1)})
                                    desc_node.text = word[0:-1]
                                    index += 1
                                                
                                                 
                                # new: + in word
                                elif '+' in word:
                                    word_node = etree.SubElement(utterance, 'w',
                                                                attrib={
                                                                '{http://www.w3.org/XML/1998/namespace}id': 'd{0}-u{1}-w{2}'.format(
                                                                    filename.group(0),
                                                                    i + 1,
                                                                    index + 1),
                                                                'tag': 'xxx',
                                                                'normalised': 'xxx'})
                                    
                                                
                                    word_node.text = word[0]+"***"
                                    index += 1
                                    out_txt.write(word+"\n")    


                                # new: % in word
                                elif '%' in word:
                                    vocal_node = etree.SubElement(utterance, 'vocal')
                                    desc_node = etree.SubElement(vocal_node, 'desc', attrib={
                                                                '{http://www.w3.org/XML/1998/namespace}id': 'd{0}-u{1}-w{2}'.format(
                                                                    filename.group(0),
                                                                    i + 1,
                                                                    index + 1)})

                                    # take away %
                                    desc_node.text = word[:-1]
                                    index += 1
                                                
                                            
                            
                        
                                # vocal-node if word in hesitation_list or laughter_list or throatclear_list
                                elif word in hesitation_list or word in laughter_list or word in throatclear_list:
                                    vocal_node = etree.SubElement(utterance, 'vocal')
                                    desc_node = etree.SubElement(vocal_node, 'desc', attrib={
                                                                '{http://www.w3.org/XML/1998/namespace}id': 'd{0}-u{1}-w{2}'.format(
                                                                    filename.group(0),
                                                                    i + 1,
                                                                    index + 1)})
                                    
                                    # take away slashes if slashes around hesitations
                                    if "/" in word:
                                        desc_node.text = word[1:-1]
                                    else:
                                        desc_node.text = word
                                    index += 1
                        
                                # normal word if word in normal_word_list
                                elif word in normal_word_list:
                                    word = word[1:-1]
                                    if word == "hmhm":
                                        word = "mhm"
                                    word_node = etree.SubElement(utterance, 'w',
                                                                attrib={
                                                                '{http://www.w3.org/XML/1998/namespace}id': 'd{0}-u{1}-w{2}'.format(
                                                                    filename.group(0),
                                                                    i + 1,
                                                                    index + 1),
                                                                    'tag': 'xxx',
                                                                    'normalised': 'xxx'})
                                    word_node.text = word
                                    index += 1
                                    out_txt.write(word+"\n")                        


                                # comment-node --> incident with subelement <desc>
                                elif "{" in word:
                                    word = re.sub("_"," " , word)
                                    # <incident>
                                    incident_node = etree.SubElement(utterance, 'incident')
                                    desc_node = etree.SubElement(incident_node, 'desc', attrib={
                                                                '{http://www.w3.org/XML/1998/namespace}id': 'd{0}-u{1}-w{2}'.format(
                                                                    filename.group(0),
                                                                    i + 1,
                                                                    index + 1)})
                                    desc_node.text = word
                                    index += 1
                                                            
                            
                                # comment-node --> kinesic, incident, vocal, other with subelement <desc>
                                elif "[" in word:
                                    word = re.sub("_"," " , word)
                                    # <incident>
                                    if word in incidents:
                                        incident_node = etree.SubElement(utterance, 'incident')
                                        desc_node = etree.SubElement(incident_node, 'desc', attrib={
                                                                '{http://www.w3.org/XML/1998/namespace}id': 'd{0}-u{1}-w{2}'.format(
                                                                    filename.group(0),
                                                                    i + 1,
                                                                    index + 1)})
                                        desc_node.text = word
                                        index += 1
                                    # <kinesic> 
                                    elif word in kinesics:
                                        kinesic_node = etree.SubElement(utterance, 'kinesic')
                                        desc_node = etree.SubElement(kinesic_node, 'desc', attrib={
                                                                '{http://www.w3.org/XML/1998/namespace}id': 'd{0}-u{1}-w{2}'.format(
                                                                    filename.group(0),
                                                                    i + 1,
                                                                    index + 1)})
                                        desc_node.text = word
                                        index += 1
                                    # <vocal>   
                                    elif word in vocals:
                                        vocal_node = etree.SubElement(utterance, 'vocal')
                                        desc_node = etree.SubElement(vocal_node, 'desc', attrib={
                                                                '{http://www.w3.org/XML/1998/namespace}id': 'd{0}-u{1}-w{2}'.format(
                                                                    filename.group(0),
                                                                    i + 1,
                                                                    index + 1)})
                                        desc_node.text = word
                                        index += 1
                                    # <other>
                                    elif word in others:
                                        other_node = etree.SubElement(utterance, 'other')
                                        desc_node = etree.SubElement(other_node, 'desc', attrib={
                                                                '{http://www.w3.org/XML/1998/namespace}id': 'd{0}-u{1}-w{2}'.format(
                                                                    filename.group(0),
                                                                    i + 1,
                                                                    index + 1)})
                                        desc_node.text = word
                                        index += 1

                                # deletion-node if "/" glued to word
                                elif word != "/" and "/" in word and not "(" in word and not "[" in word:
                                    del_node = etree.SubElement(utterance, 'del', attrib={'type': 'truncation', '{http://www.w3.org/XML/1998/namespace}id': 'd{0}-u{1}-w{2}'.format(
                                                                        filename.group(0),
                                                                        i + 1,
                                                                        index + 1)})
                                    del_node.text = word
                                    index += 1

                                # gap-node if unintelligible speech
                                elif word == "(?)":
                                    gap_node = etree.SubElement(utterance, 'gap', attrib={'reason': 'unintelligible', '{http://www.w3.org/XML/1998/namespace}id': 'd{0}-u{1}-w{2}'.format(
                                                                    filename.group(0),
                                                                    i + 1,
                                                                    index + 1)})
                                    gap_node.text = "..."
                                    index += 1


                                # unclear-node if word(s) in parantheses
                                elif "(" in word:
                                    word = word[1:-1]
                                    unclear_words = word.split("_")
                                    unclear_node = etree.SubElement(utterance, 'unclear')
                                    for uw in unclear_words:
                                        if uw == "/":
                                            pause_node = etree.SubElement(unclear_node, 'pause', attrib={'{http://www.w3.org/XML/1998/namespace}id': 'd{0}-u{1}-w{2}'.format(
                                                                    filename.group(0),
                                                                    i + 1,
                                                                    index + 1)})
                                            index += 1  
                                                                
                                        elif "/" in uw: 
                                            del_node = etree.SubElement(unclear_node, 'del', attrib={'type': 'truncation', '{http://www.w3.org/XML/1998/namespace}id': 'd{0}-u{1}-w{2}'.format(
                                                                    filename.group(0),
                                                                    i + 1,
                                                                    index + 1)})
                                            del_node.text = uw
                                            index += 1
                                                                            
                                        elif uw in hesitation_list or uw in laughter_list or uw in throatclear_list :
                                            vocal_node = etree.SubElement(unclear_node, 'vocal')
                                            desc_node = etree.SubElement(vocal_node, 'desc', attrib={'{http://www.w3.org/XML/1998/namespace}id': 'd{0}-u{1}-w{2}'.format(
                                                                    filename.group(0),
                                                                    i + 1,
                                                                    index + 1)})
                                            if "/" in uw:
                                                desc_node.text = uw[1:-1]
                                            else:
                                                desc_node.text = uw
                                            
                                            index += 1

                                        # otherwise: "normal" word (node) within unclear
                                        else:
                                            word_node = etree.SubElement(unclear_node, 'w',
                                                                    attrib={
                                                                    '{http://www.w3.org/XML/1998/namespace}id': 'd{0}-u{1}-w{2}'.format(
                                                                        filename.group(0),
                                                                        i + 1,
                                                                        index + 1),
                                                                    'tag': 'xxx',
                                                                    'normalised': 'xxx'})
                                            word_node.text = uw
                                            index += 1
                                            out_txt.write(uw+"\n")  

                                        
                                
                                # word-node for "normal" word(s) (nodes)
                                else:
                                    word_node = etree.SubElement(utterance, 'w',
                                                                attrib={
                                                                '{http://www.w3.org/XML/1998/namespace}id': 'd{0}-u{1}-w{2}'.format(
                                                                    filename.group(0),
                                                                    i + 1,
                                                                    index + 1),
                                                                'tag': 'xxx',
                                                                'normalised': 'xxx'})
                                    word_node.text = word
                                    index += 1
                                    out_txt.write(word+"\n")    


                    # write outfile
                     
                    s = etree.tostring(out_root, pretty_print=True, encoding='UTF-8')
                    out_xml.write(s)
    

if __name__ == '__main__':
    main()
