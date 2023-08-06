# -*- coding: utf-8 -*-
# Ontopy
# Copyright (C) 2007-2014 Jean-Baptiste LAMY
# LIMICS (Laboratoire d'informatique médicale et d'ingénierie des connaissances en santé), UMR_S 1142
# University Paris 13, Sorbonne paris-Cité, Bobigny, France

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

import sys
import editobj3, editobj3.introsp as introsp, editobj3.observe as observe, editobj3.field as field

class Sum(object):
  def __init__(self, parent = None):
    self.a = 0.0
    self.b = 0.0
  def get_result(self): return self.a + self.b

class Substract(object):
  def __init__(self, parent = None):
    self.a = 0.0
    self.b = 0.0
  def get_result(self): return self.a - self.b
  
class Multiply(object):
  def __init__(self, parent = None):
    self.a = 0.0
    self.b = 0.0
  def get_result(self): return self.a * self.b
  
class Divide(object):
  def __init__(self, parent = None):
    self.a = 0.0
    self.b = 1.0
  def get_result(self): return self.a / self.b


class Calculator(object):
  def __init__(self):
    self.operations = [
      Sum(),
      Substract(),
      Multiply(),
      Divide(),
      ]

descr = introsp.description(Sum)
descr.set_label("Sum")
descr.def_attr("c", field.EnumListField([0.0, 1.0, 2.0, 3.0]))
descr.def_attr("obj", field.ObjectSelectorField, addable_values = lambda o: calculator.operations)

descr = introsp.description(Substract)
descr.set_label("Substract")

descr = introsp.description(Multiply)
descr.set_label("Multiply")

descr = introsp.description(Divide)
descr.set_label("Divide")


descr = introsp.description(Calculator)
descr.set_label("Calculator")
descr.set_details("A calculator with Ontopy.Editobj!")
#descr.def_attr("operations", field.HierarchyAndObjectListField, addable_values = [introsp.Constructor(Sum), introsp.Constructor(Substract), introsp.Constructor(Multiply), introsp.Constructor(Divide)])
#descr.def_attr("operations", field.HierarchyAndObjectListField, addable_values = [introsp.Constructor(Sum, lambda c: Sum()), introsp.Constructor(Substract, lambda c: Substract()), introsp.Constructor(Multiply, lambda c: Multiply()), introsp.Constructor(Divide, lambda c: Divide())])
descr.def_attr("operations", field.HierarchyAndObjectListField, addable_values = [introsp.NewInstanceOf(Sum), introsp.NewInstanceOf(Substract), introsp.NewInstanceOf(Multiply), introsp.NewInstanceOf(Divide)], label = "")


calculator = Calculator()

editobj3.GUI = "HTML"

import editobj3.html_utils
import editobj3.html_server
import editobj3.editor

jiba = editobj3.html_utils.User("jiba", "test")

editor = editobj3.editor.EditorDialog("HTML", jiba)
editor.edit(calculator)

jiba.register_url("/editobj/calculator.html", editor)

editor.main(path = "/editobj/calculator.html")

#editor = ontopy.editobj.editor.EditorTabbedDialog("HTML", ontopy.editobj.html_utils.GUEST)
#editor.add_tab(1, "Tab n°1", calculator)
#editor.add_tab(2, "Tab n°2", calculator.operations[0])

#ontopy.editobj.html_server.EditobjHTTPServer(("localhost", 8080)).serve_forever()

#ontopy.editobj.html_server.EditobjServer(("127.0.0.1", 8080)).serve_forever()
