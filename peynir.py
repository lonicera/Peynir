#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#       peynir.py - Suprapackage Manager for Archlinux. It's also a framework for configuring Archlinux or other pacman based distribution .
#
#       Copyright 2011 Şenol Alan <alansenol@hotmail.com>
#
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.
#
#
#       Version:0.6-1

import os, sys, shutil, logging 
import xml.etree.ElementTree as etree
import urllib.request
import difflib
import subprocess
from tempfile import NamedTemporaryFile
import gettext
gettext.bindtextdomain("peynir","/opt/peynir/language")
gettext.textdomain("peynir")
_ = gettext.gettext

class Constants:
    """Constant for peynir suprapackage Manager"""
    def __init__(self):
        self.repo = '/var/cache/peynir/peynir.xml'
        self.db_dir = '/var/cache/peynir/'
        self.sprpckg_dir = '/var/cache/peynir/packages/'
        self.mirror = 'http://lonicera.byethost7.com/peynir/'
        self.db_file = 'peynir.xml'
        self.log_file = '/var/cache/peynir/peynir_log.log'
        self.confm = False
        self.cachedir = None

cons = Constants()

class Search:
    """Search or find class for peynir"""
    def similarity(self,first,second):
        self.seq=difflib.SequenceMatcher(a=first.lower(), b=second.lower())
        return round(self.seq.ratio(),1)
    
    def local_dependency(self,source,package):
        """Get local dependencies when suprapackage removing from system"""
        self.dep_list = []
        source_tree = etree.parse(cons.sprpckg_dir+source+".xml")
        source_root = source_tree.getroot()
        local_dep = source_root[2].attrib['local']
        for i in local_dep.strip().split(" "):
            if i != package and len(local_dep.strip().split(" ")) > 0:
                self.dep_list.append(i)
        return self.dep_list
    
    def local_search(self,source):
        """Search suprapackage in local"""
        dirlist = os.listdir(cons.sprpckg_dir)
        counter = 0
        for fname in dirlist:
            if source == "" or source == "all":
                text.text_formatting(fname[:-4] + " ==> " + get_description(fname[:-4]),1,'info')  
            elif self.similarity(fname[:-4],source) > 0.45 and len(dirlist) >0:
                text.text_formatting(fname[:-4] + " ==> " + get_description(fname[:-4]),1, 'info')
    
    def srch_pynr(self,srch,node,action):
        """Search suprapackage in repository"""
        repo_tree = etree.parse(cons.repo)
        repo_root = repo_tree.getroot()
        repo_search = repo_root[1].findall(node)
        if srch == "all":
            text.text_formatting(str(len(repo_root[1])) + " suprapackage have found.", 0, 'info')
            for rep in repo_root[1]:
                text.text_formatting(rep[0].text + " ==> " + get_description(rep[0].text), 1, 'info')
        else:
            for comp in range(len(repo_search)):
                if action == "find":
                    if self.similarity(str(repo_search[comp].text),str(srch)) > 0.45 and int(len(repo_search)) >0:
                        text.text_formatting("-> Found " + repo_search[comp].text + " similarity is " + str(self.similarity(str(repo_search[comp].text),str(srch))*100)+"%",1)
                if repo_search[comp].text == srch and action == "absolute":
                    return True
                    break

search = Search() 


class Repair:
    """ Check suprapackage and correct system """
    def def_check(self, package):
        tree = etree.parse(cons.sprpckg_dir+package)
        root = tree.getroot()
        steps = len(root[3])
        text.text_formatting(str(steps) + _(" step(s) will checked."),0,'debug')
        counter = 1
        for step in root[3]:
            text.text_formatting("==> Step " + str(counter) + " of " + str(steps) + " is checking",0,'debug')
            action_type = step.attrib["type"]
            if action_type == "1":
                local_pacman_dir = "/var/lib/pacman/local/"
                pac_action = step.attrib["action"]
                package = step.text
                text.text_formatting(_(package + " is checking... "),0,'debug')
                if pac_action == "install":
                    if not package in os.listdir(local_pacman_dir):
                        text.text_formatting(_("Error occured in step of "),1,'error')
                elif pac_action == "remove":
                    if package in os.listdir(local_pacman_dir).index():
                        text.text_formatting(_("Error occured in step of "),1,'error')
            elif action_type == "2":
                """ Currently simpliy checking avaible, functions of modify_add and modify_rmv maybe split into two function in which one of them is responsible for finding modifying site that can be used for repair, and adding or removing function """ 
                try:
                    if (convert(step.text) in open(step[0].attrib["source"]).read() and step[0].attrib["type"] == "remove") or ((not convert(step.text) in open(tar_file).read() and step[0].attrib["type"] == "add")):
                        text.text_formatting(_("Error occured in step of "), 1, 'error')
                except:
                    text.text_formatting(_("Couldn't found target file"),1, 'error')
            elif action_type == "3":
                """ There ara some problem with checking this step, one apporach is that executing the reverse attributes defined in the step and reexecute original code, """
                print("Bakalım ne olacak")
            counter += 1
                     
    def __init__(self,package):
        """ Below code can be replaced by variable that included in Constant class  """
        dirlist = os.listdir(cons.sprpckg_dir)
        if package == "all":
            if not dirlist:
                text.text_formatting(_("There is no installed suprapackage "),0 , 'info')
            else:
                for fname in dirlist:
                    self.def_check(fname)
        else:
            def_check(package)

        
class FileModify:
    """Class for Manupilate files"""
    def get_prop(self,source):
        """Get owner and attributes of modifiying files to restore this proporties after manuplating the file"""
        self.file_prep = []
        self.get_owner = os.popen("ls -l "+source+"|awk '{print $3}'")
        self.file_prep.append(self.get_owner.read())
        self.get_file_prop = os.popen("stat -c %a "+source)
        self.file_prep.append(self.get_file_prop.read())
        return self.file_prep
    
    def set_prop(self,source, attributes):
        """Set owner and attributes of the manupilated file borrowed from before manuplate it"""
        os.system("chmod " + attributes[1].strip() + " " + source)
        os.system("chown "+  attributes[0].strip() + " " + source)
        
    def modify_rmv(self,tar_file,srch,indicator,action,place,rplc,indent):
        """Functions for removing string from file"""
        a = self.get_prop(tar_file)
        text.text_formatting("-> removing " + action + " from " + tar_file,1, 'debug')
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
                self.set_prop(tar_file,a)
        except:
            text.text_formatting(_("Couldn't found target file"),1, 'error')
       
    def modify_add(self,tar_file,srch,indicator,action,place):
        """Functions for adding string to file"""
        text.text_formatting("-> adding " + action + " to " + tar_file, 1, 'debug')
        a = self.get_prop(tar_file)

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
                    self.set_prop(tar_file,a)
        except:
            text.text_formatting(_("Couldn't found target file"), 1, 'error')

class TextFormatting:
    def text_formatting(self,source,level, log_level):
        logging.basicConfig(filename=cons.log_file, format='%(asctime)s:%(levelname)s:%(message)s',  datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)
        self.tab_space = "   "
        for i in range(level):
            source = self.tab_space + source
        if log_level == "info":
            logging.info(source)   
        elif log_level == "warning":
            logging.warning(source)
        elif log_level == "debug":
            logging.debug(source)
        elif log_level == "error":
            logging.error(source)    
        print(source)

mdfy = FileModify()
text = TextFormatting()

class DepConf:
    def conflicts(self,source):
        tree = etree.parse(cons.sprpckg_dir+source+".xml")
        root = tree.getroot()
        """ Resolving conflicts """
        text.text_formatting(_(":: Check for conflicts..."), 0, 'debug')
        conflictcount = len(root[1])
        conflicts = root[1]
        if conflictcount > 0:
            text.text_formatting(str(conflictcount) + _(" conflicts have found."), 1, 'debug')
            text.text_formatting(_("Following suprapackage(s) will remove. "),0)
            for conf in root[1]:
                try:
                    text.text_formatting(conf.text + " ==> " + get.description(conf.text), 1, '')
                except:
                    text.text_formatting(conf.text + _(" ==> There is no description for this package"), 1, 'warning')
            if os.path.isfile(cons.sprpckg_dir + conf.text + ".xml"):
                answer = input(_("Are you want to remove these packages (Y/N): "))
                answer.upper()
            elif cons.confm:
                answer = _("Y")
            else:
                answer = _("Y")
            
            if answer == _("Y"):
                for conf in root[1]:
                    package = conf.text
                    if package_check(package):
                        remove(package,"","")
                    else:
                        text.text_formatting(package + _(" is not installed"), 0, 'warning')
            else:
                sys.exit(_("Suprapackage couldn't installed."))
        else:
            text.text_formatting(_("There is a no conflict"), 1, 'debug')
            
    def dependencies(self,source,action):
        text.text_formatting(_(":: Resolving dependencies.."), 0, 'info')
        tree = etree.parse(cons.sprpckg_dir+source+".xml")
        root = tree.getroot()
        #Bağımlılıklar çözülüyor
        dependcount = len(root[2])
        dependencies = root[2]
        if dependcount > 0:
            text.text_formatting(str(dependcount) + _(" dependencies have found."), 1, 'info')
            #Tamamen kaldırma işlemi için ....
            if action == "remove":
                text.text_formatting(_("Following suprapackage(s) will remove. "),1, 'info')
                for dep in root[2]:
                    try:
                        text.text_formatting(dep.text + " ==> " + get_description(dep.text),1)
                    except:
                        text.text_formatting(dep.text + _(" ==> There is no description for this package"), 1, 'warning')
                if cons.confm:
                    answer = _("Y")
                else:
                    answer = input(_("Are you want to remove these packages (Y/N): "))
                    answer = answer.upper()
                if answer == _("Y"):
                    for dep in root[2]:
                        package = dep.text
                        remove(package,"skip",source)
                else:
                    sys.exit(_("Dependencies coulnd't removed so remove process couldn't continue."))
            else:
                text.text_formatting(_("Following suprapackage(s) will install. "), 0, 'debug')
                for dep in root[2]:
                    try:
                        text.text_formatting(dep.text + " ==> " + get_description(dep.text), 1, 'debug')
                    except:
                        text.text_formatting(dep.text + _(" ==> There is no description for this package"), 1, 'warning')
                if cons.confm:
                    answer = _("Y")
                else:
                    answer = input(_("Are you want to install these packages (Y/N): "))
                    answer = answer.upper()
                if answer == _("Y"):
                    for dep in root[2]:
                        package = dep.text
                        if not package_check(package):
                            install(package,"","") #İç içe bağımlılık sorunu olacak o neden ilave bir fonksiyon paramatresi ise bu soruyu bir kez sordurulabilir
                        else:
                            text.text_formatting(":: " + package + _(" is already installed"), 0, 'info')
                        mdfy.modify_add(cons.sprpckg_dir+package+".xml","<Dependencies","'>"," " + source,"previous") 
                else:
                    os.remove(cons.sprpckg_dir+source+".xml")
                    sys.exit(_("Dependencies coulnd't installed so install process couldn't continue."))
        else:
            text.text_formatting(_("There is a no dependencies"), 1, 'info')
            
    def rmv_local_dependencies(self,source):
        tree = etree.parse(cons.sprpckg_dir+source+".xml")
        root = tree.getroot()
        dependcount = len(root[2])
        dependencies = root[2]
        if dependcount > 0:
            for dep in dependencies:
                if os.path.isfile(cons.sprpckg_dir + dep.text +".xml"):
                    mdfy.modify_rmv(cons.sprpckg_dir + dep.text +".xml","<Dependencies ",""," " + source,"next","",4)
                else:
                    text.text_formatting(_("There is no file to remove local dependencies"), 1, 'warning')

relationship = DepConf()
    
def db_file_check():
    if not os.path.isfile(cons.log_file):
        logging.basicConfig(filename=cons.log_file, format='%(asctime)s:%(levelname)s:%(message)s',  datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)
        text.text_formatting(_("Log file created"),0,'warning')
    if not os.path.isfile(cons.db_dir+cons.db_file):
        try:
            text.text_formatting(_("Database could'nt found. Getting from server"), 0, 'warning')
            if not os.path.isdir(cons.db_dir):
                try:
                    text.text_formatting(_("Database folder is creating..."), 0, 'info')
                    os.makedirs(cons.db_dir)
                    os.makedirs(cons.sprpckg_dir)
                except:
                    text.text_formatting(_("Database dir couldn't create"), 0, 'error')
            retrieve(cons.db_dir,cons.mirror+cons.db_file,cons.db_dir+cons.db_file)
            text.text_formatting(_("Database successfully updated."), 0, 'debug')
        except:
            text.text_formatting(_("Database couldn't updated."), 0, 'error')
            sys.exit(1)


def convert_library(find):
    result = ""
    if find == "@anc":
       result = '&'
    elif find == "@per":
       result = '%'
    return result

def convert(source):
    position = source.find('@')
    con_src = source[position:position+4]
    result = source.replace(con_src,convert_library(con_src))
    return result

def uptodate(xml_source,type_file):
    if type_file == "web":
       try:
           tree = etree.parse(urllib.request.urlopen(xml_source))
           text.text_formatting(_("-> Peynir also updating pacman repositories"), 1, 'info')
           devnull = open('/dev/null', 'w')
           try:
               subprocess.Popen("pacman -Sy --noconfirm ", shell=True, stdout=devnull).wait()
           except:
               text.text_formatting(_("There is a problem with pacman sync repository, If you continue to upgrade, you can get some error"), 1, 'warning') 
       except:
           text.text_formatting(_("Database couldn't updated."), 0, 'error')
           sys.exit(1)
    else:
        try:
            tree = etree.parse(xml_source)
        except:
            text.text_formatting(_("There is a problem with xml file"), 0, 'error')
            sys.exit(1)
            
    root = tree.getroot()
    find_node = root[0].findall('Last_update')
    up_date = find_node[0].text
    return up_date
        
def upcontrol(srch,place,stopped=False):
    if place == "repo":
       repo_tree = etree.parse(cons.repo) # Bu kısmı bir fonksiyonla kısalt
       repo_root = repo_tree.getroot()
       for step in repo_root[1]:
           for st in step:
               if stopped and st.tag == "Version":
                   return st.text
               if st.tag == "Name" and st.text == srch:
                   stopped = True
    if place == "local":
       repo_tree = etree.parse(cons.sprpckg_dir+srch+".xml")
       repo_root = repo_tree.getroot()
       for root in repo_root[0]:
           if root.tag == "Version":
               return root.text

#Bu kısım düzenlenerek üstpaketle ilgili herhangi bir bilgi de çekilebilir.
def get_description(package):
    repo_tree = etree.parse(cons.repo)
    repo_root = repo_tree.getroot()
    repo_search = repo_root[1].findall('Peynir/Name')
    repo_search1 = repo_root[1].findall('Peynir/Summary')
    for comp in range(len(repo_search)):
        if repo_search[comp].text == package:
            sayi = comp
            break
    try:
        return repo_search1[(sayi*2)+1].text
    except:
        return _("There is no description for this package")
            

def retrieve(place,url,file):
    status = "false"
    os.chdir(place)
    try:
        req=urllib.request.Request(url)
        req.add_header("User-Agent","Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US) AppleWebKit/525.13 (KHTML,     like Gecko) Chrome/0.2.149.29 Safari/525.13")
        usock = urllib.request.urlopen(req)
        data = usock.read()
        usock.close()
        urllib.request.urlcleanup() 
    except:
        text.text_formatting(file + _(" could not retrivied from mirror"), 0, 'error')
        sys.exit(1)

    fp = open(file, 'wb')
    fp.write(data)
    fp.close()
    
    

def sync_repo():
    text.text_formatting(_(":: Local database synchronizing with server"), 0, 'info')
    if not os.path.isfile(cons.db_dir+cons.db_file) or uptodate(cons.db_dir+cons.db_file,"local") != uptodate(cons.mirror+cons.db_file,"web"):
       try:
           retrieve(cons.db_dir,cons.mirror+cons.db_file,cons.db_dir+cons.db_file)
           text.text_formatting(_("Database successfully updated."), 0, 'info')
       except:
           text.text_formatting(_("Database couldn't updated."), 0, 'error')
           sys.exit(1)
    else:
       text.text_formatting(_("Database already updated."), 0, 'info')
       #sys.exit(1)


def package_check(package):
    return os.path.isfile(cons.sprpckg_dir+package+".xml")

            
def install(source, place, adress):
    if package_check(source) and not place == "local":
       sys.exit(_(":: This suprapackage already installed."))
    
    if place == "local":
        try:
            if adress != "":
                tree = etree.parse(adress+"/"+source)
                cp_adress = adress+"/"+source
            else:
                tree = etree.parse(os.getcwd()+"/"+source)
                cp_adress = ""
            if not os.path.isfile(cons.sprpckg_dir+"/"+source):
                shutil.copyfile(cp_adress, cons.sprpckg_dir+"/"+source)
            position = source.find('.')
            source = source[:position]
        except:
            print(tree)
            text.text_formatting("Suprapackage source couldn't find, check suprapackege path", 0, 'error')
            sys.exit(0)
    else:
        if cons.cachedir is None or (not cons.cachedir is None and not os.path.isfile(cons.cachedir+"/"+source + ".xml")):
            if not cons.cachedir is None and not os.path.isfile(cons.cachedir+"/"+source):
                text.text_formatting(_(source + " couldn't found in cache directory so trying to retrive from server"), 1, 'warning')
            retrieve(cons.sprpckg_dir,cons.mirror+source+".xml",cons.sprpckg_dir+source+".xml")
            tree = etree.parse(cons.sprpckg_dir+source+".xml")
        else:
            shutil.copyfile(cons.cachedir+source+".xml", cons.sprpckg_dir+"/"+source+".xml")
    tree = etree.parse(cons.sprpckg_dir+source+".xml")
    text.text_formatting(":: " + source + _(" suprapackage is installing"), 0, 'info')
    relationship.conflicts(source)
    relationship.dependencies(source,"")
    root = tree.getroot()
    steps = len(root[3])
    text.text_formatting(str(steps) + _(" step(s) will executed."), 0, 'info')
    counter = 1
    for step in root[3]:
       action_type = step.attrib["type"]
       text.text_formatting("==> Step " + str(counter)+ " of " + str(steps) + " is executing", 0, 'debug')
       #Alttaki kodu type 4 de de kullanıldığından fonksiyon haline gelse iyi olacak
       try:
           if action_type == "1":
               pac_action = step.attrib["action"]
               package = step.text
               pacman(package,pac_action)
           elif action_type == "2":
               mdfy_type = step[0].attrib["type"]
               source1 = step[0].attrib["source"]
               indicator = step[0].attrib["indicator"]
               search = step[0].attrib["search"]
               action = convert(step[0].text)
               place = step[0].attrib["place"]
               if mdfy_type == "add":
                   mdfy.modify_add(source1,search,indicator,action,place)
               else:
                   mdfy.modify_rmv(source1,search,indicator,action,place, " ",0) 
           elif action_type == "3":
               command = step.text
               if execute(command) != 0:
                   text.text_formatting(_("Error occureed in step of ") + step + ", so the installation of suprapackge will be reverted " , 0, 'error')
                   remove_action(source, "complete", step)
                   break
           elif action_type == "4":
               question = step[0].text
               text.text_formatting("-> " + str(len(step)-1) + _(" substep(s) will execute for this step"), 1, 'info')
               answer = input(question)
               mdfy.modify_add(cons.sprpckg_dir+source+".xml",question,"step","answer='"+answer+"' ","previous")
               for i in step:
                   ans_action = i.text
                   position = ans_action.find('@')
                   step_type = i.attrib["step"]
                   if int(i.attrib["step"]) > 0:
                       if int(i.attrib["step"]) == 1:
                           pac_action = step.attrib["action"]
                           package = step.text
                           if position > 0:
                               package = package[:position] + answer + package[position+7:]
                           pacman(package,pac_action)
                       elif int(i.attrib["step"]) == 2:
                           mdfy_type = i.attrib["type"]
                           source = i.attrib["source"]
                           indicator = i.attrib["indicator"]
                           search = i.attrib["search"]
                           ans_action = i.text
                           if position > 0:
                               ans_action = ans_action[:position] + answer + ans_action[position+7:]
                           place = i.attrib["place"]
                           if mdfy_type == "add":
                               mdfy.modify_add(source,search,indicator,ans_action,place)
                           else:
                               mdfy.modify_rmv(source,search,indicator,ans_action,place," ",0) 
                       elif int(i.attrib["step"]) == 3:
                           command = i.text
                           if position > 0:
                               command = ans_action[:position] + answer + ans_action[position+7:]
                           if execute(command) != 0:
                               text.text_formatting(_("Error occureed in step of ") + step + ", so the installation of suprapackge will be reverted ", 0, 'error')
                               remove_action(source, "complete", i)
                               break
                           #execute(command)
           counter = counter + 1
       except:
           text.text_formatting(_("Error occureed in step of ") + step, 0, 'error')
           sys.exit(1)

def remove(source, rmv_type, dep_source):
    if not package_check(source):
        text.text_formatting(_("This suprapackage is not installed."), 0,  'error')
        sys.exit(1)
    text.text_formatting(":: " + source + _(" suprapackage is removing"), 0, 'info')
    if rmv_type == "complete":
       relationship.dependencies(source,"remove")
    local_dep = search.local_dependency(source," ")
    
    if (len(local_dep) == 1 and not "" in local_dep and dep_source in local_dep) or rmv_type == "upgrade":
        remove_action(source, rmv_type, "")           
    elif len(local_dep) > 0 and not "" in local_dep:
       text.text_formatting(_("Following suprapackages requires ") + source + _(" suprapackage"), 0, 'info')
       for i in search.local_dependency(source," "):
           if not i == "" and not i == dep_source:
              text.text_formatting(i + " ==> " + get_description(i), 1, 'info')
       if rmv_type != "skip":
           sys.exit(1)
       else:
           text.text_formatting(_("Skipping removing ") + source + _(" suprapackage and continue remove process"), 0, 'warning') 
    else:
        remove_action(source, rmv_type, "")
        
               
def remove_action(source, rmv_type, access_point):        
    relationship.rmv_local_dependencies(source)
    try:
       tree = etree.parse(cons.sprpckg_dir+source+".xml")
       os.remove(cons.sprpckg_dir+source+".xml")
    except:
       text.text_formatting(_("Local package couldn't found"), 0, 'error')
       sys.exit(1)
    root = tree.getroot()
    steps = len(root[3])
    counter = 1
    if access_point == "":
        access_point = root[3]
        
    for step in reversed(access_point):
       action_type = step.attrib["type"]
       try:
           remove_tag = step.attrib["remove_tag"]
       except KeyError:
           remove_tag = " "
       text.text_formatting("==> Step " + str(counter)+ " of " + str(steps) + " is executing", 0, 'debug')
       try:
           if action_type == "1":
               if remove_tag == "skip":
                   text.text_formatting(_("-> Skipping this step for remove action"), 1, 'info')
               else:
                   package = step.text
                   pacman(package,"remove")
           elif action_type == "2":
               if remove_tag == "skip":
                   text.text_formatting(_("-> Skipping this step for remove action"), 1, 'info')
               else:
                   mdfy_type = step[0].attrib["type"]
                   if mdfy_type == "add":
                       mdfy_type = "remove"
                   elif mdfy_type == "remove":
                       mdfy_type = "add"
                   source = step[0].attrib["source"]
                   indicator = step[0].attrib["indicator"]
                   search = step[0].attrib["search"]
                   action = convert(step[0].text)
                   place = step[0].attrib["place"]
                   if mdfy_type == "add":
                       mdfy.modify_add(source,search,indicator,action,place)
                   else:
                       mdfy.modify_rmv(source,search,indicator,action,place, "",0) 
           elif action_type == "3" and remove_tag != "skip":
               if remove_tag == "skip":
                   text.text_formatting(_("-> Skipping this step for remove action"), 1, 'info')
               else:
                   try:
                       reverse = step.attrib["reverse"]
                       execute(reverse)
                   except:
                       text.text_formatting(_("There is no defined action for this step"), 1, 'warning')
           elif action_type == "4": # Buraya reverse özelliklerini ekle
               try:
                   answer= step[0].attrib["answer"]
                   text.text_formatting("-> " + str(len(step)-1) + _(" substep(s) will execute for this step"), 1, 'info')
                   for i in step:
                       try:
                           remove_tag = i.attrib["remove_tag"]
                       except KeyError:
                           remove_tag = " "
                       ans_action = i.text
                       position = ans_action.find('@')
                       step_type = i.attrib["step"]
                       if int(i.attrib["step"]) > 0:
                           if int(i.attrib["step"]) == 1:
                               if remove_tag == "skip":
                                   text.text_formatting(_("-> Skipping this step for remove action"), 1, 'info')
                               else:
                                   pac_action = step.attrib["action"]
                                   if pac_action == "remove":
                                       pac_action = "install"
                                   elif pac_action == "install":
                                       pac_action = "remove"
                                   package = step.text
                                   if position > 0:
                                       package = package[:position] + answer + package[position+7:]
                                       pacman(package,pac_action)
                           elif int(i.attrib["step"]) == 2:
                               if remove_tag == "skip":
                                   text.text_formatting(_("-> Skipping this step for remove action"), 1, 'info')
                               else:
                                   mdfy_type = i.attrib["type"]
                                   if mdfy_type == "add":
                                       mdfy_type = "remove"
                                   elif mdfy_type == "remove":
                                       mdfy_type = "add"
                                   source = i.attrib["source"]
                                   indicator = i.attrib["indicator"]
                                   search = i.attrib["search"]
                                   ans_action = i.text
                                   if position > 0:
                                       ans_action = ans_action[:position] + answer + ans_action[position+7:]
                                   place = i.attrib["place"]
                                   if mdfy_type == "add":
                                       mdfy.modify_add(source,search,indicator,ans_action,place)
                                   else:
                                       mdfy.modify_rmv(source,search,indicator,ans_action,place, " ",0) 
                           elif int(i.attrib["step"]) == 3:
                               if remove_tag == "skip":
                                   text.text_formatting(_("-> Skipping this step for remove action"), 1, 'info')
                               else:
                                   command = i.text
                                   if position > 0:
                                       try:
                                           reverse = i.attrib["reverse"]
                                           position = reverse.find('@')
                                           command = reverse[:position] + answer + reverse[position+7:]
                                           execute(command)
                                       except:
                                           command = ans_action[:position] + answer + ans_action[position+7:]
                                           execute(command)
                       
               except:
                   text.text_formatting(_("There is no defined action for this step"), 1, 'warning')
           counter = counter + 1
       except:
           text.text_formatting(_("Error occured when remove suprapackage"), 0, 'error') #bu ne bu, bu ne, ne hatası bu :)
           sys.exit(1)
           
    

def upgrade():
    dirlist=os.listdir(cons.sprpckg_dir)
    counter = 0
    up_list = []
    for fname in dirlist:
       if fname[-3:] == "xml" and upcontrol(fname[:-4],"local") != upcontrol(fname[:-4],"repo"):
           up_list.append(fname[:-4]);
           counter = counter + 1
    if len(up_list) == 0:
        text.text_formatting(_("There is nothing to do"), 0, 'info')
    else:
        text.text_formatting(_("Following suprapackage(s) will upgrade"), 0, 'info')
        for up in up_list[0:]:
            text.text_formatting(up + " ==> " + get_description(up), 1, 'info')
        devnull = open('/dev/null', 'w')
        try:
            text.text_formatting(_("-> Peynir first upgrade your system via pacman"), 1, 'info')
            subprocess.Popen("pacman -Su --noconfirm ", shell=True, stdout=devnull).wait()
        except:
            text.text_formatting(_("There is a problem with upgrade the system via pacman, If you continue to upgrade, I can get some error"), 1, 'warning')
        for up in up_list[0:]:
            text.text_formatting(up + _(" suprapackage is upgrading ..."), 0, 'info')
            #answer ı nasıl aktaracağız bakalım ???
            try:
                text.text_formatting(_("-> Retrieve updated suprapackage from server"), 1, 'info')
                retrieve(cons.sprpckg_dir,cons.mirror + up +".xml",cons.sprpckg_dir + up + "_bck" +".xml")
            except:
                text.text_formatting(_("-> There is a problem with getting updated suprapackage from server"), 1, 'error')
            try:
                tree = etree.parse(cons.sprpckg_dir + up +".xml")
                root = tree.getroot()
                local_dep = root[2].attrib['local']
                text.text_formatting(_("-> Transision local dependencies from old one to updated one"), 1, 'info')
                mdfy.modify_add(cons.sprpckg_dir + up + "_bck"+".xml","<Dependencies","'>"," " + local_dep,"previous")
            except:
                text.text_formatting(_("-> Error from transision local dependencies"), 0, 'error')             
            remove(up,"upgrade","")
            shutil.move(cons.sprpckg_dir + up + "_bck"+".xml", cons.sprpckg_dir + up + ".xml")
            install(up + ".xml","local","")

def pacman(package,action):
    text.text_formatting("-> " + action.strip("e") + "ing " + package + " via pacman", 1, 'info') #remove, removing eksikliğini düzelt
    if action == "install":
       retri = "pacman -S --noconfirm "+ package
    elif action == "remove":
       retri = "pacman -Rs --noconfirm "+ package
    devnull = open('/dev/null', 'w')
    subprocess.Popen(retri, shell=True, stdout=devnull).wait()

def execute(command):
    text.text_formatting("-> executing " + command + " in the shell", 1, 'info')
    retri = command
    """ Better error handling is required, check out lpms code """
    stdout = subprocess.PIPE; stderr=subprocess.PIPE
    result = subprocess.Popen(command, shell=True, stdout=stdout, stderr=stderr)
    output, err = result.communicate()
    return result.returncode
    #stdout = subprocess.PIPE; stderr=subprocess.PIPE
    #result = subprocess.Popen(retri, shell=True, stdout=stdout, stderr=stderr).wait()
    
    #return result.returncode
    #subprocess.Popen(retri, shell=True).wait()  Old code may be requied, i hope not

### Ana bölüm
def main():
    if not os.geteuid()==0:
        sys.exit(_("You must be root to run this application, please use sudo and try again."))
    db_file_check()
    for argv in sys.argv:
        if argv == "--no-confirm":
            cons.confm = True
            sys.argv.remove('--no-confirm')
    for argv in sys.argv:  
        if argv.find('--cache-dir') == 0:
            cons.cachedir = argv[12:].strip()
            if not cons.cachedir[len(cons.cachedir)-1:len(cons.cachedir)] == "/":
                cons.cachedir = cons.cachedir+"/"
                print(cons.cachedir)       
            sys.argv.remove(argv)
            
   
    if len(sys.argv) == 1:
        sys.stderr.write(_('Usage: peynir [command] [suprapackage] \n Commands: \n        -S Install suprapackage \n        -U Install local suprapackage \n        -R Remove suprapackage \n        -Rs Remove suprapackage and its dependencies \n        -Sy Update repository \n        -Su Upgrade the system \n        -Ss Search suprapackege in repository \n        -Qs Search suprapackege in local \n        -h Display the help screen \n'))
        sys.exit(1)
    elif sys.argv[1] == "-Sy":
        sync_repo()
    elif sys.argv[1] == "-Su":
        upgrade()
    elif sys.argv[1] == "-O":
        Repair("all")
    elif sys.argv[1] == "-Syu":
        sync_repo()
        upgrade()    
    elif len(sys.argv) == 1:
        sys.stderr.write(_('Usage: peynir [command] [suprapackage] \n Commands: \n        -S Install suprapackage \n        -U Install local suprapackage \n        -R Remove suprapackage \n        -Rs Remove suprapackage and its dependencies \n        -Sy Update repository \n        -Su Upgrade the system \n        -Ss Search suprapackege in repository \n        -Qs Search suprapackege in local \n        -h Display the help screen \n'))
        sys.exit(1)
    elif sys.argv[1] == "-h" or sys.argv[1] == "--help":
        sys.stderr.write(_('Usage: peynir [command] [suprapackage] \n Commands: \n        -S Install suprapackage \n        -U Install local suprapackage \n        -R Remove suprapackage \n        -Rs Remove suprapackage and its dependencies \n        -Sy Update repository \n        -Su Upgrade the system \n        -Ss Search suprapackege in repository \n        -Qs Search suprapackege in local \n        -h Display the help screen \n'))
        sys.exit(1)
    elif len(sys.argv) > 2:
        if sys.argv[1] == "-S":
            argv_len = len(sys.argv)
            raw_rqst = sys.argv[2:argv_len]
            db_file_check()
            for i in raw_rqst:
                rqst = i.lower()
                if search.srch_pynr(rqst,'Peynir/Name','absolute'):
                    install(rqst,"","")
                else:
                    text.text_formatting('error: '+ rqst +' no such a suprapackage',0)
        elif sys.argv[1] == "-R":
            argv_len = len(sys.argv)
            raw_rqst = sys.argv[2:argv_len]
            db_file_check()
            for i in raw_rqst:
                rqst = i.lower()
                remove(rqst,"","")
        elif sys.argv[1] == "-Rs":
            argv_len = len(sys.argv)
            raw_rqst = sys.argv[2:argv_len]
            db_file_check()
            for i in raw_rqst:
                rqst = i.lower()
                remove(rqst,"complete","")
        elif sys.argv[1] == "-Ss":
            argv_len = len(sys.argv)
            raw_rqst = sys.argv[2:argv_len]
            db_file_check()
            for i in raw_rqst:
                rqst = i.lower()
                text.text_formatting("Results for " + rqst,0)
                search.srch_pynr(rqst,'Peynir/Name','find')
        elif sys.argv[1] == "-Qs":
            argv_len = len(sys.argv)
            raw_rqst = sys.argv[2:argv_len]
            for i in raw_rqst:
                rqst = i.lower()
                text.text_formatting("Results for " + rqst,0)
                db_file_check()
                search.local_search(rqst) 
        elif sys.argv[1] == "-U":
            argv_len = len(sys.argv)
            raw_rqst = sys.argv[2:argv_len]
            db_file_check()
            package = sys.argv[2]
            if "/" in package:
                position = package.rfind('/')
                adress = package[:position]
                package = package[position+1:]
            else:
                adress = ""
            if package[-3:] != "xml":
                package = package+".xml"
             
            if not package_check(package[:-4]):
                install(package,"local",adress)
            else:
                text.text_formatting(_(":: This suprapackage already installed in your system."), 0, 'error')

            
        else:
            text.text_formatting(_("Invalid argument: ") + sys.argv[1], 0, 'error')
            sys.exit(1)
    else:
        sys.stderr.write(_('Usage: peynir [command] [suprapackage] \n Commands: \n        -S Install suprapackage \n        -U Install local suprapackage \n        -R Remove suprapackage \n        -Rs Remove suprapackage and its dependencies \n        -Sy Update repository \n        -Su Upgrade the system \n        -Ss Search suprapackege in repository \n        -Qs Search suprapackege in local \n        -h Display the help screen \n'))
        sys.exit(1) 
             
if __name__ == "__main__":
    main()
