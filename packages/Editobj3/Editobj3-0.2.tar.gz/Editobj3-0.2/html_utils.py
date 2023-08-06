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

from cgi import escape as escape

def html_escape(s): return escape(s).replace("\n", "<br/>")

def html_escape_arg(s): return escape(s).replace('"', "&quot;")

def html_js_escape(s): return escape(s).replace('"', '\\"').replace("\n", "\\n")

def js_escape(s): return s.replace('"', '\\"').replace("\n", "\\n")

NEED_UPDATES = set()

class User(object):
  def __init__(self, name, password = ""):
    self.name        = name
    self.password    = password
    self._obj2id     = {}
    self._id2obj     = {}
    self.next_id     = 1
    self.ws_handlers = []
    self.urls        = {}
    USERS[name] = self

  def __repr__(self): return "<%s %s>" % (self.__class__.__name__, self.name)
    
  def get_user(self): return self
  
  def obj2id(self, obj):
    if not obj in self._obj2id:
      self._obj2id[obj              ] = str(self.next_id)
      self._id2obj[str(self.next_id)] = obj
      self.next_id += 1
    return self._obj2id[obj]
    
  def id2obj(self, id):
    return self._id2obj[id]
    
  def register_url(self, path, content):
    self.urls[path] = content

  def register_url_for_local_file(self, path, filename):
    self.urls[path] = URLForLocalFile(filename)
    

class URLForLocalFile(object):
  def __init__(self, filename):
    self.filename = filename

USERS = {}
GUEST = User("guest")
