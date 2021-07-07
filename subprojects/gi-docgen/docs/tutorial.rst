.. SPDX-FileCopyrightText: 2021 GNOME Foundation
..
.. SPDX-License-Identifier: Apache-2.0 OR GPL-3.0-or-later

===============
Using GI-DocGen
===============

In order to use GI-DocGen, you will need:

- a library using GObject and generating introspection data as part of its
  build process
- a project configuration file

For the former, you should read `the gobject-introspection documentation <https://gi.readthedocs.io/en/latest/>`__,
which includes all the details on how to write introspectable API.

Writing a project configuration file
------------------------------------

The project configuration file provides some basic information describing your
project, expressed in key/value pairs, and will be exposed to the template
system used when generating the API reference through gi-docgen. Not every key
is mandatory, and the template will decide whether or not use its value when
generating the API reference. For simplicity, we're going to assume you're using
the "basic" template that is part of gi-docgen.

The project configuration file is written using `ToML <https://toml.io/en/>`__,
and you can use the ``--config`` command line option for gi-docgen.

We begin with the ``library`` preamble:

::

        [library]
        description = "The GTK toolkit"
        authors = "GTK Development Team"
        license = "GPL-2.1-or-later"
        browse_url = "https://gitlab.gnome.org/GNOME/gtk/"
        repository_url = "https://gitlab.gnome.org/GNOME/gtk.git"
        website_url = "https://www.gtk.org"

The keys above will be used in the main landing page for the library.

If your project has dependencies, and you wish to display them or cross-link
types and symbols from your API reference, you will need to describe them using
the ``dependencies`` key, for instance:

::

        # List the dependencies using their GIR namespace
        dependencies = [
          "GObject-2.0",
          "Graphene-1.0",
          "Pango-1.0",
          "Gdk-4.0",
          "Gsk-4.0",
        ]

Each dependency will need its own object, for instance:

::

        [dependencies."GObject-2.0"]
        name = "GObject"
        description = "The base type system library"
        docs_url = "https://developer.gnome.org/gobject/stable"

The ``name``, ``description``, and ``docs_url`` keys will be used when generating the
list of dependencies on the main landing page.

If you wish to add links to the source code repository for type and symbol
declarations, as well as the location of the documentation source, you will need
a ``source-location`` section:

::

        [source-location]
        # The base URL for the web UI
        base_url = "https://gitlab.gnome.org/GNOME/gtk/-/blob/master/"
        # The format for links, using "filename" and "line" for the format
        file_format = "{filename}#L{line}"

If your library has additional content, in the form of Markdown files that you
wish to include in the generated API reference, you can use the ``extra`` section:

::

        [extra]
        # A list of Markdown files; they will be parsed using the
        # same rules as the documentation coming from the introspection
        # data. The path of each file is relative to the content
        # directory specified on the command line.
        #
        # The order in which they are included will be used when
        # generating the index.
        #
        # The generated files will be placed in the root output directory
        content_files = [
          "getting_started.md",
          "building.md",
          "compiling.md",
          "running.md",
          "question_index.md",
          ...
        ]
        # Additional images referenced by the documentation; their path
        # is relative to the content directory specified on the command
        # line.
        #
        # The image files will be copied into the root documentation,
        # without replicating the directory structure in which they
        # are listed.
        content_images = [
          "images/aboutdialog.png",
          "images/action-bar.png",
          "images/appchooserbutton.png",
          "images/appchooserdialog.png",
          ...
        ]

For more information about the project configuration, please see the
:doc:``project-configuration`` page.

Generating the API reference
----------------------------

Once you have a project configuration file, and the introspection data for the
library you wish to document, all you need is to launch the ``gi-docgen`` command
line tool.

You will need to provide:

- the location of the project configuration file
- the location of the additional content files
- additional search paths for the dependencies
- the output directory for the generated files
- the location of the introspection file

A simple invocation for the installed ``Gtk-4.0.gir`` file is:

::

  gi-docgen generate -C gtk4.toml /usr/share/gir-1.0/Gtk-4.0.gir

This will generate the API reference for the ``Gtk-4.0`` namespace, and will put
the generate files under the current directory.
