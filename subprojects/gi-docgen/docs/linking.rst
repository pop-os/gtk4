.. SPDX-FileCopyrightText: 2021 GNOME Foundation
..
.. SPDX-License-Identifier: Apache-2.0 OR GPL-3.0-or-later

=====================
Linking items by name
=====================

Gi-docgen is capable of linking symbols across the same introspected namespace,
by using a qualifier fragment and the symbol name.

For instance:

.. code-block:: c

   /**
    * ExampleFoo:
    *
    * This structure is related to [struct@Bar].
    */

    /**
     * example_foo_set_bar:
     *
     * Sets [struct@Example.Bar] on an instance of `Foo`.
     */

    /**
     * ExampleFoo:bar:
     *
     * Sets an instance of [`Bar`](struct.Bar.html) on `Foo`.
     */


will all link to ``Bar``.

Backticks will be stripped, so ``[`class@Foo`]`` will correctly link to ``Foo``.

The link can either be a fully qualified name, which includes the namespace; or
a name relative to the current namespace; for instance, both of the following links
will point to ``ExampleFoo`` when generating the documentation for the "Example"
namespace:

- ``[class@Foo]``
- ``[class@Example.Foo]``

The available qualifier fragments are:

.. list-table::
   :widths: 10 15 25 50
   :header-rows: 1

   * - Fragment
     - Argument
     - Description
     - Example
   * - ``alias``
     - ``TypeName``
     - An alias to another type
     - ``[alias@Allocation]``
   * - ``callback``
     - ``TypeName``
     - A callback type
     - ``[callback@Gtk.ListBoxForeachFunc]``
   * - ``class``
     - ``TypeName``
     - An object class
     - ``[class@Widget]``, ``[class@Gdk.Surface]``, ``[class@Gsk.RenderNode]``
   * - ``const``
     - ``CONSTANT``
     - A constant or pre-processor symbol
     - ``[const@Gdk.KEY_q]``
   * - ``ctor``
     - ``TypeName.constructor``
     - A constructor function
     - ``[ctor@Gtk.Box.new]``, ``[ctor@Button.new_with_label]``
   * - ``enum``
     - ``TypeName``
     - A plain enumeration
     - ``[enum@Orientation]``
   * - ``error``
     - ``TypeName``
     - A ``GError`` domain enumeration
     - ``[error@Gtk.BuilderParseError]``
   * - ``flags``
     - ``TypeName``
     - A bitfield
     - ``[flags@Gdk.ModifierType]``
   * - ``func``
     - ``function``, ``TypeName.function``
     - A global or a type function
     - ``[func@Gtk.init]``, ``[func@show_uri]``, ``[func@Gtk.Window.list_toplevels]``
   * - ``iface``
     - ``TypeName``
     - A ``GTypeInterface``
     - ``[iface@Gtk.Buildable]``
   * - ``method``
     - ``TypeName.method``, ``TypeNameClass.method``
     - An instance or class method
     - ``[method@Gtk.Widget.show]``, ``[method@WidgetClass.add_binding]``
   * - ``property``
     - ``TypeName:property``
     - A ``GObject`` property
     - ``[property@Gtk.Orientable:orientation]``
   * - ``signal``
     - ``TypeName::signal``
     - A ``GObject`` signal
     - ``[signal@Gtk.RecentManager::changed]``
   * - ``struct``
     - ``TypeName``
     - A plain C structure or union
     - ``[struct@Gtk.TextIter]``
   * - ``vfunc``
     - ``TypeName.virtual``
     - A virtual function in a class or interface
     - ``[vfunc@Gtk.Widget.measure]``
   * - ``type``
     - ``TypeName``
     - A registered type
     - ``[type@Widget]``, ``[type@Gdk.ModifierType]``, ``[type@Gtk.TextIter]``
   * - ``id``
     - ``function``
     - A C symbol
     - ``[id@gtk_window_new]``, ``[id@g_signal_connect]``

The generic ``type`` fragment, followed by a type, will look up the given type
and generate the appropriate link for it. The type can be fully qualified or
relative to the current namespace:

::

    // Equivalent to [class@Gtk.Window]
    [type@Gtk.Window]

    // Equivalent to [enum@Gtk.Orientation]
    [type@Gtk.Orientation]

Anything that is a known type—aliases, callbacks, classes, constants,
enumerations, interfaces, structures—can be linked using the ``type`` fragment.

Additionally, the ``id`` fragment, followed by a C symbol identifier, will try
to link to the function; for instance:

::

    // Equivalent to [func@Gtk.show_uri], will link to gtk_show_uri()
    [id@gtk_show_uri]

    // Equivalent to [method@Gtk.Widget.show], will link to gtk_widget_show()
    [id@gtk_widget_show]

    // Equivalent to [func@GObject.signal_emit], will link to g_signal_emit()
    [id@g_signal_emit]

It's important to note that the ``method`` and ``func`` fragments can have
multiple meanings:

- the ``method`` fragment will match both instance and class methods, depending
  on the type used; for instance, to match an instance method you should use the
  type name, and to match a class method you should use the class name. The class
  method should not be confused with the ``vfunc`` fragment, which uses the type
  name and links to virtual methods defined in the class or interface structure.
  Class methods take the class pointer as their first argument, whereas virtual
  methods take the instance pointer as their first argument.

::

    // will link to gtk_widget_show()
    [method@Gtk.Widget.show]

    // will link to gtk_widget_class_add_binding()
    [method@Gtk.WidgetClass.add_binding]

    // will link to GtkWidgetClass.show
    [vfunc@Gtk.Widget.show]


- similarly, the ``func`` fragment will match global functions and type
  functions, depending on whether the link contains a type or not. Additionally,
  ``func`` will match function macros, which are part of the global namespace.

::

    // will link to gtk_show_uri()
    [func@Gtk.show_uri]

    // will link to gtk_window_list_toplevels()
    [func@Gtk.Window.list_toplevels]

    // will link to gtk_widget_class_bind_template_child()
    [func@Gtk.widget_class_bind_template_child]

External Links
--------------

Gi-docgen can use the same syntax to point to symbols in other namespaces
with gi-docgen-generated documentation, as long as you provide it with
a mapping from the namespace names to a base url for the docs. This is
done by defining a JavaScript map called ``baseURLs`` like this:

.. code-block:: js

    baseURLs = [
      [ 'Pango', 'https://gnome.pages.gitlab.gnome.org/pango/Pango/' ],
      [ 'PangoCairo', 'https://gnome.pages.gitlab.gnome.org/pango/PangoCairo/' ],
    ]

And specifying the path of the JavaScript file into the ``extras`` section
of the project configuration, in the ``urlmap_file`` key.
