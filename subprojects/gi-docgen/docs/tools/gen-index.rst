.. SPDX-FileCopyrightText: 2021 GNOME Foundation
..
.. SPDX-License-Identifier: Apache-2.0 OR GPL-3.0-or-later

===================
gi-docgen gen-index
===================

Generating the symbols index from introspection data
----------------------------------------------------

SYNOPSIS
========

**gi-docgen gen-index** [OPTIONS...] [GIRFILE]

DESCRIPTION
===========

The **gen-index** command generates a symbols index from introspection
data. The symbols index can be used to efficiently search symbols and
terms.

The generated index file is called ``index.json``

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
  Only load the introspection data, without generating the index.

``--content-dir DIR``
  The directories for extra content, like additional files and images
  specified in the project configuration file. This argument may be
  called multiple times to specify several lookup directories, the
  content files will be looked these directories in the same order
  they are added.

``--output-dir DIR``
  Generates the index file under ``DIR``.

INDEX FILE
==========

The index file is in `JSON format <https://json.org>`__.

The index file contains a single object with the following members:

``meta`` = ``object``
  An object with metadata about the index.

``symbols`` = ``array of objects``
  An array of all the addressable symbols.

``terms`` = ``object``
  A dictionary of all terms.

The ``meta`` object contains the following members:

``ns`` = ``s``
  The namespace name.

``version`` = ``s``
  The namespace version.

``generator`` = ``s``
  The ``gi-docgen`` string.

``generator-version`` = ``s``
  The version of ``gi-docgen``.

The ``symbols`` array contains objects with the following members:

``type`` = ``s`` (*mandatory*)
  The type of symbol: ``alias``, ``bitfield``, ``callback``, ``class``,
  ``class_method``, ``ctor``, ``domain``, ``enum``, ``function``,
  ``function_macro``, ``interface``, ``method``, ``property``, ``signal``,
  ``type_func``, ``union``, ``vfunc``.

``name`` = ``s`` (*mandatory*)
  The name of the symbol.

``ctype`` = ``s``
  The base C type for identifiers; only available for types: ``alias``,
  ``bitfield``, ``class``, ``domain``, ``enum``, ``interface``,
  ``union``.

``type_name`` = ``s``
  The type name related to a symbol; only available for types:
  ``class_method``, ``ctor``, ``method``, ``property``, ``signal``,
  ``type_func``, ``vfunc``.

``ident`` = ``s``
  The C identifier for symbols; only available for types:
  ``class_method``, ``constant``, ``ctor``, ``function``, ``function_macro``,
  ``method``, ``type_func``.

``struct_for`` = ``s``
  The C type related to a class structure; only available for the
  ``class_method`` type.

The ``terms`` dictonary contains all terms as members; each term is associated
to an array of indices in the ``symbols`` array.
