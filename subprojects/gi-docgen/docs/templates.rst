.. SPDX-FileCopyrightText: 2021 GNOME Foundation
..
.. SPDX-License-Identifier: Apache-2.0 OR GPL-3.0-or-later

=========
Templates
=========

The `generate` command of gi-docgen uses `Jinja2 <https://palletsprojects.com/p/jinja/>`__
templates to generate the HTML pages of the API reference from the
introspection data provided by a library.

Template configuration
----------------------

Each template must contain a template configuration file, with the same name as
the template all in lower case. The template configuration format is ToML.

The template configuration file can contain the following sections:

The ``metadata`` section
~~~~~~~~~~~~~~~~~~~~~~~~

Contains template metadata, like licensing and author information:

``name`` = ``s``
  The name of the template

``author_name`` = ``s``
  The name of the author of the template

``author_email`` = ``s``
  The email of the author of the template

``copyright_year`` = ``s``
  The copyright year of the template

``license`` = ``s``
  The license of the template, as an `SPDX identifier <https://spdx.org/licenses/>`__.

The ``templates`` section
~~~~~~~~~~~~~~~~~~~~~~~~~

Contains the template files for each section of the template. If the key is
not present, the default file name is used.

``class`` = ``s``
  The class template file. Default: ``class.html``

``interface`` = ``s``
  The interface template file. Default: ``interface.html``

``property`` = ``s``
  The property template file. Default: ``property.html``

``signal`` = ``s``
  The signal template file. Default: ``signal.html``

``method`` = ``s``
  The method template file. Default: ``method.html``

``vfunc`` = ``s``
  The virtual method template file. Defalt: ``vfunc.html``

``type_func`` = ``s``
  The type function template file. Default: ``type_func.html``

``ctor`` = ``s``
  The constructor function template file. Default: ``type_func.html``

``class_method`` = ``s``
  The class method template file. Default: ``class_method.html``

``error`` = ``s``
  The error domain template file. Default: ``error.html``

``flags`` = ``s``
  The bitfield template file. Default: ``flags.html``

``enum`` = ``s``
  The enumeration template file. Default: ``enum.html``

``record`` = ``s``
  The record template file. Default: ``record.html``

``union`` = ``s``
  The union template file. Default: ``union.html``

``alias`` = ``s``
  The alias template file. Default: ``alias.html``

``function`` = ``s``
  The function template file. Default: ``function.html``

``constant`` = ``s``
  The constant template file. Default: ``constant.html``

``namespace`` = ``s``
  The namespace template file. Default: ``namespace.html``

``content`` = ``s``
  The template file for additional content. Default: ``content.html``

The ``css`` section
~~~~~~~~~~~~~~~~~~~

Contains style related data.

``style`` = ``s``
  The main CSS file for the template

Th ``extra_files`` section
~~~~~~~~~~~~~~~~~~~~~~~~~~

Contains additional files that must be copied into the output directory
after generating the reference.

``files`` = ``list(s)``
  A list of files needed by the template. Each file is relative to the
  template's directory.

Template data
-------------

Each Jinja template file will be passed objects and additional data when
gi-docgen renders the API reference.

All templates will receive:

- the ``CONFIG`` object, containing the project configuration
- the ``namespace`` object, containing the GIR namespace

Additionally, each template will receive a template object containing the
information needed to render the template.
