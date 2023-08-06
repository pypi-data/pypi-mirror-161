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
editobj3.observe: Observation framework
---------------------------------------

The observe module can register listeners for any Python object. When the object is modified,
the listeners will be (asynchronously) called. The following objects can be observed: Python instance,
lists and dictionaries. A listener is a function of the form::

  def my_listener(obj, type, new, old):
    ...

where obj is the modified object, type is the type of the modification, and old and new
are the old and new values. Type can be:
  
  - object (the Python root class): one or more attributes have changed on obj. old and
    new are the old and new attribute dictionary of obj (this dictionary includes attributes
    in obj.__dict__, but also Python's property and C-level getset).
    If you want to know which attribute has changed, use dictdiff on new and old (see the
    diffdict function docstring).
  
  - list : one or more addition / deletion have occured on obj (which is a list).
    new and old are the new and old list content of obj.

  - dict : one or more assignment / deletion have occured on obj (which is a dictionary).
    new and old are the new and old dictionary values.

  - "__class__" : the class of obj has changed. new and old are the new and old classes.

The :func:`scan()` function checks all observed objects and calls the corresponding listeners.

Quick example:
  >>> from editobj3.observe import *
  >>> class C: pass
  ...
  >>> c = C()
  >>> def listener(obj, type, new, old):
  ...   if type is object:
  ...     for (attr, newvalue, oldvalue) in diffdict(new, old):
  ...       print("c.%s was %s, is now %s" % (attr, oldvalue, newvalue))
  >>> observe(c, listener)
  >>> c.x = 1
  >>> scan()
  c.x was None, is now 1
"""

__all__ = [
  "observe", "isobserved", "unobserve", "observe_tree", "unobserve_tree",
  "scan", "diffdict", "Listener", "DebugListener",
  ]

from weakref import ref, WeakSet, WeakValueDictionary, WeakKeyDictionary

import editobj3

_observed_seqs    = {}
_observed_objects = {}

def _can_be_getter(method):
  if type(method).__name__ != "method": return False
  try: return method.__code__.co_argcount == 1
  except: return False

_class_2_properties = {}
def _get_class_properties(klass):
  props = _class_2_properties.get(klass)
  if props is None:
    props = _class_2_properties[klass] = [attr for attr in dir(klass) if (not attr in IGNORED_ATTRS) and (type(getattr(klass, attr)).__name__ in PROPERTY_TYPE_NAMES)]
  return props
  
_type_2_properties = {}
def _get_type_properties(typ):
  props = _type_2_properties.get(typ)
  if props is None:
    props = _type_2_properties[typ] = [attr for attr in dir(typ) if (not attr in IGNORED_ATTRS) and attr.startswith("get") and _can_be_getter(getattr(typ, attr))]
  return props

PROPERTY_TYPE_NAMES = { "property", "getset_descriptor" }
IGNORED_ATTRS       = { "__weakref__", "__abstractmethods__" }


class Listener(object):
  def __call__(self, obj, type, new, old):
    if   type is object:
      for attr, new_value, old_value in diffdict(new, old):
        self.attr_changed(obj, attr, new_value, old_value)
    elif type is list:
      for i in old: self.list_item_removed(obj, i)
      for i in new: self.list_item_added  (obj, i)
    elif type is dict:
      for k, i in old.items(): self.dict_item_removed(obj, k, i)
      for k, i in new.items(): self.dict_item_added  (obj, k, i)
    elif type == "__class__":
      self.class_changed(obj, new, old)
  def class_changed(self, obj, new_class, old_class): pass
  def attr_changed(self, obj, attr, new_value, old_value): pass
  def list_item_added  (self, obj, item): pass
  def list_item_removed(self, obj, item): pass
  def dict_item_added  (self, obj, key, item): pass
  def dict_item_removed(self, obj, key, item): pass

class DebugListener(Listener):
  def class_changed(self, obj, new_class, old_class): print("Class of '%s' changed from %s to %s." % (obj, old_class, new_class))
  def attr_changed(self, obj, attr, new_value, old_value): print("'%s.%s' was %s, is now %s." % (obj, attr, old_value, new_value))
  def list_item_added  (self, obj, item): print("'%s' added to '%s'." % (item, obj))
  def list_item_removed(self, obj, item): print("'%s' removed from '%s'." % (item, obj))
  def dict_item_added  (self, obj, key, item): print("XXX dict changed")
  def dict_item_removed(self, obj, key, item): print("XXX dict changed")


def observe(o, listener):
  """Registers a listener for the given object. When o will be changed, the listener will
be called (asynchronously). See the module docstrings for more info about what arguments receives a listener.

:param o: the object to observe.
:param listener: the listener.
:type listener: callable"""
  if isinstance(o, editobj3.introsp.ObjectPack):
    for o2 in o.objects: observe(o2, listener)
    return
  
  i = id(o)
  observation = _observed_seqs.get(i)
  if observation: observation.listeners.append(listener)
  else:
    if   isinstance(o, list): _observed_seqs[i] = ListObservation(o, [listener])
    elif isinstance(o, set ) or isinstance(o, WeakSet): _observed_seqs[i] = SetObservation (o, [listener])
    elif isinstance(o, dict) or isinstance(o, WeakValueDictionary) or isinstance(o, WeakKeyDictionary): _observed_seqs[i] = DictObservation(o, [listener])
    
  if hasattr(o, "__dict__"):
    observation = _observed_objects.get(i)
    if observation: observation.listeners.append(listener)
    else:           _observed_objects[i] = ObjectObservation(o, [listener])
    
def isobserved(o, listener = None):
  """Returns true if the given object is observed by the given listener. If listener is None, returns the list
of active listeners for o.

:param o: the object.
:param listener: the listener, or None.
:returns: True, False or list."""
  if isinstance(o, editobj3.introsp.ObjectPack):
    for o2 in o.objects:
      if isobserved(o2, listener): return True
    return False
    
  i = id(o)
  observation = _observed_seqs.get(i) or (hasattr(o, "__dict__") and _observed_objects.get(i))
  
  if listener: return observation and (listener in observation.listeners)
  else:        return observation and observation.listeners
  
def unobserve(o, listener = None):
  """Unregisters the given listener for o. If listener is not listening o,
nothing is done. If listener is None, unregisters *all* listeners on o.

:param o: the object.
:param listener: the listener, or None."""
  if isinstance(o, editobj3.introsp.ObjectPack):
    for o2 in o.objects: unobserve(o2, listener)
    return
    
  i = id(o)
  if listener:
    observation = _observed_seqs.get(i)
    if observation:
      try: observation.listeners.remove(listener)
      except ValueError: pass
      if not observation.listeners: del _observed_seqs[i]
      
    if hasattr(o, "__dict__"):
      observation = _observed_objects.get(i)
      if observation:
        try: observation.listeners.remove(listener)
        except ValueError: pass
        if not observation.listeners: del _observed_objects[i]
        
  else:
    if i in _observed_seqs   : del _observed_seqs   [i]
    if i in _observed_objects: del _observed_objects[i]
    

class Observation(object):
  def __init__(self, o, listeners):
    self.object    = o
    self.listeners = listeners
    self.old       = self.current_value()

class ListObservation(Observation):
  type = list
  def current_value(self): return list(self.object)
  
class SetObservation(Observation):
  type = set
  def current_value(self): return set(self.object)
  
class DictObservation(Observation):
  type = dict
  def current_value(self): return dict(self.object)
  
class ObjectObservation(Observation):
  def __init__(self, o, listeners):
    self.listeners = listeners
    if isinstance(o, type): self.props = _get_type_properties (o)
    else:                   self.props = _get_class_properties(o.__class__)
    self.old       = self.current_value(o)
    self.old_class = o.__class__
    try:    self.object = weakref.ref(o)
    except: self.object = o
    
  def current_value(self, o):
    if self.props:
      #new = { prop : getattr(o, prop, None) for prop in self.props }
      new = {}
      for prop in self.props:
        v = getattr(o, prop, None)
        if (type(v).__name__ == "method"): v = v()
        new[prop] = v
      new.update(o.__dict__)
      return new
    else: return o.__dict__.copy()

    
_has_owlready2 = False
    
def scan():
  """Checks for changes in all listened objects, and calls the corresponding listeners if needed."""
  for i, observation in list(_observed_seqs.items()):
    new = observation.object
    if   isinstance(new, WeakSet            ): new = set (new)
    elif isinstance(new, WeakKeyDictionary  ): new = dict(new)
    elif isinstance(new, WeakValueDictionary): new = dict(new)
    if observation.old != new:
      for listener in observation.listeners[:]: listener(observation.object, observation.type, new, observation.old)
      observation.old = observation.current_value()
      
  for i, observation in list(_observed_objects.items()):
    if type(observation.object) is ref:
      o = observation.object()
      if o is None:
        del _observed_objects[i]
        continue
    else: o = observation.object
    
    if observation.props:
      new = observation.current_value(o)
      
      if observation.old != new:
        for listener in observation.listeners[:]: listener(o, object, new, observation.old)
        observation.old = new
    else:
      if observation.old != o.__dict__:
        for listener in observation.listeners[:]: listener(o, object, o.__dict__, observation.old)
        observation.old = observation.current_value(o)
        
    if not observation.old_class is o.__class__:
      for listener in observation.listeners[:]: listener(o, "__class__", o.__class__, observation.old_class)
      observation.old_class = o.__class__
      
  if _has_owlready2:
    import owlready2.observe
    owlready2.observe.scan_collapsed_changes()
    

def diffdict(new, old, inexistent_value = None):
  """Returns the differences between two dictionaries.
In case of addition or deletion, old or new values are set to inexistent_value.

:param new: first dictionary to compare.
:param old: second dictionary to compare.
:param inexistent_value: value used as old or new value for deletion or addition, defaults to None.
:returns: a list of the differences between the two dictionaries, like: [(key, new_value, old_value),...]
"""
  changes = []
  
  for key, val in old.items():
    new_val = new.get(key, Ellipsis)
    if   new_val is Ellipsis: changes.append((key, inexistent_value, val))
    elif new_val != val:      changes.append((key, new_val, val))
    
  for key, val in new.items():
    old_val = old.get(key, Ellipsis)
    if old_val is Ellipsis: changes.append((key, val, inexistent_value))
    
  return changes


def find_all_children(o):
  if   isinstance(o, list): l = o
  elif isinstance(o, set) or isinstance(o, tuple) or isinstance(o, frozenset): l = list(o)
  elif isinstance(o, dict): l = list(o.keys()) + list(o.values())
  else:                     l = []
  if   hasattr(o, "__dict__"):
    if l is o: l = list(l)
    
    if isinstance(o, type): l += _get_type_properties (o)
    else:                   l += _get_class_properties(o.__class__)
    l += list(o.__dict__.values())
  return l
  
def observe_tree(o, listener, find_children = find_all_children):
  """Observes o with listener, as well as any item recursively in o (if o is a list, a dict,
or have attributes). Items added to or removed from o
or one of its items are automatically observed or unobserved.
Although called "observe_tree", it works with any nested structure of lists and dicts,
including cyclic ones.

You must use :func:`unobserve_tree` to remove the listener.

:param o: the object to observe.
:param listener: the listener.
:type listener: callable
:param find_children: optional function to call for listing the children of o.
"""
  _observe_tree(o, _TreeListener(o, listener, find_children))
  
def _observe_tree(o, listener):
  if not isobserved(o, listener): # Avoid troubles with cyclic list / dict
    observe(o, listener)
    
    children = listener.find_children(o)
    for child in children:
      _observe_tree(child, listener)
      
def unobserve_tree(o, listener, find_children = find_all_children, already = None):
  """Unregisters the given tree listener for o.

:param o: the object to observe.
:param listener: the listener, or None for unregistering *all* listeners.
:param find_children: optional function to call for listing the children of o.
"""
  if already is None: already = set()
  
  if not id(o) in already:
    already.add(id(o))
    unobserve(o, listener)
    
  children = find_children(o)
  for child in children:
    if not id(child) in already:
      unobserve_tree(child, listener, find_children, already)
      
class _TreeListener:
  def __init__(self, o, listener, find_children = find_all_children):
    self.object        = o
    self.listener      = listener
    self.find_children = find_children
    
  def __eq__(self, other): return other == self.listener
  
  def __call__(self, o, type, new, old):
    if   type is list:
      for item in old:
        if not item in new: unobserve_tree(item, self)
        
      for item in new:
        if not item in old: _observe_tree (item, self)
        
    elif (type is dict) or (type is object):
      _new = new.values()
      _old = old.values()
      for item in _old:
        if not item in _new: unobserve_tree(item, self)

      for item in _new:
        if not item in _old: _observe_tree (item, self)
        
    self.listener(o, type, new, old)

