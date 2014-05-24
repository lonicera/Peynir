#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import text_formatting as text
import search
import functions
import constants as cons
import argparse, sys
import gettext, os
import peynir
gettext.bindtextdomain("peynir","/language")
gettext.textdomain("peynir")
_ = gettext.gettext

def main():
    if not os.geteuid()==0:
        sys.exit(_("You must be root to run this application, please use sudo and try again."))
    functions.db_file_check()
    parser = argparse.ArgumentParser(description='''Suprapackage Manager for Archlinux. It's also a framework for configuring Archlinux or other pacman based distribution.''', prog='peynir')
    parser.add_argument("-d", "--debug", help="Log everyhing (including info, warning and errors)", action="store_true")
    parser.add_argument("-S", nargs='*', metavar='Suprapackage', help="Install suprapackage")
    parser.add_argument("-U", metavar='Suprapackage', help="Install local suprapackage")
    parser.add_argument("-R", nargs='*', metavar='Suprapackage', help="Remove suprapackage")
    parser.add_argument("-Rs", nargs='*', metavar='Suprapackage', help="Remove suprapackage and its dependencies")
    parser.add_argument("-Sy", help="Update repository", action="store_true")
    parser.add_argument("-Syy", help="Update peynir and pacman repository", action="store_true")   
    parser.add_argument("-Su", help="Upgrade the system", action="store_true")
    parser.add_argument("-Syu", help="Upgrade the system", action="store_true")  
    parser.add_argument("-Ss", help="Search suprapackege in repository")  
    parser.add_argument("-Qs", help="Search suprapackege in local")
    parser.add_argument("-O", help="Repair system or package (not fully implemented)")
    parser.add_argument("--noconfirm", help="Do not prompt for any confirmation", action="store_true")
    parser.add_argument("--cachedir", help="[path] Overrides the default location of the suprapackage cache directory.")
    parser.add_argument("--silence", help="No output", action="store_true")

    args = parser.parse_args()
    
    if len(sys.argv)==1:
        parser.print_help()
        sys.exit(1)
    if args.noconfirm:
        cons.confm = True
    if args.debug:
        cons.debug = True
    if args.silence:
        cons.silence = True
    if args.cachedir:
        cons.cachedir = args.cachedir.strip()
        if not cons.cachedir[len(cons.cachedir)-1:len(cons.cachedir)] == "/":
            cons.cachedir = cons.cachedir+"/"
            print(cons.cachedir)
    
    if args.Sy:
        functions.sync_repo(0)
    if args.Syy:
        functions.sync_repo(1)
    if args.Su:
        functions.upgrade()
    if args.Syu:
        functions.sync_repo(1)
        functions.upgrade()
    if args.S:
        functions.db_file_check() #Burada ve diğer gereksiz kullanımları temizle
        for i in args.S:
            rqst = i.lower()
            if search.srch_pynr(rqst,'Peynir/Name','absolute'):
                functions.install(rqst,"","")
            else:
                text.text_formatting('error: '+ rqst +' no such a suprapackage',0, "warning")
    
    if args.R:
       functions.db_file_check() 
       for i in args.R:
           rqst = i.lower()
           functions.remove(rqst,"","")
    if args.Rs:
       functions.db_file_check() 
       for i in args.Rs:
           rqst = i.lower()
           functions.remove(rqst,"complete","")
    if args.Ss:
       functions.db_file_check() 
       for i in args.Ss.split():
           rqst = i.lower()
           text.text_formatting("Results for " + rqst, 0, 'info')
           search.srch_pynr(rqst,'Peynir/Name','find')
    if args.Qs:
       functions.db_file_check() 
       for i in args.Qs.split():
           rqst = i.lower()
           text.text_formatting("Results for " + rqst, 0, 'info' )
           search.local_search(rqst)
    if args.U:
       functions.db_file_check() 
       if "/" in args.U:
           position = args.U.rfind('/')
           adress = args.U[:position]
           package = args.U[position+1:]
       else:
           adress = ""
       if package[-3:] != "xml" and "." in package:
           text.text_formatting(_("Invalid package format"), 0, "error")
           sys.exit(1)
       elif not "." in package: 
           package = package+".xml"
             
       if not functions.suprapackage_check(package[:-4]):
           functions.install(package,"local",adress)
       else:
           text.text_formatting(_(">> This suprapackage already installed in your system."), 0, 'error')
