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

import sys, os, os.path, time, _thread, editobj3, editobj3.introsp as introsp, editobj3.observe as observe, editobj3.field as field
import editobj3.undoredo as undoredo

class Download(object):
  def __init__(self, remote_url, local_filename):
    self.remote_url     = remote_url
    self.local_filename = local_filename
    self.progress       = 0.0
    self.speed          = 0
    self.completed      = 0
    
  def __str__(self): return os.path.basename(self.remote_url) + " (" + str(int(100 * self.progress)) + "%)"

  def start(self):
    self.progress = 0.0
    self.speed    = 10
    
  def stop(self): pass


class DownloadManager(object):
  def __init__(self):
    self.downloads = []
    
  def __str__(self): return "Download manager"

  def add_download(self, download):
    self.insert_download(len(self.downloads) + 1, download)

  def insert_download(self, index, download):
    self.downloads.insert(index, download)
    download.start()

  def remove_download(self, download):
    download.stop()
    self.downloads.remove(download)

icon_filename = os.path.join(os.path.dirname(sys.argv[0]), "./jiba.png")

dm = DownloadManager()
dm.add_download(Download("http://python.org", "./index_python.html"))
dm.add_download(Download("http://soyaproject.org/soya", "./index_soya.html"))
dm.add_download(Download("http://soyaproject.org/slune", "./index_slune.html"))
dm.add_download(Download("http://soyaproject.org/balazar_brother", "./index_balazar_brother.html"))

def downloader():
  for download in dm.downloads[:]:
    if download.progress < 1.0:
      download.progress = download.progress + 0.001 * download.speed
      if download.progress >= 1.0:
        download.progress = 1.0
        download.completed = 1
  observe.scan()
  return 1

def run_downloader():
  import time
  time.sleep(1.0) # Wait for the app to start up
  while 1:
    downloader()
    time.sleep(0.2)
  
descr = introsp.description(Download)
descr.def_attr("progress", field.ProgressBarField)
descr.def_attr("speed", field.RangeField(0, 100), unit = "Ko/s")
descr.def_attr("completed", field.BoolField)
descr.set_icon_filename(os.path.join(os.path.dirname(sys.argv[0]), "./file.png"))

class NewDowloadFormConstructor(introsp.FormConstructor):
  def __init__(self):
    self.remote_url     = "http://"
    self.local_filename = ""

# You may want to customize the creation of the new instance -- by default, EditObj 3
# uses the form's __dict__ as named args.

#  def create_new_from_form(self, klass, parent):
#    return klass(self.remote_url, self.local_filename)

descr.set_constructor(NewDowloadFormConstructor)

descr = introsp.description(DownloadManager)
descr.set_details("To add a new download, click on the '+' button on the right.\nUse the '-' button to remove and cancel a download.")

#download_constructor = introsp.Constructor(Download, lambda download_manager: Download("http://", ""))
descr.def_attr("downloads", addable_values = [introsp.NewInstanceOf(Download)])

descr.add_action(introsp.Action("Undo", lambda undo_stack, editor, o: undo_stack.undo()))
descr.add_action(introsp.Action("Redo", lambda undo_stack, editor, o: undo_stack.redo()))

if len(sys.argv) > 1: editobj3.GUI = sys.argv[-1]

w = editobj3.edit(dm, direction = "v", on_close = sys.exit)


if editobj3.GUI == "Gtk":
  import gi
  from gi.repository import GObject as gobject
  gobject.timeout_add(200, downloader) # Gtk does not like being used along with Python thread module
else:
  import PyQt5.QtCore as qtcore
  timer = qtcore.QTimer()
  timer.timeout.connect(downloader)
  timer.setInterval(200)
  timer.start()
  #  import _thread; _thread.start_new_thread(run_downloader, ())
  pass
  
w.main()
