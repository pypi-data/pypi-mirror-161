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

import PyQt5.QtCore    as qtcore
import PyQt5.QtWidgets as qtwidgets

import editobj3
from editobj3.field import *
from editobj3.field import _WithButtonField, _RangeField, _ShortEnumField, _LongEnumField, _EnumListField

def _edit_from_field(o, widget, undo_stack):
  editobj3.edit(o, undo_stack = undo_stack)

class QtField(MultiGUIField):
  #y_flags = gtk.AttachOptions.FILL
  pass

class QtHiddenField(QtField, HiddenField): pass

class QtLabelField(QtField, LabelField, qtwidgets.QLabel):
  def __init__(self, gui, master, o, attribute, undo_stack):
    qtwidgets.QLabel.__init__(self)
    super().__init__(gui, master, o, attribute, undo_stack)
    self.setWordWrap(True)
    self.update()
    
  def update(self):
    self.setText(self.get_value())
    
class QtEntryField(QtField, EntryField, qtwidgets.QLineEdit):
  def __init__(self, gui, master, o, attribute, undo_stack):
    qtwidgets.QLineEdit.__init__(self)
    super().__init__(gui, master, o, attribute, undo_stack)
    
    self.update()
    self.editingFinished.connect(self.validate)
    
  def validate(self):
    self.set_value(self.text())
    
  def update(self):
    self.updating += 1
    try: self.setText(self.get_value() or "") # Qt does not accept None as a text
    finally: self.updating -= 1
    
class QtTextField(QtField, TextField, qtwidgets.QPlainTextEdit):
  #y_flags = gtk.AttachOptions.FILL | gtk.AttachOptions.EXPAND
  def __init__(self, gui, master, o, attribute, undo_stack):
    qtwidgets.QPlainTextEdit.__init__(self)
    super().__init__(gui, master, o, attribute, undo_stack)
    self.update()
    #self.textChanged.connect(self.validate)
    
  def focusOutEvent(self, event):
    qtwidgets.QPlainTextEdit.focusOutEvent(self, event)
    self.validate()
    
  def validate(self, *args):
    value = self.document().toPlainText()
    if value != self.get_value(): self.set_value(value)
    
  def update(self):
    self.updating += 1
    try:
      value = self.get_value()
      self.document().setPlainText(value)
    finally: self.updating -= 1
    
    
class QtIntField   (QtEntryField, IntField   ): pass
class QtFloatField (QtEntryField, FloatField ): pass
class QtStringField(QtEntryField, StringField): pass


class QtPasswordField(QtStringField, PasswordField):
  def __init__(self, gui, master, o, attribute, undo_stack):
    QtStringField.__init__(self, gui, master, o, attribute, undo_stack)
    self.setEchoMode(qtwidgets.QLineEdit.Password)

class QtEntryListField (QtTextField, EntryListField ): pass
class QtIntListField   (QtTextField, IntListField   ): pass
class QtFloatListField (QtTextField, FloatListField ): pass
class QtStringListField(QtTextField, StringListField): pass

class Qt_WithButtonField(QtField, _WithButtonField, qtwidgets.QWidget):
  def __init__(self, gui, master, o, attribute, undo_stack, field_class = None, button_text = None, on_button = None):
    qtwidgets.QWidget.__init__(self)
    super().__init__(gui, master, o, attribute, undo_stack, field_class, button_text, on_button)
    layout = qtwidgets.QHBoxLayout()
    layout.setContentsMargins(0, 0, 0, 0)
    layout.addWidget(self.string_field)
    button = qtwidgets.QToolButton()
    button.setText(editobj3.TRANSLATOR(self.button_text))
    button.setAutoRaise(True)
    button.clicked.connect(self.on_button_clicked)
    layout.addWidget(button)
    self.setLayout(layout)
    
  def on_button_clicked(self, *args): self.on_button(self.o, self, self.undo_stack)
    
class QtFilenameField(Qt_WithButtonField, FilenameField):
  def on_button(self, o, field, undo_stack):
    #filename = qtwidgets.QFileDialog.getSaveFileName(self, editobj3.TRANSLATOR("Choose a filename"), self.get_value())
    filename = qtwidgets.QFileDialog.getSaveFileName(self, None, self.get_value(), options = qtwidgets.QFileDialog.DontConfirmOverwrite)[0]
    if filename:
      self.string_field.set_value(filename)
      self.string_field.update()
      
class QtDirnameField(Qt_WithButtonField, DirnameField):
  def on_button(self, o, field, undo_stack):
    filename = qtwidgets.QFileDialog.getExistingDirectory(self, None, self.get_value())[0]
    if filename:
      self.string_field.set_value(filename)
      self.string_field.update()
      
class QtURLField(Qt_WithButtonField, URLField): pass


class QtBoolField(QtField, BoolField, qtwidgets.QCheckBox):
  def __init__(self, gui, master, o, attribute, undo_stack):
    qtwidgets.QCheckBox.__init__(self, "                         ")
    super().__init__(gui, master, o, attribute, undo_stack)
    self.update()
    self.stateChanged.connect(self.validate)
    
  def validate(self, state):
    if not self.updating:
      if   state == 0: self.set_value(False)
      elif state == 2: self.set_value(True)
      elif state == 1: self.setTristate(False)
      
  def update(self):
    self.updating += 1
    try:
      v = self.get_value()
      if v is introsp.NonConsistent:
        self.setTristate(True)
        self.setCheckState(1)
      else:
        self.setTristate(False)
        if v: self.setCheckState(2)
        else: self.setCheckState(0)
    finally: self.updating -= 1

class QtProgressBarField(QtField, ProgressBarField, qtwidgets.QProgressBar):
  def __init__(self, gui, master, o, attribute, undo_stack):
    qtwidgets.QProgressBar.__init__(self)
    super().__init__(gui, master, o, attribute, undo_stack)
    self.setMinimum(0)
    self.setMaximum(100)
    self.update()
    
  def update(self):
    v = self.get_value()
    if v is introsp.NonConsistent: self.pulse()
    else: self.setValue(int(round(100.0 * v)))
    

# class Qt_RangeField(QtField, _RangeField, qtwidgets.QSlider):
#   def __init__(self, gui, master, o, attribute, undo_stack, min, max, incr = 1):
#     qtwidgets.QSlider.__init__(self, qtcore.Qt.Horizontal)
#     self.setRange(min, max)
#     self.setPageStep(incr)
#     self.setTickPosition(qtwidgets.QSlider.TicksAbove)
#     super().__init__(gui, master, o, attribute, undo_stack, min, max, incr)
#     self.update()
#     self.valueChanged.connect(self.validate)
    
#   def validate(self, new_value): self.set_value(new_value)
  
#   def update(self):
#     self.updating += 1
#     value = self.get_value()
#     try:
#       value = int(value)
#       self.setValue(value)
#     except: pass
#     finally: self.updating -= 1

class Qt_RangeField(QtField, _RangeField, qtwidgets.QWidget):
  def __init__(self, gui, master, o, attribute, undo_stack, min, max, incr = 1):
    qtwidgets.QWidget.__init__(self)
    super().__init__(gui, master, o, attribute, undo_stack, min, max, incr)

    self.label = qtwidgets.QLabel()
    
    self.slider = qtwidgets.QSlider(qtcore.Qt.Horizontal)
    self.slider.setRange(min, max)
    self.slider.setPageStep(incr)
    self.slider.setTickPosition(qtwidgets.QSlider.TicksAbove)
    
    layout = qtwidgets.QHBoxLayout()
    layout.addWidget(self.label)
    layout.addWidget(self.slider)
    self.setLayout(layout)
    
    self.update()
    self.slider.valueChanged.connect(self.validate)
    
  def validate(self, new_value):
    self.label.setText(str(new_value))
    self.set_value(new_value)
  
  def update(self):
    self.updating += 1
    value = self.get_value()
    try:
      value = int(value)
      self.slider.setValue(value)
      self.label.setText(str(value))
    except: pass
    finally: self.updating -= 1

    
class Qt_ShortEnumField(QtField, _ShortEnumField, qtwidgets.QComboBox):
  def __init__(self, gui, master, o, attribute, undo_stack, choices, value_2_enum = None, enum_2_value = None):
    qtwidgets.QComboBox.__init__(self)
    super().__init__(gui, master, o, attribute, undo_stack, choices, value_2_enum, enum_2_value)
    self.setSizeAdjustPolicy(qtwidgets.QComboBox.AdjustToMinimumContentsLengthWithIcon)
    for choice in self.choice_keys: self.addItem(choice)
    self.activated.connect(self.validate)
    self.update()
    
  def validate(self, *args):
    i = self.currentIndex()
    if i != -1: self.set_value(self.choices[self.choice_keys[i]])
    
  def update(self):
    self.updating += 1
    try:
      i = self.choice_2_index.get(self.get_value())
      if i is None: self.setCurrentIndex(-1)
      else:         self.setCurrentIndex(i)
    finally: self.updating -= 1
    
class Qt_LongEnumField(QtField, _LongEnumField, qtwidgets.QListWidget):
  #y_flags = qt.AttachOptions.FILL | qt.AttachOptions.EXPAND
  def __init__(self, gui, master, o, attribute, undo_stack, choices, value_2_enum = None, enum_2_value = None):
    qtwidgets.QListWidget.__init__(self)
    super().__init__(gui, master, o, attribute, undo_stack, choices, value_2_enum, enum_2_value)
    for choice in self.choice_keys: self.addItem(choice)
    self.update()
    self.currentItemChanged.connect(self.validate)
    
  def edit(self, *args): # Hack, since both Editobj and Qt define an "edit()" method
    if len(args) == 1: _LongEnumField.edit(self, *args)
    else:              return qtwidgets.QListWidget.edit(self, *args)
    
  def validate(self, current, previous):
    if current:
      i = self.row(current)
      enum = self.choices[self.choice_keys[i]]
      self.set_value(enum)
      
  def update(self):
    self.updating += 1
    try:
      i = self.choice_2_index.get(self.get_value())
      if not i is None: self.setCurrentItem(self.item(i))
    finally: self.updating -= 1

class Qt_EnumListField(QtField, _EnumListField, qtwidgets.QListWidget):
  #y_flags = qt.AttachOptions.FILL | qt.AttachOptions.EXPAND
  def __init__(self, gui, master, o, attribute, undo_stack, choices, value_2_enum = None, enum_2_value = None):
    qtwidgets.QListWidget.__init__(self)
    super().__init__(gui, master, o, attribute, undo_stack, choices, value_2_enum, enum_2_value)
    for choice in self.choice_keys:
      item = qtwidgets.QListWidgetItem(choice, self)
      item.setFlags(item.flags() | qtcore.Qt.ItemIsUserCheckable)
      item.setCheckState(qtcore.Qt.Unchecked)
      
    self.update()
    self.itemChanged.connect(self.on_item_toggled)
    
  def edit(self, *args): # Hack, since both Editobj and Qt define an "edit()" method
    if len(args) == 1: _LongEnumField.edit(self, *args)
    else:              return qtwidgets.QListWidget.edit(self, *args)
    
  def on_item_toggled(self, item):
    if self.updating: return
    values = self.get_value()
    value  = self.choices[self.choice_keys[self.row(item)]]
    if values is introsp.NonConsistent: return # XXX does not support yet edition of multiple object
    if   item.checkState() == qtcore.Qt.Unchecked:
      values.remove(value)
    elif item.checkState() == qtcore.Qt.Checked:
      if isinstance(values, set): values.add   (value)
      else:                       values.append(value)
      
  def update(self):
    self.updating += 1
    try:
      values = self.get_value()
      if values is introsp.NonConsistent:
        for i in range(len(self.choices)): self.item(i).setCheckState(qtcore.Qt.Unchecked)
      else:
        if values: self.indexes = { self.choice_2_index.get(value) for value in values }
        else:      self.indexes = set()
        for i in range(len(self.choices)):
          if i in self.indexes: self.item(i).setCheckState(qtcore.Qt.Checked)
          else:                 self.item(i).setCheckState(qtcore.Qt.Unchecked)
    finally: self.updating -= 1


class QtObjectAttributeField(QtField, ObjectAttributeField, qtwidgets.QFrame):
  def __init__(self, gui, master, o, attribute, undo_stack):
    super().__init__(gui, master, o, attribute, undo_stack)
    qtwidgets.QFrame.__init__(self)
    self.setFrameShadow(qtwidgets.QFrame.Sunken)
    self.setFrameShape(qtwidgets.QFrame.StyledPanel)
    layout = qtwidgets.QHBoxLayout()
    layout.setContentsMargins(3, 3, 3, 3)
    layout.addWidget(self.attribute_pane)
    self.setLayout(layout)
    
class QtObjectSelectorField(QtField, ObjectSelectorField, qtwidgets.QWidget):
  def __init__(self, gui, master, o, attribute, undo_stack):
    qtwidgets.QWidget.__init__(self)
    self.current_addable_values = None
    self.combo  = qtwidgets.QComboBox()
    self.combo.setIconSize(qtcore.QSize(editobj3.editor_qt.SMALL_ICON_SIZE, editobj3.editor_qt.SMALL_ICON_SIZE))
    self.combo.setSizeAdjustPolicy(qtwidgets.QComboBox.AdjustToMinimumContentsLengthWithIcon)
    self.button = qtwidgets.QToolButton()
    self.button.setText(editobj3.TRANSLATOR("Edit..."))
    self.button.setAutoRaise(True)
    self.button.clicked.connect(self.on_click)
    layout = qtwidgets.QHBoxLayout()
    layout.setContentsMargins(0, 0, 0, 0)
    layout.addWidget(self.combo, 1)
    layout.addWidget(self.button, 0)
    self.setLayout(layout)
    super().__init__(gui, master, o, attribute, undo_stack)
    self.combo.activated.connect(self.on_change_object)
    self.destroyed.connect(self.on_destroyed)
    
  def on_destroyed(self):
    super().destroy()
    observe.unobserve(self.get_value(), self._value_listener)
    
  def on_click(self, *args): _edit_from_field(self.get_value(), self, self.undo_stack)
  
  def on_change_object(self, *args):
    self.set_value(self.current_addable_values[self.combo.currentIndex()])
    
  def _item_for(self, obj):
    descr = introsp.description_for_object(obj)
    icon_filename = descr.icon_filename_for(obj)
    if isinstance(icon_filename, str): icon = editobj3.editor_qt.load_small_icon(icon_filename)
    else:                              icon = None
    return icon, descr.label_for(obj)
  
  def store_item_for(self, obj):
    descr = introsp.description_for_object(obj)
    icon_filename = descr.icon_filename_for(obj)
    if isinstance(icon_filename, str): icon = editobj3.editor_qt.load_small_icon(icon_filename)
    else:                              icon = None
    return descr.label_for(obj), icon
  
  def _value_listener(self, obj, type, new, old):
    text, icon = self.store_item_for(obj)
    self.combo.setItemText(self.combo.currentIndex(), text)
    self.combo.setItemIcon(self.combo.currentIndex(), icon)
    
  def update(self):
    self.updating += 1
    try:
      current_addable_values = self.get_addable_values()
      if current_addable_values != self.current_addable_values:
        self.current_addable_values = current_addable_values
        self.combo.clear()
        for o in self.current_addable_values: self.combo.addItem(*self._item_for(o))
      value = self.get_value()
      try:               index = self.current_addable_values.index(value)
      except ValueError: index = -1
      self.combo.setCurrentIndex(index)
    finally: self.updating -= 1
    

class QtObjectListField(QtField, ObjectListField, qtwidgets.QWidget):
  #y_flags = qt.AttachOptions.FILL | qt.AttachOptions.EXPAND
  def __init__(self, gui, master, o, attribute, undo_stack):
    qtwidgets.QWidget.__init__(self)
    super().__init__(gui, master, o, attribute, undo_stack)
    
    layout = editobj3.editor_qt.OverlayLayout()
    layout.addWidget(self.hierarchy_pane)
    layout.addWidget(self.childhood_pane)
    self.setLayout(layout)
    
    # Timer is needed because, when clicking on a childhood_pane's button, the hierarchy_pane is focused out before the click occurs!
    self.timer = qtcore.QTimer()
    self.timer.timeout.connect(self.hide_selection)
    self.timer.setSingleShot(False)
    self.timer.setInterval(50)
    
    # Hack
    self.hierarchy_pane.focusInEvent  = self.hierarchy_focusInEvent
    self.hierarchy_pane.focusOutEvent = self.hierarchy_focusOutEvent
    
  # For updating childhood position
  def showEvent(self, event):
    qtwidgets.QWidget.showEvent(self, event)
    self.layout().invalidate()
    
  def hierarchy_focusInEvent(self, event):
    qtwidgets.QTreeView.focusInEvent(self.hierarchy_pane, event)
    self.timer.stop()
    
  def hierarchy_focusOutEvent(self, event):
    qtwidgets.QTreeView.focusOutEvent(self.hierarchy_pane, event)
    self.timer.start()
    
  def hide_selection(self):
    focus = qtwidgets.QApplication.focusWidget()
    if isinstance(focus, qtwidgets.QScrollArea) or (focus is self.childhood_pane.button_move_up) or (focus is self.childhood_pane.button_move_down) or (focus is self.childhood_pane.button_add) or (focus is self.childhood_pane.button_remove): return
    self.hierarchy_pane.select_node(None)
    self.timer.stop()
    
