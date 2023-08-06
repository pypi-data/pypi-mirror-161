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

import sys, os, os.path, stat

import editobj3, editobj3.introsp as introsp, editobj3.observe as observe, editobj3.field as field


class Permissions(object):
  def __init__(self, can_read, can_write, can_execute):
    self.can_read    = can_read
    self.can_write   = can_write
    self.can_execute = can_execute
    
  #def set_can_read(self, can_read):
    # XXX change the permission here
    # (not done in the example)
    # (and so on for the other attributes)


class File(object):
  def __init__(self, path):
    if isinstance(path, str): path = path
    self.path              = os.path.abspath(path)
    self.filename          = os.path.basename(path)
    try:    self.size = os.path.getsize(path)
    except: pass
    try:    mode = os.stat(path).st_mode
    except: mode = None
    if mode is not None:
      self.permissions_user  = Permissions(bool(mode & stat.S_IRUSR), bool(mode & stat.S_IWUSR), bool(mode & stat.S_IXUSR))
      self.permissions_group = Permissions(bool(mode & stat.S_IRGRP), bool(mode & stat.S_IWGRP), bool(mode & stat.S_IXGRP))
      self.permissions_other = Permissions(bool(mode & stat.S_IROTH), bool(mode & stat.S_IWOTH), bool(mode & stat.S_IXOTH))
      
    self.children = None
    
  def __str__(self): return self.filename
  
  def get_icon_filename(self):
    if os.path.isdir(self.path):    return os.path.join(os.path.dirname(sys.argv[0]), "directory.png")
    elif self.path.endswith(".py"): return os.path.join(editobj3._ICON_DIR, "python.svg")
    elif self.path.endswith(".png") or self.path.endswith(".jpeg") or self.path.endswith(".jpg"): return self.path
    else:                           return os.path.join(os.path.dirname(sys.argv[0]), "file.png")
    
  def has_children(self): return os.path.isdir(self.path)
  
  
  def get_children(self):
    if self.children is None:
      if os.path.isdir(self.path):
        self.children = [File(os.path.join(self.path, filename)) for filename in os.listdir(self.path) if not filename.startswith(".")]
        self.children.sort(key = lambda file: file.path)
        #self.children = range(10)
      else: self.children = []
    return self.children


descr = introsp.description(File)
descr.set_icon_filename(lambda o: o.get_icon_filename())
descr.def_attr("icon_filename", field.HiddenField)
descr.def_attr("size", field.IntField, unit = "Ko")
descr.def_attr("children", label = "")
descr.def_attr("permissions_user" , field.ObjectAttributeField)
descr.def_attr("permissions_group", field.ObjectAttributeField)
descr.def_attr("permissions_other", field.ObjectAttributeField)



file = File(os.path.join(".."))

if len(sys.argv) > 1: editobj3.GUI = sys.argv[-1]

editobj3.edit(file, on_close = sys.exit).main()

