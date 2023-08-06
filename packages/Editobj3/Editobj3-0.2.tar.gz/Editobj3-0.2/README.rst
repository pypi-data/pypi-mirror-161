Editobj3
========

Editobj3 is an automatic dialog box generator for Python objects. It supports several backends; currenlty
Qt, GTK and HTML are supported. The HTML backend is based on `W2UI <http://w2ui.com>`_, and can be used
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


Installation
------------

First untar the tarball.

EditObj 3 uses Python's DistUtils for installation. To install, type (as root):

cd EditObj3-*
python3 ./setup.py install

By default, EditObj 3 is installed in /usr, you can modify the
setup.cfg file if you prefer another location.


Links
-----

Editobj3 on BitBucket (development repository): https://bitbucket.org/jibalamy/editobj3

Mail me for any comment, problem, suggestion or help !

Jiba -- Jean-Baptiste LAMY -- jibalamy @ free.fr
