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
import PyQt5.QtGui     as qtgui

import editobj3
import editobj3.introsp as introsp
import editobj3.observe as observe
import editobj3.field   as field
import editobj3.editor  as editor

editobj3.GUI = "Qt"

#app = qtwidgets.QApplication(sys.argv)

class Obj(object):
  def __init__(self, name, children = None):
    self.children = children or []
    self.children2 = []
    self.name = name
    self.prop = 200

  def __str__(self): return self.name
  
o = Obj("racine", [
  Obj("corneille", [
    Obj("molière"),
  ]),
  Obj("tolkien"),
])
o.text = "A\nB\nc"
o.aaa = 3
#o.children2.append(o.children[0])

descr = introsp.description(Obj)
descr.def_attr("children", field.ObjectListField)
descr.def_attr("children2", field.ObjectListField)

#window = qtwidgets.QWidget()
#layout = qtwidgets.QVBoxLayout()
#pane = editor.EditorPane("Qt", None)
#pane.edit(o)
#layout.addWidget(pane)
#window.setLayout(layout)
#window.show()

editobj3.edit(o).main()

for attr in o.__dict__:
  print(attr, repr(getattr(o, attr)))
#sys.exit(app.exec_())
