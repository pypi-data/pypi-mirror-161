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
editobj3.field: Fields for attribute pane
-----------------------------------------

This module provides the field used by Editobj3 for editing the various attributes in the attribute panes.
For assigning a given class of field to an attribute, see :mod:`editobj3.instrosp`

The following field classes are the simplest; they do not allow editon:

.. autoclass:: HiddenField
.. autoclass:: LabelField
.. autoclass:: ProgressBarField

The following field classes allow the edition of the basic data types:

.. autoclass:: BoolField
.. autoclass:: IntField
.. autoclass:: FloatField
.. autoclass:: StringField
.. autoclass:: TextField
.. autofunction:: RangeField
.. autofunction:: EnumField

The following field classes are specialized string editors:

.. autoclass:: PasswordField
.. autoclass:: FilenameField
.. autoclass:: DirnameField
.. autoclass:: URLField

The following field classes allow the edition of lists of various data types:

.. autoclass:: IntListField
.. autoclass:: FloatListField
.. autoclass:: StringListField
.. autofunction:: EnumListField

The following field classes allow the edition of object attributes and lists of objects:

.. autoclass:: ObjectAttributeField
.. autoclass:: ObjectSelectorField
.. autoclass:: ObjectListField

.. class:: HierarchyOrObjectAttributeField(gui, master, o, attribute, undo_stack)

   Similar to ObjectAttributeField, but displays the attribute in the hierarchical tree if available.

.. class:: HierarchyOrObjectSelectorField(gui, master, o, attribute, undo_stack)

   Similar to ObjectSelectorField, but displays the attribute in the hierarchical tree if available.

.. class:: HierarchyOrObjectListField(gui, master, o, attribute, undo_stack)

   Similar to ObjectListField, but displays the attribute in the hierarchical tree if available.

.. class:: HierarchyAndObjectAttributeField

   Similar to ObjectAttributeField, but displays the attribute **both** in the hierarchical tree **and** in the attribute pane.

.. class:: HierarchyAndObjectSelectorField

   Similar to ObjectSelectorField, but displays the attribute **both** in the hierarchical tree **and** in the attribute pane.

.. class:: HierarchyAndObjectListField

   Similar to ObjectListField, but displays the attribute **both** in the hierarchical tree **and** in the attribute pane.

"""


import sys, collections, locale
import editobj3, editobj3.introsp as introsp, editobj3.undoredo as undoredo, editobj3.observe as observe

def _field(display_in_hierarchy_pane = False, display_in_attribute_pane = False, object_field = False, multiple_object_field = False):
  def _f(x):
    x.display_in_hierarchy_pane = display_in_hierarchy_pane
    x.display_in_attribute_pane = display_in_attribute_pane
    x.object_field              = object_field
    x.multiple_object_field     = multiple_object_field
    return x
  return _f

def fixed_pane_field(field_class, display_in_hierarchy_pane, display_in_attribute_pane):
  @_field(display_in_hierarchy_pane, display_in_attribute_pane, field_class.object_field, field_class.multiple_object_field)
  def _Field(gui, master, o, attribute, undo_stack):
    return field_class(gui, master, o, attribute, undo_stack)
  return _Field

def fixed_pane_field(field_class, display_in_hierarchy_pane, display_in_attribute_pane):
  @_field(display_in_hierarchy_pane, display_in_attribute_pane, field_class.object_field, field_class.multiple_object_field)
  class _FieldClass:
    def __repr__(self): return "<%s, on hierarchy pane %s, on attribute pane %s>" % (field_class.__name__, display_in_hierarchy_pane, display_in_attribute_pane)
    def __call__(self, gui, master, o, attribute, undo_stack):
      return field_class(gui, master, o, attribute, undo_stack)
  return _FieldClass()

class MultiGUIWidget(object):
  def __new__(klass, gui = None, *args, **kargs):
    if gui is None: gui = editobj3.GUI
    if not klass.__name__.startswith(gui):
      klass = getattr(__import__(getattr(klass, "_%s_MODULE" % gui), fromlist = [""]), gui + klass.__name__)
    return super().__new__(klass)
    
@_field(display_in_attribute_pane = True)
class Field(object):
  def __init__(self, gui, master, o, attribute, undo_stack):
    self.o          = o
    self.attribute  = attribute
    self.master     = master
    self.undo_stack = undo_stack
    self.updating   = 0
    
  def edit(self, o):
    self.o          = o
    self.update()
    
  def update   (self): pass
  def get_value(self): return self.attribute.get_value_for(self.o)
  def set_value(self, value):
    if self.updating: return
    self.updating += 1
    try:
      if isinstance(self.o, introsp.ObjectPack):
        objects_old_values = [(self.o.objects[i], introsp.description_for_object(self.o.objects[i])._get_attribute(self.attribute.name).get_value_for(self.o.objects[i]))
                              for i in range(len((self.o.objects))) if self.attribute.name in self.o.attrs[i]]
        objects_old_values = [(o, old_value) for (o, old_value) in objects_old_values if old_value != value]
        if not objects_old_values: return # No change
        def do_it  ():
          for o, old_value in objects_old_values: introsp.description_for_object(o)._get_attribute(self.attribute.name).set_value_for(o, value)
        def undo_it():
          for o, old_value in objects_old_values: introsp.description_for_object(o)._get_attribute(self.attribute.name).set_value_for(o, old_value)
      else:
        old_value = self.attribute.get_value_for(self.o)
        if old_value == value: return # No change
        #def do_it  (): self.attribute.set_value_for(self.o, value)
        #def undo_it(): self.attribute.set_value_for(self.o, old_value)
        do_it, undo_it = self.gen_do_it_undo_it(self.o, old_value, value)
      a = undoredo.UndoableOperation(do_it, undo_it, editobj3.TRANSLATOR("change of %s") % self.attribute.label, self.undo_stack)
    finally: self.updating -= 1
    
  def gen_do_it_undo_it(self, o, old_value, value):
    def do_it  (): self.attribute.set_value_for(o, value)
    def undo_it(): self.attribute.set_value_for(o, old_value)
    return do_it, undo_it
    
@_field()
class HiddenField(Field):
  """A field that is not displayed. Use it whenever you want to hide an attribute."""

class CoalescedChangeField(Field):
  def __init__(self, gui, master, o, attribute, undo_stack):
    Field.__init__(self, gui, master, o, attribute, undo_stack)
    self.last_undoable = None
    
  def set_value(self, value):
    if self.updating: return
    Field.set_value(self, value)
    
    if (len(self.undo_stack.undoables) >= 2) and (self.undo_stack.undoables[-2] is self.last_undoable):
      self.undo_stack.undoables[-1].coalesce_with(self.last_undoable)
    if self.undo_stack.undoables: # Can be empty when undoing / redoing
      self.last_undoable = self.undo_stack.undoables[-1]

      
    
class MultiGUIField(Field, MultiGUIWidget):
  _Gtk_MODULE    = "editobj3.field_gtk"
  _Qt_MODULE     = "editobj3.field_qt"
  _HTML_MODULE   = "editobj3.field_html"

  
class LabelField(MultiGUIField):
  """A field that displays the attribute's value, without allowing the user to modify the value."""
  def get_value(self):
    v = Field.get_value(self)
    if v is introsp.NonConsistent: return ""
    return str(v)
    
class EntryField(MultiGUIField):
  def format_func(self, v): return repr(v)
  def parse_func (self, s): return editobj3.eval(s)
  
  def get_value(self):
    v = Field.get_value(self)
    if v is introsp.NonConsistent: return ""
    return self.format_func(v)
  
  def set_value(self, s):
    if  (s == "") and self.attribute.allow_none: s = None
    elif s and (s[0] != "<"):
      try: s = self.parse_func(s)
      except: sys.excepthook(*sys.exc_info()); return
    Field.set_value(self, s)
    
class IntField(EntryField):
  """A field for editing an int. Displays as a one-line text field for entering an integer."""
  def format_func(self, v): return str(v)
  def parse_func (self, s): return int(editobj3.eval(s))
  
class FloatField(EntryField):
  """A field for editing a float. Displays as a one-line text field for entering a float number."""
  def format_func(self, v): return str(v)
  def parse_func (self, s): return float(editobj3.eval(s.replace(",", ".")))
  
class StringField(EntryField):
  """A field for editing a string  (without breakline). Displays as a one-line text field for entering a string."""
  def format_func(self, v):
    if v is None: return ""
    return str(v)
  def parse_func (self, s): return str(s)
  
class PasswordField(StringField): """A field for entering a password. Displays as a one-line text field whoose value is hidden value."""
class TextField    (StringField): """A field for editing a string (with breakline). Displays as a multi-line text field for entering a string."""

class EntryListField(EntryField):
  def get_value(self):
    v = Field.get_value(self)
    if v is introsp.NonConsistent: return ""
    return "\n".join(self.format_func(i) for i in v)
  def set_value(self, s):
    try: s = [self.parse_func(i) for i in s.split("\n") if i.strip()]
    except: return
    Field.set_value(self, s)
    
class IntListField(EntryListField):
  """A field for editing a list of integers. Displays as a multi-line text field (one item per line)."""
  def format_func(self, v): return str(v)
  def parse_func (self, s): return int(editobj3.eval(s))

class FloatListField(EntryListField):
  """A field for editing a list of float numbers. Displays as a multi-line text field (one item per line)."""
  def format_func(self, v): return str(v)
  def parse_func (self, s): return float(editobj3.eval(s.replace(",", ".")))
    
class StringListField(EntryListField):
  """A field for editing a list of strings (without breakline). Displays as a multi-line text field (one item per line)."""
  def format_func(self, v): return str(v)
  def parse_func (self, s): return str(s)
  
class _WithButtonField(MultiGUIField):
  def __init__(self, gui, master, o, attribute, undo_stack, field_class = None, button_text = None, on_button = None):
    super().__init__(gui, master, o, attribute, undo_stack)
    self.string_field = (field_class or StringField)(gui, self, o, attribute, undo_stack)
    if not button_text is None: self.button_text = button_text
    if on_button: self.on_button = on_button
    
  def update(self): self.string_field.update()
  
  def edit(self, o):
    self.o = o
    self.string_field.edit(o)
    
class FilenameField(_WithButtonField):
  """A field for editing a filename. Displays as a one-line text field with a button for opening a file."""
  button_text = "..."
class DirnameField (_WithButtonField):
  """A field for editing a directory name. Displays as a one-line text field with a button for choosing a directory."""
  button_text = "..."
class URLField     (_WithButtonField):
  """A field for editing an URL. Displays as a one-line text field with a button for opening the URL in a web browser."""
  button_text = "Goto"
  def on_button(self, o, field, undo_stack):
    import webbrowser
    webbrowser.open_new(self.get_value())
    
def WithButtonField(field_class, button_text, on_button):
  """Creates a new field class, by adding a button at the right of the given field.

:param field_class: the field class to extend.
:param button_text: the text displayed on the button.
:param on_button: a callable called when the button is clicked, with 3 arguments: the object currently edited,
                  the field, and the undo stack.
:returns: a new field class."""
  @_field(display_in_attribute_pane = True)
  def f(gui, master, o, attribute, undo_stack):
    return _WithButtonField(gui, master, o, attribute, undo_stack, field_class, button_text, on_button)
  return f


class BoolField(MultiGUIField):
  """A field for editing a boolean attribute. Displays as a checkbox."""
  def set_value(self, value):
    if isinstance(self.o, introsp.ObjectPack):
      old = introsp.description_for_object(self.o.objects[0])._get_attribute(self.attribute.name).get_value_for(self.o.objects[0])
    else:
      old = introsp.description_for_object(self.o)._get_attribute(self.attribute.name).get_value_for(self.o)
    if (old is True) or (old is False): value = bool(value)
    elif value: value = True
    else:       value = False
    MultiGUIField.set_value(self, value)
    
class ProgressBarField(MultiGUIField):
  """A field for showing completion of a task, expressed by a float attribute between 0.0 and 1.0.
Displays as a progressbar."""
  def get_value(self):
    v = Field.get_value(self)
    if v is introsp.NonConsistent: return v
    return float(v)
      

def RangeField(min, max, incr = 0):
  """A field for editing an integer or float attribute in a given range. Displays as a slider.
The choice of integer or float depends on the value passed to the function.

:param min: minimum allowed value.
:param max: maximum allowed value.
:param incr: default increments."""
  if incr == 0:
    incr = (max - min) / 5.0
    if isinstance(max, int):
      incr = int(incr)
      if incr < 1: incr = 1
  @_field(display_in_attribute_pane = True)
  def _Field(gui, master, o, attribute, undo_stack):
    return _RangeField(gui, master, o, attribute, undo_stack, min, max, incr)
  return _Field
  
class _RangeField(MultiGUIField, CoalescedChangeField):
  def __init__(self, gui, master, o, attribute, undo_stack, min, max, incr = 1):
    super().__init__(gui, master, o, attribute, undo_stack)
    self.min = min
    self.max = max
    self.update()
    
  def get_value(self):
    v = Field.get_value(self)
    if v is introsp.NonConsistent: return self.min
    return v
    
  def set_value(self, v):
    if isinstance(self.max, int): v = int(round(float(v)))
    else:                         v = float(v)
    Field.set_value(self, v)


def _prepare_choices(choices, translate = True):
  r = choices
  
  if   isinstance(choices, list):
    r = collections.OrderedDict()
    if translate:
      for i in choices: r[editobj3.TRANSLATOR(str(i))] = i
    else:
      for i in choices: r[str(i)] = i
      
  elif isinstance(choices, set):
    if translate: r = { editobj3.TRANSLATOR(str(i)) : i for i in choices }
    else:         r = { str(i)                      : i for i in choices }
    
  elif isinstance(choices, collections.OrderedDict):
    if translate:
      r = collections.OrderedDict()
      for key, value in choices.items(): r[editobj3.TRANSLATOR(str(key))] = value
      
  elif isinstance(choices, dict):
    if translate: r = { editobj3.TRANSLATOR(str(key)) : value for key, value in choices.items() }
    
  return r
  
def EnumField(choices, value_2_enum = None, enum_2_value = None, long_list = None, translate = True, allow_multiple_selection = False):
  """A field for editing attributes that can take a fixed set of possible values.
Displays as a drop-down box or a list.

:param choices: the list of possible choices. Can be a list of value, a dictionary, or a callable
                that takes one parameter (the object edited) and returns the allowed values.
:param value_2_enum: an optional function that maps choice value to their enum label, such as: map_value_to_enum_for_object(object, value) -> enum
:param enum_2_value: an optional function that maps enum label to the corresponding value, such as: map_enum_to_value_for_object(object, enum) -> value
:param long_list: if True, displays as a list. If False, displays as a drop-down box.
                  If None, Editobj3 choose automatically depending on the number of items.
:param translate: if True, the enum value are translated using :func:`editobj3.TRANSLATOR()`.
"""
  choices = _prepare_choices(choices, translate)
  @_field(display_in_attribute_pane = True)
  def _Field(gui, master, o, attribute, undo_stack):
    if callable(choices): my_choices = _prepare_choices(choices(o), translate)
    else: my_choices = choices
    if allow_multiple_selection:
      return _EnumListField (gui, master, o, attribute, undo_stack, my_choices, value_2_enum, enum_2_value)
    if long_list or ((long_list is None) and (len(my_choices) > 30)):
      return _LongEnumField (gui, master, o, attribute, undo_stack, my_choices, value_2_enum, enum_2_value)
    else:
      return _ShortEnumField(gui, master, o, attribute, undo_stack, my_choices, value_2_enum, enum_2_value)
  return _Field
  
def EnumListField(choices, value_2_enum = None, enum_2_value = None, translate = True):
  """A field for editing a set or a list that is a subset of a fixed set of possible values.
Displays as a list. This field is similar to :class:`EnumField` but allows multiple selection.

:param choices: the list of possible choices. Can be a list of value, a dictionary, or a callable
                that takes one parameter (the object edited) and returns the allowed values.
                Hint: use an ordered dict if you want to preserve order.
:param value_2_enum: an optional function that maps choice value to their enum label, such as: map_value_to_enum_for_object(object, value) -> enum
:param enum_2_value: an optional function that maps enum label to the corresponding value, such as: map_enum_to_value_for_object(object, enum) -> value
:param translate: if True, the enum value are translated using :func:`editobj3.TRANSLATOR()`.
"""
  return EnumField(choices, value_2_enum, enum_2_value, None, translate, True)

class _EnumField(MultiGUIField):
  def __init__(self, gui, master, o, attribute, undo_stack, choices, value_2_enum = None, enum_2_value = None):
    super().__init__(gui, master, o, attribute, undo_stack)
    self.choices        = choices
    self.choice_keys    = list(choices.keys())
    if not isinstance(choices, collections.OrderedDict): self.choice_keys.sort(key = locale.strxfrm)
    self.choice_2_index = { choice : self.choice_keys.index(key) for (key, choice) in self.choices.items() }
    self.value_2_enum   = value_2_enum
    self.enum_2_value   = enum_2_value
    
  def get_value(self):
    value = Field.get_value(self)
    if self.value_2_enum: value = self.value_2_enum(self.o, value)
    return value
    
  def set_value(self, enum):
    if self.enum_2_value: enum = self.enum_2_value(self.o, enum)
    Field.set_value(self, enum)
    
class _ShortEnumField(_EnumField): pass
class _LongEnumField (_EnumField): pass

class _EnumListField(_EnumField):
  def get_value(self):
    value = Field.get_value(self)
    if self.value_2_enum: value = [self.value_2_enum(self.o, enum) for enum in value]
    return value
    
  def set_value(self, enums):
    if self.enum_2_value: enums = [self.enum_2_value(self.o, enum) for enum in enums]
    Field.set_value(self, enums)

@_field(object_field = True)
class ObjectField(MultiGUIField): pass
  
@_field(object_field = True, multiple_object_field = False)
class SingleObjectField(ObjectField): pass

@_field(display_in_hierarchy_pane = False, display_in_attribute_pane = True, object_field = True, multiple_object_field = False)
class ObjectAttributeField(SingleObjectField):
  """A field for editing an object. Displays as an attribute panel embedded inside the main attribute panel.
The attribute is **not** displayed in the tree."""
  def __init__(self, gui, master, o, attribute, undo_stack):
    super().__init__(gui, master, o, attribute, undo_stack)
    import editobj3.editor as editor
    self.attribute_pane = editor.AttributePane(gui, self)
    self.update()
    
  def update(self):
    self.updating += 1
    try:
      v = self.attribute.get_value_for(self.o)
      if (v is introsp.NonConsistent) and isinstance(self.o, introsp.ObjectPack):
        v = introsp.ObjectPack([introsp.description_for_object(self.o.objects[i])._get_attribute(self.attribute.name).get_value_for(self.o.objects[i])
                               for i in range(len(self.o.objects))
                               if self.attribute.name in self.o.attrs[i]])
      self.attribute_pane.edit(v)
    finally: self.updating -= 1
    
@_field(display_in_hierarchy_pane = False, display_in_attribute_pane = True, object_field = True, multiple_object_field = False)
class ObjectSelectorField(SingleObjectField):
  """A field for editing an object attribute. Display as a drop-down box for choosing the object in a list
and a button for editing the object. The list of possible values is determined using :mod:`editobj3.introsp`
and more specifically the addable_values parameter. The attribute is **not** displayed in the tree."""
  def __init__(self, gui, master, o, attribute, undo_stack):
    super().__init__(gui, master, o, attribute, undo_stack)
    self.update()
    
  def __del__(self):
    try: # May cause error when called during program exit
      observe.unobserve(self.get_value(), self._value_listener)
    except:
      pass
    
  def edit(self, o):
    observe.unobserve(self.get_value(), self._value_listener)
    super().edit(o)
    observe.observe(self.get_value(), self._value_listener)
    
  def set_value(self, value):
    if isinstance(value, introsp.NewInstanceOf): value = value.create_new(self.o)
    observe.unobserve(self.get_value(), self._value_listener)
    super().set_value(value)
    observe.observe(value, self._value_listener)
    
  def _value_listener(self,obj, type, new, old): pass
  
  def get_addable_values(self):
    addable_values = self.attribute.addable_values_to(self.o)
    value          = self.get_value()
    if not value in addable_values: addable_values.insert(0, value)
    return addable_values
    

@_field(display_in_hierarchy_pane = False, display_in_attribute_pane = True, object_field = True, multiple_object_field = True)
class MultipleObjectField(ObjectField): pass

@_field(display_in_hierarchy_pane = False, display_in_attribute_pane = True, object_field = True, multiple_object_field = True)
class ObjectListField(MultipleObjectField):
  """A field for editing a list of objects. Display as a list with button for adding, moving and removing the
objects.  The list of possible values is determined using :mod:`editobj3.introsp`
and more specifically the addable_values parameter. The attribute is **not** displayed in the tree."""
  def __init__(self, gui, master, o, attribute, undo_stack):
    super().__init__(gui, master, o, attribute, undo_stack)
    import editobj3.editor as editor
    self.hierarchy_pane = editor.HierarchyPane(gui, self, self.edit_child, undo_stack, attribute, 1)
    self.childhood_pane = editor.ChildhoodPane(gui, self, undo_stack, attribute)
    self.hierarchy_pane.set_childhood_pane(self.childhood_pane, o, attribute)
    self.update()
    
  def edit_child(self, o, ignored_attrs = None): pass
  
  def edit(self, o):
    self.hierarchy_pane.set_childhood_pane(self.childhood_pane, o, self.attribute)
    self.hierarchy_pane.edit(o)
    super().edit(o)
  
  def update(self):
    self.hierarchy_pane.edit(self.o)
    
HierarchyOrObjectAttributeField = fixed_pane_field(ObjectAttributeField, True, False)
HierarchyOrObjectSelectorField  = fixed_pane_field(ObjectSelectorField , True, False)
HierarchyOrObjectListField      = fixed_pane_field(ObjectListField     , True, False)

HierarchyAndObjectAttributeField = fixed_pane_field(ObjectAttributeField, True, True)
HierarchyAndObjectSelectorField  = fixed_pane_field(ObjectSelectorField , True, True)
HierarchyAndObjectListField      = fixed_pane_field(ObjectListField     , True, True)
