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

class User(object):
  def __init__(self, name):
    self.name          = name
    self.password      = "123"
    
  def __str__(self): return "%s %s" % (self.__class__.__name__, self.name)
    
class Admin(User):
  pass
    
class Connection(object):
  def __init__(self):
    self.type  = "modem"
    self.speed = 60
    
class Security(object):
  def __init__(self):
    self.level            = 2
    self.allow_javascript = 0
    self.block_popup      = 0
    self.enable_antispam  = 1
    self.enable_antispam  = 1
    

class Plugin(object):
  def __init__(self, name, **kargs):
    self.__dict__ = kargs
    self.name     = name
    self.active   = 1
    
  def __repr__(self): return "Plugin '%s'" % self.name
  
class Config(object):
  def __init__(self):
    self.connection     = Connection()
    self.security       = Security()
    self.users   = [
      User("Jiba"),
      ]
    self.plugins = [
      Plugin("GPG", command = "gpg"),
      Plugin("SVG"),
      Plugin("OggVorbis", driver_filename = "/dev/dsp")
      ]
    
    self.default_plugin = self.plugins[0]

config = Config()
# os.path.join(os.path.dirname(sys.argv[0]), "./jiba.png")


descr = introsp.description(User)
descr.set_icon_filename(os.path.join(os.path.dirname(sys.argv[0]), "./jiba.png"))
descr.def_attr("list_of_int", field.IntListField)
descr.set_constructor(introsp.Constructor(lambda klass, parent: klass("")))

introsp.def_attr("default_plugin", field.ObjectSelectorField, addable_values = lambda config: [introsp.NewInstanceOf(Plugin)] + config.plugins + [None])

descr = introsp.description(Connection)
descr.set_label("Connection")
descr.def_attr("type" , field.EnumField(["modem", "DSL", "ADSL"]))
descr.def_attr("speed", field.RangeField(0, 512), unit = "Ko/s")

descr = introsp.description(Security)
descr.set_label("Security")
descr.def_attr("level"           , field.EnumField({"low":0, "medium":1, "high":2, "paranoid":3}))
descr.def_attr("allow_javascript", field.BoolField)
descr.def_attr("block_popup"     , field.BoolField)

descr = introsp.description(Plugin)
descr.def_attr("active", field.BoolField)
descr.set_constructor(introsp.Constructor(lambda klass, parent: klass("")))

descr = introsp.description(Config)
descr.set_label("Configuration")
descr.def_attr("plugins", addable_values = [introsp.NewInstanceOf(Plugin)])
descr.def_attr("users"  , addable_values = [introsp.NewInstanceOf(User), introsp.NewInstanceOf(Admin)])

# The following are not needed because Editobj is smart enough to guess them;
# they are kept only for documentation purpose.

#descr.def_attr("identification", field.ObjectAttributeField)
#descr.def_attr("connection"    , field.ObjectAttributeField)
#descr.def_attr("security"      , field.ObjectAttributeField)
#descr.set_label(lambda o: unicode(o))


if len(sys.argv) > 1: editobj3.GUI = sys.argv[-1]

editobj3.edit(config, on_close = sys.exit).main()

