.. SPDX-FileCopyrightText: 2021 GNOME Foundation
..
.. SPDX-License-Identifier: Apache-2.0 OR GPL-3.0-or-later

========
Commands
========
  
.. toctree::
    :hidden:
    :titlesonly:
    :maxdepth: 1
  
    generate
    gen-index
    check

SYNOPSIS
========

**gi-docgen** COMMAND [OPTIONS...]

The ``gi-docgen`` command line utility has several commands, each with its
own functionality and options.

COMMANDS
========

:doc:`generate`
  Generates the API reference
  
:doc:`gen-index`
  Generates the symbol indices for search

:doc:`check`
  Checks the documentation

OPTIONS
=======

All commands support the following options:

``-q, --quiet``
  Do not emit any additional information message.

``--fatal-warnings``
  Make all warnings fatal, immediately terminating the process.

``--help``
  Show an help message.

ENVIRONMENT VARIABLES
=====================

All commands support the following environment variables:

``GIDOCGEN_DEBUG``
  If set, ``gi-docgen`` will emit debugging messages.


BUGS
====

Report bugs at https://gitlab.gnome.org/GNOME/gi-docgen/issues

HOMEPAGE and CONTACT
====================

https://gnome.pages.gitlab.gnome.org/gi-docgen/

AUTHOR
======

Emmanuele Bassi
