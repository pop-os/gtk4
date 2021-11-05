.. SPDX-FileCopyrightText: 2021 GNOME Foundation
..
.. SPDX-License-Identifier: Apache-2.0 OR GPL-3.0-or-later

==================
gi-docgen generate
==================

Generating the API reference from introspection data
----------------------------------------------------

SYNOPSIS
========

**gi-docgen generate** [OPTIONS...] [GIRFILE]

DESCRIPTION
===========

The **generate** command generates the API reference from a GIR file.

GIR files are XML files that describe an API in a machine readable way,
and are typically provided by a GObject library.

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

``--dry-run``
  Only load the introspection data, without generating the reference.

``--templates-dir DIR``
  Look for templates under ``DIR``. The default location for the
  templates directory is inside the ``gi-docgen`` installation.

``--content-dir DIR``
  The directories for extra content, like additional files and images
  specified in the project configuration file. This argument may be
  called multiple times to specify several lookup directories, content
  files will be looked up in the content directories in the
  same order they are added.

``--theme-name NAME``
  The name of the template to use. Overrides the name specified by
  the project configuration file.

``--output-dir DIR``
  Generates the reference under ``DIR``.

``--no-namespace-dir``
  When specified, the files are directly generated under the output
  directory, instead of using a sub-directory based on the namespace
  name and version.

``--section NAME``
  Only generate the section ``NAME`` of the reference. Valid section
  names are: ``aliases``, ``bitfields``, ``callbacks``, ``classes``,
  ``constants``, ``domains``, ``enums``, ``functions``, ``function_macros``,
  ``interfaces``, ``structs``, and ``unions``. Additionally, ``all``
  will generate all sections, and ``none`` will generate no section.
