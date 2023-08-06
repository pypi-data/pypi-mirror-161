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

"""
editobj3.introsp -- Introspection framework
-------------------------------------------


"""

import os, os.path, types, inspect, locale
import editobj3, editobj3.undoredo as undoredo
from collections import defaultdict

_entity_classes = ()
def _init_for_owlready2():
  global _entity_classes
  import owlready2
  _entity_classes = (owlready2.ThingClass, owlready2.Thing, owlready2.PropertyClass)
  import editobj3.observe
  editobj3.observe._has_owlready2 = True
  
PROPERTY_TYPE_NAMES      = {"property", "getset_descriptor"}
IGNORED_ATTRS            = {"__weakref__", "__abstractmethods__"}
BOOL_ATTRS               = {"visible", "hidden", "active"}
DEFAULT_ADD_METHODS      = ["insert", "add", "append"]
DEFAULT_REMOVE_METHODS   = ["remove", "discard"]
DEFAULT_HAS_ITEM_METHODS = ["has"]
_NEXT_PRIORITY           = 0

def _get_methods_for_attr(base_methods, attr):
  if attr == "__list__": return base_methods
  methods = ["%s_%s" % (method, attr) for method in base_methods]
  if attr.endswith("s"): methods = [method[:-1] for method in methods] + methods
  return methods

def _method_has_nb_args(method, nb):
  try: return method.__code__.co_argcount == nb
  except: return False
  

def print_info(o):
  """Prints the information available from introsp for the given object.

:param o: the object."""
  
  descr = description_for_object(o)
  print("Introsp info about:", o)
  print("Label        :", descr.label_for(o))
  print("Details      :", descr.details_for(o))
  print("Icon filename:", descr.icon_filename_for(o))
  print("Actions      :", ", ".join(action.label for action in descr.actions_for(None, None, o)))
  property_attributes = descr.property_attributes_of(o)
  if property_attributes:
    print("Property attributes:", ", ".join(attribute.name for attribute in property_attributes))
  print("Attributes:")
  for attribute in descr.attributes_of(o):
    field_class = attribute.field_class_for(o)
    unit        = attribute.unit_for(o)
    print("  %s: %s" % (attribute.name, field_class))
    if unit: print("  %s: %s" % (attribute.name, unit))
    if field_class.multiple_object_field:
      print("  %s: addable values: %s" % (attribute.name, attribute.addable_values_to(o)))
      print("  %s: can add to: %s, can remove from: %s, can reorder: %s" % (attribute.name, attribute.can_add_to(o), attribute.can_remove_from(o), attribute.can_reorder(o)))
      print("  %s: actions on a child:" % attribute.name, ", ".join(action.label for action in descr.actions_for(o, attribute, None)))
      

class Attribute(object):
  def __init__(self, name, field_class = "auto", unit = "", priority = 0, inverse_attr = None, optional = True, get_method = "auto", set_method = "auto", addable_values = None, add_method = "auto", remove_method = "auto", reorder_method = "auto", has_item_method = "auto", label = None):
    self.name            = name
    self.field_class     = field_class
    self.unit            = unit
    self.priority        = priority
    self.inverse_attr    = inverse_attr
    self.optional        = optional
    self.get_method      = get_method
    self.set_method      = set_method
    self.addable_values  = addable_values
    self.add_method      = add_method
    self.remove_method   = remove_method
    self.reorder_method  = reorder_method
    self.has_item_method = has_item_method
    self.allow_none      = False
    
    if (self.get_method and (self.get_method != "auto")) or (self.set_method and (self.set_method != "auto")):
      self.is_property = True
      self.optional    = False # Properties cannot be optional
    else:
      self.is_property = False
      
    if label is None: label = name.replace("_", " ")
    if label: self.label = editobj3.TRANSLATOR(label)
    else:     self.label = ""
    
  def update(self, **kargs):
    if ("label" in kargs) and kargs["label"]: kargs["label"] = editobj3.TRANSLATOR(kargs["label"])
    self.__dict__.update(kargs)
    
    if (self.get_method and (self.get_method != "auto")) or (self.set_method and (self.set_method != "auto")):
      self.is_property = True
      self.optional    = False # Properties cannot be optional
    else:
      self.is_property = False
      
  def __eq__  (self, other): return (self.name == other.name) and (self.__class__ is other.__class__)
  def __hash__(self): return hash((self.name, self.__class__))
    
  def copy(self):
    return Attribute(self.name, self.field_class, self.unit, self.priority, self.inverse_attr, self.optional, self.get_method, self.set_method, self.addable_values, self.add_method, self.remove_method, self.reorder_method, self.has_item_method, self.label)
    
  def field_class_for(self, o, dont_get_value = False):
    if self.field_class != "auto": return self.field_class
    
    # Default heuristic rules
    import editobj3.field as field
    if self.name == "__list__": return field.HierarchyOrObjectListField
    if self.name.startswith("_"): return field.HiddenField

    if dont_get_value and (self.has_item_method != "auto"):
      return field.HierarchyOrObjectSelectorField
    val = self.get_value_for(o)
    if   isinstance(val, bool ): return field.BoolField
    elif isinstance(val, float): return field.FloatField
    elif isinstance(val, int):
      if ((val == 1) or (val == 0)) and (self.name.startswith("is") or self.name.startswith("has") or self.name.endswith("enabled") or self.name.endswith("Enabled") or (self.name in BOOL_ATTRS)): return field.BoolField
      return field.IntField
    elif isinstance(val, str):
      if self.name == "password": return field.PasswordField
      if self.name.endswith("filename") or self.name.endswith("Filename"): return field.FilenameField
      if self.name.endswith("url") or self.name.endswith("Url") or self.name.endswith("URL"): return field.URLField
      if (len(val) > 200) or ("\n" in val): return field.TextField
      else:                                 return field.StringField
    elif isinstance(val, list) or isinstance(val, set) or isinstance(val, tuple) or isinstance(val, dict): return field.HierarchyOrObjectListField
    elif isinstance(val, object) and hasattr(val, "__dict__"):
      if (self.name == "parent") or (self.name == "master") or (self.name == "root"): return field.HiddenField
      return field.HierarchyOrObjectSelectorField
    return field.HiddenField
    
  def unit_for    (self, o): return self.unit
  def priority_for(self, o): return self.priority
  
  def _call_method(self, method, o, *args):
    if callable(method):     return method(o, *args)
    if method:               return getattr(o, method)(*args)
    raise AttributeError("No such method")
    
  def _call_insert_or_add_method(self, method, o, value, index):
    if index is None:
      if self.name == "__list__": index = len(o)
      else:                       index = len(self.get_value_for(o))
    if not callable(method): method = getattr(o.__class__, method)
    try:              return method(o, index, value)
    except TypeError: return method(o, value)
    
  def get_value_for(self, o, default = None):
    if self.get_method == "auto": return getattr(o, self.name, default)
    return self._call_method(self.get_method, o)
    
  def can_set_value_for(self, o): return bool(self.set_method)
  
  def set_value_for(self, o, value):
    if self.set_method == "auto": return setattr(o, self.name, value)
    return self._call_method(self.set_method, o, value)
    
  def addable_values_to(self, o):
    if not self.addable_values: return []
    if   callable  (self.addable_values):      addable_values = self.addable_values(o)
    elif isinstance(self.addable_values, str): addable_values = getattr(o, self.addable_values)()
    else:                                      addable_values = self.addable_values
    return sorted(addable_values, key = lambda value: (-int(str(value).startswith("(")), locale.strxfrm(str(value))))
    
  def can_add_to(self, o):
    if self.add_method != "auto": return bool(self.add_method)
    for method in _get_methods_for_attr(DEFAULT_ADD_METHODS, self.name):
      if hasattr(o, method): return True
    values = self.get_value_for(o, self.name)
    if (values is o) or (self.name == "__list__"): return False
    return description_for_object(values)._get_attribute("__list__").can_add_to(values)
    
  def add_to(self, o, value, index = None):
    if self.add_method != "auto": return self._call_insert_or_add_method(self.add_method, o, value, index)
    for method in _get_methods_for_attr(DEFAULT_ADD_METHODS, self.name):
      if hasattr(o, method): return self._call_insert_or_add_method(method, o, value, index)
    values = self.get_value_for(o, self.name)
    if (values is o) or (self.name == "__list__"): return False
    return description_for_object(values)._get_attribute("__list__").add_to(values, value, index)
    
  def can_remove_from(self, o):
    if self.remove_method != "auto": return bool(self.remove_method)
    for method in _get_methods_for_attr(DEFAULT_REMOVE_METHODS, self.name):
      if hasattr(o, method): return True
    values = self.get_value_for(o, self.name)
    if (values is o) or (self.name == "__list__"): return False
    return description_for_object(values)._get_attribute("__list__").can_remove_from(values)
    
  def remove_from(self, o, value):
    if self.remove_method != "auto": return self._call_method(self.remove_method, o, value)
    for method in _get_methods_for_attr(DEFAULT_REMOVE_METHODS, self.name):
      if hasattr(o, method): return getattr(o, method)(value)
    values = self.get_value_for(o, self.name)
    if (values is o) or (self.name == "__list__"): return False
    return description_for_object(values)._get_attribute("__list__").remove_from(values, value)
    
  def has_item_for(self, o):
    if self.has_item_method != "auto": return self._call_method(self.has_item_method, o)
    for method in _get_methods_for_attr(DEFAULT_HAS_ITEM_METHODS, self.name):
      if hasattr(o, method): return getattr(o, method)()
    return self.get_value_for(o)
    
  def can_reorder(self, o):
    if self.reorder_method != "auto": return bool(self.reorder_method)
    return isinstance(self.get_value_for(o), list)
    
  def reorder(self, o, value, direction):
    if self.reorder_method != "auto": return self._call_method(self.reorder_method, o, value, direction)
    values = self.get_value_for(o)
    index = values.index(value)
    if direction == -1:
      if index > 0:               values[index - 1], values[index] = values[index], values[index - 1]
    else:
      if index < len(values) - 1: values[index + 1], values[index] = values[index], values[index + 1]
      
  def __repr__(self):
    if   self.get_method == "auto":     get = ""
    elif self.get_method:               get = ", get with '%s'" % self.get_method
    else:                               get = ", write-only"
    if   self.set_method == "auto":     set = ""
    elif self.set_method:               set = ", set with '%s'" % self.set_method
    else:                               set = ", read-only"
    return "<Attribute '%s'%s%s>" % (self.name, get, set)
    


_TYPE_DESCRS  = {}
_CLASS_DESCRS = {}
def description_for_class(klass):
  """Returns the class description for the given class.
The class description is created if not already existing.

:param Klass: the class.
:returns: a class description (:class:`ClassDescr`).
"""
  descr = _CLASS_DESCRS.get(klass)
  if not descr: descr = _CLASS_DESCRS[klass] = ClassDescr(klass, getattr(klass, "__mro__", None) or klass.mro())
  return descr
description = description_for_class

def description_for_type(type):
  """Returns the description for the given type.
The description is created if not already existing.

:param type: the type.
:returns: a class description (:class:`ClassDescr`).
"""
  descr = _TYPE_DESCRS.get(type)
  if not descr: descr = _TYPE_DESCRS[type] = TypeDescr(type, getattr(type, "__mro__", None) or type.mro())
  return descr

def description_for_object(o):
  """Returns the class description for the given object.
The class description is created if not already existing.

:param o: the object.
:returns: a class description (:class:`ClassDescr`).
"""
  if isinstance(o, type):
    return description_for_type(o)
  else:
    return description_for_class(o.__class__)

class ClassDescr(object):
  """A class description. It describes the attributes of the class and their types, the associated icon,...
Editobj3 is able to automatically guess the attributes and their types, but you can overide the guessed
value by calling various methods of the class description.

.. warning::
   You should not create ClassDescr, but rather call :func:`description`."""
  def _get_parent_description(self, klass): return description_for_class(klass)
  
  def __init__(self, klass, inherited_classes):
    self.klass            = klass
    self.attributes       = {}
    self.actions          = {}
    self.cactions         = {}
    self.icon_filename    = None
    self.label            = None
    self.details          = None
    self.constructor      = None
    if not object is inherited_classes[-1]: inherited_classes = inherited_classes + [object]
    self.inherited_descrs = [self._get_parent_description(klass) for klass in inherited_classes[1:]]
    self.inherited_descrs.insert(0, self)
    
    self.attributes.update(self.search_attributes(klass))
    
    self.is_owl_entity = isinstance(klass, _entity_classes)
    
  def create_attribute(self, name):
    if name in self.attributes: return self.attributes[name]
    for descr in self.inherited_descrs:
      if name in descr.attributes:
        attribute = descr.attributes[name].copy()
        break
    else: attribute = Attribute(name)
    return attribute
    
  def search_attributes(self, klass):
    attributes = {}
    for attr in dir(klass):
      if attr in IGNORED_ATTRS: continue
      kval = getattr(klass, attr)
      
      if   type(kval).__name__ in PROPERTY_TYPE_NAMES:
        attribute             = attributes.get(attr) or self.create_attribute(attr)
        attribute.is_property = True
        attribute.optional    = False
        if isinstance(kval, property):
          if not kval.fset: attribute.set_method = None
          if not kval.fget: attribute.get_method = None
        else:
          if not kval.__set__: attribute.set_method = None
          if not kval.__get__: attribute.get_method = None
        attributes[attribute.name] = attribute
        
      elif attr.startswith("set") and (len(attr) > 3) and _method_has_nb_args(kval, 2):
        if attr[3] == "_": attr2 = attr[4:]
        else:              attr2 = attr[3].lower() + attr[4:]
        attribute             = attributes.get(attr2) or self.create_attribute(attr2)
        attribute.set_method  = attr
        attribute.is_property = True
        attributes[attribute.name] = attribute
        
      elif attr.startswith("get") and (len(attr) > 3) and _method_has_nb_args(kval, 1):
        if attr[3] == "_": attr2 = attr[4:]
        else:              attr2 = attr[3].lower() + attr[4:]
        attribute             = attributes.get(attr2) or self.create_attribute(attr2)
        attribute.get_method  = attr
        attribute.is_property = True
        attribute.optional    = False
        attributes[attribute.name] = attribute
    return attributes
  
  def __repr__(self): return ("<%s for %s, attributes:\n  " % (self.__class__.__name__, self.klass)) + "\n  ".join([repr(attribute) for attribute in self.attributes.values()]) + "\n>"
  
  def set_label(self, label):
    """Set the label for this class. If no label is provided, the str() function is used.

:param label: either a string (the label) or a callable (taking one argument, the object, and returning the label)."""
    self.label = label
    
  def set_details(self, details):
    """Set the details for this class. If no details are provided, an empty string is used.

:param details: either a string (the details) or a callable (taking one argument, the object, and returning the details)."""
    self.details = details
    
  def set_icon_filename(self, icon_filename):
    """Set the icon filename for this class. If no icon is provided, a Python icon is used.

:param icon_filename: either a string (the icon filename) or a callable (taking one argument, the object, and returning the icon filename)."""
    self.icon_filename = icon_filename

  def set_constructor(self, constructor):
    """Set the constructor for this class. By default, EditObj 3 creates new instances by calling the class with a single argument: the parent objet.
If your class's __init__ does not work like that, you can either set a Constructor, or create a FormConstructor subclass if you need to ask some information to the user prior to create the instance.

Example of Constructor if the class's __init__ does not expect any argument:

>>> descr.set_constructor(introsp.Constructor(lambda klass, parent: klass()))

Example of a FormConstructor asking the user for a "name" argument:

>>> class MyFormConstructor(introsp.FormConstructor):
>>>   def __init__(self):
>>>     self.name = "default name"
>>> descr.set_constructor(MyFormConstructor)

:param constructor: a Constructor object, a FormConstructor subclass, or None for using the class itself as a constructor."""
    self.constructor = constructor
    
  #def def_attr(self, attr, field_class = "auto", unit = "auto", priority = "auto", inverse_attr = "auto", optional = "auto", get_method = "auto", set_method = "auto", addable_values = "auto", add_method = "auto", remove_method = "auto", reorder_method = "auto", has_item_method = "auto", label = None, allow_none = False):
  def def_attr(self, attr, field_class = 0, **kargs):
    """def_attr(attr, field_class = "auto", unit = "auto", priority = "auto", inverse_attr = "auto", optional = "auto", get_method = "auto", set_method = "auto", addable_values = "auto", add_method = "auto", remove_method = "auto", reorder_method = "auto", has_item_method = "auto", label = None)

This method is similar to :func:`editobj3.introsp.def_attr`, but it is restricted to the class described by this class description (including subclasses)."""
    global _NEXT_PRIORITY
    attribute = self.attributes[attr] = self.create_attribute(attr)
    
    if field_class != 0: kargs["field_class"] = field_class # Allows to give the field_class argument by position
    
    if not "priority" in kargs:
      attribute.priority = _NEXT_PRIORITY
      _NEXT_PRIORITY += 1
    elif kargs["priority"] is None: del kargs["priority"]
    
    if ("label" in kargs) and (kargs["label"]): kargs["label"] = editobj3.TRANSLATOR(kargs["label"])
    
    if kargs.get("field_class", 0) is None: raise ValueError("None is not a valid Field class; use editobj3.field.HiddenField")
    
    attribute.update(**kargs)
    
    # if field_class     != "auto": attribute.field_class     = field_class
    # if unit            != "auto": attribute.unit            = unit
    # if not priority    is  None :
    #   if priority      != "auto": attribute.priority        = priority
    #   else:                       attribute.priority        = _NEXT_PRIORITY; _NEXT_PRIORITY += 1
    # if inverse_attr    != "auto": attribute.inverse_attr    = inverse_attr
    # if optional        != "auto": attribute.optional        = optional
    # if get_method      != "auto": attribute.get_method      = get_method
    # if set_method      != "auto": attribute.set_method      = set_method
    # if addable_values  != "auto": attribute.addable_values  = addable_values
    # if add_method      != "auto": attribute.add_method      = add_method
    # if remove_method   != "auto": attribute.remove_method   = remove_method
    # if reorder_method  != "auto": attribute.reorder_method  = reorder_method
    # if has_item_method != "auto": attribute.has_item_method = has_item_method
    # if label           !=  None : attribute.label           = editobj3.TRANSLATOR(label)
    # return attribute
    
  def add_action(self, action):
    if isinstance(action, ActionOnAChild):
      if action.attr in self.cactions: self.cactions[action.attr][action.name] = action
      else:                            self.cactions[action.attr] = { action.name : action }
    else:                              self.actions [action.name] = action
    
  def create_new(self, parent):
    for descr in self.inherited_descrs:
      if descr.constructor: return descr.constructor.create_new(self.klass, parent)
    return self.klass(parent)
    
  # Per-instance methods
  
  def label_for(self, o):
    for descr in self.inherited_descrs:
      if descr.label:
        if callable(descr.label): return descr.label(o)
        else:                     return descr.label
    return str(o)
    
  def details_for(self, o):
    for descr in self.inherited_descrs:
      if descr.details:
        if callable(descr.details): return descr.details(o)
        else:                       return descr.details
    if hasattr(o, "details") or ("details" in self.attributes): return self._get_attribute("details").get_value_for(o)
    return ""
    
  def icon_filename_for(self, o):
    for descr in self.inherited_descrs:
      if descr.icon_filename:
        if callable(descr.icon_filename): return descr.icon_filename(o)
        else:                             return descr.icon_filename
    if hasattr(o, "icon_filename") or ("icon_filename" in self.attributes): return self._get_attribute("icon_filename").get_value_for(o)
    return os.path.join(editobj3._ICON_DIR, "python.svg")

  def attributes_of(self, o):
    attributes = { attribute.name : attribute # Keep only one attribute per name
                   for descr in reversed(self.inherited_descrs) 
                   for attribute in descr.attributes.values()
                   if attribute.optional == False }
    if hasattr(o.__class__, "__attrs__"):
      for attr in o.__attrs__():
        if not attr in attributes: attributes[attr] = self._get_attribute(attr, False)
    else:
      o_dict = getattr(o, "__dict__", None)
      if o_dict:
        for attr in o_dict:
          if not attr in attributes: attributes[attr] = self._get_attribute(attr, False)
    return sorted(attributes.values(), key = lambda attribute: (attribute.priority, locale.strxfrm(attribute.label)))
    
  def property_attributes_of(self, o = None):
    return set({ attribute.name : attribute for descr in reversed(self.inherited_descrs) for attribute in descr.attributes.values() if attribute.is_property }.values())
    
  def _get_attribute(self, attr, register = True):
    for descr in self.inherited_descrs:
      if attr in descr.attributes: return descr.attributes[attr]
    attribute = Attribute(attr)
    if register: self.attributes[attr] = attribute
    return attribute
    
  def actions_for(self, parent, attribute, o):
    actions = {}
    for descr in reversed(self.inherited_descrs): actions.update(descr.actions)
    actions = { action for action in actions.values() if action.filter(o) }
    
    for o_attribute in self.attributes_of(o):
      field_class = o_attribute.field_class_for(o)
      if field_class.object_field:
        if field_class.multiple_object_field:
          if(o_attribute.can_add_to       (o) and
             o_attribute.addable_values_to(o)): actions.add(AppendAction(o_attribute))
        elif(o_attribute.can_set_value_for(o) and
             o_attribute.addable_values_to(o)): actions.add(SetAction(o_attribute))
        
    if parent:
      cactions     = {}
      parent_descr = description_for_object(parent)
      for descr in reversed(parent_descr.inherited_descrs):
        if attribute.name in descr.cactions: cactions.update(descr.cactions[attribute.name])
      actions.update(action for action in cactions.values() if action.filter(parent, attribute, o))
      
      field_class = attribute.field_class_for(parent)
      if field_class.object_field:
        if field_class.multiple_object_field:
          if(attribute.can_add_to       (parent) and
             attribute.addable_values_to(parent)): actions.add(InsertAction(attribute))
          if attribute.can_remove_from  (parent) : actions.add(_REMOVE_ACTION)
          if attribute.can_reorder      (parent) : actions.add(_MOVE_UP_ACTION); actions.add(_MOVE_DOWN_ACTION)
        else:
          if(attribute.can_set_value_for(parent) and
             attribute.addable_values_to(parent)): actions.add(ReplaceAction(attribute))
        
    actions = sorted(actions, key = lambda action: (action.priority, locale.strxfrm(action.label)))
    return actions
    
  def do_action(self, action, undo_stack, editor, o, *args): return action.do(undo_stack, editor, o, *args)

class TypeDescr(ClassDescr):
  def _get_parent_description(self, type): return description_for_type(type)
  

class Action(object):
  def __init__(self, name, func, filter = None, accept_object_pack = False, default = False, field_class = None, priority = 0):
    self.name                = name
    self.func                = func
    self.field_class         = field_class
    self.accept_object_pack  = accept_object_pack
    self.default             = default
    self.label               = editobj3.TRANSLATOR(self.name)
    self.priority            = priority
    if filter: self.filter   = filter
    
  def filter(self, o): return True
  
  def do(self, undo_stack, editor, o, *args):
    if callable(self.func): return self.func(undo_stack, editor, o, *args)
    else:                   return getattr(o, self.func)(undo_stack, editor, *args)
      
class ActionOnAChild(Action):
  def __init__(self, attr, name, func, filter = None, accept_object_pack = False, default = False, field_class = None, priority = 0):
    Action.__init__(self, name, func, filter, accept_object_pack, default, field_class, priority)
    self.attr = attr
    
  def filter(self, o, attribute, child): return True


class AddAction(object):
  def choose_new_child(self, editor, o, callback0, callback, label):
    addable_values = NamedList(self.attribute.addable_values_to(o), label)
    
    return_value = [None]
    def on_validate(new_child):
      if (new_child is None) or (new_child is addable_values): return
      if   isinstance(new_child, NewInstanceOf):
        new_child = new_child.create_new(o)
        if new_child is None: return
      elif isinstance(new_child, ObjectPack):
        for i in range(len(new_child.objects)):
          if isinstance(new_child.objects[i], NewInstanceOf): new_child.objects[i] = new_child.objects[i].create_new(o)
      callback0(new_child)
      callback (new_child)
      
    if   len(addable_values.children) >  1: editobj3.edit(addable_values, on_validate = on_validate, flat_list = True, width = 1024, height = 752, master = editor)
    elif len(addable_values.children) == 1: on_validate(addable_values.children[0])
    
  def do_insert(self, undo_stack, parent, index, new_child):
    if isinstance(new_child, ObjectPack): new_childs =  new_child.objects
    else:                                 new_childs = [new_child]
    
    def do_it():
      values = self.attribute.get_value_for(parent)
      for new_child in new_childs:
        if not new_child in values: # Else, already added by the constructor
          self.attribute.add_to(parent, new_child, index)
          
    def undo_it():
      for new_child in new_childs: self.attribute.remove_from(parent, new_child)
      
    undoredo.UndoableOperation(do_it, undo_it, editobj3.TRANSLATOR("add '%s'") % ", ".join(description_for_object(i).label_for(i) for i in new_childs), undo_stack)
    return new_child
    
  def do_set(self, undo_stack, o, new_value):
    old_value = self.attribute.get_value_for(o)
    
    def do_it  (): self.attribute.set_value_for(o, new_value)
    def undo_it(): self.attribute.set_value_for(o, old_value)
    
    undoredo.UndoableOperation(do_it, undo_it, editobj3.TRANSLATOR("set '%s'") % description_for_object(new_value).label_for(new_value), undo_stack)
    return new_value
  

class SetAction(Action, AddAction):
  def __init__(self, attribute):
    self.attribute = attribute
    Action.__init__(self, editobj3.TRANSLATOR("Set %s...") % attribute.label, None)
    
  def do(self, undo_stack, editor, o, callback):
    def callback0(new_child): self.do_set(undo_stack, o, new_child)
    return self.choose_new_child(editor, o, callback0, callback, editobj3.TRANSLATOR("Set %s to...") % self.attribute.label)
    
class AppendAction(Action, AddAction):
  def __init__(self, attribute):
    self.attribute = attribute
    Action.__init__(self, editobj3.TRANSLATOR("Add %s...") % attribute.label, None)
    
  def do(self, undo_stack, editor, o, callback):
    def callback0(new_child): self.do_insert(undo_stack, o, None, new_child)
    return self.choose_new_child(editor, o, callback0, callback, editobj3.TRANSLATOR("Add %s...") % self.attribute.label)
    
class ReplaceAction(ActionOnAChild, AddAction):
  def __init__(self, attribute):
    self.attribute = attribute
    ActionOnAChild.__init__(self, attribute.name, editobj3.TRANSLATOR("Replace %s...") % attribute.label, None)
    
  def do(self, undo_stack, editor, parent, attribute, o, callback):
    def callback0(new_child): self.do_set(undo_stack, parent, new_child)
    return self.choose_new_child(editor, parent, callback0, callback, editobj3.TRANSLATOR("Replace %s by...") % self.attribute.label)
    
class InsertAction(ActionOnAChild, AddAction):
  def __init__(self, attribute):
    self.attribute = attribute
    ActionOnAChild.__init__(self, attribute.name, editobj3.TRANSLATOR("Insert %s...") % attribute.label, None)
    
  def do(self, undo_stack, editor, parent, attribute, o, callback):
    def callback0(new_child):
      values = self.attribute.get_value_for(parent)
      if hasattr(values, "index"): index = values.index(o) + 1
      else:                        index = None
      self.do_insert(undo_stack, parent, index, new_child)
    return self.choose_new_child(editor, parent, callback0, callback, editobj3.TRANSLATOR("Insert %s...") % self.attribute.label)
    
class RemoveAction(ActionOnAChild):
  def __init__(self): ActionOnAChild.__init__(self, "__remove__", editobj3.TRANSLATOR("Remove"), None, accept_object_pack = True)
  
  def do(self, undo_stack, editor, parent, attributes, o):
    if isinstance(parent, ObjectPack): parents = parent.objects; objects = o.objects
    else:                              parents = [parent];       objects = [o];       attributes = [attributes]
    indexes    = [None] * len(parents)
    for i in range(len(parents)):
      values        = attributes[i].get_value_for(parents[i])
      if hasattr(values, "index"): indexes[i] = values.index(objects[i])
      
    def do_it():
      for i in range(len(parents)): attributes[i].remove_from(parents[i], objects[i])
      
    def undo_it():
      for i in range(len(parents)): attributes[i].add_to(parents[i], objects[i], indexes[i])
      
    labels = "', '".join([description_for_object(o).label_for(o) for o in objects])
    undoredo.UndoableOperation(do_it, undo_it, editobj3.TRANSLATOR("remove '%s'") % labels, undo_stack)

    
class MoveAction(ActionOnAChild):
  def __init__(self, name, direction):
    ActionOnAChild.__init__(self, "__move__", editobj3.TRANSLATOR(name), None, accept_object_pack = True)
    self.direction = direction
    
  def do(self, undo_stack, editor, parent, attributes, o):
    print(attributes)
    if isinstance(parent, ObjectPack): parents = parent.objects; objects = o.objects
    else:                              parents = [parent];       objects = [o];       attributes = [attributes]
    
    parents_attributes_objects = []
    for i in range(len(parents)):
      values    = attributes[i].get_value_for(parents[i])
      index     = values.index(objects[i])
      if (self.direction == -1) and (index <=               0): return # Cannot move up
      if (self.direction ==  1) and (index >= len(values) - 1): return # Cannot move down
      parents_attributes_objects.append((index, parents[i], attributes[i], objects[i]))
    parents_attributes_objects.sort(key = lambda index_parent_attribute_o: index_parent_attribute_o[0])
    
    def move_up():
      for index, parent, attribute, o in parents_attributes_objects: attribute.reorder(parent, o, -1)
      
    def move_down():
      for index, parent, attribute, o in reversed(parents_attributes_objects): attribute.reorder(parent, o, 1)
      
    labels = "', '".join([description_for_object(o).label_for(o) for o in objects])
    if self.direction == -1: undoredo.UndoableOperation(move_up  , move_down, editobj3.TRANSLATOR("move up '%s'"  ) % labels, undo_stack)
    else:                    undoredo.UndoableOperation(move_down, move_up  , editobj3.TRANSLATOR("move down '%s'") % labels, undo_stack)

    
_REMOVE_ACTION    = RemoveAction()
_MOVE_UP_ACTION   = MoveAction("Move up"  , -1)
_MOVE_DOWN_ACTION = MoveAction("Move down",  1)


class NewInstanceOf(object):
  def __init__(self, klass, label = None, icon_filename = None):
    self._klass = klass
    if label:         self._label = label
    else:             self._label = editobj3.TRANSLATOR("(new %s)" % klass.__name__)
    if icon_filename: self.icon_filename = icon_filename
  def __str__ (self): return self._label
  def __repr__(self): return "<NewInstanceOf for %s>" % self._klass.__name__
  def create_new(self, parent): return description(self._klass).create_new(parent)

class Constructor(object):
  def __init__(self, func):
    self._func  = func
  def create_new(self, klass, parent):
    return self._func(klass, parent)
  
class FormConstructor(object):
  @classmethod
  def create_new(FormClass, klass, parent):
    form = FormClass()
    form._klass = klass
    ok = [0]
    def on_validate(o):
      if o: ok[0] = 1
    editobj3.edit(form, on_validate = on_validate)
    if ok[0]: return form.create_new_from_form(klass, parent)
    
  def __str__ (self): return editobj3.TRANSLATOR("(new %s)" % self._klass.__name__)
  def __repr__(self): return "<FormConstructor for %s>" % self._klass.__name__
  
  def create_new_from_form(self, klass, parent):
    d = self.__dict__.copy()
    del d["_klass"]
    return klass(**d)


class NamedList(object):
  def __init__(self, children, name):
    self.children = children
    self._name    = name
  def __str__(self): return self._name
  
description(NamedList).def_attr("children", label = "", priority = None, add_method = None, remove_method = None, reorder_method = None)

add_action = description(object).add_action

def _edit_in_new_window_action(undo_stack, editor, o):
  import editobj3.editor
  editobj3.edit(o, undo_stack = undo_stack, master = editor)

_EDIT_ACTION = Action("Edit in new window...", _edit_in_new_window_action)
add_action(_EDIT_ACTION)


def def_attr(attr, field_class = 0, **kargs):
  """def_attr(attr, field_class = "auto", unit = "auto", priority = "auto", inverse_attr = "auto", optional = "auto", get_method = "auto", set_method = "auto", addable_values = "auto", add_method = "auto", remove_method = "auto", reorder_method = "auto", has_item_method = "auto", label = None)

Defines an attribute.

:param attr: the name of the attribute, or "__list__".
:param field_class: the class of field used to edit the attribute (see editobj3.field), or None to hide the attribute.
:param unit: the unit displayed on the right of the editing field (default to no unit).
:param priority: the priority value, used for ordering the attributes in the attribute pane (default: display the attributes
                 in the order they have been def_attr'ed); use None if you don't want to change the priority.
:param inverse_attr: the name of the inverse attribute (e.g. 'parent' attribute is tipically the inverse of 'children');
                     inverse attributes are automatically hidden in the tree view (default: not inverse attribute).
:param optional: the attribute may not be defined for all instances of the class
                 (default: True, except for property and get/set attributes).
:param get_method: the method for getting the value of the attribute.
:param set_method: the method for setting the value of the attribute.
:param addable_values: the list of possible values to add (to a list or set attribute),
                       or the value that the attribute can take for (for non-list object attribute).
                       Can also be a callable that returns the list of addable values for the given object (given in argument).
                       Use :class:`NewInstanceOf` for allowing the addition of fresh new instances of a given class.
:param add_method: the method for adding items to the attribute's value (only meaningful for list or set attribute)
                   Notice that ADD_METHOD also accept insert-like method (this should be preferred for ordered values).
:param remove_remove: the method for removing items from the attribute's value.
:param reorder_method: the method for reordering items in the attribute's value.
:param has_item_method: the method for testing the presence of items in the attribute's value.
:param label: the label for displaying the attribute (default to the attribute name).

All method parameters can be a method name, a callable, or None (to disable the corresponding functionality).

Except for the two first parameters, all parameters to def_attr() must be given by name, for example:

>>> introsp.def_attr("hit_points", field.IntField, unit = "HP")
>>> introsp.def_attr("items", field.ObjectListField,
                     addable_values = [NewInstanceOf(Item)],
                     add_method = "add_item",
                     )
"""
  found = False
  for descr in _CLASS_DESCRS.values():
    if attr in descr.attributes:
      descr.def_attr(attr, field_class, **kargs)
      found = True
  if not found: description(object).def_attr(attr, field_class, **kargs)

description(list ).def_attr("__list__", label = "", priority = None, optional = False, get_method = lambda o: o, set_method = None)
description(tuple).def_attr("__list__", label = "", priority = None, optional = False, get_method = lambda o: o, set_method = None, reorder_method = None, add_method = None, remove_method = None)
description(set  ).def_attr("__list__", label = "", priority = None, optional = False, get_method = lambda o: o, set_method = None, reorder_method = None)


class ObjectPack(object):
  def __init__(self, objects):
    self.objects             = objects
    self.attributes          = [description_for_object(o).attributes_of         (o) for o in objects]
    self.property_attributes = [description_for_object(o).property_attributes_of(o) for o in objects]
    self.attrs               = [{ attribute.name for attribute in o_attributes } for o_attributes in self.attributes]
    self.property_attrs      = [{ attribute.name for attribute in o_attributes } for o_attributes in self.property_attributes]
    
class NonConsistent(object):
  def __repr__(self): return "NonConsistent"
  def __bool__(self): return False
NonConsistent = NonConsistent()

class Inexistent(object):
  def __repr__(self): return "Inexistent"
  def __bool__(self): return False
Inexistent = Inexistent()

_OBJECT_PACK_ATTRIBUTES = {}
def _object_pack_attribute(name): return _OBJECT_PACK_ATTRIBUTES.get(name) or ObjectPackAttribute(name)

class ObjectPackAttribute(Attribute):
  def __init__(self, name):
    Attribute.__init__(self, name)
    _OBJECT_PACK_ATTRIBUTES[name] = self
    
  def unit_for(self, pack):
    unit = ""
    for i in range(len(pack.objects)):
      if self.name in pack.attrs[i]:
        new_unit = description_for_object(pack.objects[i])._get_attribute(self.name).unit_for(pack.objects[i])
        if unit and new_unit and (unit != new_unit): return ""
        unit = new_unit
    return unit
    
  def priority_for(self, pack):
    for i in range(len(pack.objects)):
      if self.name in pack.attrs[i]:
        priority = description_for_object(pack.objects[i])._get_attribute(self.name).priority_for(pack.objects[i])
        if priority: return priority
    return 0
    
  def field_class_for(self, pack, dont_get_value = False):
    field_class = None
    for i in range(len(pack.objects)):
      if self.name in pack.attrs[i]:
        new_field_class = description_for_object(pack.objects[i])._get_attribute(self.name).field_class_for(pack.objects[i], dont_get_value)
        if field_class and new_field_class and (not field_class is new_field_class): return None
        field_class = new_field_class
    return field_class
    
  def addable_values_to(self, o): return []

  def can_add_to(self, o): return False
  
  def can_remove_from(self, o):
    for i in range(len(o.objects)):
      if description_for_object(o.objects[i])._get_attribute(self.name).can_remove_from(o.objects[i]): return True
      
  def can_reorder(self, o):
    for i in range(len(o.objects)):
      if description_for_object(o.objects[i])._get_attribute(self.name).can_reorder(o.objects[i]): return True
      
  def get_value_for(self, pack):
    value = NonConsistent
    for i in range(len(pack.objects)):
      if self.name in pack.attrs[i]:
        v = description_for_object(pack.objects[i])._get_attribute(self.name).get_value_for(pack.objects[i])
        if value is NonConsistent: value = v
        elif value != v: return NonConsistent
    return value

  def set_value_for(self, pack, value):
    for i in range(len(pack.objects)):
      if self.name in pack.attrs[i]:
        description_for_object(pack.objects[i])._get_attribute(self.name).set_value_for(pack.objects[i], value)

  def __getitem__(self, index): return self

  
class ObjectPackDescription(object):
  attributes       = {} # For def_attr
  inherited_descrs = []
  is_owl_entity    = False
  def icon_filename_for(self, pack):
    icon_filenames = set()
    for o in pack.objects:
      icon_filenames.add(description_for_object(o).icon_filename_for(o))
    icon_filenames = sorted(icon_filenames)
    if len(icon_filenames) == 1: icon_filenames = icon_filenames * 2
    return icon_filenames
    
  def label_for   (self, pack): return editobj3.TRANSLATOR("(pack of %s objects)") % len(pack.objects)
  def details_for (self, pack): return ""
  
  def attributes_of(self, pack):
    attrs = set()
    for o_attrs in pack.attrs: attrs.update(o_attrs)
    attributes = [self._get_attribute(attr) for attr in attrs]
    return sorted(attributes, key = lambda attribute: (attribute.priority_for(pack), locale.strxfrm(attribute.label))) 
    
  def property_attributes_of(self, pack):
    attrs = set()
    for o_attrs in pack.property_attrs: attrs.update(o_attrs)
    return [self._get_attribute(attr) for attr in attrs]
    
  def _get_attribute(self, attr): return _object_pack_attribute(attr)
  
  def actions_for(self, parents, attributes, objects):
    if parents:        parents    = parents.objects
    else:              parents    = [None] * len(objects.objects)
    if not attributes: attributes = [None] * len(objects.objects)
    actions = set()
    for i in range(len(objects.objects)):
      actions.update(description_for_object(objects.objects[i]).actions_for(parents[i], attributes[i], objects.objects[i]))
    return actions
    
  def do_action(self, action, undo_stack, editor, pack, *args):
    if isinstance(action, ActionOnAChild):
      parents    = pack.objects
      attributes = args[0]
      objects    = args[1].objects
      if action.accept_object_pack:
        new_parents    = []
        new_attributes = []
        new_objects    = []
        for i in range(len(parents)):
          if action in description_for_object(objects[i]).actions_for(parents[i], attributes[i], objects[i]):
            new_parents   .append(parents   [i])
            new_attributes.append(attributes[i])
            new_objects   .append(objects   [i])
        return action.do(undo_stack, editor, ObjectPack(new_parents), new_attributes, ObjectPack(new_objects), *args[2:])
        
      else:
        for i in range(len(parents)):
          if action in description_for_object(objects[i]).actions_for(parents[i], attributes[i], objects[i]):
            description_for_object(parents[i]).do_action(action, undo_stack, parents[i], attributes[i], objects[i], *args[2:])
            
    else:
      if action.accept_object_pack:
        objects = ObjectPack([o for o in pack.objects if action in description_for_object(o).actions_for(None, None, o)])
        return action.do(undo_stack, editor, objects, *args)
        
      else:
        for o in pack.objects:
          descr = description_for_object(o)
          if action in descr.actions_for(None, None, o): descr.do_action(action, undo_stack, editor, o, *args)
        
_CLASS_DESCRS[ObjectPack] = ObjectPackDescription()
