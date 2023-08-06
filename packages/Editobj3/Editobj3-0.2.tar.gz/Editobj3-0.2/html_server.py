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

import sys, os, os.path, urllib.parse, urllib.request, json, base64
from io import StringIO
#try:    import ssl
#except: ssl = None

import asyncio, aiohttp, aiohttp.web, aiohttp.http_websocket

import editobj3, editobj3.field_html
#from editobj3.http_ws_server  import *
from editobj3.html_utils      import *
from editobj3.editor_html     import *
import editobj3.observe as observe
import editobj3.introsp as introsp

editobj3.eval = lambda x: x # Security !

JS_DIR = os.path.join(os.path.dirname(editobj3.__file__), "js")
if not os.path.exists(JS_DIR):
  JS_DIR = os.path.join("/usr", "share", "editobj3", "js")
  if not os.path.exists(JS_DIR):
    JS_DIR = os.path.join("/usr", "local", "share", "editobj3", "js")
    if not os.path.exists(JS_DIR):
      JS_DIR = os.path.join("/usr", "share", "python-editobj3", "js")
      
APPLICATION = None


class EditobjServer(aiohttp.web.Application):
  def __init__(self, on_startup = None, *args, **kargs):
    aiohttp.web.Application.__init__(self, *args, **kargs)
    self.commit_task = None
    
    if on_startup:
      def on_startup2(app): self.loop.call_later(0.05, on_startup)
      self.on_startup.append(on_startup2)
    self.router.add_static("/editobj/js/", JS_DIR)
    self.router.add_get   ("/editobj/icons/{icon}", self.on_icons)
    self.router.add_get   ("/editobj/editor.html", self.on_editor)
    self.router.add_get   ("/editobj/editor.ws", self.on_open_websocket)
    self.router.add_get   ("/editobj/{obj}", self.on_other)
    self.router.add_get   ("/editobj/auth/", self.on_auth)
    
  EXT_2_CONTENT_TYPE = {
    "html" : "text/html",
    "css"  : "text/css",
    "js"   : "text/javascript",
    "xml"  : "text/xml",
    "txt"  : "text/plain",
    "py"   : "text/python",
    "png"  : "image/png",
    "gif"  : "image/gif",
    "jpeg" : "image/jpeg",
    "jpg"  : "image/jpeg",
    "svg"  : "image/svg+xml",
  }
  def guess_content_type(self, filename):
    return self.EXT_2_CONTENT_TYPE.get(filename.rsplit(".")[-1], "text/plain")
    
  def get_current_user(self, request):
    auth_header = request.headers.get("Authorization", "")
    if auth_header.strip() == "": return GUEST
    auth_header = auth_header[6:].strip() # 6 == len("Basic ")
    user_name, password = base64.b64decode(auth_header).decode("latin").split(":")
    user = USERS.get(user_name)
    if user and (user.password == password): return user
    return GUEST
    
  async def on_auth(self, request):
    #elif (user is GUEST) and path.startswith("/auth/"):
    return aiohttp.web.Response(status = 401, headers = { "WWW-Authenticate" : 'Basic realm="editobj"' })
  
  async def on_icons(self, request):
    format, icon = url_2_icon["/editobj/icons/%s" % request.match_info.get("icon")]
    #format = self.EXT_2_CONTENT_TYPE[format]
    if isinstance(icon, str):
      #return aiohttp.web.Response(content_type = format, body = open(icon, "rb").read())
      return aiohttp.web.FileResponse(icon)
    else:
      return aiohttp.web.Response(content_type = format, body = icon)
    
  async def on_editor(self, request):
    user   = self.get_current_user(request)
    editor = user.id2obj(request.query["id"])
    return aiohttp.web.Response(content_type = "text/html", text = html_page_for_editor(editor, self.server_host, self.server_port))
  
  async def on_other(self, request):
    user = self.get_current_user(request)
    
    if (request.path in user.urls) or (request.path in GUEST.urls):
      obj = user.urls.get(request.path) or GUEST.urls.get(request.path)
      if   isinstance(obj, BaseDialog):
        return aiohttp.web.Response(content_type = "text/html", text = html_page_for_editor(obj, self.server_host, self.server_port))
      elif hasattr(obj, "get_html"):
        return aiohttp.web.Response(content_type = "text/html", text = obj.get_html())
      elif isinstance(obj, URLForLocalFile):
        content_type = self.guess_content_type(obj.filename)
        if content_type.startswith("text"):
          return aiohttp.web.Response(content_type = "text/html", text = open(obj.filename).read())
        else:
          return aiohttp.web.Response(content_type = "text/html", text = open(obj.filename, "rb").read())

    if user is GUEST:
      return aiohttp.web.Response(status = 401, headers = { "WWW-Authenticate" : 'Basic realm="editobj"' })
      
    raise ValueError(user, request.path)

  async def on_open_websocket(self, request):
    user      = self.get_current_user(request)
    websocket = EditobjWebSocket(self, user, request)
    return await websocket.run()
  
  def run(self, host = "127.0.0.1", port = 8080, *args, **kargs):
    global APPLICATION
    
    self.server_host = host
    self.server_port = port
    observe.scan = self.scan
    APPLICATION  = self
    
    aiohttp.web.run_app(self, host = host, port = port, *args, **kargs)
    
  def scan(self):
    _observe_scan()
    self.schedule_commit()
    
  def schedule_commit(self):
    if self.commit_task: self.commit_task.cancel()
    self.commit_task = self.loop.create_task(self.commit())
    #self.loop.call_later(0.1, self.commit_task)
    
  async def commit(self):
    updated_editors = set()
    for user in USERS.values():
      for ws_handler in user.ws_handlers:
        js = ""
        if ws_handler.editor.get_need_update():
          js += ws_handler.editor.get_update_js()
          updated_editors.add(ws_handler.editor)
        if ws_handler.dialog and ws_handler.dialog.get_need_update():
          js += ws_handler.dialog.get_update_js()
          updated_editors.add(ws_handler.dialog)
        if js:
          await ws_handler.send_ws_data(js)

    for editor in updated_editors: editor.clear_update()

_observe_scan = observe.scan


class EditobjWebSocket(object):
  def __init__(self, application, user, request):
    self.application = application
    self.user        = user
    self.request     = request
    self.response    = aiohttp.web.WebSocketResponse()
    self.editor      = user.id2obj(request.query["id"])
    self.dialog      = None
    
    self.user.ws_handlers.append(self)
    
  async def run(self):
    await self.response.prepare(self.request)
    
    async for msg in self.response:
      if msg.type == aiohttp.WSMsgType.TEXT:
        await self.on_ws_data_received(msg.data)
        
      elif msg.type == aiohttp.WSMsgType.ERROR:
        print('ws connection closed with exception %s' % self.response.exception())
        self.on_closed()
        break
        
    self.on_closed()
    return self.response
  
  async def on_ws_data_received(self, data):
    data = json.loads(data)
    
    if   data[0] == "setattr":
      field = self.user.id2obj(data[1])
      field.set_value(data[2])
      
    elif data[0] == "click":
      field = self.user.id2obj(data[1])
      field.on_click()
      self.application.scan()
      
    elif data[0] == "closed":
      dialog = self.user.id2obj(data[1])
      dialog.on_closed()
      self.application.scan()
      
    elif data[0] == "getnode":
      if data[2] == "#":
        hierarchy_pane = self.user.id2obj(data[1])
        j = "[%s]" % hierarchy_pane.root_node.get_json()
      else:
        parent = self.user.id2obj(data[2])
        j = parent.get_children_node_json()
      await self.send_ws_data("""data_received(%s, %s);""" % (j, data[3]))
      
    elif data[0] == "editnodes":
      editor =  self.user.id2obj(data[1])
      nodes  = [self.user.id2obj(id) for id in data[2:]]
      editor.on_selection_changed(nodes)
      await self.application.commit()
      
    elif data[0] == "nodeaction":
      node = self.user.id2obj(data[1])
      node.do_action_by_label(data[2])
      
    elif data[0] == "tbclick":
      editor = self.user.id2obj(data[1])
      editor.on_click(data[2])
      
    elif data[0] == "tab":
      editor = self.user.id2obj(data[1])
      editor.on_tab(data[2], data[3])
      await self.application.commit()
      
  async def send_ws_data(self, data):
    await self.response.send_str(data)
    
  def on_closed(self):
    self.user.ws_handlers.remove(self)
    




def html_page_for_editor(editor, host, port):
    if   isinstance(editor, HTMLEditorDialog):
      if editor.menubar: resizer = """
function resize_full_height() { BYID("%s").style.height = (window.innerHeight - 6 - $("#tb%s").height()) + "px"; }
""" % (editor.editor_pane._id, editor._id)
      else: resizer = """
function resize_full_height() { BYID("%s").style.height = (window.innerHeight - 1) + "px"; }
""" % (editor.editor_pane._id)
      
    elif isinstance(editor, HTMLEditorTabbedDialog):
      if editor.menubar: resizer = """function resize_full_height() { var h = (window.innerHeight - 10 - $("#tabs%s").height() - $("#tb%s").height()) + "px";\n""" % (editor._id, editor._id)
      else:              resizer = """function resize_full_height() { var h = (window.innerHeight - 3 - $("#tabs%s").height()) + "px";\n""" % editor._id
      for editor_pane in editor.tabs:
        resizer += """  if(BYID("%s")) BYID("%s").style.height = h;\n""" % (editor_pane._id, editor_pane._id)
      resizer += "}\n"
    else: resizer = """
function resize_full_height() { BYID("%s").style.height = (window.innerHeight - 1) + "px"; }
""" % editor._id

    html = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <title>%s</title>
    <link rel="stylesheet" href="/editobj/js/w2ui-1.3.2.css" />
    <script type="text/javascript" src="/editobj/js/jquery-1.11.0.min.js"></script>
    <script type="text/javascript" src="/editobj/js/w2ui-1.3.2.js"></script>
    <style type='text/css'>
.w2ui-icon { width: %spx; height: %spx; }
.w2ui-sidebar .w2ui-sidebar-div .w2ui-node .w2ui-node-image { width: %spx; height: %spx; }
.w2ui-sidebar .w2ui-sidebar-div .w2ui-node-caption { padding-top: 7px; }
.w2ui-sidebar .w2ui-sidebar-div td.w2ui-node-data { padding: 0px; }
.w2ui-sidebar .w2ui-sidebar-div td.w2ui-node-data .w2ui-node-image.w2ui-icon { margin-top: 0px; margin-bottom: 0px; }
.icon-add2 { background: url(/editobj/icons/1) no-repeat center; background-size: contain; }
.icon-remove { background: url(/editobj/icons/2) no-repeat center; background-size: contain; }
.icon-up { background: url(/editobj/icons/3) no-repeat center; background-size: contain; }
.icon-down { background: url(/editobj/icons/4) no-repeat center; background-size: contain; }
.editobj-button {
  background-color: #FAFAFA;
  text-align: center;
  border: 1px solid #AAAAAA;
  border-radius: 3px;
  cursor: default;
 }
.editobj-button:hover {
  background-color: #FFFFFF;
 }
.editobj-button:active {
  background-color: #EEEEEE;
 }
input[type=checkbox] { -ms-transform: scale(1.5); -moz-transform: scale(1.5); -webkit-transform: scale(1.5); -o-transform: scale(1.5); padding: 10px; }
    </style>
    <script type="text/javascript">
function BYID(id) { return document.getElementById(id) };
ws = new WebSocket("ws://%s:%s/editobj/editor.ws?id=%s");
ws.onmessage = function(event) {
  eval(event.data);
};
queue = new Array();
next_queue_id = 1;
function ws_send_and_wait(data, callback) {
  if (ws.readyState == 0) {
    setTimeout(function() { ws_send_and_wait(data, callback); }, 100);
  }
  else {
    var queue_id = next_queue_id;
    next_queue_id = next_queue_id + 1;
    data.push(queue_id);
    ws.send(JSON.stringify(data));
    queue[queue_id] = callback;
  }
}
function data_received(json, queue_id) {
  queue[queue_id](json);
  delete queue[queue_id];
}
function create_css_class(classname, content) {
  var style = document.createElement("style");
  style.type = "text/css";
  style.innerHTML = "." + classname + " {" + content + "}";
  document.getElementsByTagName("head")[0].appendChild(style);
}
%s
$(window).resize(resize_full_height);

%s
    </script>
  </head>
  <body style="margin: 0px; background: #EEEEEE;">
%s

<script>
$(function () {
%s
resize_full_height();
});
</script>
  </body>
</html>
""" % (html_escape(introsp.description_for_object(editor.o).label_for(editor.o)), SMALL_ICON_SIZE, SMALL_ICON_SIZE, SMALL_ICON_SIZE, SMALL_ICON_SIZE, host, port, editor._id, resizer, editobj3.field_html.FIELD_JS + editobj3.editor_html.EDITOR_JS, editor.get_html(), editor.get_ready_js())
    return html

