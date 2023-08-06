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

import editobj3
from editobj3.field      import *
from editobj3.html_utils import *
from editobj3.field import _WithButtonField, _RangeField, _ShortEnumField, _LongEnumField, _EnumListField

FIELD_JS = ""

class HTMLField(MultiGUIField):
  y_flags = "fill"
  def __init__(self, gui, master, o, attribute, undo_stack, *args):
    super().__init__(gui, master, o, attribute, undo_stack, *args)
    self._id = master.get_user().obj2id(self)
    self.need_update = 0
    
  def get_user(self): return self.master.get_user()
  
  def get_html       (self): return ""
  def get_ready_js   (self): return ""
  def get_update_js  (self): return ""
  def clear_update   (self): self.need_update = 0
  def get_need_update(self): return self.need_update
  def update         (self):
    if not hasattr(self, "_id"): return # we are updating during __init__
    self.need_update = 1
    

class HTMLHiddenField(HTMLField, HiddenField): pass
  
class HTMLLabelField(HTMLField, LabelField):
  def __init__(self, gui, master, o, attribute, undo_stack):
    super().__init__(gui, master, o, attribute, undo_stack)
    
  def get_html(self):
    return """<span id="%s">%s</span>""" % (self._id, html_escape(str(self.get_value())))
  
  def get_update_js(self):
    return """BYID("%s").html = "%s";""" % (self._id, js_escape(self.get_value()))
    

FIELD_JS += """function on_Field_changed(self) { ws.send(JSON.stringify(["setattr", self.id, self.value])); };\n"""

class HTMLEntryField(HTMLField, EntryField):
  def get_html(self): 
    return """<input id="%s" type="text" value="%s" onchange="on_Field_changed(this);" style="width:100%%;"/>""" % (self._id, html_escape_arg(self.get_value()))
    
  def get_update_js(self):
    return """BYID("%s").value = "%s";""" % (self._id, js_escape(self.get_value()))
    
class HTMLTextField(HTMLField, TextField):
  y_flags = "expand"
  def get_html(self):
    return """<textarea id="%s" onchange="on_Field_changed(this);" style="width:100%%;">%s</textarea>""" % (self._id, html_escape(str(self.get_value())))
    
  def get_update_js(self):
    return """BYID("%s").value = "%s";""" % (self._id, js_escape(self.get_value()))
    
    
class HTMLIntField   (HTMLEntryField, IntField   ): pass # XXX no "spin-button" since they don't allow entering e.g. "1 + 2" as an integer !
class HTMLFloatField (HTMLEntryField, FloatField ): pass
class HTMLStringField(HTMLEntryField, StringField): pass

class HTMLPasswordField(HTMLStringField, PasswordField):
  def get_html(self): 
    return """<input id="%s" type="password" value="%s" onchange="on_Field_changed(this);" style="width:100%%;"/>""" % (self._id, html_escape_arg(self.get_value()))


class HTMLEntryListField (HTMLTextField, EntryListField ): pass
class HTMLIntListField   (HTMLTextField, IntListField   ): pass
class HTMLFloatListField (HTMLTextField, FloatListField ): pass
class HTMLStringListField(HTMLTextField, StringListField): pass

def with_button_html(widget, on_button, button_text):
  return u"""<table cellspacing="0" style="width: 100%%;"><tr style="width: 100%%;"><td style="padding: 0px; width: 78%%">%s<td onclick="%s" class="editobj-button" style="margin-left: 20px; width: 20%%;"/>%s</td></tr></table>""" % (widget, on_button, button_text)

FIELD_JS += """function on_Button_clicked(id) { ws.send(JSON.stringify(["click", id])); };\n"""

class HTML_WithButtonField(HTMLField, _WithButtonField):
  #def __init__(self, gui, master, o, attribute, undo_stack, field_class = None, button_text = None, on_button = None):
  #  super().__init__(gui, master, o, attribute, undo_stack, field_class, button_text, on_button)
  def get_html(self): 
    return with_button_html(self.string_field.get_html(), """on_Button_clicked("%s")""" % self._id, html_escape_arg(editobj3.TRANSLATOR(self.button_text)))
    #return """%s<input id="%s" type="button" value="%s" onclick="on_Button_clicked(this.id);"/>""" % (self.string_field.get_html(), self._id, html_escape_arg(editobj3.TRANSLATOR(self.button_text)))
    
  def update(self): self.string_field.update()
  
  def get_need_update(self): return self.string_field.get_need_update() # Needed because attribute pane need_update can be false while some of its fields need update
  
  def get_update_js(self): return self.string_field.get_update_js()
    
  def clear_update(self):
    super().clear_update()
    self.string_field.clear_update()
    
  def on_click(self): self.on_button(self.o, self, self.undo_stack)
  
class HTMLFilenameField(HTML_WithButtonField, FilenameField):
  def on_button(self, o, field, undo_stack):
    pass # XXX
    
class HTMLDirnameField(HTML_WithButtonField, DirnameField):
  def on_button(self, o, field, undo_stack):
    pass # XXX
    
class HTMLURLField(HTML_WithButtonField, URLField):
  def on_button(self, o, field, undo_stack):
    self.get_user().add_update("""window.open("%s", "_blank");""" % (js_escape(self.get_value())))
    

FIELD_JS += """function on_Bool_changed(self) { ws.send(JSON.stringify(["setattr", self.id, self.checked])); };\n"""

class HTMLBoolField(HTMLField, BoolField):
  def get_value(self):
    if super().get_value(): return "checked"
    else:                 return ""
    
  def get_html(self):
    if self.get_value() == "checked": v = ' checked="checked"'
    else:                             v = ""
    return """<input id="%s" type="checkbox"%s onchange="on_Bool_changed(this);"/>""" % (self._id, v)
    
  def get_update_js(self):
    return """BYID("%s").checked = "%s";""" % (self._id, self.get_value())
    

class HTMLProgressBarField(HTMLField, ProgressBarField):
  def get_value(self): return "%s%%" % int(round(super().get_value() * 100.0))
  
  def get_html(self):
    return """<span id="%s">%s</span>""" % (self._id, html_escape(str(self.get_value())))
    
  def get_update_js(self):
    return """BYID("%s").html = "%s";""" % (self._id, self.get_value())
    
    
class HTML_RangeField(HTMLField, _RangeField):
  def __init__(self, gui, master, o, attribute, undo_stack, min, max, incr = 1):
    super().__init__(gui, master, o, attribute, undo_stack, min, max, incr)
    self.min = min
    self.max = max
    
  def get_html(self): 
    return u"""<input id="%s" type="range" value="%s" min="%s" max="%s" onchange="on_Field_changed(this);" style="width:100%%;"/>""" % (self._id, self.get_value(), self.min, self.max)
    
  def get_update_js(self):
    return """BYID("%s").value = "%s";""" % (self._id, self.get_value())
    
    
class HTML_ShortEnumField(HTMLField, _ShortEnumField):
  def set_value(self, value): super().set_value(self.choices[self.choice_keys[int(value)]])
    
  def get_html(self):
    index = self.choice_2_index.get(self.get_value())
    options = "".join("""<option value="%s"%s>%s</option>""" % (i, ' selected="selected"' if i == index else "", html_escape(self.choice_keys[i])) for i in range(len(self.choice_keys)))
    return u"""<select id="%s" onchange="on_Field_changed(this);" style="width:100%%; background-color: #FFFFFF;">%s</select>""" % (self._id, options)
    
  def get_update_js(self):
    return """BYID("%s").value = "%s";""" % (self._id, self.choice_2_index.get(self.get_value()))
    
class HTML_LongEnumField(HTMLField, _LongEnumField):
  y_flags = "expand"
  def set_value(self, value): super().set_value(self.choices[self.choice_keys[int(value)]])
    
  def get_html(self):
    index   = self.choice_2_index.get(self.get_value())
    options = "".join("""<option value="%s"%s>%s</option>""" % (i, ' selected="selected"' if i == index else "", html_escape(self.choice_keys[i])) for i in range(len(self.choice_keys)))
    size    = min(6, len(self.choices))
    return u"""<select id="%s" size="%s" onchange="on_Field_changed(this);" style="width:100%%; background-color: #FFFFFF;">%s</select>""" % (self._id, size, options)

  def get_update_js(self):
    return """BYID("%s").value = "%s";""" % (self._id, self.choice_2_index.get(self.get_value()))
    


FIELD_JS += """
function on_EnumList_changed(self) {
  var values = new Array();
  for (i in self.options) {
    if (self.options[i].selected) { values.push(i); }
  }
  ws.send(JSON.stringify(["setattr", self.id, values]));
};\n"""

class HTML_EnumListField(HTMLField, _EnumListField):
  y_flags = "expand"
  def set_value(self, value): super().set_value([self.choices[self.choice_keys[int(i)]] for i in value])
  
  def get_html(self):
    index   = set(self.choice_2_index.get(value) for value in self.get_value())
    options = "".join("""<option value="%s"%s>%s</option>""" % (i, ' selected="selected"' if i in index else "", html_escape(self.choice_keys[i])) for i in range(len(self.choice_keys)))
    size    = min(6, len(self.choices))
    return u"""<select id="%s" multiple="multiple" size="%s" onchange="on_EnumList_changed(this);" style="width:100%%;">%s</select>""" % (self._id, size, options)
    
  def get_update_js(self):
    values = self.get_value()
    user   = self.get_user()
    js     = """var self = BYID("%s");""" % self._id
    if values is introsp.NonConsistent: values = []
    self.indexes = { self.choice_2_index.get(value) for value in values }
    for i in range(len(self.choices)):
      js += """\nself.options[%s].selected = %s;""" % (i, str(i in self.indexes).lower())
    return js
    

class HTMLObjectAttributeField(HTMLField, ObjectAttributeField):
  def get_html(self): return self.attribute_pane.get_html()
  
  def get_ready_js(self): return self.attribute_pane.get_ready_js()
  
  def update(self): ObjectAttributeField.update(self)
  
  def get_need_update(self): return True # Needed because attribute pane need_update can be false while some of its fields need update
  
  def get_update_js(self): return self.attribute_pane.get_update_js()
    
  def clear_update(self):
    super().clear_update()
    self.attribute_pane.clear_update()

FIELD_JS += """
function on_Selector_changed(self) {
  ws.send(JSON.stringify(["setattr", self.id, self.value]));
  self.style.background = self.options[self.value].style.background;
};\n"""

class HTMLObjectSelectorField(HTMLField, ObjectSelectorField):
  def __init__(self, gui, master, o, attribute, undo_stack):
    self.current_addable_values = None
    super().__init__(gui, master, o, attribute, undo_stack)
    
  def set_value(self, value): super().set_value(self.current_addable_values[int(value)])
  
  def get_html(self):
    self.current_addable_values = self.get_addable_values()
    value = self.get_value()
    descr = introsp.description_for_object(value)
    icon_filename = descr.icon_filename_for(value)
    if isinstance(icon_filename, list): icon = icon[0] # Not yet supported
    if isinstance(icon_filename, str ): icon = '''background:url('%s') no-repeat 1px 1px; background-size: contain; ''' % (editobj3.editor_html.load_small_icon(icon_filename))
    else:                               icon = ""
    #return u"""<select id="%s" onchange="on_Selector_changed(this);" style="%spadding-left: %spx; background-color: #FFFFFF; width:78%%;">%s</select><input type="button" value="%s" onclick="on_Button_clicked('%s');" style="width:22%%; height:100%%;"/>""" % (self._id, icon, editobj3.editor_html.SMALL_ICON_SIZE + 10, self.get_inner_html(self.current_addable_values), editobj3.TRANSLATOR("Edit..."), self._id)
    #return u"""<div><select id="%s" onchange="on_Selector_changed(this);" style="%spadding-left: %spx; background-color: #FFFFFF; width:78%%;">%s</select><div class="editobj-button" onclick="on_Button_clicked('%s');" style="width:22%%; float:right; display:inline-block;">%s</div></div>""" % (self._id, icon, editobj3.editor_html.SMALL_ICON_SIZE + 10, self.get_inner_html(self.current_addable_values), self._id, editobj3.TRANSLATOR("Edit..."))
    #return """<table cellspacing="0" style="width: 100%%;"><tr style="width: 100%%;"><td style="padding: 0px; width: 78%%"><select id="%s" onchange="on_Selector_changed(this);" style="%spadding-left: %spx; background-color: #FFFFFF; width:99%%;">%s</select><td onclick="on_Button_clicked('%s');" class="editobj-button" style="margin-left: 20px; width: 20%%;"/>%s</td></tr></table>""" % (self._id, icon, editobj3.editor_html.SMALL_ICON_SIZE + 10, self.get_inner_html(self.current_addable_values), self._id, editobj3.TRANSLATOR("Edit..."))
    return with_button_html("""<select id="%s" onchange="on_Selector_changed(this);" style="%spadding-left: %spx; background-color: #FFFFFF; width:99%%;">%s</select>""" % (self._id, icon, editobj3.editor_html.SMALL_ICON_SIZE + 10, self.get_inner_html(self.current_addable_values)), "on_Button_clicked('%s');" % self._id, editobj3.TRANSLATOR("Edit..."))
      
  def get_inner_html(self, current_addable_values):
    index = current_addable_values.index(self.get_value())
    html  = ""
    for i in range(len(current_addable_values)):
      value = current_addable_values[i]
      descr = introsp.description_for_object(value)
      icon_filename = descr.icon_filename_for(value)
      if isinstance(icon_filename, list): icon = icon[0] # Not yet supported
      if isinstance(icon_filename, str ): icon = ''' style="background:url('%s') no-repeat 1px 1px white; background-size: contain; height: %spx; padding-left: %spx; padding-top: 2px"''' % (editobj3.editor_html.load_small_icon(icon_filename), editobj3.editor_html.SMALL_ICON_SIZE + 1, editobj3.editor_html.SMALL_ICON_SIZE + 10)
      else:                               icon = ""
      html += """<option value="%s"%s%s>%s</option>""" % (i, ' selected="selected"' if i == index else "", icon, html_escape(descr.label_for(value)))
    return html
    
  def get_update_js(self):
    if not hasattr(self, "_id"): return # we are updating during __init__
    current_addable_values = self.get_addable_values()
    if current_addable_values != self.current_addable_values:
      #self.current_addable_values = current_addable_values # Not here, since update should not modify the field (since if can be displayed in several browser windows)
      js = """BYID("%s").innerHTML = "%s";""" % (self._id, js_escape(self.get_inner_html(current_addable_values)))
    else: js = ""
    index = current_addable_values.index(self.get_value())
    js += """
var self = BYID("%s");
self.value = "%s";
self.style.background = self.options[self.value].style.background;
""" % (self._id, index)
    return js
    
  def clear_update(self):
    super().clear_update()
    self.current_addable_values = self.get_addable_values() # Not here, since update should not modify the field (since if can be displayed in several browser windows)
    
  def on_click(self):
    # XXX
    editobj3.edit(self.get_value(), master = self, undo_stack = self.undo_stack)
    
  def _value_listener(self, obj, type, new, old):
    self.update()
    
  def __del__(self):
    observe.unobserve(self.get_value(), self._value_listener)
    

class HTMLObjectListField(HTMLField, ObjectListField):
  y_flags = "expand"
  def __init__(self, gui, master, o, attribute, undo_stack):
    super().__init__(gui, master, o, attribute, undo_stack)
    
  def get_html(self): return """<div id="%s">%s</div>""" % (self._id, self.get_inner_html())
  
  def get_inner_html(self): return """%s%s""" % (self.childhood_pane.get_html(), self.hierarchy_pane.get_html())

  def get_ready_js(self):
    return self.hierarchy_pane.get_ready_js() + self.childhood_pane.get_ready_js()
    
  def update(self): ObjectListField.update(self)
  
  def get_need_update(self): return self.hierarchy_pane.get_need_update() or self.childhood_pane.get_need_update()
 # Needed because attribute pane need_update can be false while some of its fields need update
  
  def get_update_js(self): return self.hierarchy_pane.get_update_js() + self.childhood_pane.get_update_js()
  
  def clear_update(self):
    super().clear_update()
    self.hierarchy_pane.clear_update()
    self.childhood_pane.clear_update()
