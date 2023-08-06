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

import sys
import editobj3, editobj3.introsp as introsp, editobj3.observe as observe, editobj3.field as field

class Sum(object):
  def __init__(self):
    self.a = 0.0
    self.b = 0.0
  def get_result(self): return self.a + self.b

class Substract(object):
  def __init__(self):
    self.a = 0.0
    self.b = 0.0
  def get_result(self): return self.a - self.b
  
class Multiply(object):
  def __init__(self):
    self.a = 0.0
    self.b = 0.0
  def get_result(self): return self.a * self.b
  
class Divide(object):
  def __init__(self):
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

descr = introsp.description(Substract)
descr.set_label("Substract")

descr = introsp.description(Multiply)
descr.set_label("Multiply")

descr = introsp.description(Divide)
descr.set_label("Divide")


descr = introsp.description(Calculator)
descr.set_label("Calculator")
descr.set_details("A calculator with Editobj3!")
descr.def_attr("operations", label = "")


calculator = Calculator()


if len(sys.argv) > 1: editobj3.GUI = sys.argv[-1]

editobj3.edit(calculator, on_close = sys.exit).main()

