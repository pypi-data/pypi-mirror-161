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
editobj3.undoredo: Multiple undo/redo framework
-----------------------------------------------

This module contains a multiple undo/redo framework. It is used by Editobj3 dialog boxes,
and it automatically call :func:`editobj3.observe.scan()` when doing or undoing an operation.

.. data:: stack
   :annotation: the default undo/redo stack.
"""

__all__ = ["Stack", "UndoableOperation"]

import editobj3.observe as observe

class Stack(object):
  """An undo/redo stack.

:param limit: the maximum number of undo/redo, defaults to 20."""
  def __init__(self, limit = 20):
    self.limit     = limit
    self.undoables = []
    self.redoables = []
      
  def can_undo(self):
    """Returns True if it is possible to undo an operation."""
    if self.undoables: return self.undoables[-1]
    return False
  
  def can_redo(self):
    """Returns True if it is possible to redo an operation."""
    if self.redoables: return self.redoables[-1]
    return False
  
  def do_operation(self, operation):
    """Does the operation. Can be overriden, e.g. to save data after the changes performed by the operation.

:param operation: the operation.
:type operation: :class:`Operation`"""
    operation.do_func()
    
  def undo(self):
    """Undoes the last operation available."""
    if not self.undoables: raise ValueError("No operation to undo!")
    undo = self.undoables.pop()
    opposite = undo.opposite()
    
  def redo(self):
    """Redoes the last operation available."""
    if not self.redoables: raise ValueError("No operation to redo!")
    redo = self.redoables.pop()
    opposite = redo.opposite()
    
  def clear(self):
    """Clears all undo/redo operations."""
    self.undoables = []
    self.redoables = []

  def merge_last_operations(self, name = "", nb = 2):
    """Merges the NB last operations. They will now be undone / redone as a single operation, with the given NAME."""
    if not name: name = ", ".join(undoable.name for undoable in self.undoables[-nb:])
    doers   = [undoable.do_func   for undoable in self.undoables[-nb:]]
    undoers = [undoable.undo_func for undoable in self.undoables[-nb:]]
    def do_it():
      for doer in doers: doer()
    def undo_it():
      for undoer in reversed(undoers): undoer()
      
    del self.undoables[-nb + 1:]
    self.undoables[-1].do_func   = do_it
    self.undoables[-1].undo_func = undo_it
    self.undoables[-1].name      = name
    return self.undoables[-1]
  
  def __repr__(self):
    return "<%s, undoables:\n%s\n  redoables:\n%s\n>" % (
      self.__class__.__name__,
      "\n".join(["    %s" % repr(i) for i in self.undoables]),
      "\n".join(["    %s" % repr(i) for i in self.redoables]),
      )
    
stack = Stack()


class _Operation(object):
  def __init__(self, do_func, undo_func, name = "", stack_ = stack):
    self.do_func   = do_func
    self.undo_func = undo_func
    self.name      = name
    self.stack     = stack_ or stack
    stack.do_operation(self)
    
  def __repr__(self):
    return "<%s '%s' do_func='%s' undo_func='%s'>" % (self.__class__.__name__, self.name, self.do_func, self.undo_func)
    
class UndoableOperation(_Operation):
  """UndoableOperation(do_func, undo_func, name = "", stack = undoredo.stack)

An operation that can be undone.

:param do_func: a callable that do the operation when called.
:param undo_func: a callable that undo the operation when called.
:param name: the name of the operation.
:param stack: the undo/redo stack to add the operation to, defaults to undoredo.stack.
"""
  def __init__(self, do_func, undo_func, name = "", stack = None):
    _Operation.__init__(self, do_func, undo_func, name, stack)
    stack.undoables.append(self)
    if len(self.stack.undoables) > self.stack.limit: del self.stack.undoables[0]
    observe.scan()
    
  def opposite(self):
    return _RedoableOperation(self.undo_func, self.do_func, self.name, self.stack)

  def coalesce_with(self, previous_undoable_operation):
    self.undo_func = previous_undoable_operation.undo_func
    previous_undoable_operation.stack.undoables.remove(previous_undoable_operation)
    
class _RedoableOperation(_Operation):
  def __init__(self, do_func, undo_func, name = "", stack = stack):
    _Operation.__init__(self, do_func, undo_func, name, stack)
    stack.redoables.append(self)
    observe.scan()
    
  def opposite(self):
    return UndoableOperation(self.undo_func, self.do_func, self.name, self.stack)


