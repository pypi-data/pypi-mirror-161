====================================
PyAMS SQLAlchemy integration package
====================================

.. contents::


What is PyAMS?
==============

PyAMS (Pyramid Application Management Suite) is a small suite of packages written for applications
and content management with the Pyramid framework.

**PyAMS** is actually mainly used to manage web sites through content management applications (CMS,
see PyAMS_content package), but many features are generic and can be used inside any kind of web
application.

All PyAMS documentation is available on `ReadTheDocs <https://pyams.readthedocs.io>`_; source code
is available on `Gitlab <https://gitlab.com/pyams>`_ and pushed to `Github
<https://github.com/py-ams>`_. Doctests are available in the *doctests* source folder.


What is PyAMS SQLAlchemy?
=========================

SQLALchemy is a very common ORM package for Python. As PyAMS relies on ZODB connections, this
package provides components which can be used to define SQL "sessions" through management
interface, which are then integrated into main transactions using a two-phases commit manager.

This package also provides optional features to extend PyAMS_scheduler package with new tasks
which can launch SQL commands.
