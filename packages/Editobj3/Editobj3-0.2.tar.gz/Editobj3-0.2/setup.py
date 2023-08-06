#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Editobj3
# Copyright (C) 2007-2014 Jean-Baptiste LAMY

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import os, os.path, sys, glob

HERE = os.path.relpath(os.path.dirname(os.path.abspath(__file__)))

if len(sys.argv) <= 1: sys.argv.append("install")


import setuptools

#data_files = [os.path.join("js", file) for file in os.listdir("js") if (file != "CVS") and (file != ".hg") and (file != ".svn") and (file != ".arch-ids")] \
#           + [os.path.join("icons", file) for file in os.listdir("icons") if (file != "CVS") and (file != ".hg") and (file != ".svn") and (file != ".arch-ids")]

setuptools.setup(
  name         = "Editobj3",
  version      = "0.2",
  license      = "LGPLv3+",
  description  = "An automatic dialog box generator for Python objects, supporting multiple graphical backends: Qt, GTK and HTML (single-user or with multiple users).",
  long_description = open(os.path.join(HERE, "README.rst")).read(),
  
  author       = "Lamy Jean-Baptiste (Jiba)",
  author_email = "jibalamy@free.fr",
  url          = "https://bitbucket.org/jibalamy/editobj3",
  
  classifiers  = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
    "Operating System :: OS Independent",
    "Environment :: Web Environment",
    "Environment :: X11 Applications :: Qt",
    "Environment :: X11 Applications :: GTK",
    "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
    "Topic :: Scientific/Engineering :: Human Machine Interfaces",
    "Topic :: Software Development :: User Interfaces",
    "Topic :: Software Development :: Libraries :: Python Modules",
    ],
  
  package_dir  = {"editobj3" : HERE},
  packages     = ["editobj3"],
  
  package_data = {"editobj3" : ["icons/*", "js/*"]}
  )
