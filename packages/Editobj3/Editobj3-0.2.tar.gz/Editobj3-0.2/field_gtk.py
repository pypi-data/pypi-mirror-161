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

import gi
from gi.repository import GObject as gobject, Gdk as gdk, Gtk as gtk, GdkPixbuf as gdkpixbuf

import editobj3
from editobj3.field import *
from editobj3.field import _WithButtonField, _RangeField, _ShortEnumField, _LongEnumField, _EnumListField

def _edit_from_field(o, widget, undo_stack): # GTK does not like that we show a non-modal dialog box when a modal dialog box is displayed
  p = widget
  while p:
    p = p.get_parent()
    if isinstance(p, gtk.Window) and p.get_modal():
      editobj3.edit(o, undo_stack = undo_stack, on_validate = lambda obj: None)
      return
  editobj3.edit(o, undo_stack = undo_stack)

class GtkField(MultiGUIField):
  y_flags = gtk.AttachOptions.FILL

class GtkHiddenField(GtkField, HiddenField): pass
  
class GtkLabelField(GtkField, LabelField, gtk.Label):
  def __init__(self, gui, master, o, attribute, undo_stack):
    gtk.Label.__init__(self)
    super().__init__(gui, master, o, attribute, undo_stack)
    self.update()
    
  def update(self):
    self.set_text(self.get_value())
    
class GtkEntryField(GtkField, EntryField, gtk.Entry):
  def __init__(self, gui, master, o, attribute, undo_stack):
    gtk.Entry.__init__(self)
    super().__init__(gui, master, o, attribute, undo_stack)
    
    self.update()
    self.connect("focus_out_event", self.validate)
    self.connect("key_press_event", self.validate)
    
  def validate(self, widget, event):
    if (event.type == gdk.EventType.KEY_PRESS) and ((not event.string) or (not event.string in "\r\n")): return
    self.set_value(self.get_text())
    
  def update(self):
    self.updating += 1
    try: self.set_text(self.get_value() or "") # GTK does not accept None as a text
    finally: self.updating -= 1

class GtkTextField(GtkField, TextField, gtk.ScrolledWindow):
  y_flags = gtk.AttachOptions.FILL | gtk.AttachOptions.EXPAND
  def __init__(self, gui, master, o, attribute, undo_stack):
    gtk.ScrolledWindow.__init__(self)
    self.set_policy(gtk.PolicyType.AUTOMATIC, gtk.PolicyType.AUTOMATIC)
    self.set_shadow_type(gtk.ShadowType.IN)
    self.set_size_request(-1, 125)
    self.text = gtk.TextView()
    self.text.set_wrap_mode(gtk.WrapMode.WORD)
    self.text.set_size_request(150, -1)
    self.text.connect("focus_out_event", self.validate)
    self.add(self.text)
    super().__init__(gui, master, o, attribute, undo_stack)
    self.update()
    
  def validate(self, *args):
    buffer = self.text.get_buffer()
    s = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), 1)
    self.set_value(s)
    
  def update(self):
    self.updating += 1
    try:
      value = self.get_value()
      buffer = self.text.get_buffer()
      if buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), 1) != value: buffer.set_text(value)
    finally: self.updating -= 1
    
    
class GtkIntField   (GtkEntryField, IntField   ): pass # XXX no "spin-button" since they don't allow entering e.g. "1 + 2" as an integer !
class GtkFloatField (GtkEntryField, FloatField ): pass
class GtkStringField(GtkEntryField, StringField): pass

class GtkPasswordField(GtkStringField, PasswordField):
  def __init__(self, gui, master, o, attribute, undo_stack):
    GtkStringField.__init__(self, gui, master, o, attribute, undo_stack)
    self.set_visibility(0)


class GtkEntryListField (GtkTextField, EntryListField ): pass
class GtkIntListField   (GtkTextField, IntListField   ): pass
class GtkFloatListField (GtkTextField, FloatListField ): pass
class GtkStringListField(GtkTextField, StringListField): pass
    
class Gtk_WithButtonField(GtkField, _WithButtonField, gtk.HBox):
  def __init__(self, gui, master, o, attribute, undo_stack, field_class = None, button_text = None, on_button = None):
    gtk.HBox.__init__(self)
    super().__init__(gui, master, o, attribute, undo_stack, field_class, button_text, on_button)
    self.pack_start(self.string_field, 1, 1, 0)
    button = gtk.Button(editobj3.TRANSLATOR(self.button_text))
    button.connect("clicked", self.on_button_clicked)
    self.pack_end(button, 0, 1, 0)
  
  def on_button_clicked(self, *args): self.on_button(self.o, self, self.undo_stack)
    
class GtkFilenameField(Gtk_WithButtonField, FilenameField):
  def on_button(self, o, field, undo_stack):
    dialog = gtk.FileChooserDialog(action = gtk.FileChooserAction.SAVE, buttons = (gtk.STOCK_CANCEL, gtk.ResponseType.CANCEL, gtk.STOCK_OK, gtk.ResponseType.OK))
    dialog.set_resizable(1)
    dialog.set_current_name(self.get_value())
    if dialog.run() == gtk.ResponseType.OK:
      filename = dialog.get_filename()
      if filename:
        self.string_field.set_value(filename)
        self.string_field.update()
    dialog.destroy()
    
class GtkDirnameField(Gtk_WithButtonField, DirnameField):
  def on_button(self, o, field, undo_stack):
    dialog = gtk.FileChooserDialog(action = gtk.FileChooserAction.CREATE_FOLDER, buttons = (gtk.STOCK_CANCEL, gtk.ResponseType.CANCEL, gtk.STOCK_OK, gtk.ResponseType.OK))
    dialog.set_resizable(1)
    dialog.set_current_folder(self.get_value())
    if dialog.run() == gtk.ResponseType.OK:
      folder = dialog.get_current_folder()
      if folder:
        self.string_field.set_value(folder)
        self.string_field.update()
    dialog.destroy()
    
class GtkURLField(Gtk_WithButtonField, URLField): pass


class GtkBoolField(GtkField, BoolField, gtk.CheckButton):
  def __init__(self, gui, master, o, attribute, undo_stack):
    gtk.CheckButton.__init__(self)
    self.connect("toggled", self.validate)
    self.connect("clicked", self.clicked)
    super().__init__(gui, master, o, attribute, undo_stack)
    self.update()
    
  def validate(self, *event): self.set_value(self.get_active())
    
  def clicked(self, *event):
    if self.get_inconsistent(): self.set_inconsistent(0)
    
  def update(self):
    self.updating += 1
    try:
      v = self.get_value()
      if v is introsp.NonConsistent: self.set_inconsistent(1)
      else: self.set_active(v)
    finally: self.updating -= 1


class GtkProgressBarField(GtkField, ProgressBarField, gtk.ProgressBar):
  def __init__(self, gui, master, o, attribute, undo_stack):
    gtk.ProgressBar.__init__(self)
    super().__init__(gui, master, o, attribute, undo_stack)
    self.update()
    
  def update(self):
    v = self.get_value()
    if v is introsp.NonConsistent: self.pulse()
    else: self.set_fraction(v)


class Gtk_RangeField(GtkField, _RangeField, gtk.HScale):
  def __init__(self, gui, master, o, attribute, undo_stack, min, max, incr = 1):
    gtk.HScale.__init__(self)
    self.adjustment = gtk.Adjustment(0, min, max, incr)
    self.set_adjustment(self.adjustment)
    self.set_digits(0)
    super().__init__(gui, master, o, attribute, undo_stack, min, max, incr)
    self.connect("value_changed", self.validate)
    
  def validate(self, *args): self.set_value(self.adjustment.get_value())
  
  def update(self):
    self.updating += 1
    try: self.adjustment.set_value(self.get_value())
    finally: self.updating -= 1
    
    
class Gtk_ShortEnumField(GtkField, _ShortEnumField, gtk.ComboBox):
  def __init__(self, gui, master, o, attribute, undo_stack, choices, value_2_enum = None, enum_2_value = None):
    gtk.ComboBox.__init__(self)
    self.liststore = gtk.ListStore(str)
    self.set_model(self.liststore)
    cell = gtk.CellRendererText()
    self.pack_start(cell, 1)
    self.add_attribute(cell, 'text', 0)
    super().__init__(gui, master, o, attribute, undo_stack, choices, value_2_enum, enum_2_value)
    for choice in self.choice_keys: self.liststore.append((choice,))
    self.connect("changed", self.validate)
    self.update()
    
  def validate(self, *args):
    i = self.get_active()
    if i != -1: self.set_value(self.choices[self.choice_keys[i]])
    
  def update(self):
    self.updating += 1
    try:
      i = self.choice_2_index.get(self.get_value())
      if i is None: self.set_active(-1)
      else:         self.set_active(i)
    finally: self.updating -= 1
    
class Gtk_LongEnumField(GtkField, _LongEnumField, gtk.ScrolledWindow):
  y_flags = gtk.AttachOptions.FILL | gtk.AttachOptions.EXPAND
  def __init__(self, gui, master, o, attribute, undo_stack, choices, value_2_enum = None, enum_2_value = None):
    gtk.ScrolledWindow.__init__(self)
    self.set_policy(gtk.PolicyType.AUTOMATIC, gtk.PolicyType.AUTOMATIC)
    self.set_shadow_type(gtk.ShadowType.IN)
    self.set_size_request(-1, 125)
    
    super().__init__(gui, master, o, attribute, undo_stack, choices, value_2_enum, enum_2_value)
    
    self.liststore = gtk.ListStore(str)
    for choice in self.choice_keys: self.liststore.append((choice,))
    renderer = gtk.CellRendererText()
    self.treeview = gtk.TreeView(self.liststore)
    self.treeview.set_headers_visible(0)
    self.treeview.append_column(gtk.TreeViewColumn(None, renderer, text = 0))
    self.add(self.treeview)
    
    self.update()
    self.treeview.get_selection().connect("changed", self.validate)
    
  def validate(self, *args):
    liststore, iter = self.treeview.get_selection().get_selected()
    if iter:
      enum = self.choices[self.choice_keys[int(liststore.get_path(iter)[0])]]
      self.set_value(enum)
      
  def update(self):
    self.updating += 1
    try:
      selection = self.treeview.get_selection()
      selection.unselect_all()
      self.i = self.choice_2_index.get(self.get_value())
      if not self.i is None:
        selection.select_iter(self.liststore.get_iter(self.i))
        self.treeview.scroll_to_cell(self.i)
    finally: self.updating -= 1
    
class Gtk_EnumListField(GtkField, _EnumListField, gtk.ScrolledWindow):
  y_flags = gtk.AttachOptions.FILL | gtk.AttachOptions.EXPAND
  def __init__(self, gui, master, o, attribute, undo_stack, choices, value_2_enum = None, enum_2_value = None):
    gtk.ScrolledWindow.__init__(self)
    self.set_policy(gtk.PolicyType.AUTOMATIC, gtk.PolicyType.AUTOMATIC)
    self.set_shadow_type(gtk.ShadowType.IN)
    self.set_size_request(-1, 125)
    
    super().__init__(gui, master, o, attribute, undo_stack, choices, value_2_enum, enum_2_value)
    self.liststore = gtk.ListStore(bool, str)
    for choice in self.choice_keys: self.liststore.append((False, choice))
    renderer1 = gtk.CellRendererToggle()
    renderer2 = gtk.CellRendererText  ()
    self.treeview = gtk.TreeView(self.liststore)
    self.treeview.set_headers_visible(0)
    self.treeview.append_column(gtk.TreeViewColumn(None, renderer1, active = 0))
    self.treeview.append_column(gtk.TreeViewColumn(None, renderer2, text   = 1))
    self.add(self.treeview)
    
    self.update()
    renderer1.connect("toggled", self.on_cell_toggled, self.liststore)
    
  def on_cell_toggled(self, widget, path, model):
    values = self.get_value()
    value  = self.choices[self.choice_keys[int(path)]]
    if values is introsp.NonConsistent: return # XXX does not support yet edition of multiple object
    if model[path][0]:
      values.remove(value)
      model[path][0] = False
    else:
      if isinstance(values, set): values.add   (value)
      else:                       values.append(value)
      model[path][0] = True
      
  def update(self):
    self.updating += 1
    try:
      values = self.get_value()
      if values is introsp.NonConsistent:
        for i in range(len(self.choices)): self.liststore[i][0] = False
      else:
        if values: self.indexes = { self.choice_2_index.get(value) for value in values }
        else:      self.indexes = set()
        for i in range(len(self.choices)): self.liststore[i][0] = i in self.indexes
    finally: self.updating -= 1

    
class GtkObjectAttributeField(GtkField, ObjectAttributeField, gtk.Frame):
  def __init__(self, gui, master, o, attribute, undo_stack):
    super().__init__(gui, master, o, attribute, undo_stack)
    gtk.Frame.__init__(self)
    self.set_shadow_type(gtk.ShadowType.IN)
    self.attribute_pane.set_property("border-width", 2)
    self.add(self.attribute_pane)
    
class GtkObjectSelectorField(GtkField, ObjectSelectorField, gtk.HBox):
  def __init__(self, gui, master, o, attribute, undo_stack):
    gtk.HBox.__init__(self)
    self.current_addable_values = None
    self.combo = gtk.ComboBox()
    space_render  = gtk.CellRendererText()
    pixbuf_render = gtk.CellRendererPixbuf()
    text_render   = gtk.CellRendererText()
    self.combo.pack_start(space_render , 0)
    self.combo.pack_start(pixbuf_render, 0)
    self.combo.pack_start(text_render  , 0)
    self.combo.add_attribute(space_render , 'text'  , 2)
    self.combo.add_attribute(pixbuf_render, 'pixbuf', 1)
    self.combo.add_attribute(text_render  , 'text'  , 0)
    self.button = gtk.Button(editobj3.TRANSLATOR("Edit..."))
    self.button.connect("clicked", self.on_click)
    self.pack_start(self.combo , 1, 1, 0)
    self.pack_end  (self.button, 0, 1, 0)
    
    super().__init__(gui, master, o, attribute, undo_stack)
    
    self.combo.connect("changed", self.on_change_object)
    
  def destroy(self):
    super().destroy()
    observe.unobserve(self.get_value(), self._value_listener)
    
  def on_click(self, *args): _edit_from_field(self.get_value(), self, self.undo_stack)
  
  def on_change_object(self, *args):
    self.set_value(self.current_addable_values[self.combo.get_active()])
  
  def store_item_for(self, obj):
    descr = introsp.description_for_object(obj)
    icon_filename = descr.icon_filename_for(obj)
    if isinstance(icon_filename, str): pixbuf = editobj3.editor_gtk.load_small_icon(icon_filename)
    else:                              pixbuf = None
    return (descr.label_for(obj), pixbuf, " ")
    
  def _value_listener(self, obj, type, new, old):
    self.liststore[self.combo.get_active()] = self.store_item_for(obj)
    
  def update(self):
    self.updating += 1
    try:
      current_addable_values = self.get_addable_values()
      if current_addable_values != self.current_addable_values:
        self.current_addable_values = current_addable_values
        self.liststore = gtk.ListStore(str, gdkpixbuf.Pixbuf, str)
        for i in self.current_addable_values: self.liststore.append(self.store_item_for(i))
        
        self.combo.set_model(self.liststore)
      value = self.get_value()
      self.combo.set_active(self.current_addable_values.index(value))
    finally: self.updating -= 1
    

class GtkObjectListField(GtkField, ObjectListField, gtk.Overlay):
  y_flags = gtk.AttachOptions.FILL | gtk.AttachOptions.EXPAND
  def __init__(self, gui, master, o, attribute, undo_stack):
    gtk.Overlay.__init__(self)
    super().__init__(gui, master, o, attribute, undo_stack)
    self.scroll = gtk.ScrolledWindow()
    self.scroll.set_min_content_height(136) # Required for childhood pane
    self.scroll.set_policy(gtk.PolicyType.AUTOMATIC, gtk.PolicyType.AUTOMATIC)
    self.scroll.set_shadow_type(gtk.ShadowType.IN)
    self.scroll.add(self.hierarchy_pane)
    self.add(self.scroll)
    self.add_overlay(self.childhood_pane)
    self.childhood_pane.set_property("halign", gtk.Align.END)
    self.childhood_pane.set_property("valign", gtk.Align.START)
    self.childhood_pane.set_margin_top(3)
    self.childhood_pane.set_margin_right(3)
    self.hierarchy_pane.connect("focus_out_event", self.on_focus_out)
    
  def on_focus_out(self, *args):
    self.timer = gobject.timeout_add(200, self.hide_selection)
  
  def hide_selection(self):
    try:
      if self.childhood_pane.button_move_up.has_focus() or self.childhood_pane.button_move_down.has_focus() or self.childhood_pane.button_add.has_focus() or self.childhood_pane.button_remove.has_focus():
        return True
      else:
        self.hierarchy_pane.select_node(None)
        return False
    except: return False
    

#class GtkHierarchyAndObjectAttributeField(GtkObjectAttributeField, HierarchyAndObjectAttributeField): pass
#class GtkHierarchyAndObjectSelectorField(GtkObjectSelectorField, HierarchyAndObjectSelectorField): pass
#class GtkHierarchyAndObjectListField(GtkObjectListField, HierarchyAndObjectListField): pass
