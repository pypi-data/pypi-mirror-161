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

import string
import editobj3.introsp as introsp
from editobj3.editor     import *
from editobj3.html_utils import *

EDITOR_JS = ""

class Menu(object):
  def __init__(self, master, label, command, arg, image, type, radio_group):
    self._id = master.get_user().obj2id(self)
    self.submenus    = []
    self.label       = editobj3.TRANSLATOR(label)
    self.command     = command
    self.arg         = arg
    self.image       = image
    self.type        = type
    self.radio_group = radio_group
  
  def __len__(self): return len(self.submenus)
  
  def insert(self, pos, menu): self.submenus.insert(pos, menu)
  
  def on_click(self):
    if self.command:
      if self.arg: self.command(self.arg)
      else:        self.command()
      
  def get_json(self):
    l = ['id:"%s"' % self._id, 'caption:"%s"' % js_escape(self.label)]
    if self.submenus:
      l.append('type:"menu"')
      l.append('items:[%s]' % ",".join(submenu.get_json() for submenu in self.submenus))
    else: l.append('type:"%s"' % self.type)
    if self.image: l.append('icon:"icon%s"' % (load_small_icon(self.image).rsplit("/", 1)[-1].split(".", 1)[0]))
    if self.type == "radio": l.append('group:"%s"' % self.radio_group)
    return "{%s}" % ",".join(l)
    
    
class BaseDialog(object):
  def build_default_menubar(self):
    self.next_radio_group = 1
    self.current_radio_group = None
    
    self.file_menu = self.add_to_menu(self.menubar  , 1, u"File")
    #self.close_menu= self.add_to_menu(self.file_menu, 0, u"Close", self.on_ok)
    self.edit_menu = self.add_to_menu(self.menubar  , 1, u"Edit") # , self.on_edit_menu) # Not yet supported by W2UI for submenu
    self.undo_menu = self.add_to_menu(self.edit_menu, 0, u"Undo" , self.on_undo, accel = u"C-Z")
    self.redo_menu = self.add_to_menu(self.edit_menu, 0, u"Redo" , self.on_redo, accel = u"C-Y")
    if self.on_validate:
      self.validate_menu = self.add_to_menu(self.menubar, 0, u"Validate", self.on_click)
      
  def add_to_menu(self, menu, has_submenu, label, command = None, arg = None, accel = "", accel_enabled = 1, image = None, type = "button", pos = -1):
    if type == "radio":
      if self.current_radio_group is None:
        self.current_radio_group = self.next_radio_group
        self.next_radio_group += 1
    else: self.current_radio_group = None
    if pos == -1: pos = len(menu)
    new_menu = Menu(self, label, command, arg, image, type, self.current_radio_group)
    menu.insert(pos, new_menu)
    return new_menu
    
  def add_separator_to_menu(self, menu, pos = -1):
    self.current_radio_group = None
    if pos == -1: pos = len(menu)
    new_menu = Menu(self, "", None, None, None, "break", 0)
    menu.insert(pos, new_menu)
    return new_menu
    
  def get_menubar_json(self):
    return """
onClick: function (event) {
if (event.subItem != null)
     ws.send(JSON.stringify(['click', event.subItem.id]));
else ws.send(JSON.stringify(['click', event.target]));
}, items: [%s]""" % ",".join(menu.get_json() for menu in self.menubar)
  
  def set_menu_enable(self, menu, enable):
    self.update_js += """tb%s.%sable("%s")\n""" % (self._id, "en" if enable else "dis", menu._id)
    
  def set_menu_label (self, menu, label):
    self.update_js += """tb%s.set("%s", {caption: "%s"})\n""" % (self._id, menu._id, label)
    
  # Not yet supported by W2UI for submenu
  #def on_edit_menu(self, *args):
  #  undo = self.undo_stack.can_undo()
  #  redo = self.undo_stack.can_redo()
  #  if undo: self.set_menu_enable(self.undo_menu, 1); self.set_menu_label(self.undo_menu, "%s %s" % (editobj3.TRANSLATOR(u"Undo"), undo.name))
  #  else:    self.set_menu_enable(self.undo_menu, 0); self.set_menu_label(self.undo_menu, editobj3.TRANSLATOR(u"Undo"))
  #  if redo: self.set_menu_enable(self.redo_menu, 1); self.set_menu_label(self.redo_menu, "%s %s" % (editobj3.TRANSLATOR(u"Redo"), redo.name))
  #  else:    self.set_menu_enable(self.redo_menu, 0); self.set_menu_label(self.redo_menu, editobj3.TRANSLATOR(u"Redo"))
    
  def on_undo(self, *args):
    if self.undo_stack.can_undo(): self.undo_stack.undo()
  def on_redo(self, *args):
    if self.undo_stack.can_redo(): self.undo_stack.redo()
    
  def on_ok(self, *args):
    if self.on_close: self.on_close()
    
  def main(self, host = "127.0.0.1", port = 8080, path = "/editobj/main.html"):
    import webbrowser, editobj3.html_server
    self.master.register_url(path, self)
    def on_startup(): webbrowser.open_new(url)
    server = editobj3.html_server.EditobjServer(on_startup = on_startup)
    url    = "http://%s:%s%s" % (host, port, path)
    print("* Editobj3 * Editor dialog ready at %s !" % url)
    server.run(host, port)
    
  default_width  = 1024
  default_height =  768
  def set_default_size(self, width, height):
    self.default_width  = width
    self.default_height = height
    
  def show(self):
    user = self.get_user()
    root_editor = self
    while not isinstance(root_editor.master, User): root_editor = root_editor.master
    for ws_handler in user.ws_handlers:
      if ws_handler.editor is root_editor:
        ws_handler.dialog = self
        self.ws_handler = ws_handler
        break
    else:
      if self.is_dialog: # Dialog => must have a root editor!
        raise ValueError("Cannot find root editor / WS handler for dialog!")
        
    import editobj3.html_server
    if editobj3.html_server.APPLICATION: editobj3.html_server.APPLICATION.schedule_commit()
    
  def on_click(self):
    self.validated = True
    self.on_validate(self.get_selected_object())
    
  def on_closed(self):
    if self.on_validate and not self.validated: self.on_validate(None)
    if not self.ws_handler is None:
      self.ws_handler.dialog = None
      self.ws_handler = None
      

class HTMLEditorDialog(EditorDialog, BaseDialog):
  def __init__(self, gui = None, master = None, direction = "h", on_validate = None, edit_child_in_self = 1, undo_stack = None, on_close = None, menubar = True):
    self.master      = master or GUEST # Default to guest user
    self.menubar     = []
    super().__init__(gui, master, direction, on_validate, edit_child_in_self, undo_stack, on_close, menubar)
    self._id = self.master.get_user().obj2id(self)
    self.is_dialog   = not isinstance(self.master, User)
    self.on_close    = on_close
    self.need_update = True
    self.validated   = False
    self.update_js   = ""
    
  def get_user(self): return self.master.get_user()
  
  def get_o(self): return self.editor_pane.o
  o = property(get_o)
  
  def get_html(self):
    self.need_update = False
    if self.is_dialog: return ""
    else:
      return """
<div id="%s">
%s
</div>
""" % (self._id, self.get_inner_html())
  
  def get_inner_html(self):
    if self.menubar:
      html = """<div id="tb%s" style="padding: 2px; border-bottom: 1px solid #aaaaaa;  box-shadow: 0px 0px 5px #999; position: relative; z-index: 999;">MENUBAR</div>\n""" % self._id
    else: html = ""
    return html + self.editor_pane.get_html()
    
  READY_JS_TEMPLATE = string.Template("""
dialog$id = w2popup.open({ title: "$title", showMax: true, showClose: true, modal: $modal, buttons: "$buttons", body: "$body",
  onOpen : function (event) { event.onComplete = function () {
    $ready_js
    BYID("$editor_pane_id").style.height = (window.innerHeight - $delta_y) + "px";
    layout$editor_pane_id.resize();
  }},
  onMax: function (event) { event.onComplete = function () { layout$editor_pane_id.resize(); }},
  onMin: function (event) { event.onComplete = function () { layout$editor_pane_id.resize(); }},
  onClose: function (event) { ws.send(JSON.stringify(['closed', '$id'])); },
  width: window.innerWidth * 0.8, height: window.innerHeight
});
""")
  def get_ready_js(self):
    if self.is_dialog:
      o = self.o
      title = introsp.description_for_object(o).label_for(o).replace("\n", " ").replace("\t", " ")
      if self.on_validate:
        buttons  = """<input type="button" value="%s" onclick="w2popup.close();"/>&nbsp;&nbsp;&nbsp;""" % editobj3.TRANSLATOR("Cancel")
        buttons += """<input type="button" value="%s" onclick="ws.send(JSON.stringify(['click', '%s'])); w2popup.close();"/>""" % (editobj3.TRANSLATOR("Validate"), self._id)
      else: buttons = ""
      js = self.READY_JS_TEMPLATE.substitute(id = self._id, editor_pane_id = self.editor_pane._id,
                                             title = html_js_escape(title), modal = "true" if self.on_validate else "false",
                                             buttons = js_escape(buttons), body = js_escape(self.get_inner_html()),
                                             ready_js = self.editor_pane.get_ready_js(),
                                             width = self.default_width, height = self.default_height,
                                             delta_y = 120 if self.menubar else 100)
    else: js = self.editor_pane.get_ready_js()
    if self.menubar: js += """
tb%s = $('#tb%s').w2toolbar({ name: 'tb%s', %s});
""" % (self._id, self._id, self._id, self.get_menubar_json())
    return js
    
  def get_need_update(self): return self.need_update or self.update_js or self.editor_pane.get_need_update()
  
  def get_update_js(self):
    if self.need_update:
      if self.is_dialog: return self.get_ready_js()
      else: return """window.open("/editobj/editor.html?id=%s", "_blank");""" % self._id
    else: return self.editor_pane.get_update_js() + self.update_js
      
  def clear_update(self):
    self.need_update = False
    self.update_js   = ""
    self.editor_pane.clear_update()
    
  
class HTMLEditorTabbedDialog(EditorTabbedDialog, BaseDialog):
  def __init__(self, gui = None, master = None, direction = "h", on_validate = None, edit_child_in_self = 1, undo_stack = None, on_close = None, menubar = True):
    self.master      = master or GUEST # Default to guest user
    self.menubar     = []
    super().__init__(gui, master, direction, on_validate, edit_child_in_self, undo_stack, on_close, menubar)
    self._id = self.master.get_user().obj2id(self)
    self.is_dialog   = not isinstance(self.master, User)
    self.on_close    = on_close
    self.need_update = True
    self.validated   = False
    self.update_js   = ""
    self.current_tab = 0
    self.tab_labels  = []
    self.tabs        = []
    
  def add_tab(self, name, label, o = None):
    # XXX does not support adding / removing tabs after showing the dialog box / page
    editor_pane = super().add_tab(name, label, o)
    self.tab_labels.append(label)
    self.tabs.append(editor_pane)
    return editor_pane
    
  def remove_tab(self, name):
    # XXX does not support adding / removing tabs after showing the dialog box / page
    self.tab_labels.remove(name)
    self.tabs.remove(self.editor_panes[names])
    super.remove_tab(name)
    
  def on_tab(self, tab, already_sent):
    old_tab = self.current_tab
    self.current_tab = int(tab)
    current = self.get_current_editor_pane()
    if already_sent is None:
      self.update_js += """$("#tab%s_%s").html("%s");""" % (self._id, self.current_tab, js_escape(current.get_html()))
      self.update_js += current.get_ready_js()
      self.update_js += """tabs_received_%s["%s"] = true;""" % (self._id, self.current_tab)
    self.update_js += """BYID("tab%s_%s").style.display = "none";"""  % (self._id, old_tab)
    self.update_js += """BYID("tab%s_%s").style.display = "block";""" % (self._id, self.current_tab)
    self.update_js += """resize_full_height();\n"""
    
  def get_current_editor_pane(self): return self.tabs[self.current_tab]
  
  def get_user(self): return self.master.get_user()
  
  def get_o(self): return self.get_current_editor_pane().o
  o = property(get_o)
  
  def get_html(self):
    self.need_update = False
    if self.is_dialog: return ""
    else:
      return """
<div id="%s">
%s
</div>
""" % (self._id, self.get_inner_html())
  
  def get_inner_html(self):
    if self.menubar:
      html = """<div id="tb%s" style="padding: 2px; box-shadow: 0px 0px 5px #999;">MENUBAR</div>\n""" % self._id
    else: html = ""
    html += """
<div id="tabs%s" style="width: 100%%;">TABS</div>
""" % (self._id)
    for i in range(len(self.editor_panes)):
      if i == self.current_tab:
        html += """<div id="tab%s_%s">%s</div>""" % (self._id, i, self.get_current_editor_pane().get_html())
      else:
        html += """<div id="tab%s_%s" style="display: none;">TAB</div>""" % (self._id, i)
    return html

  READY_JS_TEMPLATE = string.Template("""
dialog$id = w2popup.open({ title: "$title", showMax: true, showClose: true, modal: $modal, buttons: "$buttons", body: "$body",
  onOpen : function (event) { event.onComplete = function () {
    $ready_js
    BYID("$editor_pane_id").style.height = (window.innerHeight - $delta_y) + "px";
    layout$editor_pane_id.resize();
  }},
  onMax: function (event) { event.onComplete = function () { layout$editor_pane_id.resize(); }},
  onMin: function (event) { event.onComplete = function () { layout$editor_pane_id.resize(); }},
  onClose: function (event) { ws.send(JSON.stringify(['closed', '$id'])); },
  width: window.innerWidth * 0.8, height: window.innerHeight
});
""")
  def get_ready_js(self):
    if self.is_dialog:
      o = self.o
      title = introsp.description_for_object(o).label_for(o).replace("\n", " ").replace("\t", " ")
      if self.on_validate:
        buttons  = """<input type="button" value="%s" onclick="w2popup.close();"/>&nbsp;&nbsp;&nbsp;""" % editobj3.TRANSLATOR("Cancel")
        buttons += """<input type="button" value="%s" onclick="ws.send(JSON.stringify(['click', '%s'])); w2popup.close();"/>""" % (editobj3.TRANSLATOR("Validate"), self._id)
      else: buttons = ""
      js = self.READY_JS_TEMPLATE.substitute(id = self._id, editor_pane_id = self.get_current_editor_pane()._id,
                                             title = html_js_escape(title), modal = "true" if self.on_validate else "false",
                                             buttons = js_escape(buttons), body = js_escape(self.get_inner_html()),
                                             ready_js = self.get_current_editor_pane().get_ready_js(),
                                             width = self.default_width, height = self.default_height,
                                             delta_y = 120 if self.menubar else 100)
    else: js = self.get_current_editor_pane().get_ready_js()
    if self.menubar: js += """
tb%s = $('#tb%s').w2toolbar({ name: 'tb%s', %s});
""" % (self._id, self._id, self._id, self.get_menubar_json())
    js += """
tabs_received_%s = new Array();
tabs_received_%s["%s"] = true;
$("#tabs%s").w2tabs({name: "tabs%s", active: "%s", tabs: [%s], style:"background-color: transparent;",
  onClick: function (event) { ws.send(JSON.stringify(["tab", "%s", event.target, tabs_received_%s[event.target]])); }
});
""" % (self._id, self._id, self.current_tab, self._id, self._id, self.current_tab, ",".join('{id:"%s", caption:"%s"}' % (i, js_escape(self.tab_labels[i])) for i in range(len(self.editor_panes))), self._id, self._id)
    return js
    
  def get_need_update(self): return self.need_update or self.update_js or self.get_current_editor_pane().get_need_update()
  
  def get_update_js(self):
    if self.need_update:
      if self.is_dialog: return self.get_ready_js()
      else: return """window.open("/editobj/editor.html?id=%s", "_blank");""" % self._id
    else: return self.update_js + self.get_current_editor_pane().get_update_js()
    
  def clear_update(self):
    self.need_update = False
    self.update_js   = ""
    self.get_current_editor_pane().clear_update()
    
  
class HTMLEditorPane(EditorPane):
  def __init__(self, gui, master, edit_child_in_self = 1, undo_stack = None, direction = "h"):
    super().__init__(gui, master, edit_child_in_self, undo_stack)
    self._id = master.get_user().obj2id(self)
    
  def get_user(self): return self.master.get_user()
  
  def get_o(self): return self.attribute_pane.o
  o = property(get_o)
  
  def get_html(self):
    return """
<div id="%s" style="width: 100%%; height: 752px;"></div>
<span id="editor%s">
%s
<div style="padding-top: 1em; clear:left;">%s</div>
</span>
""" % (self._id, self._id, self.icon_pane.get_html(), self.attribute_pane.get_html())
    
  def get_inner_html(self):
    return """
<span id="editor%s">
%s
<div style="padding-top: 1em; clear:left;">%s</div>
</span>
""" % (self._id, self.icon_pane.get_html(), self.attribute_pane.get_html())

  READY_JS_TEMPLATE = string.Template("""
$layout = $$("#$id").w2layout(
{ name: "$layout", padding: 0, panels: [
{ type: "left", minSize: 0, style: "border: 1px solid #AAAAAA; border-top: none;", size: window.innerWidth * 0.4, resizable: true, toolbar: { $toolbars style: "border: 1px solid #aaaaaa; border-top:none;" } },
{ type: "main", minSize: 550, style: "background: #EEEEEE; padding: 10px;" }
]});
$layout.content("left", $tree);
$layout.content("main", BYID("editor$id"));
$tb = $layout.panels[0].toolbar;
$tb.tree = $tree;
""")
  
  def get_ready_js(self, self_id = ""):
    if not self_id: self_id = "layout%s" % self._id
    js = self.attribute_pane.get_ready_js() + self.hierarchy_pane.get_ready_js() + self.READY_JS_TEMPLATE.substitute(id = self._id, layout = "%s" % self_id, toolbars = self.childhood_pane.get_toolbar_items(), tree = "tree%s" % self.hierarchy_pane._id, tb = "tb%s" % self.childhood_pane._id)
    if not self.hierarchy_visible:
      js += """layout%s.hide("left", true);""" % self._id
    return js
    
  def get_need_update(self): return self.icon_pane.get_need_update() or self.attribute_pane.get_need_update() or self.hierarchy_pane.get_need_update() or self.childhood_pane.get_need_update()
  
  def get_update_js(self):
    return "\n".join([self.icon_pane     .get_update_js(),
                      self.attribute_pane.get_update_js(),
                      self.hierarchy_pane.get_update_js(),
                      self.childhood_pane.get_update_js(),
                      ]).strip()
    
  def clear_update(self):
    self.icon_pane     .clear_update()
    self.attribute_pane.clear_update()
    self.hierarchy_pane.clear_update()
    self.childhood_pane.clear_update()
    
  def _set_hierarchy_visible(self, visible):
    self.hierarchy_visible = visible
     

class HTMLAttributePane(AttributePane):
  def __init__(self, gui, master, edit_child = None, undo_stack = None):
    super().__init__(gui, master, edit_child, undo_stack)
    self.labels_fields_units = []
    self._id = master.get_user().obj2id(self)
    self.need_update  = False
  
  def get_need_update(self): return self.need_update
    
  def edit(self, o, ignored_attrs = None):
    if self.o is o: return
    AttributePane.edit(self, o, ignored_attrs)
    
  def _delete_all_fields(self):
    self.labels_fields_units = []
    self.need_update = True
    
  def _new_field(self, attribute, field_class, unit, i):
    field = field_class(self.gui, self, self.o, attribute, self.undo_stack)
    self.labels_fields_units.append((attribute.label, field, unit))
    return field
    
  def get_user(self): return self.master.get_user()
  
  def get_inner_html(self):
    html  = ""
    for label, field, unit in self.labels_fields_units:
      html += """<tr><td>%s</td><td style="width: 100%%;">%s</td><td>%s</td></tr>\n""" % (html_escape(label).replace(" ", "&nbsp;"), field.get_html(), html_escape(unit))
    return html
    
  def get_html(self):
    self.need_update = False
    return """<table id="%s" border="0" style="width:100%%;">\n%s</table>\n""" % (self._id, self.get_inner_html())
    
  def get_ready_js(self):
    jss = []
    for label, field, unit in self.labels_fields_units:
      js = field.get_ready_js()
      if js: jss.append(js)
    return "\n".join(jss)
    
  def get_update_js(self):
    if self.need_update:
      return """
BYID("%s").innerHTML="%s";
%s
""" % (self._id, js_escape(self.get_inner_html()), self.get_ready_js())
    else:
      jss = []
      for label, field, unit in self.labels_fields_units:
        if field.get_need_update(): jss.append(field.get_update_js())
      return "\n".join(jss)
      
  def clear_update(self):
    self.need_update = False
    for label, field, unit in self.labels_fields_units: field.clear_update()
    
class HTMLIconPane(IconPane):
  def __init__(self, gui, master, edit_child = None, undo_stack = None):
    super().__init__(gui, master)
    self._id = master.get_user().obj2id(self)
    self.need_update = 0
    self.icon_filename = ""
    self.label         = ""
    self.details       = ""
    
  def _set_icon_filename_label_details(self, icon_filename, label, details):
    if (icon_filename != self.icon_filename) or (label != self.label) or (details != self.details):
      self.icon_filename = icon_filename
      self.label         = label
      self.details       = details
      self.need_update   = True
      
  def get_html(self):
    return u"""<span id="%s">%s</span>""" % (self._id, self.get_inner_html())
    
  def get_inner_html(self):
    icon_filename = self.descr.icon_filename_for(self.o)
    if isinstance(icon_filename, list):
      icon = """<div style="padding: 1em; float: left;">"""
      x = y = 0
      for filename in icon_filename:
        icon += """<img src="%s" style="position: absolute; left: %spx; top: %spx;"/>""" % (load_big_icon(filename), x, y)
        x += 30
        y += 15
      icon += """<img src="%s" style="margin-left: %spx; margin-top: %spx; visibility: hidden;"/>""" % (load_big_icon(filename), x - 30, y - 30)
      icon += """</div>"""
    elif icon_filename:
      icon = """<img src="%s" style="float: left; padding-right: 1em;"/>""" % load_big_icon(icon_filename)
    else: icon = ""
    return """
%s
<div style="padding-left: 10em;">
<h3>%s</h3>
<p>%s</p>
</div>
""" % (icon, html_escape(self.label), html_escape(self.details))
    
  def get_ready_js(self): return ""
  def get_need_update(self): return self.need_update

  def get_update_js(self):
    if self.need_update: return """BYID("%s").innerHTML = "%s";""" % (self._id, js_escape(self.get_inner_html()))
    return ""
    
  def clear_update(self): self.need_update = False
    
  
class HTMLChildhoodPane(ChildhoodPane):
  def __init__(self, gui, master, undo_stack = None, restrict_to_attribute = None):
    super().__init__(gui, master, undo_stack, restrict_to_attribute)
    self._id = master.get_user().obj2id(self)
    self.need_update = False
    self.visibles    = None
    
  def get_user(self): return self.master.get_user()
  
  def set_button_visibilities(self, visible1, visible2, visible3, visible4):
    if self.visibles != (visible1, visible2, visible3, visible4):
      self.visibles = visible1, visible2, visible3, visible4
    self.need_update = True
    
  def get_toolbar_items(self):
    return u"""items: [
{ type: "button", id: "up", caption: "", img: "icon-up"%s},
{ type: "button", id: "down", caption: "", img: "icon-down"%s},
{ type: "break", id: "break0"},
{ type: "button", id: "add", caption: "", img: "icon-add2"%s},
{ type: "button", id: "remove", caption: "", img: "icon-remove"%s},
], onClick : function(event) {
if (event.subItem != null)
     ws.send(JSON.stringify(["tbclick", "%s", event.subItem.text]));
else ws.send(JSON.stringify(["tbclick", "%s", event.target]));
},
""" % (", disabled: true" if not self.visibles[0] else "",
       ", disabled: true" if not self.visibles[3] else "",
       ", disabled: true" if not self.visibles[1] else "",
       ", disabled: true" if not self.visibles[2] else "",
       self._id, self._id)
    
  def get_html(self): return u"""<div id="%s" style="border: 1px solid #BBB; border-top-left-radius: 3px; border-top-right-radius: 3px;"></div>""" % (self._id)
  
  def get_ready_js(self):
    return """
tb%s = $("#%s").w2toolbar({name:"tb%s",%s});
tb%s.tree = tree%s;
""" % (self._id, self._id, self._id, self.get_toolbar_items(), self._id, self.hierarchy_pane._id)
    
  def get_need_update(self): return self.need_update
  
  def get_update_js(self):
    if self.need_update:
      js = """
tb%s.%s("up");
tb%s.%s("add");
tb%s.%s("remove");
tb%s.%s("down");
""" % (self._id, "enable" if self.visibles[0] else "disable",
       self._id, "enable" if self.visibles[1] else "disable",
       self._id, "enable" if self.visibles[2] else "disable",
       self._id, "enable" if self.visibles[3] else "disable") 
      add_actions = self.get_add_actions()
      if len(add_actions) == 1: js += """tb%s.set("add", {type:"button"});""" % self._id
      else:
        js += """
tb%s.set("add", {type:"menu", items: [%s]});
""" % (self._id, ",".join("""{text:"%s"}""" % js_escape(add_action.label) for add_action in add_actions))
        
      return js
    return ""
    
  def clear_update(self): self.need_update = False
  
  def on_click(self, action):
    if   action == "add":    self.on_add()
    elif action == "remove": self.on_remove()
    elif action == "up":     self.on_move_up()
    elif action == "down":   self.on_move_down()
    else: # Submenu add action
      add_actions = self.get_add_actions()
      for add_action in add_actions:
        if add_action.label == action:
          self.hierarchy_pane._action_activated(add_action, self.parent_o, self.attribute, self.o)
          break

class DynamicNode(object):
  def __init__(self, parent):
    self.children         = []
    self.children_created = False
    self.is_expandable    = False
    if isinstance(parent, DynamicNode):
      self.parent         = parent
    else:
      self.parent         = None
      self.update_children()
    self.update_js = ""
    self.getting_node = False
    
  def has_children(self): raise NotImplementedError
  def create_children(self, old_children = None): return []
  
  def expand(self):
    # XXX
    pass
    
  def expanded(self):
    if not self.children_created:
      self.children_created = True
      self.getting_node = True
      self.update_children()
      self.getting_node = False
    return self.children
    
  def collapsed(self): pass
      
  def update(self): pass
  
  def update_children(self):
    if self.children_created:
      old_children = self.children[:]
      new_children = self.create_children(old_children)
      old_children_set = set(old_children)
      new_children_set = set(new_children)
      
      for child in old_children[::-1]:
        if not child in new_children_set:
          if not self.getting_node: self.update_js += """tree%s.remove("%s");\n""" % (self.hierarchy_pane._id, child._id)
          child.destroy()
          
      kept_children = [child for child in new_children if child in old_children_set]
      
      for i in range(len(self.children)): self.children[i].index     = i
      for i in range(len(kept_children)): kept_children[i].new_index = i
      
      if kept_children:
        for child in kept_children:
          if child.new_index == child.index : continue # Swap with itself
          swap_with = self.children[child.new_index]
          self.update_js += """swapnode(tree%s,"%s","%s","%s");\n""" % (self.hierarchy_pane._id, self._id, child._id, swap_with._id)
          swap_with.index = child.index
          child.index     = child.new_index
          self.children[swap_with.index] = swap_with
          self.children[child    .index] = child
          
        for child in kept_children: del child.new_index
        
      for i in range(len(new_children)):
        new_children[i].index = i
        if not new_children[i] in old_children_set:
          if len(self.children) > i: before_id = '"%s"' % self.children[i]._id
          else:                      before_id = "null"
          self.children.insert(i, new_children[i])
          if not self.getting_node:
            if self.flat_list:
              if before_id == "null": self.update_js += """tree%s.add(%s);\n""" % (self.hierarchy_pane._id, new_children[i].get_json())
              else:                   self.update_js += """tree%s.insert(%s , %s);\n""" % (self.hierarchy_pane._id, before_id, new_children[i].get_json())
            else:
              self.update_js += """tree%s.insert("%s", %s, %s);\n""" % (self.hierarchy_pane._id, self._id, before_id, new_children[i].get_json())
            self.update_js += """create_icon_style(tree%s.get("%s").img);\n""" % (self.hierarchy_pane._id, new_children[i]._id)
            
      if self.update_js: self.update_js += "\n"
      
      for child in new_children:
        if not child in old_children_set:
          child.update_children()
          
      self.children = new_children
      
    else:
      if self.flat_list: pass
      else:
        is_expandable = bool(self.has_children())
        # XXX
        #if   is_expandable and (not self.is_expandable): self.tree.append(self.tree.get_iter(self.path()))
        #elif self.is_expandable and (not is_expandable): del self.tree[self.path() + (0,)]
        self.is_expandable = is_expandable
        
  def destroy(self):
    for child in self.children[::-1]: child.destroy()
    if self.parent: self.parent.children.remove(self)
    self.hierarchy_pane.nodes_needing_update.discard(self)
    
    
class HTML_HierarchyNode(HierarchyNode, DynamicNode):
  def __init__(self, hierarchy_pane, parent_node, attribute, o, restrict_to_attribute, flat_list):
    super().__init__(hierarchy_pane, parent_node, attribute, o, restrict_to_attribute, flat_list)
    self._id = self.hierarchy_pane.get_user().obj2id(self)
    
  def get_children_node_json(self):
    self.expanded() # XXX
    json =  "[%s]" % ",".join(node.get_json() for node in self.children)
    return json

  def get_json(self, with_children = False):
    icon_filename = self.descr.icon_filename_for(self.o)
    if isinstance(icon_filename, list): icon = icon[0] # Not yet supported
    if isinstance(icon_filename, str ): icon = ',img:"icon%s"' % (load_small_icon(icon_filename).rsplit("/", 1)[-1].split(".", 1)[0])
    else:                               icon = ""
    actions = self.get_actions()
    menu    = ",".join("""{id:"%s",text:"%s"}""" % (i+1, js_escape(actions[i].label)) for i in range(len(actions)))
    if with_children:
      return """{id:"%s",expanded:true,menu:[%s],nodes:[%s],text:"%s"%s}""" % (self._id, menu, ",".join(node.get_json() for node in self.children), js_escape(str(self)), icon)
    else:
      return """{id:"%s"%s,menu:[%s],text:"%s"%s}""" % (self._id, ",plus:true" if self.has_children() else "", menu, js_escape(str(self)), icon)
    
  def get_actions(self): return self.hierarchy_pane.get_actions(self.parent.o if self.parent else None, self.attribute, self.o)
  
  def do_action_by_label(self, label):
    for action in self.get_actions():
      if action.label == label:
        self.hierarchy_pane._action_activated(action, self.parent.o if self.parent else None, self.attribute, self.o)
        break
        
  def update(self):
    self.hierarchy_pane.nodes_needing_update.add(self)
    
  def get_update_js(self):
    if (self.parent is None) and self.flat_list: return self.update_js # Not shown => update only children list
    return self.update_js + """update_node(tree%s,"%s","%s",%s);""" % (self.hierarchy_pane._id, self.parent._id if self.parent else "#", self._id, self.get_json())
    
  def clear_update(self): self.update_js = ""
  
  def __str__(self):
    if self.attribute and not self.restrict_to_attribute: attr_label = self.attribute.label
    else:                                                 attr_label = ""
    if attr_label: return '''<span size="smaller" style="color:#aaaaaa;">%s</span> %s''' % (html_escape(attr_label), html_escape(self.descr.label_for(self.o)))
    return html_escape(self.descr.label_for(self.o))
    
  


EDITOR_JS += """
created_icon_styles = new Array();
function create_icon_style(name) {
  if ((name != null) && (!created_icon_styles[name])) {
    create_css_class(name, "background: url(/editobj/icons/" + name.substring(4) + ") no-repeat center; background-size: contain;");
    created_icon_styles[name] = true;
  }
}
function create_icon_styles(nodes) {
  for (i in nodes) create_icon_style(nodes[i].img);
}
function update_node(tree, parent, id, data) {
  var previous = tree.get(id);
  tree.refresh(id);
  create_icon_style(data.img);
}
function swapnode(tree, parent_id, id1, id2) {
  parent = tree.get(parent_id);
  var i = parent.nodes.indexOf(tree.get(id1));
  var j = parent.nodes.indexOf(tree.get(id2));
  var tmp = parent.nodes[i];
  parent.nodes[i] = parent.nodes[j];
  parent.nodes[j] = tmp;
  //tree.refresh();
  tree.refresh(parent_id);
}
"""

  
class HTMLHierarchyPane(HierarchyPane):
  Node = HTML_HierarchyNode
  def __init__(self, gui, master, edit_child, undo_stack = None, restrict_to_attribute = None, flat_list = 0):
    super().__init__(gui, master, edit_child, undo_stack, restrict_to_attribute, flat_list)
    self._id                  = master.get_user().obj2id(self)
    self.tree                 = None
    self.selected_parent      = None
    self.selected_attribute   = None
    self.selected_node        = None
    self.selected             = None
    self.nodes_needing_update = set()
    
  def get_user(self): return self.master.get_user()
  
  def get_html(self, div = True):
    return """<div id="%s" style="width: 100%%; height: 10em; border-left: 1px solid #BBB; border-right: 1px solid #BBB; border-bottom: 1px solid #BBB; border-bottom-left-radius: 3px; border-bottom-right-radius: 3px;">DIV</div>""" % self._id

  def get_inner_html(self): return ""
  
  READY_JS_TEMPLATE = string.Template("""
if (BYID("$id")) $tree = $$("#$id");
else             $tree = $$();
  $tree = $tree.w2sidebar({ name: "$tree", nodes: [$nodes] });
$tree.setMultiple(true);
$tree.onExpand = function(parent, data) {
  if (!$tree.get(parent).nodes.length)
    ws_send_and_wait(["getnode", "$id", parent], function (nodes) {
      create_icon_styles(nodes);
      $tree.add(parent, nodes);
    });
};
$tree.onClick = function(event) {
  event.onComplete = function() {
    var i, json = ["editnodes", "$id"];
    for(i = 0; i < $tree.selected.length; i++) { json.push($tree.selected[i]); }
    ws.send(JSON.stringify(json));
  };
};
$tree.onContextMenu = function(event) { $tree.menu = $tree.get(event.target).menu; };
$tree.onMenuClick = function(event) {
  ws.send(JSON.stringify(["nodeaction", event.target, $tree.menu[event.menuIndex].text]));
};
create_icon_styles($tree.nodes);
create_icon_styles($tree.nodes[0].nodes);
""")
  def get_ready_js(self):
    if self.flat_list: nodes = ",".join(node.get_json() for node in self.root_node.children)
    else:              nodes = self.root_node.get_json(True)
    return self.READY_JS_TEMPLATE.substitute(id = self._id, tree = "tree%s" % self._id, nodes = nodes)
    
  def get_need_update(self): return self.nodes_needing_update
  
  def get_update_js(self):
    if self.nodes_needing_update: return "\n".join(node.get_update_js() for node in self.nodes_needing_update)
    return ""
    
  def clear_update(self):
    for node in self.nodes_needing_update: node.clear_update()
    self.nodes_needing_update = set()
    
  def edit(self, o):
    if o is self.o: return
    
    HierarchyPane.edit(self, o)
    
    self.root_node.expanded()
    if self.flat_list:
      self.childhood_pane.edit(None, None, self.o)
    else:
      self.select_node(self.root_node)
      
  def expand_tree_at_level(self, level):
    pass # XXX
    
  def select_node(self, node):
    pass # XXX
    
  def on_selection_changed(self, selected_nodes):
    if len(selected_nodes) == 0:
      self.edit_child(None)
      if self.childhood_pane: self.childhood_pane.edit(None, None, None)
      self.selected_node = None
      return
      
    if len(selected_nodes) == 1:
      node = self.selected_node = selected_nodes[0]
      if node.parent: self.selected_parent = node.parent.o
      else:           self.selected_parent = None
      self.selected           = node.o
      self.selected_attribute = node.attribute
      
      self.edit_child(self.selected, self.get_ignored_attrs([node]))
      if self.childhood_pane: self.childhood_pane.edit(self.selected_parent, self.selected_attribute, self.selected)
      
    else:
      nodes = self.selected_node = selected_nodes
      self.selected_parent    = introsp.ObjectPack([(node.parent and node.parent.o) for node in nodes])
      self.selected           = introsp.ObjectPack([node.o for node in nodes])
      self.selected_attribute = [node.attribute for node in nodes]
      
      self.edit_child(self.selected, self.get_ignored_attrs(nodes))
      if self.childhood_pane: self.childhood_pane.edit(self.selected_parent, self.selected_attribute, self.selected)
  




import os, io, PIL.Image as Image

SMALL_ICON_SIZE = 32

_small_icons   = {}
_big_icons     = {}
url_2_icon     = {}
_next_image_id = 1

def guess_image_format(filename):
  filename = filename.lower()
  if filename.endswith(".svg"):  return "image/svg+xml"
  if filename.endswith(".png"):  return "image/png"
  if filename.endswith(".jpeg"): return "image/jpeg"
  if filename.endswith(".jpg"):  return "image/jpeg"
  return "image/xxx"

def load_big_icon(filename):
  url = _big_icons.get(filename)
  if not url:
    global _next_image_id
    ext = filename.rsplit(".")[-1]
    url = _big_icons[filename] = "/editobj/icons/%s" % _next_image_id
    url_2_icon[url] = guess_image_format(filename), filename
    _next_image_id += 1
  return url

def load_small_icon(filename):
  url = _small_icons.get(filename)
  if not url:
    global _next_image_id
    ext = filename.rsplit(".")[-1]
    url = _small_icons[filename] = "/editobj/icons/%s" % _next_image_id
    format = guess_image_format(filename)
    _next_image_id += 1
    if format == "image/svg+xml": # No resize needed
      url_2_icon[url] = format, filename
    else:
      image = Image.open(filename)
      w, h = image.size
      if (w > SMALL_ICON_SIZE) or (h > SMALL_ICON_SIZE):
        if w > h: image.thumbnail((SMALL_ICON_SIZE, int(float(SMALL_ICON_SIZE) * h / w)), Image.ANTIALIAS)
        else:     image.thumbnail((int(float(SMALL_ICON_SIZE) * w / h), SMALL_ICON_SIZE), Image.ANTIALIAS)
      buf = io.BytesIO()
      image.save(buf, "JPEG" if format == "image/jpeg" else "PNG")
      url_2_icon[url] = format, buf.getvalue()
  return url

load_small_icon(os.path.join(editobj3._ICON_DIR, "add.svg")) # ID 1
load_small_icon(os.path.join(editobj3._ICON_DIR, "remove.svg")) # ID 2
load_small_icon(os.path.join(editobj3._ICON_DIR, "up.svg")) # ID 3
load_small_icon(os.path.join(editobj3._ICON_DIR, "down.svg")) # ID 4
