#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import text_formatting as text, os, shutil, get_text
from tempfile import NamedTemporaryFile


"""Module for Manupilate files"""
def get_prop(source):
    """Get owner and attributes of modifiying files to restore this proporties after manuplating the file"""
    file_prep = []
    get_owner = os.popen("ls -l "+source+"|awk '{print $3}'")
    file_prep.append(get_owner.read())
    get_file_prop = os.popen("stat -c %a "+source)
    file_prep.append(get_file_prop.read())
    return file_prep
    
def set_prop(source, attributes):
    """Set owner and attributes of the manupilated file borrowed from before manuplate it"""
    os.system("chmod " + attributes[1].strip() + " " + source)
    os.system("chown "+  attributes[0].strip() + " " + source)
        
def modify_rmv(tar_file,srch,indicator,action,place,rplc,indent):
    """Functions for removing string from file"""
    a = get_prop(tar_file)
    text.text_formatting("-> removing " + action + " from " + tar_file, 1, 'info')
    try:
        with open(tar_file) as fin, NamedTemporaryFile(dir='.', delete=False) as fout:
            counter = 0
            for line in fin:
                if place == "first" and counter == 0:
                    line = line.replace(action,rplc)
                elif srch in line:
                    position = line.find(indicator)
                    if place == "previous":
                        line = line[:position].replace(action,rplc).strip() + line[position:]
                    elif place == "next":
                        if indent >0:
                            tabs = " "
                            line = line[:position] + line[position:].replace(action,rplc)
                            for i in range(indent):
                                line = tabs + line
                        else:
                            line = line[:position] + line[position:].replace(action,rplc)
                if place == "after" or place == "before":
                    if action in line:
                        line = ""
                fout.write(line.encode('utf8'))
                counter = counter + 1
            os.rename(fout.name, tar_file)
            set_prop(tar_file,a)
    except:
        text.text_formatting(_("Couldn't found target file"),1, 'error')
     
def modify_add(tar_file,srch,indicator,action,place):
    """Functions for adding a string to file"""
    text.text_formatting("-> adding " + action + " to " + tar_file, 1, 'info')
    a = get_prop(tar_file)

    try:
        if place == "last":
            open(tar_file,"a").write("\n" + action)
        else:
            
            with open(tar_file) as fin, NamedTemporaryFile(dir='.', delete=False) as fout:
                counter = 0
                for line in fin:
                    if place == "first" and counter == 0:
                        line = action + "\n" + line
                    elif srch in line:
                        position = line.find(indicator)
                        if place == "previous":
                            line = line[:position] + action + line[position:]
                        elif place == "next":
                            line = line[:position+len(indicator)] + action + line[position+len(indicator):]
                        elif place == "after":
                            line = line + action + "\n"
                        elif place == "before":
                            line = action + "\n" + line
                    fout.write(line.encode('utf8'))
                    counter = counter + 1
                shutil.move(fout.name, tar_file)
                set_prop(tar_file,a)
    except:
        text.text_formatting(_("Couldn't found target file"), 1, 'error')
