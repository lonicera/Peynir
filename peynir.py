#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#       peynir.py - Suprapackage Manager for Archlinux. It's also a framework for configuring Archlinux or other distribution pacman based. 
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

import os, sys
import xml.etree.ElementTree as etree 
import urllib.request
import difflib
from tempfile import NamedTemporaryFile

repo = '/var/cache/peynir/peynir.xml'
db_dir = '/var/cache/peynir/'
sprpckg_dir = '/var/cache/peynir/packages/'
mirror = 'http://www.alansistem.com/peynir/'
log_dir = '/var/log/peynir/'
db_file = 'peynir.xml'

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
		tree = etree.parse(urllib.request.urlopen(xml_source))
	else:
		tree = etree.parse(xml_source)
	root = tree.getroot()
	find_node = root[0].findall('Last_update')
	up_date = find_node[0].text
	return up_date

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


def srch_pynr(srch,node,action):
	repo_tree = etree.parse(repo)
	repo_root = repo_tree.getroot()
	repo_search = repo_root[1].findall(node)
	result = "false"
	for comp in range(len(repo_search)):
		if action == "find":
			if similarity(str(repo_search[comp].text),str(srch)) > 0.45:
				return ("Found " + repo_search[comp].text + " similarity is " + str(similarity(str(repo_search[comp].text),str(srch))*100)+"%")
		if repo_search[comp].text == srch and action == "absolute":
			result = "true"
			return result
			break 
		
def retrieve(place,url,file):
	status = "false"
	os.chdir(place)
	try:
		usock = urllib.request.urlopen(url)
		data = usock.read()
		usock.close()
	except:
		print(file + " could not retrivied from mirror")
		
	fp = open(file, 'wb')
	fp.write(data)
	fp.close()
	if fp.close():
		status = "true"
	else:
		status = "false"
	return status
	
def sync_repo():
	#print(uptodate(db_dir+db_file,"local"))
	#print(uptodate(mirror+db_file,"web"))
	if not os.path.isfile(db_dir+db_file) or uptodate(db_dir+db_file,"local") != uptodate(mirror+db_file,"web"):
		try:
			retrieve(db_dir,mirror+db_file,db_dir+db_file)
			print("Database successfully updated.")
		except:
			print("Database couldn't updated.")
	else:
		print("Database already updated.")
		
def package_check(package):
	check_fail = "true"
	package_check = os.path.isfile(sprpckg_dir+package+".xml")
	if package_check:
		check_fail = "false"
		#sys.exit("\nThis suprapackage already installed.\n")
	return check_fail

def conflict(source):
	retrieve(sprpckg_dir,mirror+source+".xml",sprpckg_dir+source+".xml")
	tree = etree.parse(sprpckg_dir+source+".xml")
	root = tree.getroot()
	#Çakışmalar çözülüyor
	print("Check for conflicts...")
	conflictcount = len(root[1])
	conflicts = root[1]
	if conflictcount > 0:
		print(str(conflictcount) + " conflicts have found.")
		print("Following suprapackage(s) will remove. " )
		for conf in root[1]:
			print(conf.text)
		answer = input("Are you want to remove these packages (Y/N): ")
		if answer == "Y" or answer == "y":
			for conf in root[1]:
				package = conf.text
				if package_check(package) == "false":
					remove(package)
				else:
					print(package + " is not installed")
		else:
			sys.exit("\nSuprapackage coulnd't installed.\n")
	else:
		print("There is a no conflict")

def dependencies(source):
	print("Resolving dependencies..")
	retrieve(sprpckg_dir,mirror+source+".xml",sprpckg_dir+source+".xml")
	tree = etree.parse(sprpckg_dir+source+".xml")
	root = tree.getroot()
	#Bağımlılıklar çözülüyor
	dependcount = len(root[2])
	dependencies = root[2]
	if dependcount > 0:
		print(str(dependcount) + " dependencies have found.")
		print("Following suprapackage(s) will install. " )
		for dep in root[2]:
			print(dep.text)
		answer = input("Are you want to install these packages (Y/N): ")
		if answer == "Y" or answer == "y":
			for dep in root[2]:
				package = dep.text
				if package_check(package) == "true":
					install(package) #İç içe bağımlılık sorunu olacak o neden ilave bir fonksiyon paramatresi ise bu soruyu bir kez sordurulabilir
				else:
					print(package + " is already installed")
	else:
		print("There is a no dependencies")

def install(source):
	if package_check(source) == "false":
		sys.exit("\nThis suprapackage already installed.\n")
	print(source + " suprapackage is installing")
	conflict(source)
	dependencies(source)
	retrieve(sprpckg_dir,mirror+source+".xml",sprpckg_dir+source+".xml")
	tree = etree.parse(sprpckg_dir+source+".xml")
	root = tree.getroot()
	steps = len(root[3])
	print(str(steps) + " step(s) will executed.")
	counter = 1
	for step in root[3]:
		action_type = step.attrib["type"]
		print(str(counter)+ " of " + str(steps) + " is executing")
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
				answer = input(question)
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

def remove(source):
	if package_check(source) == "true":
		sys.exit("\nThis suprapackage is not installed.\n")
	print(source + " suprapackage is removing")
	tree = etree.parse(sprpckg_dir+source+".xml")
	os.remove(sprpckg_dir+source+".xml")
	root = tree.getroot()
	steps = len(root[3])
	counter = 1
	for step in root[3]:
		action_type = step.attrib["type"]
		print(str(counter)+ " of " + str(steps) + " is executing")
		if action_type == "1":
			package = step.text
			rmv(package)
		elif action_type == "2":
			mdfy_type = step[0].attrib["type"]
			source = step[0].attrib["source"]
			indicator = step[0].attrib["indicator"]
			search = step[0].attrib["search"]
			action = convert(step[0].text)
			place = step[0].attrib["place"]
			modify(source,search,indicator,action,place,"remove")
		counter = counter + 1
				
def modify(tar_file,srch,indicator,action,place,mdfy_type):
	if mdfy_type == "add":
		modify_add(tar_file,srch,indicator,action,place)
	elif mdfy_type == "remove":
		modify_rmv(tar_file,srch,indicator,action,place," ")
		
def modify_add(tar_file,srch,indicator,action,place):
	get_owner = os.popen("ls -l "+tar_file+"|awk '{print $3}'")
	old_owner = get_owner.read()
	get_prop = os.popen("stat -c %a "+tar_file)
	old_prop = get_prop.read()
	if place == "last":
		open(tar_file,"a").write("\n" + action) 
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
					line = line[:position+1] + action + line[position+1:]
				elif place == "after":
					line = line + action + "\n"
				elif place == "before":
					line = action + "\n" + line
			fout.write(line.encode('utf8'))
			counter = counter + 1
		os.rename(fout.name, tar_file)
		#Alttaki satırları fonksiyona dönüştürver gari
		os.system("chmod " + old_prop.strip() + " " + tar_file)
		os.system("chown "+  old_owner.strip() + " " + tar_file)

def modify_rmv(tar_file,srch,indicator,action,place,rplc):
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
				elif place == "after" or place == "before":
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
			print(fname[:-4]+" Güncelle")
			counter = counter + 1
	for up in up_list[0:]:
		remove(up)
		install(up)

def pacman(package,action):
	import subprocess
	if action == "install":
		retri = "pacman -S --noconfirm "+ package
	elif action == "remove":
		retri = "pacman -R --noconfirm "+ package
	subprocess.Popen(retri, shell=True).wait()
	
def execute(command):
	import subprocess
	retri = command
	subprocess.Popen(retri, shell=True).wait()
	
	
def rmv(package):
	import subprocess
	retri = "pacman -R --noconfirm "+ package
	subprocess.Popen(retri, shell=True)		 		

### Ana bölüm
def main():
	#log_create("gnome",1,"oldu")
	if not os.geteuid()==0:
		sys.exit("\nYou must be root to run this application, please use sudo and try again.\n") 
	
	if len(sys.argv) == 1:
		sys.stderr.write('Usage: peynir [command] [options] \n')
		sys.exit(1)
	elif sys.argv[1] == "-Sy" and len(sys.argv) == 2 :
		sync_repo()
	elif sys.argv[1] == "-Su" and len(sys.argv) == 2 :
		upgrade()
	elif len(sys.argv) == 2 :
		sys.stderr.write('Usage: peynir [command] [options] \n')
		sys.exit(1)
	
    
	if sys.argv[1] == "-S":
		argv_len = len(sys.argv)
		raw_rqst = sys.argv[2:argv_len]
		#print(raw_rqst) #Burası daha sonra kaldırılacak.
		for i in raw_rqst:
			rqst = i.lower()
			#rqst = sys.argv[2].lower().strip() #Burada belki gelen kodun heriki tarafındaki boşluklar atılabilir 
			if srch_pynr(rqst,'Peynir/Name','absolute') == "true":
				install(rqst)
			else:
				print('error: '+ rqst +' no such a suprapackage')
	elif sys.argv[1] == "-R":
		argv_len = len(sys.argv)
		raw_rqst = sys.argv[2:argv_len]
		#print(raw_rqst)
		for i in raw_rqst:
			rqst = i.lower()
			#rqst = sys.argv[2].lower().strip() #Burada belki gelen kodun heriki tarafındaki boşluklar atılabilir 
			remove(rqst)
	elif sys.argv[1] == "-Ss":
		argv_len = len(sys.argv)
		raw_rqst = sys.argv[2:argv_len]
		#print(raw_rqst)
		for i in raw_rqst:
			rqst = i.lower()
			print("Results for " + rqst)
			print(srch_pynr(rqst,'Peynir/Name','find'))
			
					
if __name__ == "__main__":
    main()
		
