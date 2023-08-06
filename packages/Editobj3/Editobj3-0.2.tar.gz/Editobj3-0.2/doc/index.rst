Welcome to Editobj3's documentation!
************************************

Editobj3 is an automatic dialog box generator for Python objects. It supports several backends; currenlty
GTK and HTML are supported. The HTML backend is based on `W2UI <http://w2ui.com>`_, and can be used
either in local single user mode, or in distributed multiple users mode.

Editobj3 dialog boxes are composed of an attribute list, a luxurious good-looking but useless icon and
title bar, and a tree view (if the edited object is part of a tree-like structure). Editobj3 includes an
advanced introspection module that usually guesses how to edit any object; it can also be customized for a
given class of object through the editobj3.introsp module. Editobj3 also supports the simultaneous
edition of a group of objects, as if they were a single object.

Additional helper modules are included:

 - editobj3.observe: Observation framework

 - editobj3.undoredo: Multiple undo/redo framework

 - editobj3.http_ws_server: HTTP server with WebSocket support, with an interface similar to Python's http.server module

Editobj3 has been created by Jean-Baptiste Lamy. It is available under the GNU LGPL licence.

In case of trouble, please contact Jean-Baptiste Lamy <jibalamy **@** free **.** fr>



.. figure:: images/editobj3_gtk.png
   :scale: 50 %
   :align: center

   Screenshot of an Editobj3 dialog box with GTK backend

.. figure:: images/editobj3_html.png
   :scale: 50 %
   :align: center

   Screenshot of an Editobj3 dialog box with HTML backend

Links
=====

Editobj3 on BitBucket (development repository): https://bitbucket.org/jibalamy/editobj3


Automatic dialog box generation
===============================

.. automodule:: editobj3
   :members:

.. automodule:: editobj3.introsp
   :members:

.. automodule:: editobj3.editor
   :members:

.. automodule:: editobj3.field

Extending Editobj3 with additional Field or Editor widgets
----------------------------------------------------------

Backends specificities
======================

GTK backend
-----------

HTML backend
------------


Helper modules
==============

.. automodule:: editobj3.observe
   :members:

.. automodule:: editobj3.undoredo
   :members:


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

