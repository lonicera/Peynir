#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os,logging, shutil, subprocess, sys
from peynir import constants as cons, text_formatting as text, file_modify, dep_conf as relationship
import urllib.request
import gettext
import xml.etree.ElementTree as etree

gettext.bindtextdomain("peynir","/language")
gettext.textdomain("peynir")
_ = gettext.gettext


def get_root(source):
    tree = etree.parse(source)
    root = tree.getroot()
    return root

def suprapackage_check(package):
    return os.path.isfile(cons.sprpckg_dir+package+".xml")

def question_mark(question, text, source, modify_type):
    position = text.find('@')
    if modify_type == "install":
        answer = input(question)
        file_modify.modify_add(cons.sprpckg_dir+source+".xml",text,"question","answer='"+answer+"' ","previous")
    else:
        answer= question
    text = text[:position] + answer + text[position+7:]
    return text

def db_file_check():
    if not os.path.isfile(cons.log_file):
        logging.basicConfig(filename=cons.log_file, format='%(asctime)s:%(levelname)s:%(message)s',  datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)
        text.text_formatting(_("Log file created"), 0, 'warning')
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

def convert(searchFor):
    dict_spcl = {'@anc': '&', '@per': '%'}
    for k in dict_spcl:
        if k in searchFor:
            position = searchFor.find('@')
            con_src = searchFor[position:position+4]
            result = searchFor.replace(k,dict_spcl[k])
        else:
            result = searchFor
        return result

def uptodate(xml_source,type_file,pacman):
    if type_file == "web":
       try:
           tree = etree.parse(urllib.request.urlopen(xml_source))
           if pacman == 1:
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
       repo_root = get_root(cons.repo)
       for step in repo_root[1]:
           for st in step:
               if stopped and st.tag == "Version":
                   return st.text
               if st.tag == "Name" and st.text == srch:
                   stopped = True
    if place == "local":
       repo_root = get_root(cons.sprpckg_dir+srch+".xml")
       for root in repo_root[0]:
           if root.tag == "Version":
               return root.text

#Bu kısım düzenlenerek üstpaketle ilgili herhangi bir bilgi de çekilebilir.
def get_description(package):
    repo_root = functions.get_root(cons.repo)
    repo_search = repo_root[1].findall('Peynir/Name')
    repo_search1 = repo_root[1].findall('Peynir/Summary')
    for comp in range(len(repo_search)):
        if repo_search[comp].text == package:
            sayi = comp
            break
    try:
        return repo_search1[(sayi*2)+1].text
    except:
        return _("There is no description for this suprapackage")

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

def sync_repo(pacman):
    text.text_formatting(_(">> Local database synchronizing with server"), 0, 'info')
    if not os.path.isfile(cons.db_dir+cons.db_file) or uptodate(cons.db_dir+cons.db_file,"local",pacman) != uptodate(cons.mirror+cons.db_file,"web",pacman):
       try:
           retrieve(cons.db_dir,cons.mirror+cons.db_file,cons.db_dir+cons.db_file)
           text.text_formatting(_("Database successfully updated."), 0, 'info')
       except:
           text.text_formatting(_("Database couldn't updated."), 0, 'error')
           sys.exit(1)
    else:
       text.text_formatting(_("Database already updated."), 0, 'info')
       #sys.exit(1)

def install(source, place, adress):
    if suprapackage_check(source) and not place == "local":
        text.text_formatting(_(">> This suprapackage already installed."), 0, 'error')
        sys.exit(1)
    
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
    text.text_formatting(">> " + source + _(" suprapackage is installing"), 0, 'info')
    relationship.conflicts(source)
    relationship.dependencies(source,"")
    root = tree.getroot()
    steps = len(root[3])
    text.text_formatting(str(steps) + _(" step(s) will executed."), 0, 'info')
    counter = 1
    for step in root[3]:
       action_type = step.attrib["type"]
       text.text_formatting("==> Step " + str(counter)+ " of " + str(steps) + " is executing", 0, 'info')
       #Alttaki kodu type 4 de de kullanıldığından fonksiyon haline gelse iyi olacak
       try:
           if action_type == "1":
               package = step.text
               if "question" in step.attrib:
                   package = question_mark(step.attrib["question"], package, source, "install")
               pac_action = step.attrib["action"]
               pacman(package,pac_action)
           elif action_type == "2":
               mdfy_type = step.attrib["modify"]
               source1 = step.attrib["source"]
               indicator = step.attrib["indicator"]
               search = step.attrib["search"]
               action = step.text
               place = step.attrib["place"]
               if "question" in step.attrib:
                   action = question_mark(step.attrib["question"], action, source, "install")
               if mdfy_type == "add":
                   mdfy.modify_add(source1,search,indicator,action,place)
               else:
                   mdfy.modify_rmv(source1,search,indicator,action,place, " ",0) 
           elif action_type == "3":
               command = step.text
               if "question" in step.attrib:
                   command = question_mark(step.attrib["question"], command, source, "install")

               if execute(command) != 0:
                   text.text_formatting(_("Error ") + step + _(", so the installation of suprapackge will be reverted ") , 0, 'error')
                   remove_action(source, "complete", step)
                   break
           counter = counter + 1
       except:
           text.text_formatting(_("Error occureed in step of ") + step, 0, 'error')
           sys.exit(1)

def remove(source, rmv_type, dep_source):
    from peynir import search
    if not suprapackage_check(source):
        text.text_formatting(_("This suprapackage is not installed."), 0,  'error')
        sys.exit(1)
    text.text_formatting(">> " + source + _(" suprapackage is removing"), 0, 'info')
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
        text.text_formatting(_("Local suprapackage couldn't found"), 0, 'error')
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
       text.text_formatting("==> Step " + str(counter)+ " of " + str(steps) + " is executing", 0, 'info')
       try:
           if action_type == "1":
               if remove_tag == "skip":
                   text.text_formatting(_("-> Skipping this step for remove action"), 1, 'info')
               else:
                   package = step.text
                   if "question" in step.attrib:
                       package = question_mark(step.attrib["answer"], package, "", "remove") 
                   pacman(package,"remove")
           elif action_type == "2":
               if remove_tag == "skip":
                   text.text_formatting(_("-> Skipping this step for remove action"), 1, 'info')
               else:
                   mdfy_type = step.attrib["modify"]
                   if mdfy_type == "add":
                       mdfy_type = "remove"
                   elif mdfy_type == "remove":
                       mdfy_type = "add"
                   source = step.attrib["source"]
                   indicator = step.attrib["indicator"]
                   search = step.attrib["search"]
                   action = convert(step.text)
                   place = step.attrib["place"]
                   if "question" in step.attrib:
                       action = question_mark(step.attrib["answer"], action, "", "remove")
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
                       if "question" in step.attrib:
                           reverse = question_mark(step.attrib["answer"], action, "", "remove")
                       execute(reverse)
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
       if fname[-3:] == "xml" and upcontrol(fname[:-4],"local") != upcontrol(fname[:-4],"repo") and search.srch_pynr(fname[:-4],'Peynir/Name','find'):
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

def package_check(package):
    instlist=[]
    antilist=[]
    for i in package.split():
        retri = "pacman -Ss " + i
        devnull = open('/dev/null', 'w')
        if not subprocess.Popen(retri, shell=True, stdout=devnull).wait() and len(i) >2:
           instlist.append(i)
        else:
            antilist.append(i)
    return instlist, antilist
    
def pacman(package,action):
    text.text_formatting("-> " + action.strip("e") + "ing " + package + " via pacman", 1, 'info') #remove, removing eksikliğini düzelt
    if ' '.join(package_check(package)[1]):
          text.text_formatting(_("-> Following package(s) not found in pacman repository, so skipped " + ' '.join(package_check(package)[1])), 1, 'error')
    if action == "install":
       retri = "pacman -S --noconfirm "+ ' '.join(package_check(package)[0])
    elif action == "remove":
       retri = "pacman -Rs --noconfirm "+ ' '.join(package_check(package)[0])
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
