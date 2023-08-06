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

import sys, os, os.path, editobj3, editobj3.introsp as introsp, editobj3.observe as observe, editobj3.field as field, editobj3.undoredo as undoredo, editobj3.editor as editor

class Module(object):
  def __init__(self, module, image = None):
    self.module          = module
    self.details         = module.__doc__ or ""
    self.submodules      = []
    if image:
      self.icon_filename = image
      
  def __str__(self): return self.module.__name__

mod = Module(editobj3, os.path.join(os.path.dirname(sys.argv[0]), "./dialog.png"))
mod.url = "http://home.gna.org/oomadness/en/editobj"
mod.version = editobj3.VERSION
mod.submodules.append(Module(introsp))
mod.submodules.append(Module(observe))
mod.submodules.append(Module(undoredo))
mod.submodules.append(Module(editor))
mod.submodules.append(Module(field))


descr = introsp.description(Module)
descr.def_attr("module"       , field.HiddenField)
descr.def_attr("details"      , field.HiddenField)
descr.def_attr("icon_filename", field.HiddenField)
descr.def_attr("submodules", label = "", remove_method = None, reorder_method = None)

# The following are not needed because Editobj is smart enough to guess them;
# they are kept only for documentation purpose.

#descr.set_details(lambda o: o.details)
#descr.set_label  (lambda o: str(o))

if len(sys.argv) > 1: editobj3.GUI = sys.argv[-1]

editobj3.edit(mod, on_close = sys.exit).main()
