#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import file_modify as mdfy
import constants as cons
import functions
import text_formatting as text, os, sys
import gettext
import search


gettext.bindtextdomain("peynir","/language")
gettext.textdomain("peynir")
_ = gettext.gettext

def conflicts(source):
    root = functions.get_root(cons.sprpckg_dir+source+".xml")
    """ Resolving conflicts """
    text.text_formatting(_(">> Check for conflicts..."), 0, 'info')
    conflictcount = len(root[1])
    conflicts = root[1]
    if conflictcount > 0:
        text.text_formatting(str(conflictcount) + _(" conflicts have found."), 1, 'info')
        text.text_formatting(_("Following suprapackage(s) will remove. "), 0, 'info')
        for conf in root[1]:
            try:
                text.text_formatting(conf.text + " ==> " + get.description(conf.text), 1, '')
            except:
                text.text_formatting(conf.text + _(" ==> There is no description for this suprapackage"), 1, 'warning')
        if os.path.isfile(cons.sprpckg_dir + conf.text + ".xml"):
            answer = input(_("Are you want to remove these suprapackages (Y/N): ")) 
            answer.upper()
        elif cons.confm:
            answer = _("Y")
        else:
            answer = _("Y")
        
        if answer == _("Y"):
            for conf in root[1]:
                package = conf.text
                if suprapackage_check(package):
                    remove(package,"","")
                else:
                    text.text_formatting(package + _(" is not installed"), 0, 'warning')
        else:
            text.text_formatting(package + _("Suprapackage couldn't installed."), 0, 'error')
            sys.exit(1)
    else:
        text.text_formatting(_("There is a no conflict"), 1, 'info')
            
def dependencies(source,action):
    text.text_formatting(_(">> Resolving dependencies.."), 0, 'info')
    root = functions.get_root(cons.sprpckg_dir+source+".xml")
    #Bağımlılıklar çözülüyor
    dependcount = len(root[2])
    dependencies = root[2]
    if dependcount > 0:
        text.text_formatting(str(dependcount) + _(" dependencies have found."), 1, 'info')
        #Tamamen kaldırma işlemi için ....
        if action == "remove":
            text.text_formatting(_("Following suprapackage(s) will remove. "), 1, 'info')
            for dep in root[2]:
                try:
                    text.text_formatting(dep.text + " ==> " + get_description(dep.text), 1, 'info')
                except:
                    text.text_formatting(dep.text + _(" ==> There is no description for this suprapackage"), 1, 'warning')
            if cons.confm:
                answer = _("Y")
            else:
                answer = input(_("Are you want to remove these suprapackages (Y/N): "))
                answer = answer.upper()
            if answer == _("Y"):
                for dep in root[2]:
                    package = dep.text
                    functions.remove(package,"skip",source)
            else:
                text.text_formatting(_("Dependencies coulnd't removed so remove process couldn't continue."), 0, 'error')
                sys.exit(1)
        else:
            text.text_formatting(_("Following suprapackage(s) will install. "), 0, 'info')
            for dep in root[2]:
                if not search.srch_pynr(dep.text,'Peynir/Name','absolute') and not suprapackage_check(str(dep.text)):
                    text.text_formatting(dep.text + _(" couldn't found in repository, you can install it manually"), 1, 'warning')
                    os.remove(cons.sprpckg_dir + source + ".xml")
                    sys.exit(1)
                else:
                    try:
                        text.text_formatting(dep.text + " ==> " + get_description(dep.text), 1, 'info')
                    except:
                        text.text_formatting(dep.text + _(" ==> There is no description for this suprapackage"), 1, 'info')
            if cons.confm:
                answer = _("Y")
            else:
                answer = input(_("Are you want to install these suprapackages (Y/N): "))
                answer = answer.upper()
            if answer == _("Y"):
                for dep in root[2]:
                    package = dep.text
                    if not functions.suprapackage_check(package):
                        functions.install(package,"","") #İç içe bağımlılık sorunu olacak o neden ilave bir fonksiyon paramatresi ise bu soruyu bir kez sordurulabilir
                    else:
                        text.text_formatting(">> " + package + _(" is already installed"), 0, 'info')
                    mdfy.modify_add(cons.sprpckg_dir+package+".xml","<Dependencies","'>"," " + source,"previous") 
            else:
                os.remove(cons.sprpckg_dir+source+".xml")
                text.text_formatting(_("Dependencies coulnd't installed so install process couldn't continue."), 0, 'error')
                sys.exit(1)
    else:
        text.text_formatting(_("There is a no dependencies"), 1, 'info')
            
def rmv_local_dependencies(source):
    root = functions.get_root(cons.sprpckg_dir+source+".xml")
    dependcount = len(root[2])
    dependencies = root[2]
    if dependcount > 0:
        for dep in dependencies:
            if os.path.isfile(cons.sprpckg_dir + dep.text +".xml"):
                mdfy.modify_rmv(cons.sprpckg_dir + dep.text +".xml","<Dependencies ",""," " + source,"next","",4)
            else:
                text.text_formatting(_("There is no file to remove local dependencies"), 1, 'warning')
