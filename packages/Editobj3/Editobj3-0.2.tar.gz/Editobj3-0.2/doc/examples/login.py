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

import sys, os, os.path, editobj3, editobj3.introsp as introsp, editobj3.observe as observe, editobj3.field as field
import editobj3.undoredo as undoredo

class User(object):
  def __init__(self, login, icon_filename, session, language):
    self.login         = login
    self.password      = ""
    self.icon_filename = icon_filename
    self.session       = session
    self.language      = language
    
  def __str__(self): return self.login


class UserSelection(object):
  def __init__(self):
    self.users = []
    
  def __str__(self): return "User selection"
  

icon_filename = os.path.join(os.path.dirname(sys.argv[0]), "./jiba.png")

user_selection = UserSelection()
user_selection.users.append(User("Jiba"    , icon_filename, "WindowMaker", "Français"))
user_selection.users.append(User("Blam"    , icon_filename, "FluxBox"    , "Français"))
user_selection.users.append(User("Marmoute", icon_filename, "Gnome"      , "Français"))


descr = introsp.description(User)
descr.def_attr("icon_filename", field.HiddenField)
descr.def_attr("session" , field.EnumField(["WindowMaker", "FluxBox", "LXDE", "Gnome", "KDE"]))
descr.def_attr("language", field.EnumField(["Français", "Italiano", "English", "Esperanto"], long_list = 1))

# The following are not needed because Editobj is smart enough to guess them;
# they are kept only for example purpose.
#descr.def_attr("password", field.PasswordField)
#descr.set_icon_filename(lambda o: o.icon_filename)

descr = introsp.description(UserSelection)
descr.set_details("1) Choose a user\n2) Type a valid password\n3) Login!")

descr.add_action(introsp.Action("Undo", lambda undo_stack, editor, o: undoredo.stack.undo()))
descr.add_action(introsp.Action("Redo", lambda undo_stack, editor, o: undoredo.stack.redo()))


def on_validate(user):
  if isinstance(user, User):
    print("%s has loged in in with password '%s', language '%s' and session type '%s'." % (user.login, user.password, user.language, user.session))
  else:
    print("User has canceled.")
  sys.exit()
  
if len(sys.argv) > 1: editobj3.GUI = sys.argv[-1]

editobj3.edit(user_selection, on_validate = on_validate).main()
