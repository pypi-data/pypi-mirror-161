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

from xml.sax.saxutils import escape
import gi
from gi.repository import GObject as gobject, Gdk as gdk, Gtk as gtk, GdkPixbuf as gdkpixbuf

import editobj3.introsp as introsp
from editobj3.editor import *

MENU_LABEL_2_IMAGE = {
  "Open..."        : gtk.STOCK_OPEN,
  "Save"           : gtk.STOCK_SAVE,
  "Save as..."     : gtk.STOCK_SAVE_AS,
  "Close"          : gtk.STOCK_CLOSE,
  "Undo"           : gtk.STOCK_UNDO,
  "Redo"           : gtk.STOCK_REDO,
  "Paste"          : gtk.STOCK_PASTE,
  "Preferences..." : gtk.STOCK_PREFERENCES,
  }

class GtkBaseDialog(BaseDialog):
  def on_response(self, dialog, response):
    if self.on_validate:
      if response == gtk.ResponseType.OK: self.on_validate(self.get_selected_object())
      else:                               self.on_validate(None)
    self.window.destroy()
      
  def build_default_menubar(self):
    self.accel_group = gtk.AccelGroup()
    self.window.add_accel_group(self.accel_group)
    self.current_radio_group = None
    
    self.menubar = gtk.MenuBar()
    self.window.get_child().pack_start(self.menubar, 0, 1, 0)
    
    BaseDialog.build_default_menubar(self)
    
  def add_to_menu(self, menu, has_submenu, label, command = None, arg = None, accel = "", accel_enabled = 1, image = None, type = u"button", pos = -1):
    if isinstance(menu, gtk.MenuItem):
      m = menu.get_submenu()
      if not m:
        m = gtk.Menu()
        menu.set_submenu(m)
      menu = m
    stock = MENU_LABEL_2_IMAGE.get(label)
    if stock: menu_item = gtk.ImageMenuItem.new_from_stock(stock, self.accel_group)
    elif image:
      gtk.stock_add([(label, editobj3.TRANSLATOR(label).replace("_", "__"), gtk.gdk.SHIFT_MASK, 46, "")])
      icon_factory.add(label, gtk.IconSet(image))
      menu_item = gtk.ImageMenuItem(label)
      self.current_radio_group = None
    elif type == "check":
      menu_item = gtk.CheckMenuItem(editobj3.TRANSLATOR(label).replace("_", "__"))
      self.current_radio_group = None
    elif type == "radio":
      menu_item = gtk.RadioMenuItem(self.current_radio_group, editobj3.TRANSLATOR(label).replace("_", "__"))
      self.current_radio_group = menu_item
    else:
      menu_item = gtk.MenuItem(editobj3.TRANSLATOR(label).replace("_", "__"))
      self.current_radio_group = None
    if command:
      if arg: menu_item.connect("activate", command, arg)
      else:   menu_item.connect("activate", command)
    menu.insert(menu_item, pos)
    
    if accel:
      mod = gdk.ModifierType(0)
      if isinstance(accel, int): key = accel
      else:
        if u"C-" in accel: mod |= gdk.ModifierType.CONTROL_MASK
        if u"S-" in accel: mod |= gdk.ModifierType.SHIFT_MASK
        key = ord(accel[-1])
      menu_item.add_accelerator("activate", self.accel_group, key, mod, gtk.AccelFlags.VISIBLE)
      if not accel_enabled:
        menu_item.connect("can-activate-accel", self.can_activate_accel)
    return menu_item
  
  def can_activate_accel(self, widget, signal):
    widget.stop_emission("can-activate-accel")
    return False
    
  def add_separator_to_menu(self, menu, pos = -1):
    menu.get_submenu().insert(gtk.SeparatorMenuItem(), pos)
    self.current_radio_group = None
    
  def set_menu_checked(self, menu, checked): menu.set_active(checked)
  def set_menu_enable (self, menu, enable):  menu.set_sensitive(enable)
  def set_menu_label  (self, menu, label):   menu.get_child().set_text(label)
  
  def on_dialog_closed(self, *args):
    self.window.destroy()
    if self.on_close: self.on_close()
    
  def main(self):
    self.show()
    gtk.main()
  
  def set_default_size(self, w, h): self.window.set_default_size(w, h)
    
  def show(self): self.window.show_all()


class GtkEditorDialog(EditorDialog, GtkBaseDialog):
  def __init__(self, gui = None, master = None, direction = "h", on_validate = None, edit_child_in_self = 1, undo_stack = None, on_close = None, menubar = True):
    if on_validate:
      flags = gtk.DialogFlags.MODAL | gtk.DialogFlags.DESTROY_WITH_PARENT | getattr(gtk.DialogFlags, "USE_HEADER_BAR", 0)
      buttons = (gtk.STOCK_CANCEL, gtk.ResponseType.CANCEL, gtk.STOCK_OK, gtk.ResponseType.OK)
      self.window = gtk.Dialog(None, None, flags, buttons)
      self.window.connect("response", self.on_response)
    else:
      self.window = gtk.Window(gtk.WindowType.TOPLEVEL)
      self.window.connect("delete_event", self.on_dialog_closed)
      self.box    = gtk.VBox()
      self.window.add(self.box)
    self.window.connect("delete_event", self.on_dialog_closed)
    
    super().__init__(gui, master, direction, on_validate, edit_child_in_self, undo_stack, on_close, menubar)
    self.window.get_child().pack_start(self.editor_pane, 1, 1, 0)
    self.window.set_default_size(_screen.width() - 128, _screen.height() - 64)
    
  def edit(self, o):
    EditorDialog.edit(self, o)
    label = self.editor_pane.hierarchy_pane.descr.label_for(o)
    self.window.set_title(label.replace("\n", " ").replace("\t", " "))
    return self
  

class GtkEditorTabbedDialog(EditorTabbedDialog, GtkBaseDialog):
  def __init__(self, gui = None, master = None, direction = "h", on_validate = None, edit_child_in_self = 1, undo_stack = None, on_close = None, menubar = True):
    if on_validate:
      flags = gtk.DialogFlags.MODAL | gtk.DialogFlags.DESTROY_WITH_PARENT | getattr(gtk.DialogFlags, "USE_HEADER_BAR", 0)
      buttons = (gtk.STOCK_CANCEL, gtk.ResponseType.CANCEL, gtk.STOCK_OK, gtk.ResponseType.OK)
      self.window = gtk.Dialog(None, None, flags, buttons)
      self.window.connect("response", self.on_response)
      self.window.show_all()
    else:
      self.window = gtk.Window(gtk.WindowType.TOPLEVEL)
      self.box    = gtk.VBox()
      self.window.add(self.box)
    self.window.connect("delete_event", self.on_dialog_closed)
      
    super().__init__(gui, master, direction, on_validate, edit_child_in_self, undo_stack, on_close, menubar)
    self.notebook = gtk.Notebook()
    self.window.get_child().pack_start(self.notebook, 1, 1, 0)
      
  def add_tab(self, name, label, o = None):
    editor_pane = super().add_tab(name, label, o)
    label = gtk.Label(label)
    label.set_alignment(1.0, 0.5)
    self.notebook.append_page(editor_pane, label)
    return editor_pane
    
  def remove_tab(self, name):
    for i in range(len(self.editor_panes)):
      if self.editor_panes[name] is self.notebook.get_nth_page(i):
        self.notebook.remove_page(i)
        break
    super.remove_tab(name)
    
  def get_current_editor_pane(self): return self.notebook.get_nth_page(self.notebook.get_current_page())
  
  
  
class GtkEditorPane(EditorPane, gtk.Paned):
  def __init__(self, gui, master, edit_child_in_self = 1, undo_stack = None, direction = "h"):
    gtk.Paned.__init__(self)
    if direction == "h": self.set_orientation(gtk.Orientation.HORIZONTAL)
    else:                self.set_orientation(gtk.Orientation.VERTICAL)
    super().__init__(gui, master, edit_child_in_self, undo_stack)
    
    #self.box = gtk.VBox()
    self.box = gtk.Box()
    self.box.set_orientation(gtk.Orientation.VERTICAL)
    self.box.pack_start(self.icon_pane     , 0, 1, 0)
    self.box.pack_start(self.attribute_pane, 0, 1, 0)
    self.scroll1 = gtk.ScrolledWindow()
    self.scroll2 = gtk.ScrolledWindow()
    self.scroll1.set_policy(gtk.PolicyType.AUTOMATIC, gtk.PolicyType.AUTOMATIC)
    self.scroll2.set_policy(gtk.PolicyType.NEVER    , gtk.PolicyType.AUTOMATIC)
    self.scroll1.set_shadow_type(gtk.ShadowType.IN)
    self.scroll1.add(self.hierarchy_pane)
    self.scroll2.add_with_viewport(self.box)
    self.scroll2.get_child().set_shadow_type(gtk.ShadowType.NONE)
    self.hi_box = gtk.Overlay()
    self.hi_box.add(self.scroll1)
    self.hi_box.add_overlay(self.childhood_pane)
    self.childhood_pane.set_property("halign", gtk.Align.END)
    self.childhood_pane.set_property("valign", gtk.Align.START)
    self.childhood_pane.set_margin_top(3)
    self.childhood_pane.set_margin_right(3)
    if direction == "h": self.pack1(self.hi_box , 1, 0)
    else:                self.pack1(self.hi_box , 0, 0)
    self.pack2(self.scroll2, 1, 0)
    
  def edit(self, o):
    EditorPane.edit(self, o)
    self.show_all()
    
  def _set_hierarchy_visible(self, visible):
    if visible:
      if self.get_position() == 0: self.set_position(500)
      self.scroll1.set_size_request(300, 200)
      self.child_set_property(self.hi_box, "shrink", 0)
    else:
      self.scroll1.set_size_request(0, 0)
      self.child_set_property(self.hi_box, "shrink", 1)
      def f(): self.set_position(0)
      gobject.timeout_add(0, f)
      
 
_screen = gdk.Screen()

class GtkAttributePane(AttributePane, gtk.Grid):
  def __init__(self, gui, master, edit_child = None, undo_stack = None):
    gtk.Grid.__init__(self)
    super().__init__(gui, master, edit_child, undo_stack)
    self.set_column_spacing(2)
    self.set_row_spacing(3)
    self.connect("destroy", self._destroyed)
    self.can_expand = 0
    
  def edit(self, o, ignored_attrs = None):
    if self.o is o: return
    self.can_expand = 0
    AttributePane.edit(self, o, ignored_attrs)
    
    if isinstance(self.master, EditorPane):
      if self.can_expand: self.master.box.set_child_packing(self, 1, 1, 0, gtk.PackType.START)
      else:               self.master.box.set_child_packing(self, 0, 1, 0, gtk.PackType.START)
      self.master.box.show_all()
      min_size, natural_size = self.master.box.get_preferred_size()
      if self.master.direction == "h": self.master.scroll2.set_min_content_height(min(natural_size.height, 800, _screen.height() - 128))
      else:                            self.master.scroll2.set_min_content_height(min(natural_size.height, 500, _screen.height() - 128))
    else: self.show_all()
    
  def _delete_all_fields(self):
    for widget in list(self.get_children()): widget.destroy()
    
  def _new_field(self, attribute, field_class, unit, i):
    field = field_class(self.gui, self, self.o, attribute, self.undo_stack)
    label = gtk.Label(attribute.label)
    label.set_alignment(0.0, 0.0)
    label.set_margin_top(5)
    self.attach(label, 0, i, 1, 1)
    self.attach(field, 1, i, 1, 1)
    field.set_hexpand(1)
    if unit:
      unit_label = gtk.Label(unit)
      unit_label.set_alignment(0.0, 0.5)
      self.attach(unit_label, 2, i, 1, 1)
    if field.y_flags & gtk.AttachOptions.EXPAND:
      field.set_vexpand(1)
      self.can_expand = 1
    return field
    

class GtkIconPane(IconPane, gtk.HBox):
  def __init__(self, gui, master):
    gtk.HBox.__init__(self)
    super().__init__(gui, master)
    
    self.image = None
    self.label = gtk.Label()
    self.label.set_line_wrap(1)
    self.label.set_alignment(0.0, 0.6)
    self.label.set_padding(10, 0)
    self.pack_end(self.label, 1, 1, 0)
    self.connect("destroy", self._destroyed)
    
  def _set_icon_filename_label_details(self, icon_filename, label, details):
    if   not icon_filename:
      if self.image:
        self.image.destroy()
        self.image = None
        
    elif isinstance(icon_filename, str):
      if isinstance(self.image, gtk.Fixed):
        self.image.destroy()
        self.image = None
      if not self.image:
        self.image = gtk.Image()
        self.image.set_alignment(0.5, 0.0)
        self.image.set_padding(10, 10)
        self.pack_start(self.image, 0, 1, 0)
        self.image.show_all()
      self.image.set_from_pixbuf(load_big_icon(icon_filename))
      
    else:
      if self.image: self.image.destroy()
      self.image = gtk.Fixed()
      self.image.set_border_width(5)
      x = y = 0
      icon_filename.sort()
      icon_filename.reverse()
      for filename in icon_filename:
        i = gtk.Image()
        i.set_from_pixbuf(load_big_icon(filename))
        self.image.put(i, x, y)
        x += 30
        y += 15
      self.pack_start(self.image, 0, 1, 0)
      self.image.show_all()
      
    if details: self.label.set_markup("<b>%s</b>\n\n%s\n" % (escape(label), escape(details)))
    else:       self.label.set_markup("<b>%s</b>"         %  escape(label))
    self.show_all()
  

class GtkChildhoodPane(ChildhoodPane, gtk.VBox):
  def __init__(self, gui, master, undo_stack = None, restrict_to_attribute = None):
    gtk.VBox.__init__(self)
    super().__init__(gui, master, undo_stack, restrict_to_attribute)
    
    self.button_move_up   = gtk.Button()
    self.button_add       = gtk.Button()
    self.button_remove    = gtk.Button()
    self.button_move_down = gtk.Button()
    self.button_move_up  .set_image(gtk.Image.new_from_stock(gtk.STOCK_GO_UP  , gtk.IconSize.BUTTON))
    self.button_add      .set_image(gtk.Image.new_from_stock(gtk.STOCK_ADD    , gtk.IconSize.BUTTON))
    self.button_remove   .set_image(gtk.Image.new_from_stock(gtk.STOCK_REMOVE , gtk.IconSize.BUTTON))
    self.button_move_down.set_image(gtk.Image.new_from_stock(gtk.STOCK_GO_DOWN, gtk.IconSize.BUTTON))
    self.button_move_up  .connect("clicked", self.on_move_up)
    self.button_add      .connect("clicked", self.on_add)
    self.button_remove   .connect("clicked", self.on_remove)
    self.button_move_down.connect("clicked", self.on_move_down)
    self.pack_start(self.button_move_up  , 0, 1, 0)
    self.pack_start(self.button_add      , 0, 1, 0)
    self.pack_start(self.button_remove   , 0, 1, 0)
    self.pack_start(self.button_move_down, 0, 1, 0)
    self.button_move_up  .set_relief(gtk.ReliefStyle.NONE)
    self.button_add      .set_relief(gtk.ReliefStyle.NONE)
    self.button_remove   .set_relief(gtk.ReliefStyle.NONE)
    self.button_move_down.set_relief(gtk.ReliefStyle.NONE)
    self.set_property("visible", 0)
    self.set_property("no-show-all", 1)
    
  def set_button_visibilities(self, visible1, visible2, visible3, visible4):
    if visible1 or visible2 or visible3 or visible4:
      self.button_move_up  .set_property("visible", visible1)
      self.button_add      .set_property("visible", visible2)
      self.button_remove   .set_property("visible", visible3)
      self.button_move_down.set_property("visible", visible4)
      self.button_move_up  .set_property("no-show-all", not visible1)
      self.button_add      .set_property("no-show-all", not visible2)
      self.button_remove   .set_property("no-show-all", not visible3)
      self.button_move_down.set_property("no-show-all", not visible4)
      self.set_property("visible", 1)
      self.set_property("no-show-all", 0)
      self.show_all()
    else:
      self.set_property("visible", 0)
      self.set_property("no-show-all", 1)
      

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
      if not self.flat_list: self.tree.append(None)
      self.update()
      self.update_children()
      
  def path(self):
    if self.parent: return self.parent.path() + (self.index,)
    if self.flat_list: return ()
    else:              return (0,)
    
  def get_by_path(self, path, i = 0):
    if self.flat_list and not self.parent:
      pass
    else:
      if i == len(path) - 1: return self
      i += 1
    return self.children[path[i]].get_by_path(path, i)
    
  def has_children(self): raise NotImplementedError
  def create_children(self, old_children = None): return []
  
  def expand(self):
    path = self.path()
    if path: self.tree.view.expand_to_path(gtk.TreePath(path))
    
  def expanded(self):
    if not self.children_created:
      self.children_created = True
      self.update_children()
      if self.is_expandable: del self.tree[self.path() + (len(self.children),)]
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
      
      #print()
      #print(old_children, "=>", new_children)
      
      for child in old_children[::-1]:
        if not child in new_children_set: child.destroy()
        
      kept_children = [child for child in new_children if child in old_children_set]
      
      for i in range(len(self.children)): self.children[i].index     = i
      for i in range(len(kept_children)): kept_children[i].new_index = i
      
      if kept_children:
        for child in kept_children:
          if child.new_index == child.index : continue # Swap with itself
          swap_with = self.children[child.new_index]
          #print("  swap", child.path(), "with", swap_with.path())
          self.tree.swap(self.tree.get_iter(child.path()), self.tree.get_iter(swap_with.path()))
          swap_with.index = child.index
          child.index     = child.new_index
          self.children[swap_with.index] = swap_with
          self.children[child    .index] = child
          
        for child in kept_children: del child.new_index
        
      if self.flat_list: iter = None
      else:              iter = self.tree.get_iter(self.path())
      for i in range(len(new_children)):
        new_children[i].index = i
        if not new_children[i] in old_children_set:
          self.children.insert(i, new_children[i])
          self.tree.insert(iter, i)
          
      for child in new_children:
        if not child in old_children_set:
          child.update()
          child.update_children()
          
      self.children = new_children
      
    else:
      if self.flat_list: pass
      else:
        is_expandable = bool(self.has_children())
        if   is_expandable and (not self.is_expandable): self.tree.append(self.tree.get_iter(self.path()))
        elif self.is_expandable and (not is_expandable): del self.tree[self.path() + (0,)]
        self.is_expandable = is_expandable
        
  def destroy(self):
    for child in self.children[::-1]: child.destroy()
    path = self.path()
    if self.parent: self.parent.children.remove(self)
    if path and (self.tree.view.tree is self.tree): # Else, the TreeView is displaying a new tree.
      del self.tree[path]
    

class Gtk_HierarchyNode(HierarchyNode, DynamicNode):
  def update(self):
    icon_filename = self.descr.icon_filename_for(self.o)
    if isinstance(icon_filename, str): pixbuf = load_small_icon(icon_filename)
    else:                              pixbuf = None
    path = self.path()
    if path: self.tree[path] = str(self), pixbuf
    
  def __str__(self):
    if self.attribute and not self.restrict_to_attribute: attr_label = self.attribute.label
    else:                                                 attr_label = ""
    if attr_label: return '''<span size="smaller" weight="ultralight">%s</span> %s''' % (escape(attr_label), escape(self.descr.label_for(self.o)))
    return escape(self.descr.label_for(self.o))
    
    
class GtkHierarchyPane(HierarchyPane, gtk.TreeView):
  Node = Gtk_HierarchyNode
  def __init__(self, gui, master, edit_child, undo_stack = None, restrict_to_attribute = None, flat_list = 0):
    self.tree = gtk.TreeStore(str, gdkpixbuf.Pixbuf)
    self.tree.view = self
    gtk.TreeView.__init__(self, self.tree)
    column = gtk.TreeViewColumn(None)
    
    self.set_headers_visible(0)
    pixbuf_render = gtk.CellRendererPixbuf()
    column.pack_start(pixbuf_render, 0)
    column.add_attribute(pixbuf_render, "pixbuf", 1)
    text_render = gtk.CellRendererText()
    column.pack_start(text_render, 0)
    column.add_attribute(text_render, "markup", 0)
    self.append_column(column)
    
    super().__init__(gui, master, edit_child, undo_stack, restrict_to_attribute, flat_list)
    self.connect("destroy", self._destroyed)
    self.get_selection().set_mode(gtk.SelectionMode.MULTIPLE)
    self.get_selection().connect("changed", self.on_selection_changed)
    self.set_size_request(200, 200)
    self.selected_parent     = None
    self.selected_attribute  = None
    self.selected_node       = None
    self.selected            = None
    self.last_button         = 0
    
    #self.connect("row-expanded"      , self._expanded)
    self.connect("test-expand-row"   , self.on_expanded)
    self.connect("row-collapsed"     , self.on_collapsed)
    self.connect("button_press_event", self.on_button_pressed)
    
  def edit(self, o):
    if o is self.o: return
    
    old_tree = self.tree
    self.tree = gtk.TreeStore(str, gdkpixbuf.Pixbuf)
    self.tree.view = self
    self.set_model(None)
    old_tree.clear()
    
    HierarchyPane.edit(self, o)
    self.root_node.expanded()
    self.set_model(self.tree)
    if self.flat_list:
      self.childhood_pane.edit(None, None, self.o)
    else:
      self.expand_to_path((gtk.TreePath((0,))))
      self.select_node(self.root_node)
      #self.select_object(o)
    self.show_all()
    
  def expand_tree_at_level(self, level): self._expand_tree_at_level(level, (0,))
    
  def _expand_tree_at_level(self, level, path):
    self.expand_to_path(path)
    if len(path) < level:
      for i in range(self.tree.iter_n_children(self.tree[path].iter)):
        self._expand_tree_at_level(level, path + (i,))
        
  def select_node(self, node):
    self.get_selection().unselect_all()
    if node:
      path = node.path()
      if path: self.get_selection().select_path(path)
    elif self.flat_list and self.childhood_pane:
      self.childhood_pane.edit(None, None, self.o)
      
  def on_expanded(self, treeview, iter, path):
    node = self.root_node.get_by_path(path)
    node.expanded()
    self.handler_block_by_func(self.on_expanded)
    self.expand_to_path(path)
    self.handler_unblock_by_func(self.on_expanded)
    return True
    
  def on_collapsed(self, treeview, iter, path):
    node = self.root_node.get_by_path(path)
    node.collapsed()
    
  def on_button_pressed(self, widget, event):
    if event.type == gdk.EventType._2BUTTON_PRESS:
      actions = self.get_actions(self.selected_parent, self.selected_attribute, self.selected)
      for action in actions:
        if action.default:
          #self._action_activated(None, self.selected, action, self.selected_parent)
          self._action_activated(action, self.selected_parent, self.selected_attribute, self.selected)
          break
    else:
      self.last_button      = event.button
      self.last_button_time = event.time
      
  def on_selection_changed(self, *args):
    tree, rows = self.get_selection().get_selected_rows()
    if len(rows) == 0:
      #self.edit_child(None)
      delayed(lambda: self.edit_child(None)) # Delay because focus out event must be received by Field widget BEFORE edditing a new object!
      if self.childhood_pane: self.childhood_pane.edit(None, None, None)
      self.selected_node = None
      return
      
    if len(rows) == 1:
      node = self.selected_node = self.root_node.get_by_path(rows[0])
      if node.parent: self.selected_parent = node.parent.o
      else:           self.selected_parent = None
      self.selected           = node.o
      self.selected_attribute = node.attribute
      
      delayed(lambda: self.edit_child(self.selected, self.get_ignored_attrs([node]))) # Delay because focus out event must be received by Field widget BEFORE edditing a new object!
      
      if self.childhood_pane: self.childhood_pane.edit(self.selected_parent, self.selected_attribute, self.selected)
      
    else:
      nodes = self.selected_node = [self.root_node.get_by_path(row) for row in rows]
      self.selected_parent    = introsp.ObjectPack([(node.parent and node.parent.o) for node in nodes])
      self.selected           = introsp.ObjectPack([node.o for node in nodes])
      self.selected_attribute = [node.attribute for node in nodes]
      
      delayed(lambda: self.edit_child(self.selected, self.get_ignored_attrs(nodes))) # Delay because focus out event must be received by Field widget BEFORE edditing a new object!
      
      if self.childhood_pane: self.childhood_pane.edit(self.selected_parent, self.selected_attribute, self.selected)
      
    if self.last_button == 3:
      self.last_button = 0
      actions = self.get_actions(self.selected_parent, self.selected_attribute, self.selected)
      self.show_action_menu(actions, self.last_button_time)
      
  def on_action_activated(self, event, action): self._action_activated(action, self.selected_parent, self.selected_attribute, self.selected)
  
  def show_action_menu(self, actions, button_time = None):
    self._popup_menu = gtk.Menu() # The menu must be kept in memory, else it does not appear.
    #gtk.MenuItem("Test")
    for action in actions:
      menu_item = gtk.MenuItem(action.label)
      menu_item.connect("activate", self.on_action_activated, action)
      self._popup_menu.append(menu_item)
    self._popup_menu.show_all()
    self._popup_menu.popup(None, None, None, None, 0, button_time or gtk.get_current_event_time())


  
def delayed(f):
  gobject.timeout_add(0, f)
  return False
  
SMALL_ICON_SIZE = 32

_small_icons = {}
_big_icons   = {}

def load_big_icon(filename):
  pixbuf = _big_icons.get(filename)
  if not pixbuf: pixbuf = _big_icons[filename] = gdkpixbuf.Pixbuf.new_from_file(filename)
  return pixbuf

def load_small_icon(filename):
  pixbuf = _small_icons.get(filename)
  if not pixbuf:
    pixbuf = load_big_icon(filename)
    w = pixbuf.get_width()
    h = pixbuf.get_height()
    if (w > SMALL_ICON_SIZE) or (h > SMALL_ICON_SIZE):
      if w > h: pixbuf = pixbuf.scale_simple(SMALL_ICON_SIZE, int(float(SMALL_ICON_SIZE) * h / w), gdkpixbuf.InterpType.BILINEAR)
      else:     pixbuf = pixbuf.scale_simple(int(float(SMALL_ICON_SIZE) * w / h), SMALL_ICON_SIZE, gdkpixbuf.InterpType.BILINEAR)
    _small_icons[filename] = pixbuf
  return pixbuf
