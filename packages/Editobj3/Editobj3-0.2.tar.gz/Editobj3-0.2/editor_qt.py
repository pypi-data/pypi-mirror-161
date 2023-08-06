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

import os.path
from xml.sax.saxutils import escape

import PyQt5.QtCore    as qtcore
import PyQt5.QtWidgets as qtwidgets
import PyQt5.QtGui     as qtgui

import editobj3.introsp as introsp
from editobj3.editor import *

MENU_LABEL_2_IMAGE = {
  "Open..."        : "document-open",
  "Save"           : "document-save",
  "Save as..."     : "document-save-as",
  "Close"          : "window-close",
  "Undo"           : "edit-undo",
  "Redo"           : "edit-redo",
  "Paste"          : "edit-paste",
  "Preferences..." : "preferences-desktop",
  }

_KEEP = set()
def delayed(func, *args):
  def on_timer():
    func(*args)
    _KEEP.discard(timer)
  timer = qtcore.QTimer()
  timer.timeout.connect(on_timer)
  timer.setInterval(0)
  timer.setSingleShot(True)
  timer.start()
  _KEEP.add(timer)
  return timer

class QtBaseDialog(BaseDialog):
  def init_window(self, on_validate, master = None):
    if on_validate:
      self.window = qtwidgets.QDialog()
      self.window.setModal(True)
      self.layout = qtwidgets.QVBoxLayout()
      self.layout.setContentsMargins(0, 0, 0, 0)
      self.layout.setSpacing(0)
      
      self.cancel_button = qtwidgets.QPushButton(editobj3.TRANSLATOR("Cancel"))
      self.ok_button     = qtwidgets.QPushButton(editobj3.TRANSLATOR("Ok"))
      self.cancel_button.clicked.connect(lambda : self.window.done(0))
      self.ok_button    .clicked.connect(lambda : self.window.done(1))
      self.cancel_button.setIcon(qtgui.QIcon.fromTheme("dialog-cancel"))
      self.ok_button    .setIcon(qtgui.QIcon.fromTheme("dialog-ok"))
      self.cancel_button.setAutoDefault(False)
      self.ok_button    .setDefault(True)
      
      button_layout = qtwidgets.QHBoxLayout()
      button_layout.setContentsMargins(5, 5, 5, 5)
      button_layout.setSpacing(20)
      button_layout.addStretch(1)
      button_layout.addWidget(self.cancel_button)
      button_layout.addWidget(self.ok_button)
      
      self.layout.addLayout(button_layout)
      self.window.setLayout(self.layout)
    else:
      if master:
        if isinstance(master, QtBaseDialog): master = master.window
        self.window = qtwidgets.QDialog(master)
      else:
        self.window = qtwidgets.QWidget()
      self.window.closeEvent = self.closeEvent
      self.layout = qtwidgets.QVBoxLayout()
      self.layout.setContentsMargins(0, 0, 0, 0)
      self.layout.setSpacing(0)
      self.window.setLayout(self.layout)
      
  def build_default_menubar(self):
    self._menus = []
    self.current_radio_group = None
    self.menubar = qtwidgets.QMenuBar()
    self.layout.insertWidget(0, self.menubar)
    
    BaseDialog.build_default_menubar(self)
    
  def add_to_menu(self, menu, has_submenu, label, command = None, arg = None, accel = "", accel_enabled = True, image = None, type = u"button", pos = -1):
    if command:
      if arg: command2 = lambda *args: command(*(list(args) + [arg]))
      else:   command2 = command
      
    stock = MENU_LABEL_2_IMAGE.get(label)
    if has_submenu:
      submenu = qtwidgets.QMenu(editobj3.TRANSLATOR(label))
      self._menus.append(submenu)
      if pos == -1: menu.addMenu(submenu)
      else:         menu.insertMenu(menu.actions()[pos], submenu)
      if command: submenu.aboutToShow.connect(command2)
      return submenu
    
    else:
      action = qtwidgets.QAction(editobj3.TRANSLATOR(label), self.window)
      self._menus.append(action)
      if pos == -1: menu.addAction(action)
      else:         menu.insertAction(menu.actions()[pos], action)
      
      if   type == "check":
        action.setCheckable(True)
        self.current_radio_group = None
        if command: action.toggled.connect(command2)
      
      elif type == "radio":
        action.setCheckable(True)
        if not self.current_radio_group: self.current_radio_group = qtwidgets.QActionGroup(self.window)
        self.current_radio_group.addAction(action)
        if command: action.toggled.connect(command2)
        
      else:
        self.current_radio_group = None
        if isinstance(stock, qtgui.QIcon):                              image = stock
        elif stock and (not image) and qtgui.QIcon.hasThemeIcon(stock): image = qtgui.QIcon.fromTheme(stock)
        if image: action.setIcon(image)
        if command: action.triggered.connect(command2)
        
      if accel:
        accel = accel.replace("C-", "Ctrl+").replace("S-", "Shift+")
        action.setShortcut(qtgui.QKeySequence(accel))
        if not accel_enabled: action.setShortcutContext(qtcore.Qt.WidgetShortcut)
      return action
    
  def add_separator_to_menu(self, menu, pos = -1):
    if pos == -1: menu.addSeparator()
    else:         menu.insertSeparator(menu.actions()[pos])
    self.current_radio_group = None
    
  def set_menu_checked(self, menu, checked): menu.setChecked(checked)
  def set_menu_enable (self, menu, enable):  menu.setEnabled(enable)
  def set_menu_label  (self, menu, label):
    if isinstance(menu, qtwidgets.QMenu): menu.setTitle(label)
    else:                                 menu.setText (label)
    
  def close_dialog(self): self.window.close()
  def closeEvent(self, event):
    if self.on_dialog_closed(): event.accept()
    else:                       event.ignore()
  def on_dialog_closed(self, *args):
    if self.on_close: self.on_close()
    return True
  
  def main(self):
    self.show()
    return qtcore.QCoreApplication.exec_()
  
  def set_default_size(self, w, h): self.window.resize(w, h)
  
  def show(self):
    if self.on_validate:
      r = self.window.exec_()
      if r: self.on_validate(self.get_selected_object())
      else: self.on_validate(None)
      self.window.destroy()
    else: self.window.show()
  

class QtEditorDialog(EditorDialog, QtBaseDialog):
  def __init__(self, gui = None, master = None, direction = "h", on_validate = None, edit_child_in_self = 1, undo_stack = None, on_close = None, menubar = True):
    self.init_window(on_validate, master)
    super().__init__(gui, master, direction, on_validate, edit_child_in_self, undo_stack, on_close, menubar)
    if menubar: self.layout.insertWidget(1, self.editor_pane, 1)
    else:       self.layout.insertWidget(0, self.editor_pane, 1)
      
  def edit(self, o):
    EditorDialog.edit(self, o)
    label = self.editor_pane.hierarchy_pane.descr.label_for(o)
    self.window.setWindowTitle(label.replace("\n", " ").replace("\t", " "))
    return self


class QtEditorTabbedDialog(EditorTabbedDialog, QtBaseDialog):
  def __init__(self, gui = None, master = None, direction = "h", on_validate = None, edit_child_in_self = 1, undo_stack = None, on_close = None, menubar = True):
    self.init_window(on_validate, master)
    super().__init__(gui, master, direction, on_validate, edit_child_in_self, undo_stack, on_close, menubar)
    self.notebook = qtwidgets.QTabWidget()
    self.notebook.currentChanged.connect(self.on_tab_changed)
    if menubar: self.layout.insertWidget(1, self.notebook, 1)
    else:       self.layout.insertWidget(0, self.notebook, 1)

  # For updating the childhood pane layout
  def on_tab_changed(self, index):
    editor_pane = self.notebook.widget(index)
    self.show_tab(editor_pane)
    editor_pane.hi_box.layout().invalidate()
    
  def show(self):
    QtBaseDialog.show(self)
    editor_pane = self.notebook.currentWidget()
    if editor_pane:
      self.show_tab(editor_pane)
      editor_pane.hi_box.layout().invalidate()
      
  def add_tab(self, name, label, o = None, func = None):
    editor_pane = super().add_tab(name, label, o)
    editor_pane.func = func
    self.notebook.addTab(editor_pane, label)
    return editor_pane
  
  def remove_tab(self, name):
    for i in range(len(self.editor_panes)):
      if self.editor_panes[name] is self.notebook.widget(i):
        self.notebook.removeTab(i)
        break
    super.remove_tab(name)
    
  def get_current_editor_pane(self): return self.notebook.currentWidget()


class OverlayLayout(qtwidgets.QLayout):
  def __init__(self):
    qtwidgets.QLayout.__init__(self)
    self._items = []
    self.overlay_offset_x = 3
    self.overlay_offset_y = 4
    
  def count(self): return len(self._items)
  def addItem(self, item): self._items.append(item)
  def itemAt(self, i):
    if 0 <= i < len(self._items): return self._items[i]
  def takeAt(self, i):
    if 0 <= i < len(self._items):
      item = self._items[i]
      del self._items[i]
      return item
    
  def setGeometry(self, rect):
    self._items[0].setGeometry(rect)
    
    def set_geom1():
      size = self._items[1].sizeHint()
      size2 = self._items[0].widget().viewport().size()
      self._items[1].setGeometry(qtcore.QRect(rect.left() + size2.width() - size.width() - self.overlay_offset_x, rect.top() + self.overlay_offset_y, size.width(), size.height()))
    delayed(set_geom1)
    
  def sizeHint(self): return self._items[0].sizeHint()
  def minimumSize(self): return self._items[0].minimumSize()

class QtEditorPane(EditorPane, qtwidgets.QSplitter):
  def __init__(self, gui, master, edit_child_in_self = 1, undo_stack = None, direction = "h"):
    qtwidgets.QSplitter.__init__(self)
    if direction == "h": self.setOrientation(qtcore.Qt.Horizontal)
    else:                self.setOrientation(qtcore.Qt.Vertical)
    super().__init__(gui, master, edit_child_in_self, undo_stack)
    
    self.box = qtwidgets.QWidget()
    layout = qtwidgets.QVBoxLayout()
    layout.setContentsMargins(3, 3, 3, 3)
    layout.addWidget(self.icon_pane)
    layout.addWidget(self.attribute_pane)
    self.box.setLayout(layout)
    self.scroll2 = qtwidgets.QScrollArea()
    self.scroll2.setWidgetResizable(True)
    self.scroll2.setSizeAdjustPolicy(qtwidgets.QAbstractScrollArea.AdjustToContents)
    self.scroll2.setHorizontalScrollBarPolicy(qtcore.Qt.ScrollBarAlwaysOff)
    
    self.hi_box = qtwidgets.QWidget()
    layout2 = OverlayLayout()
    layout2.addWidget(self.hierarchy_pane)
    layout2.addWidget(self.childhood_pane)
    self.hi_box.setLayout(layout2)
    self.addWidget(self.hi_box)
    self.addWidget(self.scroll2)
    self.setCollapsible(1, False)
    
  def edit(self, o):
    EditorPane.edit(self, o)
    
    self.scroll2.setWidget(None)
    self.scroll2.setWidget(self.box)
    
    width = self.box.sizeHint().width()
    max_width = qtwidgets.QApplication.desktop().screenGeometry(self).width() - 64
    if not self.isCollapsible(0): max_width = max_width - self.hi_box.sizeHint().width() - self.handleWidth()
    if width <= max_width:
      self.scroll2.setMinimumWidth(width)
      self.scroll2.setHorizontalScrollBarPolicy(qtcore.Qt.ScrollBarAlwaysOff)
    else:
      self.scroll2.setMinimumWidth(max_width)
      self.scroll2.setHorizontalScrollBarPolicy(qtcore.Qt.ScrollBarAsNeeded)

  def _set_hierarchy_visible(self, visible):
    if visible:
      if self.isCollapsible(0):
        self.setCollapsible(0, False)
        self.setSizes([1, 1])
    else:
      self.setCollapsible(0, True)
      self.setSizes([0, 1])
      
  def sizeHint(self):
    if self.isCollapsible(0):
      size = qtcore.QSize(self.scroll2.sizeHint())
      size.setWidth (size.width()  + self.handleWidth())
      size.setHeight(size.height() + 40) # For ObjectPack edition => bigger icon pane
      return size
    else: return qtwidgets.QSplitter.sizeHint(self)
      

class QtAttributePane(AttributePane, qtwidgets.QWidget):
  def __init__(self, gui, master, edit_child = None, undo_stack = None):
    qtwidgets.QWidget.__init__(self)
    super().__init__(gui, master, edit_child, undo_stack)
    self.destroyed.connect(self._destroyed)
    self.can_expand = 0
    self._re_edit_timer = None
    
    self.grid_layout = qtwidgets.QGridLayout()
    self.grid_layout.setHorizontalSpacing(2)
    self.grid_layout.setVerticalSpacing(3)
    self.grid_layout.setContentsMargins(0, 0, 0, 0)
    self.setLayout(self.grid_layout)
    
  def _re_edit(self):
    if not self._re_edit_timer:
      self._re_edit_timer = delayed(self.edit, self.o)
      
  def edit(self, o, ignored_attrs = None):
    if self._re_edit_timer:
      self._re_edit_timer.stop()
      self._re_edit_timer = None
    #if self.o is o: return
    self.can_expand = 0
    
    AttributePane.edit(self, o, ignored_attrs)
    #if isinstance(self.master, EditorPane):
      #if self.can_expand: self.master.box.set_child_packing(self, 1, 1, 0, qt.PackType.START)
      #else:               self.master.box.set_child_packing(self, 0, 1, 0, qt.PackType.START)
      #self.master.box.show_all()
      #min_size, natural_size = self.master.box.get_preferred_size()
      #if self.master.direction == "h": self.master.scroll2.set_min_content_height(min(natural_size.height, 800, _screen.height() - 128))
      #else:                            self.master.scroll2.set_min_content_height(min(natural_size.height, 500, _screen.height() - 128))
    #else: self.show_all()
    
  def _delete_all_fields(self):
    layout = self.layout()
    for i in reversed(range(layout.count())): 
      layout.itemAt(i).widget().setParent(None)
      
  def _new_field(self, attribute, field_class, unit, i):
    label = qtwidgets.QLabel(attribute.label)
    field = field_class(self.gui, self, self.o, attribute, self.undo_stack)
    #label.set_alignment(0.0, 0.0)
    #label.set_margin_top(5)
    self.grid_layout.addWidget(label, i, 0, 1, 1)
    self.grid_layout.addWidget(field, i, 1, 1, 1)
    #field.set_hexpand(1)
    if unit:
      unit_label = qtwidgets.QLabel(unit)
      #unit_label.set_alignment(0.0, 0.5)
      self.grid_layout.addWidget(unit_label, i, 2, 1, 1)
    #if field.y_flags & qt.AttachOptions.EXPAND:
      #field.set_vexpand(1)
    #  self.can_expand = 1
    return field


class OverlayedIconLayout(qtwidgets.QLayout):
  def __init__(self, icon_pane):
    qtwidgets.QLayout.__init__(self)
    self.icon_pane = icon_pane
    self._items = []
    
  def count(self): return len(self._items)
  def addItem(self, item): self._items.append(item)
  def itemAt(self, i):
    if 0 <= i < len(self._items): return self._items[i]
  def takeAt(self, i):
    if 0 <= i < len(self._items):
      item = self._items[i]
      del self._items[i]
      return item
    
  def setGeometry(self, rect):
    x = y = 10
    for item in self._items:
      size = item.sizeHint()
      item.setGeometry(qtcore.QRect(rect.left() + x, rect.top() + y, size.width(), size.height()))
      x += 30
      y += 15
      
  def sizeHint(self): return self.minimumSize()
  def minimumSize(self):
    x = y = 20
    max_width = max_height = 0
    for item in self._items:
      size = item.sizeHint()
      if x + size.width()  > max_width : max_width  = x + size.width ()
      if y + size.height() > max_height: max_height = x + size.height()
      x += 30
      y += 15
    return qtcore.QSize(max_width, max_height)
    

class QtIconPane(IconPane, qtwidgets.QWidget):
  def __init__(self, gui, master):
    qtwidgets.QWidget.__init__(self)
    super().__init__(gui, master)
    
    self.label = qtwidgets.QLabel()
    self.label.setWordWrap(True)
    self.label.setAlignment(qtcore.Qt.AlignTop | qtcore.Qt.AlignJustify)
    self.label.setTextFormat(qtcore.Qt.RichText)
    self.label.setTextInteractionFlags(qtcore.Qt.TextSelectableByMouse | qtcore.Qt.TextSelectableByKeyboard | qtcore.Qt.LinksAccessibleByMouse)
    self.destroyed.connect(self._destroyed)
    self.images = []
    
    layout = qtwidgets.QHBoxLayout()
    self.icons_layout = OverlayedIconLayout(self)
    layout.addLayout(self.icons_layout)
    layout.addWidget(self.label, 1)
    self.setLayout(layout)
    
  def set_nb_images(self, nb):
    if   nb < len(self.images):
      for image in self.images[nb:]: image.setParent(None)
      self.images = self.images[:nb]
      
    elif nb > len(self.images):
      for i in range(nb - len(self.images)):
        image = qtwidgets.QLabel()
        self.images.append(image)
        self.icons_layout.addWidget(image)
        
  def _set_icon_filename_label_details(self, icon_filename, label, details):
    if details: self.label.setText(("<b>%s</b><br/><br/>%s\n" % (escape(label), escape(details))).replace("\n", "<br/>"))
    else:       self.label.setText(("<b>%s</b>"               %  escape(label)).replace("\n", "<br/>"))
    
    self.label.setMinimumSize(self.label.sizeHint())
    
    if   not icon_filename: self.set_nb_images(0)
    
    elif isinstance(icon_filename, str):
      self.set_nb_images(1)
      self.images[0].setPixmap(load_big_icon(icon_filename))
      
    else:
      self.set_nb_images(len(icon_filename))
      icon_filename.sort()
      icon_filename.reverse()
      i = 0
      for filename in icon_filename:
        self.images[i].setPixmap(load_big_icon(filename))
        i += 1

def _load_qt_icon(name):
  icon = qtgui.QIcon.fromTheme(name)
  if icon.isNull():
    return qtgui.QIcon(os.path.join(editobj3._ICON_DIR, "%s.svg" % name))
  return icon
  
        
class QtChildhoodPane(ChildhoodPane, qtwidgets.QWidget):
  def __init__(self, gui, master, undo_stack = None, restrict_to_attribute = None):
    qtwidgets.QWidget.__init__(self)
    super().__init__(gui, master, undo_stack, restrict_to_attribute)
    self.setAutoFillBackground(True)
    self.button_move_up   = qtwidgets.QToolButton()
    self.button_add       = qtwidgets.QToolButton()
    self.button_remove    = qtwidgets.QToolButton()
    self.button_move_down = qtwidgets.QToolButton()
    self.button_move_up  .setIcon(_load_qt_icon("up"    ))
    self.button_add      .setIcon(_load_qt_icon("add"   ))
    self.button_remove   .setIcon(_load_qt_icon("remove"))
    self.button_move_down.setIcon(_load_qt_icon("down"  ))
    self.button_move_up  .setAutoRaise(True)
    self.button_add      .setAutoRaise(True)
    self.button_remove   .setAutoRaise(True)
    self.button_move_down.setAutoRaise(True)
    self.button_move_up  .clicked.connect(self.on_move_up)
    self.button_add      .clicked.connect(self.on_add)
    self.button_remove   .clicked.connect(self.on_remove)
    self.button_move_down.clicked.connect(self.on_move_down)
    #icon_size = qtcore.QSize(editobj3.editor_qt.SMALL_ICON_SIZE, editobj3.editor_qt.SMALL_ICON_SIZE)
    #self.button_move_up  .setSizeHint(icon_size)
    #self.button_add      .setIconSize(icon_size)
    #self.button_remove   .setIconSize(icon_size)
    #self.button_move_down.setIconSize(icon_size)
    
    layout = qtwidgets.QVBoxLayout()
    layout.setContentsMargins(0, 0, 0, 0)
    layout.addWidget(self.button_move_up)
    layout.addWidget(self.button_add)
    layout.addWidget(self.button_remove)
    layout.addWidget(self.button_move_down)
    self.setLayout(layout)
    
  def set_button_visibilities(self, visible1, visible2, visible3, visible4):
    if visible1 or visible2 or visible3 or visible4:
      self.button_move_up  .setVisible(bool(visible1))
      self.button_add      .setVisible(bool(visible2))
      self.button_remove   .setVisible(bool(visible3))
      self.button_move_down.setVisible(bool(visible4))
      self.setVisible(True)
    else:
      self.setVisible(False)


class DynamicTree(qtcore.QAbstractItemModel):
  def set_root_node(self, root_node):
    self.root_node = root_node
    self.children  = [root_node]
    self.o_has_any_children = True

  def expanded(self): return self.children
    
  def parent(self, index):
    if not index.isValid(): return qtcore.QModelIndex()
    node = index.internalPointer()
    #if node.parent is self.root_node: return qtcore.QModelIndex()
    if node is self: return qtcore.QModelIndex()
    if node is self.root_node: return self.createIndex(0, 0, self)
    return self.createIndex(node.parent.index, 0, node.parent)
  
  def hasChildren(self, index):
    if not index.isValid(): return True
    return index.internalPointer().o_has_any_children
  
  def rowCount(self, index):
    if not index.isValid(): return 1
    return len(index.internalPointer().expanded())
  
  def columnCount(self, index): return 1
  
  def index(self, row, column, parent_index):
    if not self.hasIndex(row, column, parent_index): return qtcore.QModelIndex()
    if parent_index.isValid(): parent = parent_index.internalPointer()
    else:                      parent = self
    return self.createIndex(row, column, parent.children[row])
  
  def data(self, index, role):
    if index.isValid():
      if   role == qtcore.Qt.DisplayRole:    return str(index.internalPointer())
      elif role == qtcore.Qt.DecorationRole: return index.internalPointer().get_icon()
    return qtcore.QVariant()

class DynamicFlatList(DynamicTree):
  def set_root_node(self, root_node): self.root_node = root_node
    
  def rowCount(self, index):
    if not index.isValid(): return len(self.root_node.expanded())
    return len(index.internalPointer().expanded())
  
  def parent(self, index):
    if not index.isValid(): return qtcore.QModelIndex()
    node = index.internalPointer()
    if node is self.root_node: return qtcore.QModelIndex()
    return self.createIndex(node.parent.index, 0, node.parent)
  
  def index(self, row, column, parent_index):
    if not self.hasIndex(row, column, parent_index): return qtcore.QModelIndex()
    if parent_index.isValid(): parent = parent_index.internalPointer()
    else:                      parent = self.root_node
    return self.createIndex(row, column, parent.children[row])

  
class DynamicNode(object):
  def __init__(self, parent):
    self.children         = []
    self.children_created = False
    self.is_expandable    = False
    self.index            = 0
    if isinstance(parent, DynamicNode):
      self.parent         = parent
      self.tree           = parent.tree
    else:
      self.parent         = None
      self.tree           = parent
      self.update()
      self.update_children()
      
  def has_children(self): raise NotImplementedError
  def create_children(self, old_children = None): return []
  
  def qt_index(self): return self.tree.createIndex(self.index, 0, self)
  
  def expand(self): self.tree.view.expand(self.qt_index())
  
  def expanded(self):
    if not self.children_created:
      self.children_created = True
      self.update_children()
    return self.children
  
  def collapsed(self):
    if self.children_created:
      self.children_created = False
      for child in self.children[::-1]: child.destroy()
      self.is_expandable = False
      self.update_children()
      
  def update(self): pass
  
  def update_children(self):
    if self.children_created:
      old_children = self.children[:]
      new_children = self.create_children(old_children)
      old_children_set = set(old_children)
      new_children_set = set(new_children)
      
      for child in old_children[::-1]:
        if not child in new_children_set: child.destroy()
        
      kept_children = [child for child in new_children if child in old_children_set]
      
      for i in range(len(self.children)): self.children[i].index     = i
      for i in range(len(kept_children)): kept_children[i].new_index = i
      
      qt_index = self.qt_index()
      if kept_children:
        for child in kept_children:
          child_index = self.children.index(child)
          if child.new_index == child_index : continue # Already at the right position
          
          self.tree.beginMoveRows(qt_index, child_index, child_index, qt_index, child.new_index)
          child.index = child.new_index
          del self.children[child_index]
          self.children.insert(child.new_index, child)
          self.tree.endMoveRows()
          
        for child in kept_children: del child.new_index
        
      for i in range(len(new_children)):
        new_children[i].index = i
        if not new_children[i] in old_children_set:
          self.tree.beginInsertRows(qt_index, i, i)
          self.children.insert(i, new_children[i])
          self.tree.endInsertRows()
          
      for child in new_children:
        if not child in old_children_set:
          child.update()
          child.update_children()
          
      self.children = new_children
      
    else:
      if self.flat_list: pass
      else:              self.is_expandable = bool(self.has_children())
      
  def destroy(self):
    for child in self.children[::-1]: child.destroy()
    if self.parent and (self.tree.view.tree is self.tree):
      qt_parent_index = self.parent.qt_index()
      self.tree.beginRemoveRows(qt_parent_index, self.index, self.index)
      self.parent.children.remove(self)
      self.tree.endRemoveRows()
    

class Qt_HierarchyNode(HierarchyNode, DynamicNode):
  def update(self):
    icon_filename = self.descr.icon_filename_for(self.o)
    #if isinstance(icon_filename, str): icon = load_small_icon(icon_filename)
    #else:                              icon = None
    index = self.qt_index()
    self.tree.dataChanged.emit(index, index)
    
  def get_icon(self):
    icon_filename = self.descr.icon_filename_for(self.o)
    if isinstance(icon_filename, str): return load_small_icon(icon_filename)
    
  def __str__(self):
    if self.attribute and not self.restrict_to_attribute: attr_label = self.attribute.label
    else:                                                 attr_label = ""
    if attr_label: return '''%s : %s''' % (attr_label, self.descr.label_for(self.o))
    return self.descr.label_for(self.o)
  
# class HierarchyScrollBar(qtwidgets.QScrollBar):
#   def __init__(self, hierarchy_pane):
#     qtwidgets.QScrollBar.__init__(self, qtcore.Qt.Vertical)
#     self.hierarchy_pane = hierarchy_pane

#   def hideEvent(self, event):
#     qtwidgets.QScrollBar.hideEvent(self, event)
#     print("cachée")
#     #self..overlay_offset_x = 3

#   def showEvent(self, event):
#     qtwidgets.QScrollBar.showEvent(self, event)
#     print("visible")
#     #self..overlay_offset_x = 3 + self.

class QtHierarchyPane(HierarchyPane, qtwidgets.QTreeView):
  Node = Qt_HierarchyNode
  def __init__(self, gui, master, edit_child, undo_stack = None, restrict_to_attribute = None, flat_list = 0):
    qtwidgets.QTreeView.__init__(self)
    
    self.setSelectionMode(qtwidgets.QAbstractItemView.ExtendedSelection)
    self.setHeaderHidden(True)
    self.setIconSize(qtcore.QSize(editobj3.editor_qt.SMALL_ICON_SIZE, editobj3.editor_qt.SMALL_ICON_SIZE))
    
    super().__init__(gui, master, edit_child, undo_stack, restrict_to_attribute, flat_list)
    self.destroyed.connect(self._destroyed)
    self.selected_parent     = None
    self.selected_attribute  = None
    self.selected_node       = None
    self.selected            = None
    self.last_button         = 0
    
    self.collapsed.connect(self.on_collapsed)
    self.pressed.connect(self.on_button_pressed)
    self.doubleClicked.connect(self.on_double_click)
    
  def edit(self, *args):
    if len(args) >= 3: return qtwidgets.QTreeView.edit(self, *args)
    o = args[0]
    if o is self.o: return

    if self.flat_list: self.tree = DynamicFlatList(); self.setRootIsDecorated(False)
    else:              self.tree = DynamicTree()
    self.tree.view = self
    
    
    HierarchyPane.edit(self, o)
    self.tree.set_root_node(self.root_node)
    self.root_node.expanded()
    self.setModel(self.tree)
    self.selectionModel().selectionChanged.connect(self.on_selection_changed)
    if self.flat_list:
      self.childhood_pane.edit(self.childhood_pane_parent, self.childhood_pane_attribute, self.o)
    else:
      self.setExpanded(self.root_node.qt_index(), True)
      self.selectionModel().select(self.root_node.qt_index(), qtcore.QItemSelectionModel.ClearAndSelect)
      
  def expand_tree_at_level(self, level): self.expandToDepth(level)
  
  def select_node(self, node):
    self.selectionModel().clearSelection()
    if   node:                                   self.selectionModel().select(node.qt_index(), qtcore.QItemSelectionModel.Select)
    elif self.flat_list and self.childhood_pane: self.childhood_pane.edit(self.childhood_pane_parent, self.childhood_pane_attribute, self.o)
    
  def on_collapsed(self, index):
    node = index.internalPointer()
    node.collapsed()
    
  def on_double_click(self, index):
    actions = self.get_actions(self.selected_parent, self.selected_attribute, self.selected)
    for action in actions:
      if action.default:
        self._action_activated(action, self.selected_parent, self.selected_attribute, self.selected)
        break
      
  def on_button_pressed(self, index):
    if qtgui.QGuiApplication.mouseButtons() == qtcore.Qt.RightButton:
      actions = self.get_actions(self.selected_parent, self.selected_attribute, self.selected)
      self.show_action_menu(actions)
      
  def on_selection_changed(self, selected, deselected):
    indexes = self.selectionModel().selectedIndexes()
    if len(indexes) == 0:
      self.edit_child(None)
      if self.childhood_pane: self.childhood_pane.edit(self.childhood_pane_parent, self.childhood_pane_attribute, None)
      self.selected_node = None
      return
    
    if len(indexes) == 1:
      node = self.selected_node = indexes[0].internalPointer()
      if node.parent: self.selected_parent = node.parent.o
      else:           self.selected_parent = None
      self.selected           = node.o
      self.selected_attribute = node.attribute
      
      self.edit_child(self.selected, self.get_ignored_attrs([node]))
      if self.childhood_pane: self.childhood_pane.edit(self.selected_parent, self.selected_attribute, self.selected)
      
    else:
      nodes = self.selected_node = [index.internalPointer() for index in indexes]
      self.selected_parent    = introsp.ObjectPack([(node.parent and node.parent.o) for node in nodes])
      self.selected           = introsp.ObjectPack([node.o for node in nodes])
      self.selected_attribute = [node.attribute for node in nodes]
      
      self.edit_child(self.selected, self.get_ignored_attrs(nodes))
      if self.childhood_pane: self.childhood_pane.edit(self.selected_parent, self.selected_attribute, self.selected)
      
  def on_action_activated(self, action):
    if self.selected:
      self._action_activated(action, self.selected_parent, self.selected_attribute, self.selected)
    else:
      self._action_activated(action, None, self.restrict_to_attribute, self.o)
      
  def show_action_menu(self, actions):
    self._popup_menu = qtwidgets.QMenu() # The menu must be kept in memory, else it does not appear.
    for action in actions:
      menu_item = qtwidgets.QAction(action.label, self._popup_menu)
      menu_item.triggered.connect(lambda checked, action = action: self.on_action_activated(action))
      if action.default:
        font = qtgui.QFont(menu_item.font())
        font.setBold(True)
        menu_item.setFont(font)
      self._popup_menu.addAction(menu_item)
    self._popup_menu.popup(qtgui.QCursor.pos())

  
SMALL_ICON_SIZE = 32

_small_icons = {}
_big_icons   = {}

def load_big_icon(filename):
  pixmap = _big_icons.get(filename)
  if not pixmap: pixmap = _big_icons[filename] = qtgui.QPixmap(filename)
  return pixmap

def load_small_icon(filename):
  icon = _small_icons.get(filename)
  if not icon: icon = _small_icons[filename] = qtgui.QIcon(filename)
  return icon
