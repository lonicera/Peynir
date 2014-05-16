#!/usr/bin/env python3
# -*- coding: utf-8 -*
import xml.etree.ElementTree as etree

def geting_root(source):
    tree = etree.parse(source)
    root = tree.getroot()
    return root
