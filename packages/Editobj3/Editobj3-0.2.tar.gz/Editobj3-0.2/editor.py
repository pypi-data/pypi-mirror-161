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

"""editobj3.editor -- The main widget for object edition 

"""

import locale
import editobj3, editobj3.introsp as introsp, editobj3.observe as observe, editobj3.undoredo as undoredo, editobj3.field
from editobj3.introsp import Inexistent


class PaneRepartitor(object):
  def is_displayed_in_hierarchy_pane(self, attribute, o, field_class = None): return False
  def is_displayed_in_attribute_pane(self, attribute, o, field_class = None): return True


class MultiGUIEditor(editobj3.field.MultiGUIWidget):
  _Gtk_MODULE    = "editobj3.editor_gtk"
  _Qt_MODULE     = "editobj3.editor_qt"
  _HTML_MODULE   = "editobj3.editor_html"

class BaseDialog(object):
  def build_default_menubar(self):
    self.file_menu = self.add_to_menu(self.menubar  , 1, u"File")
    self.close_menu= self.add_to_menu(self.file_menu, 0, u"Close", self.close_dialog)
    self.edit_menu = self.add_to_menu(self.menubar  , 1, u"Edit" , self.on_edit_menu)
    self.undo_menu = self.add_to_menu(self.edit_menu, 0, u"Undo" , self.on_undo, accel = u"C-Z")
    self.redo_menu = self.add_to_menu(self.edit_menu, 0, u"Redo" , self.on_redo, accel = u"C-Y")
    
  def add_to_menu(self, menu, has_submenu, label, command = None, arg = None, accel = "", accel_enabled = 1, image = None, type = u"button", pos = -1): raise NotImplementedError
  def add_separator_to_menu(self, menu, pos = -1): raise NotImplementedError
  
  def set_menu_checked(self, menu, checked): raise NotImplementedError
  def set_menu_enable (self, menu, enable):  raise NotImplementedError
  def set_menu_label  (self, menu, label):   raise NotImplementedError
  
  def on_edit_menu(self, *args):
    undo = self.undo_stack.can_undo()
    redo = self.undo_stack.can_redo()
    if undo: self.set_menu_enable(self.undo_menu, 1); self.set_menu_label(self.undo_menu, "%s %s" % (editobj3.TRANSLATOR(u"Undo"), undo.name))
    else:    self.set_menu_enable(self.undo_menu, 0); self.set_menu_label(self.undo_menu,            editobj3.TRANSLATOR(u"Undo"))
    if redo: self.set_menu_enable(self.redo_menu, 1); self.set_menu_label(self.redo_menu, "%s %s" % (editobj3.TRANSLATOR(u"Redo"), redo.name))
    else:    self.set_menu_enable(self.redo_menu, 0); self.set_menu_label(self.redo_menu,            editobj3.TRANSLATOR(u"Redo"))
    
  def on_undo(self, *args):
    if self.undo_stack.can_undo(): self.undo_stack.undo()
  def on_redo(self, *args):
    if self.undo_stack.can_redo(): self.undo_stack.redo()
    
  def close_dialog    (self): self.on_dialog_closed()
  def on_dialog_closed(self, *args): raise NotImplementedError
  def set_default_size(self, w, h):  raise NotImplementedError
    
  def show(self): raise NotImplementedError
  def main(self): raise NotImplementedError
  


class EditorDialog(MultiGUIEditor):
  def __init__(self, gui = None, master = None, direction = "h", on_validate = None, edit_child_in_self = 1, undo_stack = None, on_close = None, menubar = True):
    self.gui         = gui or editobj3.GUI
    self.on_validate = on_validate
    self.on_close    = on_close
    self.undo_stack  = undo_stack or undoredo.stack
    self.editor_pane = EditorPane(gui, self, edit_child_in_self, self.undo_stack, direction)
    if menubar: self.build_default_menubar()
    
  def edit      (self, o): return self.editor_pane.edit      (o)
  def edit_child(self, o): return self.editor_pane.edit_child(o)
  def get_selected_object(self): return self.editor_pane.attribute_pane.o

class EditorTabbedDialog(MultiGUIEditor):
  def __init__(self, gui, master = None, direction = "h", on_validate = None, edit_child_in_self = 1, undo_stack = None, on_close = None, menubar = True):
    self.gui                = gui or editobj3.GUI
    self.on_validate        = on_validate
    self.on_close           = on_close
    self.undo_stack         = undo_stack or undoredo.stack
    self.direction          = direction
    self.edit_child_in_self = edit_child_in_self
    self.editor_panes       = {}
    self.editor_pane        = EditorPane(gui, self, edit_child_in_self, self.undo_stack, direction)
    if menubar: self.build_default_menubar()
    
  def add_tab(self, name, label, o = None):
    self.editor_panes[name] = editor_pane = EditorPane(self.gui, self, self.edit_child_in_self, self.undo_stack, self.direction)
    if not o is None: editor_pane.edit(o)
    return editor_pane
  
  def show_tab(self, editor_pane):
    if editor_pane.func:
      o = editor_pane.func()
      editor_pane.edit(o)
      
  def remove_tab(self, name): del self.editor_panes[name]
  def get_current_editor_pane(self): raise NotImplementedError
  def get_selected_object(self): return self.get_current_editor_pane().o


class EditorPane(MultiGUIEditor):
  def __init__(self, gui, master, edit_child_in_self = 1, undo_stack = None, direction = "h"):
    undo_stack = undo_stack or undoredo.stack
    self.gui                = gui
    self.master             = master
    self.direction          = direction
    self.edit_child_in_self = edit_child_in_self
    self.childhood_pane     = ChildhoodPane(gui, self, undo_stack)
    self.hierarchy_pane     = HierarchyPane(gui, self, self.edit_child, undo_stack)
    self.attribute_pane     = AttributePane(gui, self, self.edit_child, undo_stack)
    self.attribute_pane.pane_repartitor = self.hierarchy_pane
    self.icon_pane          = IconPane     (gui, self)
    self.hierarchy_pane.set_childhood_pane(self.childhood_pane)
    
  def set_pane_repartitor(self, pane_repartitor):
    self.hierarchy_pane.pane_repartitor = self.attribute_pane.pane_repartitor = pane_repartitor
    
  def edit(self, o):
    self.hierarchy_pane.edit(o)
    self.icon_pane     .edit(o)
    self.attribute_pane.edit(o)
    if self.hierarchy_pane.root_node and self.hierarchy_pane.root_node.can_have_children(): self._set_hierarchy_visible(1)
    else:                                                                                   self._set_hierarchy_visible(0)
    
  def edit_child(self, o, ignored_attrs = None):
    self.on_edit_child(o)
    if self.edit_child_in_self:
      self.icon_pane     .edit(o)
      self.attribute_pane.edit(o, ignored_attrs)
      
  def on_edit_child(self, o): pass
  def _set_hierarchy_visible(self, visible): pass
  

class AttributePane(MultiGUIEditor, PaneRepartitor):
  def __init__(self, gui, master, edit_child = None, undo_stack = None):
    self.gui              = gui
    self.master           = master
    self.undo_stack       = undo_stack or undoredo.stack
    self.o                = None
    self.attributes       = []
    self.attr_2_attribute = {}
    self.ignored_attrs    = set()
    self.pane_repartitor  = self
    
    if edit_child: self.edit_child = edit_child
    
  def _re_edit(self): self.edit(self.o)
  
  def _listener(self, o, type, new, old):
    if   type == "__class__": self.edit(None); self.edit(o)
    
    elif type is object:
      diffs = observe.diffdict(new, old, Inexistent)
      for attr, new_val, old_val in diffs:
        if (old_val is Inexistent) or (new_val is Inexistent):
          self._re_edit()
          return
        
      need_updates = { attr for attr, new_val, old_val in diffs }
      for attribute in self.property_attributes: need_updates.add(attribute.name)
      
      for attr in need_updates:
        field = self.fields.get(attr)
        if field: field.update()
        
  def _listener2(self, o, diffs):
    from owlready2 import IRIS
    diffs2 = []
    for attr, new, old in diffs:
      pred = IRIS.get(attr)
      if pred: diffs2.append((pred.python_name, new, old))
      else:    diffs2.append((attr, new, old))
    diffs = diffs2
   
    for attr, new, old in diffs:
      if (not attr in self.attr_2_attribute) and (old == []):
        self._re_edit()
        return
      
    need_updates = { attr for attr, new_val, old_val in diffs }
    need_updates.update(attribute.name for attribute in self.property_attributes)
    need_updates.update(attribute.name for attribute in self.descr.property_attributes_of(self.o))
    
    for attr in need_updates:
      field = self.fields.get(attr)
      if field: field.update()
      
  def _destroyed(self, *args): observe.unobserve(self.o, self._listener)

  def edit(self, o, ignored_attrs = None):
    if not self.o is None:
      if self.descr.is_owl_entity:
        import owlready2.observe
        owlready2.observe.unobserve(self.o, owlready2.observe.CollapsedListener(self._listener2))
      else:
        observe.unobserve(self.o, self._listener)
        
    self.descr = introsp.description_for_object(o)
    
    if   ignored_attrs:      self.ignored_attrs = ignored_attrs
    elif self.ignored_attrs: self.ignored_attrs = set()
    
    if o is None:
      attributes = []
    else:
      if hasattr(o, "__edited__"): o.__edited__(self)
      attributes = [attribute for attribute in self.descr.attributes_of(o) if not attribute.name in self.ignored_attrs]
      
    if o and self.o and (self.attributes == attributes):
      self.o = o
      self.property_attributes = self.descr.property_attributes_of(o)
      
      if not o is None:
        for field in self.fields.values(): field.edit(o)
        
    else:
      if not self.o is None:
        self._delete_all_fields()
        
      self.o                   = o
      self.property_attributes = self.descr.property_attributes_of(o)
      self.attributes          = attributes
      self.attr_2_attribute    = { attribute.name : attribute for attribute in attributes }
      
      if not o is None:
        self._set_nb_fields(len(attributes))
        i = 0
        self.fields = {}
        for attribute in attributes:
          field_class = attribute.field_class_for(o)
          if field_class is editobj3.field.HiddenField: continue
          if not self.pane_repartitor.is_displayed_in_attribute_pane(attribute, o, field_class): continue
          self.fields[attribute.name] = self._new_field(attribute, field_class, attribute.unit_for(o), i)
          i += 1
          
    if not o is None:
      if self.descr.is_owl_entity:
        import owlready2.observe
        owlready2.observe.observe(self.o, owlready2.observe.CollapsedListener(self._listener2))
      else:
        observe.observe(self.o, self._listener)
        
  edit_child = edit
  
  def _delete_all_fields(self): pass
  def _set_nb_fields(self, nb): pass
  def _new_field(self, attribute, field_class, unit, i): pass


class IconPane(MultiGUIEditor):
  def __init__(self, gui, master):
    self.master         = master
    self.o              = None
    self.descr          = None
    
  def edit(self, o):
    if o is self.o: return
    if not self.o is None:
      if self.descr.is_owl_entity:
        import owlready2.observe
        owlready2.observe.unobserve(self.o, owlready2.observe.CollapsedListener(self._listener))
      else:
        observe.unobserve(self.o, self._listener)
        
    self.o     = o
    self.descr = introsp.description_for_object(o)
    
    if hasattr(o, "__edited__"): o.__edited__(self)
    
    if not o is None:
      self._update()
      if self.descr.is_owl_entity:
        import owlready2.observe
        owlready2.observe.observe(self.o, owlready2.observe.CollapsedListener(self._listener))
      else:
        observe.observe(self.o, self._listener)
    else: self._set_icon_filename_label_details("", "", "")
    
  def _listener(self, o, type = None, new = None, old = None): self._update()
  
  def _update(self):
    self._set_icon_filename_label_details(self.descr.icon_filename_for(self.o), self.descr.label_for(self.o), self.descr.details_for(self.o))
    
  def _set_icon_filename_label_details(self, icon_filename, label, details): pass
  
  def _destroyed(self, *args):
    if self.descr.is_owl_entity:
      import owlready2.observe
      owlready2.observe.unobserve(self.o, owlready2.observe.CollapsedListener(self._listener))
    else:
      observe.unobserve(self.o, self._listener)
  

def _not_empty(g):
  try: g.__next__()
  except StopIteration: return 0
  return 1
  

class ChildhoodPane(MultiGUIEditor):
  def __init__(self, gui, master, undo_stack = None, restrict_to_attribute = None):
    self.undo_stack            = undo_stack or undoredo.stack
    self.restrict_to_attribute = restrict_to_attribute
    self.hierarchy_pane        = None
    self.nodes                 = []
    self.master                = master
    
  def edit(self, parent, attribute, o):
    self.parent_o  = parent
    self.attribute = attribute
    self.o         = o
    
    can_reorder = can_remove = can_add = False
    if parent is o: # ObjectListField / flat list => edit the hidden "root" element
      if attribute:
        if isinstance(o, introsp.ObjectPack):
          for i in range(len(o.objects)):
            if attribute[i]:
              if attribute[i].can_add_to     (parent.objects[i]) and attribute[i].addable_values_to(parent.objects[i]): can_add  = True
        else:
          can_add     = attribute.can_add_to(parent) and attribute.addable_values_to(parent)
          
    else:
      if attribute:
        if isinstance(o, introsp.ObjectPack):
          for i in range(len(o.objects)):
            if attribute[i]:
              if attribute[i].can_reorder    (parent.objects[i]): can_reorder = True
              if attribute[i].can_remove_from(parent.objects[i]): can_remove  = True
              if attribute[i].can_add_to     (parent.objects[i]) and attribute[i].addable_values_to(parent.objects[i]): can_add  = True
        else:
          can_reorder = attribute.can_reorder(parent)
          can_remove  = attribute.can_remove_from(parent)
          can_add     = attribute.can_add_to(parent) and attribute.addable_values_to(parent)
    if (not can_add) and not attribute:
      for o_attribute in introsp.description_for_object(o).attributes_of(o):
        if (o_attribute.can_add_to(o) and o_attribute.addable_values_to(o)):
          can_add = True
          break
    self.set_button_visibilities(can_reorder, can_add, can_remove, can_reorder)
    
  def set_button_visibilities(self, visible1, visible2, visible3, visible4): pass
  
  def get_add_actions(self):
    if self.restrict_to_attribute:
      return [action
              for action in introsp.description_for_object(self.o).actions_for(self.parent_o, self.attribute, self.o)
              if isinstance(action, introsp.AddAction) and action.attribute == self.restrict_to_attribute]
    else:
      return [action
              for action in introsp.description_for_object(self.o).actions_for(self.parent_o, self.attribute, self.o)
              if self.hierarchy_pane.filter_add_action(action, self.parent_o, self.o, only_add = True)]
      r = []
      for action in introsp.description_for_object(self.o).actions_for(self.parent_o, self.attribute, self.o):
        if isinstance(action, introsp.AddAction):
          if isinstance(action, introsp.ActionOnAChild):
            if self.hierarchy_pane.pane_repartitor.is_displayed_in_hierarchy_pane(action.attribute, self.parent_o):
              r.append(action)
          else:
            if self.hierarchy_pane.pane_repartitor.is_displayed_in_hierarchy_pane(action.attribute, self.o):
              r.append(action)
      return r
      
  def on_add(self, *args):
    add_actions = self.get_add_actions()
    if   len(add_actions) == 0: return
    elif len(add_actions) == 1: self.hierarchy_pane._action_activated(add_actions[0], self.parent_o, self.attribute, self.o)
    else:                       self.hierarchy_pane.show_action_menu(add_actions)
    
  def on_remove(self, *args):
    introsp.description_for_object(self.parent_o).do_action(introsp._REMOVE_ACTION, self.undo_stack, self.hierarchy_pane.get_editor(), self.parent_o, self.attribute, self.o)
    
  def on_move_up(self, *args):
    introsp.description_for_object(self.parent_o).do_action(introsp._MOVE_UP_ACTION, self.undo_stack, self.hierarchy_pane.get_editor(), self.parent_o, self.attribute, self.o)
    
  def on_move_down(self, *args):
    introsp.description_for_object(self.parent_o).do_action(introsp._MOVE_DOWN_ACTION, self.undo_stack, self.hierarchy_pane.get_editor(), self.parent_o, self.attribute, self.o)

    
  
class HierarchyPane(MultiGUIEditor, PaneRepartitor):
  Node = None
  def __init__(self, gui, master, edit_child, undo_stack = None, restrict_to_attribute = None, flat_list = False):
    self.gui                      = gui
    self.master                   = master
    self.edit_child               = edit_child
    self.o                        = None
    self.root_node                = None
    self.undo_stack               = undo_stack or undoredo.stack
    self.childhood_pane           = None
    self.childhood_pane_parent    = None
    self.childhood_pane_attribute = None
    self.restrict_to_attribute    = restrict_to_attribute
    self.flat_list                = flat_list
    self.pane_repartitor          = self
    
  def is_displayed_in_hierarchy_pane(self, attribute, o, field_class = None):
    if not field_class: field_class = attribute.field_class_for(o)
    return field_class.display_in_hierarchy_pane
    
  def is_displayed_in_attribute_pane(self, attribute, o, field_class = None):
    if not field_class: field_class = attribute.field_class_for(o)
    return field_class.display_in_attribute_pane
    
  def set_childhood_pane(self, childhood_pane, parent = None, attribute = None):
    self.childhood_pane           = childhood_pane
    self.childhood_pane_parent    = parent
    self.childhood_pane_attribute = attribute
    self.childhood_pane.hierarchy_pane = self
    
  def _destroyed(self, *args):
    if self.root_node: self.root_node.destroy()
    
  def expand_object(self, o):
    node = self.root_node.node_for_object(o)
    if node: node.expand()
    
  def select_object(self, o):
    if isinstance(o, introsp.ObjectPack): self.select_node(self.root_node.node_for_object(o.objects[0]))
    else:                                 self.select_node(self.root_node.node_for_object(o))
    
  def edit(self, o):
    if o is self.o: return
    
    if self.root_node: self.root_node.destroy()
    
    self.o         = o
    self.descr     = introsp.description_for_object(o)
    self.root_node = self.Node(self, self.tree, None, o, self.restrict_to_attribute, self.flat_list)
    
    if self.childhood_pane: self.childhood_pane.edit(self.childhood_pane_parent, self.childhood_pane_attribute, o)
    
  def get_actions(self, parent_o, attribute, o):
    return [action for action in introsp.description_for_object(o).actions_for(parent_o, attribute, o)
            if self.filter_add_action(action, parent_o, o, only_add = False)]
    
  def filter_add_action(self, action, parent_o, o, only_add = False):
    if isinstance(action, introsp.AddAction):
      if isinstance(action, introsp.ActionOnAChild):
        if self.pane_repartitor.is_displayed_in_hierarchy_pane(action.attribute, parent_o): return True
      else:
        if self.pane_repartitor.is_displayed_in_hierarchy_pane(action.attribute, o): return True
    else: return not only_add
    
  def get_editor(self):
    if isinstance(self.master, EditorPane):
      if isinstance(self.master.master, EditorDialog): return self.master.master
      else:                                            return self.master
    return self
    
  def _action_activated(self, action, parent, attribute, o):
    if isinstance(action, introsp.AddAction):
      def callback(new_child):
        if (not new_child is None) and self.selected_node:
          if not isinstance(action, introsp.ActionOnAChild):
            self.selected_node.expand()
            for child_node in self.selected_node.children:
              if child_node.o is new_child: self.select_node(child_node)
          else:
            for child_node in self.selected_node.parent.children:
              if child_node.o is new_child: self.select_node(child_node)
      extra = [callback]
    else: extra = []
    if isinstance(action, introsp.ActionOnAChild):
      r = introsp.description_for_object(parent).do_action(action, self.undo_stack, self.get_editor(), parent, attribute, o, *extra)
    else:
      r = introsp.description_for_object(o     ).do_action(action, self.undo_stack, self.get_editor(), o, *extra)
      
          
  def show_action_menu(self, actions): pass
  
  def get_ignored_attrs(self, nodes): return { node.attribute.inverse_attr  for node in nodes  if node.parent and node.attribute }


  
  
def _ordered(x):
  if   isinstance(x, set      ): return list (x)
  elif isinstance(x, frozenset): return tuple(x)
  elif isinstance(x, dict     ): return list (x.values())
  return x
  
class HierarchyNode(object):
  def __init__(self, hierarchy_pane, parent_node, attribute, o, restrict_to_attribute, flat_list):
    self.hierarchy_pane        = hierarchy_pane
    self.descr                 = introsp.description_for_object(o)
    self.attribute             = attribute
    self.o                     = o
    self.o_has_any_children    = 0
    self.o_has_children        = {}
    self.o_children_getter     = None
    self.o_children            = None
    self.observeds             = []
    self.restrict_to_attribute = restrict_to_attribute
    self.flat_list             = flat_list
    
    if attribute: self.inverse_attr = attribute.inverse_attr
    else:         self.inverse_attr = None
    
    self._observe(self.o)
    
    self.update_hierarchy_attributes()
    for attribute, star in self.hierarchy_attributes: self.update_has_children_for_attribute(attribute, star)
    
    super(HierarchyNode, self).__init__(parent_node)
    
  def _observe(self, x):
    if self.descr.is_owl_entity:
      import owlready2.observe
      owlready2.observe.observe(x, owlready2.observe.CollapsedListener(self._listener2))
    else:
      observe.observe(x, self._listener)
    self.observeds.append(x)
    
  def _unobserve(self, x):
    if self.descr.is_owl_entity:
      import owlready2.observe
      owlready2.observe.unobserve(x, owlready2.observe.CollapsedListener(self._listener2))
    else:
      observe.unobserve(x, self._listener)
    self.observeds.remove(x)
    
  def can_have_children(self): return bool(self.hierarchy_attributes)
  
  def has_children(self): return self.o_has_any_children
  
  def update_hierarchy_attributes(self):
    if   self.flat_list and self.attribute: self.hierarchy_attributes = []
    elif self.restrict_to_attribute:
      attribute   = self.descr._get_attribute(self.restrict_to_attribute.name)
      field_class = attribute.field_class_for(self.o)
      self.hierarchy_attributes = [(attribute, field_class.multiple_object_field)]
    else:
      self.hierarchy_attributes = []
      for attribute in self.descr.attributes_of(self.o):
        if attribute.name == self.inverse_attr: continue
        field_class = attribute.field_class_for(self.o, dont_get_value = True)
        if self.hierarchy_pane.pane_repartitor.is_displayed_in_hierarchy_pane(attribute, self.o, field_class):
          self.hierarchy_attributes.append((attribute, field_class.multiple_object_field))
    
  def update_has_children_for_attribute(self, attribute, star):
    new_has_children = attribute.has_item_for(self.o)
    
    if not new_has_children is self.o_has_children.get(attribute, Inexistent):
      if attribute in self.o_has_children:
        old_has_children = self.o_has_children[attribute]
        if (isinstance(old_has_children, list) or isinstance(old_has_children, set) or isinstance(old_has_children, dict)): self._unobserve(old_has_children)
      self.o_has_children[attribute] = new_has_children
      if (isinstance(new_has_children, list) or isinstance(new_has_children, set) or isinstance(new_has_children, dict)): self._observe(new_has_children)
    if new_has_children: self.o_has_any_children = True
    else:
      for has_children in self.o_has_children.values():
        if has_children: self.o_has_any_children = True; break
      else: self.o_has_any_children = False
      
  def update_children_for_attribute(self, attribute, star):
    new_o_children = attribute.get_value_for(self.o)
    if (new_o_children is None) or (star and (len(new_o_children) == 0)): self.o_has_children[attribute] = False
    else:                                                                 self.o_has_children[attribute] = True
    if not new_o_children is self.o_children.get(attribute, Inexistent):
      if attribute in self.o_children: self._unobserve(self.o_children[attribute])
      self.o_children[attribute] = new_o_children
      self._observe(new_o_children)
      
  def create_children(self, old_children = ()):
    if not self.o_has_any_children: return []
    
    if self.o_children is None:
      self.o_children = {}
      for has_children in self.o_has_children.values():
        if (isinstance(has_children, list) or isinstance(has_children, set) or isinstance(has_children, dict)): self._unobserve(has_children)
      for attribute, star in self.hierarchy_attributes: self.update_children_for_attribute(attribute, star)
      
    old = { (child.attribute, id(child.o)) : child for child in old_children }
    children = []
    
    for attribute, star in self.hierarchy_attributes:
      if self.o_has_children[attribute]:
        if star:
          for o in self.o_children[attribute]:
            children.append(old.get((attribute, id(o))) or self.__class__(self.hierarchy_pane, self, attribute, o, self.restrict_to_attribute, self.flat_list))
        else:
          o = self.o_children[attribute]
          children.append(old.get((attribute, id(o))) or self.__class__(self.hierarchy_pane, self, attribute, o, self.restrict_to_attribute, self.flat_list))
          
    return children
    
  def _listener(self, o, type, new, old):
    self.update()
    if   (type is list) or (type is set) or (type is dict):
      if self.o_children is None:
        for attribute, star in self.hierarchy_attributes:
          if self.o_has_children[attribute] is o: self.update_has_children_for_attribute(attribute, star)
          
      else:
        for attribute, star in self.hierarchy_attributes:
          if o is attribute.get_value_for(self.o):
            self.update_children_for_attribute(attribute, star)
          
      self.update_children()
      
    elif type is object:
      self.update_hierarchy_attributes()
      
      changed_attrs = { attr for attr, new_value, old_value in observe.diffdict(new, old, Inexistent) }
      need_update   = 0
      if self.o_children is None:
        for attribute, star in self.hierarchy_attributes:
          if attribute.name in changed_attrs: self.update_has_children_for_attribute(attribute, star); need_update = 1
      else:
        for attribute, star in self.hierarchy_attributes:
          if attribute.name in changed_attrs: self.update_children_for_attribute(attribute, star); need_update = 1
          
      if need_update: self.update_children()
      
    elif type == "__class__":
      self.descr = introsp.description_for_object(self.o)
      self.update_hierarchy_attributes()
      if self.o_children is None:
        for attribute, star in self.hierarchy_attributes: self.update_has_children_for_attribute(attribute, star)
      else:
        for attribute, star in self.hierarchy_attributes: self.update_children_for_attribute(attribute, star)
        self.update_children()
        
  def _listener2(self, o, diffs):
    from owlready2 import IRIS
    
    self.update()
    
    changed_attrs = set()
    for attr, new_value, old_value in diffs:
      pred = IRIS.get(attr)
      if pred: changed_attrs.add(pred.python_name)
      else:    changed_attrs.add(attr)
    changed_attrs.update(attribute.name for attribute in self.descr.property_attributes_of(self.o))
    
    if ("http://www.w3.org/1999/02/22-rdf-syntax-ns#type" in changed_attrs):
      self.descr = introsp.description_for_object(self.o)
      self.update_hierarchy_attributes()
      if self.o_children is None:
        for attribute, star in self.hierarchy_attributes: self.update_has_children_for_attribute(attribute, star)
      else:
        for attribute, star in self.hierarchy_attributes: self.update_children_for_attribute(attribute, star)
        self.update_children()
        
    else:
      self.descr = introsp.description_for_object(self.o)
      self.update_hierarchy_attributes()
      
      need_update   = 0
      if self.o_children is None:
        for attribute, star in self.hierarchy_attributes:
          if attribute.name in changed_attrs: self.update_has_children_for_attribute(attribute, star); need_update = 1
      else:
        for attribute, star in self.hierarchy_attributes:
          if attribute.name in changed_attrs: self.update_children_for_attribute(attribute, star); need_update = 1
          
      if need_update: self.update_children()
      
  def destroy(self):
    super().destroy()
    for i in list(self.observeds): self._unobserve(i)
    
  def node_for_object(self, o):
    if self.o is o: return self
    for node in self.children:
      r = node.node_for_object(o)
      if r: return r
      
  def recursive(self):
    yield self
    for child in self.children: yield from child
      
  def __repr__(self): return "<Node for %s>" % self.o
  
  def __str__(self):
    if self.attribute and not self.restrict_to_attribute: attr_label = self.attribute.label
    else:                                                 attr_label = ""
    if attr_label: return '''%s: %s''' % (attr_label, self.descr.label_for(self.o))
    return self.descr.label_for(self.o)
  

