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

import sys, os

import PyQt5.QtCore    as qtcore
import PyQt5.QtWidgets as qtwidgets

import editobj3
import editobj3.introsp as introsp
import editobj3.observe as observe
import editobj3.field   as field
import editobj3.editor  as editor

editobj3.GUI = "Qt"

app = qtwidgets.QApplication(sys.argv)

class Point(object):
  def __init__(self):
    self.x = 1
    self.y = 2
  def __repr__(self): return "Point(%s, %s)" % (self.x, self.y)
  
class Obj(object):
  def __init__(self):
    self.prop = 1
    self.prop_deux = 200
    self.texte = "Bla\nBla\nBla..."
    self.password = "abcd"
    self.filename = "/tmp/t.txt"
    self.url = "http://python.org"
    self.boo = True
    self.level = 1
    self.level2 = 2
    self.flags = ["A"]
    self.point = Point()
o = Obj()

descr = introsp.description(Obj)
descr.def_attr("prop", field.RangeField(0, 100))
descr.def_attr("level"           , field.EnumField({"low":0, "medium":1, "high":2, "paranoid":3}))
descr.def_attr("level2"          , field.EnumField(list(range(50))))
descr.def_attr("flags"           , field.EnumListField(["A", "B", "C", "D"]))
#descr.def_attr("point"           , field.ObjectAttributeField)

window = qtwidgets.QWidget()
layout = qtwidgets.QVBoxLayout()
attribute_pane = editor.AttributePane("Qt", None)
attribute_pane.edit(o)
layout.addWidget(attribute_pane)
window.setLayout(layout)
window.show()

app.exec_()
for attr in o.__dict__:
  print(attr, repr(getattr(o, attr)))
#sys.exit(app.exec_())
