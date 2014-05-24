#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from peynir import constants as cons 
import logging
def text_formatting(source,level, log_level):
    logging.basicConfig(filename=cons.log_file, format='%(asctime)s:%(levelname)s:%(message)s',  datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)
    tab_space = "   "
    for i in range(level):
        source = tab_space + source
    if log_level == "info" and cons.debug:
        logging.info(source)   
    elif log_level == "warning":
        logging.warning(source)
    elif log_level == "debug":
        logging.debug(source)
    elif log_level == "error":
        logging.error(source)    
    if not cons.silence:
        print(source)
