.. SPDX-FileCopyrightText: 2021 GNOME Foundation
..
.. SPDX-License-Identifier: Apache-2.0 OR GPL-3.0-or-later

===============
gi-docgen check
===============

Check the documentation in the introspection data
-------------------------------------------------

SYNOPSIS
========

**gi-docgen check** [OPTIONS...] [GIRFILE]

DESCRIPTION
===========

The **check** command runs a series of checks on the introspection
file, to verify that public API is properly documented. It can be used 
as part of a test suite.

OPTIONS
=======

``--add-include--path DIR``
  Adds ``DIR`` to the list of paths used to find introspection data
  files included in the given ``GIRFILE``. The default search path
  for GIR files is ``$XDG_DATA_DIRS/gir-1.0`` and ``$XDG_DATA_HOME/gir-1.0``;
  this option is typically used to include uninstalled GIR files, or
  non-standard locations.

``-C, --config FILE``
  Loads a project configuration file.
