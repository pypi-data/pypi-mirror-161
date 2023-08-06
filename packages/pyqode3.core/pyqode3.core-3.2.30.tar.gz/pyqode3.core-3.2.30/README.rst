.. image:: https://raw.githubusercontent.com/pyQode/pyQode/master/media/pyqode-banner.png

About
-----


This is a fork of PyQode, which is now developed as the editor component for Rapunzel_ and OpenSesame_. The original PyQode repository (<= v2) is no longer maintained.

**pyqode.core** is the core framework of the `pyQode` project.

It contains the base classes and a set of extensions (modes/panels/managers)
needed to develop a specialised code editor.

It also provides a basic generic code editor that you can use as a fallback
when there is no specialised editor for a given language.

.. _OpenSesame: https://osdoc.cogsci.nl/
.. _Rapunzel: https://rapunzel.cogsci.nl/


License
-------

pyQode is licensed under the **MIT license**.


Requirements
------------

pyqode.core depends on the following libraries:

- Python 2 (**>=2.7**) or Python 3 (**>= 3.2**)
- PyQt5 or PyQt4 or PySide
- pygments
- pyqode.qt
- future
- qtawesome (optional)
