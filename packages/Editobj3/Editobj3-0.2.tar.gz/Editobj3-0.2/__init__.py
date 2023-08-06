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

"""Editobj3 -- An automatic dialog box generator

Editobj is able to generate a dialog box for editing almost any Python object. The dialog box is
composed of an attribute list, a luxurious good-looking but useless icon and title bar, and a tree
view (if the edited object is part of a tree-like structure). The default dialog box can be
customized and adapted for a given class of object through the editobj3.introsp module.

Editobj3 has multiple GUI support; it currently supports Qt, Gtk and HTML.

Editobj3 was inspired by Java's "Bean Editor", however the intial concept have been extended by
adding icons, tree views, undo/redo, translation support, automatic update on object changes,
and support for editing several objects as if there was only one (see editobj3.introsp.ObjectPack).


The editobj3 package contains the following modules:

 * editobj3.introsp: High level, highly customizable introspection (go there for customizing Editobj3 dialog boxes)
 * editobj3.observe: Observation framework
 * editobj3.undoredo: Multiple undo/redo support
 * editobj3.editor: The editor dialog boxes and related widgets
 * editobj3.field: The set of basic fields for attribute panes


The following global variables can be changed:

 * editobj3.GUI: the default GUI system (default is Qt if available, else Gtk, else HTML)
 * editobj3.TRANSLATOR: the translator function used for translating dialog boxes.

It can be set to a translator function (such as the ones from the gettext module).


The edit() function in this module is an easy way to quickly edit an object. More complex edition
can be done using the widget available in editobj3.editor.
"""

import os, os.path

_ICON_DIR = os.path.join(os.path.dirname(__file__), "icons")
if not os.path.exists(_ICON_DIR):
  _ICON_DIR = os.path.join("/usr", "share", "editobj3", "icons")
  if not os.path.exists(_ICON_DIR):
    _ICON_DIR = os.path.join("/usr", "local", "share", "editobj3", "icons")
    if not os.path.exists(_ICON_DIR):
      _ICON_DIR = os.path.join("/usr", "share", "python-editobj3", "icons")
      
_eval = eval
def eval(s):
  return _eval(s)

VERSION = "0.2"

GUI = "Qt"

TRANSLATOR = lambda s: s

def edit(o, on_validate = None, direction = "h", undo_stack = None, width = -1, height = -1, expand_tree_at_level = False, selected = None, edit_child_in_self = True, on_close = None, on_edit_child = None, flat_list = False, master = None, menubar = True):
  global GUI
  if not GUI:
    try:
      import PyQt5
      GUI = "Qt"
    except:
      try:
        import gi
        from gi.repository import Gtk as gtk
        GUI = "Gtk"
      except:
        GUI = "HTML"
        
  if GUI == "Qt":
    import sys, PyQt5.QtWidgets as qtwidgets
    if qtwidgets.QApplication.startingUp(): qtwidgets.app = qtwidgets.QApplication(sys.argv)
    
  import editobj3.editor
  dialog = editobj3.editor.EditorDialog(GUI, master, direction, on_validate, edit_child_in_self, undo_stack, on_close, menubar)
  if flat_list: dialog.editor_pane.hierarchy_pane.flat_list = True
  if (width != -1) or (height != -1): dialog.set_default_size(width, height)
  if on_edit_child:
    dialog.editor_pane.on_edit_child = on_edit_child
  dialog.edit(o)
  if expand_tree_at_level: dialog.editor_pane.hierarchy_pane.expand_tree_at_level(expand_tree_at_level)
  if selected:
    dialog.editor_pane.hierarchy_pane.edit_child(selected)
  dialog.show()
  return dialog

