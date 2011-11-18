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
#       Version:0.2-1

import os, sys, shutil
import xml.etree.ElementTree as etree
import urllib.request
import difflib
from tempfile import NamedTemporaryFile

repo = '/var/cache/peynir/peynir.xml'
db_dir = '/var/cache/peynir/'
sprpckg_dir = '/var/cache/peynir/packages/'
mirror = 'http://lonicera.byethost7.com/'
log_dir = '/var/log/peynir/'
db_file = 'peynir.xml'

def text_formatting(source,level):
    tab_space = "   "
    for i in range(level):
        source = tab_space + source
    print(source)
    
def db_file_check():
    if not os.path.isfile(db_dir+db_file):
        try:
            print("Database could'nt found. Getting from server")
            retrieve(db_dir,mirror+db_file,db_dir+db_file)
            print("Database successfully updated.")
        except:
            print("Database couldn't updated.")
            sys.exit(1)

def similarity(first,second):
    seq=difflib.SequenceMatcher(a=first.lower(), b=second.lower())
    return round(seq.ratio(),1)

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

#bu ve altındaki fonksiyon log oluşturmak oluşturulan girdileri düzenlemek için
def indent(elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
       if not elem.text or not elem.text.strip():
           elem.text = i + "  "
       if not elem.tail or not elem.tail.strip():
           elem.tail = i
       for elem in elem:
           indent(elem, level+1)
       if not elem.tail or not elem.tail.strip():
           elem.tail = i
    else:
       if level and (not elem.tail or not elem.tail.strip()):
           elem.tail = i

def printxml(xml):
    import xml.etree.ElementTree as et
    elem = et.fromstring(xml)
    indent(elem)
    return et.tostring(elem)

#Log oluşturmak için ilk deneme
def log_create(package,step_no,status):
    log_check = os.path.isfile(log_dir+package+".xml")
    if log_check:
       with open(log_dir+package+".xml") as fin, NamedTemporaryFile(dir='.', delete=False) as fout:
           for line in fin:
               last_step_no = step_no -1
               last_entry = line.find("no='"+str(last_step_no)+"'")
               print(last_entry)
               if last_entry > 0:
                   line = line + "\n" + "<steps no='"+str(step_no)+"' status='"+status+"'> </step>"
               elif step_no == 1 and line.find("<steps>") >0:
                   line = line + "\n" + "<step no='1' status='"+status+"'> </step>"
               fout.write(line.encode('utf8'))
           os.rename(fout.name, log_dir+package+".xml")
       duz = printxml(open(log_dir+package+".xml").read())
       open(log_dir+package+".xml", "w").write(duz)
    else:
       file = open(log_dir+package+".xml", 'w')
       std_content = printxml("<log><steps>\n  </steps></log>")
       file.write("<?xml version='1.0' encoding='utf-8'?>\n")
       file.write(std_content)
       file.close()

#Bu fonksiyon kodları kısaltmak üzere tasarladığım bir deneme; bir xml dosyasının belirli bölgesini seçmek için kullanılacak
def uptodate(xml_source,type_file):
    if type_file == "web":
       try:
           tree = etree.parse(urllib.request.urlopen(xml_source))
       except:
           print("Database couldn't updated.")
           sys.exit(1)
    else:
        try:
            tree = etree.parse(xml_source)
        except:
            print("There is a problem with xml file")
            sys.exit(1)
            
    root = tree.getroot()
    find_node = root[0].findall('Last_update')
    up_date = find_node[0].text
    return up_date

def local_dependency(source,package):
    dep_list = []
    source_tree = etree.parse(sprpckg_dir+source+".xml")
    source_root = source_tree.getroot()
    local_dep = source_root[2].attrib['local']
    for i in local_dep.strip().split(" "):
        if i != package and len(local_dep.strip().split(" ")) > 0:
            dep_list.append(i)
        return dep_list
        
def upcontrol(srch,place):
    if place == "repo":
       repo_tree = etree.parse(repo) # Bu kısmı bir fonksiyonla kısalt
       repo_root = repo_tree.getroot()
       result = "false"
       for step in repo_root[1]:
           #print(step.tag)
           stopped = "false"
           for st in step:
               if stopped == "true" and st.tag == "Version":
                   return st.text
               if st.tag == "Name" and st.text == srch:
                   stopped = "true"
    if place == "local":
       repo_tree = etree.parse(sprpckg_dir+srch+".xml") # Bu kısmı bir fonksiyonla kısalt
       repo_root = repo_tree.getroot()
       for root in repo_root[0]:
           if root.tag == "Version":
               return root.text

#Bu kısım düzenlenerek paketle ilgili herhangi bir bilgi de çekilebilir.
def get_description(package):
    repo_tree = etree.parse(repo)
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
        return "There is no description for this package"
			
def srch_pynr(srch,node,action):
    db_file_check()
    repo_tree = etree.parse(repo)
    repo_root = repo_tree.getroot()
    repo_search = repo_root[1].findall(node)
    result = "false"
    for comp in range(len(repo_search)):
       if action == "find":
           if similarity(str(repo_search[comp].text),str(srch)) > 0.45:
               print("Found " + repo_search[comp].text + " similarity is " + str(similarity(str(repo_search[comp].text),str(srch))*100)+"%")
       if repo_search[comp].text == srch and action == "absolute":
           result = "true"
           return result
           break

def retrieve(place,url,file):
    status = "false"
    os.chdir(place)
    try:
        req=urllib.request.Request(url)
        req.add_header("User-Agent","Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US) AppleWebKit/525.13 (KHTML,     like Gecko) Chrome/0.2.149.29 Safari/525.13")
        usock = urllib.request.urlopen(req)
        data = usock.read()
        usock.close() 
    except:
        print(file + " could not retrivied from mirror")
        sys.exit(1)

    fp = open(file, 'wb')
    fp.write(data)
    fp.close()
    if fp.close():
       status = "true"
    else:
       status = "false"
    return status

def sync_repo():
    if not os.path.isfile(db_dir+db_file) or uptodate(db_dir+db_file,"local") != uptodate(mirror+db_file,"web"):
       try:
           retrieve(db_dir,mirror+db_file,db_dir+db_file)
           print("Database successfully updated.")
       except:
           print("Database couldn't updated.")
           sys.exit(1)
    else:
       print("Database already updated.")
       sys.exit(1)

def package_check(package):
    check_fail = "true"
    package_check = os.path.isfile(sprpckg_dir+package+".xml")
    if package_check:
       check_fail = "false"
       #sys.exit("\nThis suprapackage already installed.\n")
    return check_fail

def conflict(source):
    #retrieve(sprpckg_dir,mirror+source+".xml",sprpckg_dir+source+".xml")
    tree = etree.parse(sprpckg_dir+source+".xml")
    root = tree.getroot()
    #Çakışmalar çözülüyor
    text_formatting("Check for conflicts...",0)
    conflictcount = len(root[1]) #Çakışma buldu ama sistemde yoksa çakışma var demesine gerek yok
    conflicts = root[1]
    if conflictcount > 0:
       text_formatting(str(conflictcount) + " conflicts have found.",1)
       text_formatting("Following suprapackage(s) will remove. ",0)
       for conf in root[1]:
           try:
               text_formatting(conf.text + " ==> " + get_description(conf.text),1)
           except:
               text_formatting(conf.text + " ==> There is no description for this package",1)
       answer = input("Are you want to remove these packages (Y/N): ")
       if answer == "Y" or answer == "y":
           for conf in root[1]:
               package = conf.text
               if package_check(package) == "false":
                   remove(package,"")
               else:
                   print(package + " is not installed")
       else:
           sys.exit("Suprapackage coulnd't installed.")
    else:
       text_formatting("There is a no conflict",1)

def dependencies(source,action):
    text_formatting("Resolving dependencies..",0)
    #retrieve(sprpckg_dir,mirror+source+".xml",sprpckg_dir+source+".xml")
    tree = etree.parse(sprpckg_dir+source+".xml")
    root = tree.getroot()
    #Bağımlılıklar çözülüyor
    dependcount = len(root[2])
    dependencies = root[2]
    if dependcount > 0:
       text_formatting(str(dependcount) + " dependencies have found.",1)
       #Tamamen kaldırma işlemi için ....
       if action == "remove":
           text_formatting("Following suprapackage(s) will remove. ",1 )
           for dep in root[2]:
               try:
                   text_formatting(dep.text + " ==> " + get_description(dep.text),1)
               except:
                   text_formatting(dep.text + " ==> There is no description for this package",1)
           answer = input("Are you want to remove these packages (Y/N): ")
           if answer == "Y" or answer == "y":
               for dep in root[2]:
                   package = dep.text
                   if len(local_dependency(package,source)) == 0:
                       text_formatting("There is no dependencies in your system",0)
                       #print(package + " suprapackage is removing")
                       remove(package,"ddd")
                   else:
                        text_formatting("Following suprapackages requies " + package + " suprapackage",0)
                        for i in local_dependency(package,source):
                            text_formatting(i + " ==> " + get_description(i),1)
           else:
               sys.exit("Dependencies coulnd't removed so remove process couldn't continue.")
       else:
           print("Following suprapackage(s) will install. " )
           for dep in root[2]:
               try:
                   text_formatting(dep.text + " ==> " + get_description(dep.text),1)
               except:
                   text_formatting(dep.text + " ==> There is no description for this package",1)
           answer = input("Are you want to install these packages (Y/N): ")
           if answer == "Y" or answer == "y":
               for dep in root[2]:
                   package = dep.text
                   if package_check(package) == "true":
                       print(package + " suprapackage is installing")
                       install(package,"") #İç içe bağımlılık sorunu olacak o neden ilave bir fonksiyon paramatresi ise bu soruyu bir kez sordurulabilir
                   else:
                       print(package + " is already installed")
                   modify_add(sprpckg_dir+package+".xml","<Dependencies","'>"," " + source,"previous") 
           else:
               os.remove(sprpckg_dir+source+".xml")
               sys.exit("Dependencies coulnd't installed so install process couldn't continue.")
    else:
       text_formatting("There is a no dependencies",1)

def install(source, place):
    if package_check(source) == "false":
       sys.exit("This suprapackage already installed.")
    
    if place == "local":
       tree = etree.parse(os.getcwd()+"/"+source)
       shutil.copyfile(source, sprpckg_dir+"/"+source)
       position = source.find('.')
       source = source[:position]
    else:
       retrieve(sprpckg_dir,mirror+source+".xml",sprpckg_dir+source+".xml")
       tree = etree.parse(sprpckg_dir+source+".xml")
    conflict(source)
    dependencies(source,"")
    root = tree.getroot()
    steps = len(root[3])
    print(str(steps) + " step(s) will executed.")
    print(source + " suprapackage is installing")
    counter = 1
    for step in root[3]:
       action_type = step.attrib["type"]
       print("==> Step " + str(counter)+ " of " + str(steps) + " is executing")
       #Alttaki kodu type 4 de de kullanıldığından fonksiyon haline gelse iyi olacak
       #Hata kontrolü kısmı başlangıcı
       try:
           if action_type == "1":
               pac_action = step.attrib["action"]
               package = step.text
               pacman(package,pac_action)
           elif action_type == "2":
               mdfy_type = step[0].attrib["type"]
               source = step[0].attrib["source"]
               indicator = step[0].attrib["indicator"]
               search = step[0].attrib["search"]
               action = convert(step[0].text)
               place = step[0].attrib["place"]
               modify(source,search,indicator,action,place,mdfy_type)
           elif action_type == "3":
               command = step.text
               execute(command)
           elif action_type == "4":
               question = step[0].text
               text_formatting("-> " + str(len(step)-1) + " substep(s) will execute for this step",1)
               answer = input(question)
               modify_add(sprpckg_dir+source+".xml",question,"step","answer='"+answer+"' ","previous")
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
                           modify(source,search,indicator,ans_action,place,mdfy_type)
                       elif int(i.attrib["step"]) == 3:
                           command = i.text
                           if position > 0:
                               command = ans_action[:position] + answer + ans_action[position+7:]
                           execute(command)
           counter = counter + 1
       except:
           print("Error occureed in step of " + step)
           sys.exit(1)

def remove(source, rmv_type):
    if package_check(source) == "true":
       sys.exit("This suprapackage is not installed.")
    if rmv_type == "complete":
       dependencies(source,"remove")
    print(source + " suprapackage is removing")
    try:
       tree = etree.parse(sprpckg_dir+source+".xml")
       os.remove(sprpckg_dir+source+".xml")
    except:
       print("Local package couldn't found")
       sys.exit(1)
    root = tree.getroot()
    steps = len(root[3])
    counter = 1
    for step in reversed(root[3]):
       action_type = step.attrib["type"]
       try:
           remove_tag = step.attrib["remove_tag"]
       except KeyError:
           remove_tag = " "
       print("==> Step " + str(counter)+ " of " + str(steps) + " is executing")
       try:
           if action_type == "1":
               if remove_tag == "skip":
                   text_formatting("-> Skipping this step for remove action",1)
               else:
                   package = step.text
                   pacman(package,"remove")
           elif action_type == "2":
               if remove_tag == "skip":
                   text_formatting("-> Skipping this step for remove action",1)
               else:
                   mdfy_type = step[0].attrib["type"]
                   if mdfy_type == "add":
                       mdfy_type = "remove"
                   elif mdfy_type == "remove":
                       mdfy_type == "add"
                   source = step[0].attrib["source"]
                   indicator = step[0].attrib["indicator"]
                   search = step[0].attrib["search"]
                   action = convert(step[0].text)
                   place = step[0].attrib["place"]
                   modify(source,search,indicator,action,place,mdfy_type)
           elif action_type == "3" and remove_tag != "skip":
               if remove_tag == "skip":
                   text_formatting("-> Skipping this step for remove action",1)
               else:
                   try:
                       reverse = step.attrib["reverse"]
                       execute(reverse)
                   except:
                       text_formatting("There is no defined action for this step",1)
           elif action_type == "4": # Buraya reverse özelliklerini ekle
               try:
                   answer= step[0].attrib["answer"]
                   text_formatting("-> " + str(len(step)-1) + " substep(s) will execute for this step",1)
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
                                   text_formatting("-> Skipping this step for remove action",1)
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
                                   text_formatting("-> Skipping this step for remove action",1)
                               else:
                                   mdfy_type = i.attrib["type"]
                                   if mdfy_type == "add":
                                       mdfy_type = "remove"
                                   elif mdfy_type == "remove":
                                       mdfy_type == "add"
                                   source = i.attrib["source"]
                                   indicator = i.attrib["indicator"]
                                   search = i.attrib["search"]
                                   ans_action = i.text
                                   if position > 0:
                                       ans_action = ans_action[:position] + answer + ans_action[position+7:]
                                   place = i.attrib["place"]
                                   modify(source,search,indicator,ans_action,place,mdfy_type)
                           elif int(i.attrib["step"]) == 3:
                               if remove_tag == "skip":
                                   text_formatting("-> Skipping this step for remove action",1)
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
                   text_formatting("There is no defined action for this step",1)
           counter = counter + 1
       except:
           print("Error")
           sys.exit(1)
     
def modify(tar_file,srch,indicator,action,place,mdfy_type):
    if mdfy_type == "add":
       modify_add(tar_file,srch,indicator,action,place)
    elif mdfy_type == "remove":
       modify_rmv(tar_file,srch,indicator,action,place," ")

def modify_add(tar_file,srch,indicator,action,place):
    text_formatting("-> adding" + action + " to " + tar_file,1)
    get_owner = os.popen("ls -l "+tar_file+"|awk '{print $3}'")
    old_owner = get_owner.read()
    get_prop = os.popen("stat -c %a "+tar_file)
    old_prop = get_prop.read()
    if place == "last":
       open(tar_file,"a").write("\n" + action)
    with open(tar_file) as fin, NamedTemporaryFile(dir='.', delete=False) as fout: #Buraya try ile bir kod ekleyerek dosya bulunamadığındaki hatayı engelle
       counter = 0
       for line in fin:
           if place == "first" and counter == 0:
               line = action + "\n" + line
           elif srch in line:
               position = line.find(indicator)
               if place == "previous":
                   line = line[:position] + action + line[position:]
               elif place == "next":
                   line = line[:position+1] + action + line[position+1:]
               elif place == "after":
                   line = line + action + "\n"
               elif place == "before":
                   line = action + "\n" + line
           fout.write(line.encode('utf8'))
           counter = counter + 1
       shutil.move(fout.name, tar_file)
       #os.rename(fout.name, tar_file)
       #Alttaki satırları fonksiyona dönüştürver gari
       os.system("chmod " + old_prop.strip() + " " + tar_file)
       os.system("chown "+  old_owner.strip() + " " + tar_file)

def modify_rmv(tar_file,srch,indicator,action,place,rplc):
    text_formatting("-> removing" + action + " from " + tar_file,1)
    get_owner = os.popen("ls -l "+tar_file+"|awk '{print $3}'")
    old_owner = get_owner.read()
    get_prop = os.popen("stat -c %a "+tar_file)
    old_prop = get_prop.read()
    with open(tar_file) as fin, NamedTemporaryFile(dir='.', delete=False) as fout:
       counter = 0
       for line in fin:
           if place == "first" and counter == 0:
               line = line.replace(action,rplc).strip()
           elif srch in line:
               position = line.find(indicator)
               if place == "previous":
                   line = line[:position].replace(action,rplc).strip() + line[position:]
               elif place == "next":
                   line = line[:position] + line[position:].replace(action,rplc).strip()
           if place == "after" or place == "before":
               if action in line:
                   line = ""
           fout.write(line.encode('utf8'))
           counter = counter + 1
       os.rename(fout.name, tar_file)
       os.system("chmod " + old_prop.strip() + " " + tar_file)
       os.system("chown "+  old_owner.strip() + " " + tar_file)

def upgrade():
    dirlist=os.listdir(sprpckg_dir)
    counter = 0
    up_list = []
    for fname in dirlist:
       if upcontrol(fname[:-4],"local") != upcontrol(fname[:-4],"repo"):
           up_list.append(fname[:-4]);
           print(fname[:-4]+" Guncelle")
           counter = counter + 1
    if len(up_list) == 0:
        text_formatting("There is nothing to do",0)
    else:
        text_formatting("Following suprapackage(s) will upgrade",0)
        for up in up_list[0:]:
            print(up)
            remove(up,"")
            install(up,"")

def pacman(package,action):
    text_formatting("-> " + action + "ing " + package + " via pacman",1) #remove, removing eksikliğini düzelt
    import subprocess
    if action == "install":
       retri = "pacman -S --noconfirm "+ package
    elif action == "remove":
       retri = "pacman -R --noconfirm "+ package
    subprocess.Popen(retri, shell=True).wait()

def execute(command):
    text_formatting("-> executing " + command + " in the shell",1)
    import subprocess
    retri = command
    subprocess.Popen(retri, shell=True).wait()

### Ana bölüm
def main():
    #log_create("gnome",1,"oldu")
    if not os.geteuid()==0:
       sys.exit("You must be root to run this application, please use sudo and try again.")
    
    if len(sys.argv) == 1:
        sys.stderr.write('Usage: peynir [command] [suprapackage] \n Commands: \n        -S Install suprapackage \n        -U Install local suprapackage \n        -R Remove suprapackage \n        -Sy Update repository \n        -Su Upgrade the system \n        -Ss Search suprapackege in repository \n        -h Display the help screen \n')
        sys.exit(1)
    elif sys.argv[1] == "-Sy":
        sync_repo()
    elif sys.argv[1] == "-Su":
        upgrade()
    elif len(sys.argv) == 1:
        sys.stderr.write('Usage: peynir [command] [suprapackage] \n Commands: \n        -S Install suprapackage \n        -U Install local suprapackage \n        -R Remove suprapackage \n        -Sy Update repository \n        -Su Upgrade the system \n        -Ss Search suprapackege in repository \n        -h Display the help screen \n')
        sys.exit(1)
    elif sys.argv[1] == "-h" or sys.argv[1] == "--help":
       sys.stderr.write('Usage: peynir [command] [suprapackage] \n Commands: \n        -S Install suprapackage \n        -U Install local suprapackage \n        -R Remove suprapackage \n        -Sy Update repository \n        -Su Upgrade the system \n        -Ss Search suprapackege in repository \n        -h Display the help screen \n')
       sys.exit(1)
    elif len(sys.argv) > 2:
        if sys.argv[1] == "-S":
            argv_len = len(sys.argv)
            raw_rqst = sys.argv[2:argv_len]
            for i in raw_rqst:
                rqst = i.lower()
                #rqst = sys.argv[2].lower().strip() #Burada belki gelen kodun heriki tarafındaki boşluklar atılabilir
                if srch_pynr(rqst,'Peynir/Name','absolute') == "true":
                    db_file_check()
                    install(rqst,"")
                else:
                    print('error: '+ rqst +' no such a suprapackage')
        elif sys.argv[1] == "-R":
            argv_len = len(sys.argv)
            raw_rqst = sys.argv[2:argv_len]
            for i in raw_rqst:
                rqst = i.lower()
                #rqst = sys.argv[2].lower().strip() #Burada belki gelen kodun heriki tarafındaki boşluklar atılabilir
                db_file_check()
                remove(rqst,"")
        elif sys.argv[1] == "-Rs":
            argv_len = len(sys.argv)
            raw_rqst = sys.argv[2:argv_len]
            for i in raw_rqst:
                rqst = i.lower()
                #rqst = sys.argv[2].lower().strip() #Burada belki gelen kodun heriki tarafındaki boşluklar atılabilir
                db_file_check()
                remove(rqst,"complete")
        elif sys.argv[1] == "-Ss":
            argv_len = len(sys.argv)
            raw_rqst = sys.argv[2:argv_len]
            for i in raw_rqst:
                rqst = i.lower()
                print("Results for " + rqst)
                db_file_check()
                srch_pynr(rqst,'Peynir/Name','find')
        elif sys.argv[1] == "-U":
            argv_len = len(sys.argv)
            raw_rqst = sys.argv[2:argv_len]
            print(sys.argv[2])
            db_file_check()
            package = sys.argv[2]
            if package[-3:] != "xml":
                package = package+".xml"
            if package_check(package[:-4]) == "true":
                install(package,"local")
            else:
                print("This suprapackage already installed in your system.")
        else:
            print("Invalid argument: " + sys.argv[1])
            sys.exit(1)
    else:
        sys.stderr.write('Usage: peynir [command] [suprapackage] \n Commands: \n        -S Install suprapackage \n        -U Install local suprapackage \n        -R Remove suprapackage \n        -Sy Update repository \n        -Su Upgrade the system \n        -Ss Search suprapackege in repository \n        -h Display the help screen \n')
        sys.exit(1) 
			 
if __name__ == "__main__":
    main()
