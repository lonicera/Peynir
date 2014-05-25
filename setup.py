#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import peynir
 
setup (
    name = "Peynir",
    version = peynir.__version__,
    description="Peynir is a suprapackage manager for Archlinux.",
    long_description="""\
Peynir is a suprapackage manager for Archlinux. It's also a framework for configuring Archlinux or other pacman based distribution. Name of Peynir has been inspired from Yaourt, a pacman wrapper for AUR. Meaning Peynir in Turkish is a cheese.
""",
author="Şenol Alan",
    author_email="",
    license='GNU',
    url="https://github.com/lonicera/Peynir",
    entry_points = {
        'console_scripts': ['peynir=peynir.peynir:main'],
    },
    include_package_data=True,
    zip_safe = True
)
