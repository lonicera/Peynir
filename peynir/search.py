#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import difflib
from peynir import functions, constants as cons, text_formatting as text 
import gettext, os
gettext.bindtextdomain("peynir","/language")
gettext.textdomain("peynir")
_ = gettext.gettext


"""Search or find module for peynir"""
def similarity(first,second):
    seq=difflib.SequenceMatcher(a=first.lower(), b=second.lower())
    return round(seq.ratio(),1)
    
def local_dependency(source,package):
    """Get local dependencies when suprapackage removing from system"""
    dep_list = []
    source_root = functions.get_root(cons.sprpckg_dir+source+".xml")
    local_dep = source_root[2].attrib['local']
    for i in local_dep.strip().split(" "):
        if i != package and len(local_dep.strip().split(" ")) > 0:
            dep_list.append(i)
    return dep_list
    
def local_search(source):
    """Search suprapackage in local"""
    dirlist = os.listdir(cons.sprpckg_dir)
    counter = 0
    for fname in dirlist:
        if source == "" or source == "all":
            text.text_formatting(fname[:-4] + " ==> " + functions.get_description(fname[:-4]),1,'info')  
        elif similarity(fname[:-4],source) > 0.45 and len(dirlist) >0:
            text.text_formatting(fname[:-4] + " ==> " + functions.get_description(fname[:-4]),1, 'info')
    
def srch_pynr(srch,node,action):
    """Search suprapackage in repository"""
    repo_root = functions.get_root(cons.repo)
    repo_search = repo_root[1].findall(node)
    if srch == "all":
        text.text_formatting(str(len(repo_root[1])) + " suprapackages have found.", 0, 'info')
        for rep in repo_root[1]:
            text.text_formatting(rep[0].text + " ==> " + functions.get_description(rep[0].text), 1, 'info')
    else:
        for comp in range(len(repo_search)):
            if action == "find":
                if similarity(str(repo_search[comp].text),str(srch)) > 0.45 and int(len(repo_search)) >0:
                    text.text_formatting(_("-> Found ") + repo_search[comp].text + _(" similarity is ") + str(similarity(str(repo_search[comp].text),str(srch))*100)+"%", 1, 'info')
            if repo_search[comp].text == srch and action == "absolute":
                return True
                break
