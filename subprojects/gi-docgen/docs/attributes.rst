.. SPDX-FileCopyrightText: 2021 GNOME Foundation
..
.. SPDX-License-Identifier: Apache-2.0 OR GPL-3.0-or-later

Introspection attributes
========================

GI-DocGen consumes the following attributes found in the introspection data when
generating the API reference for that data.

Properties
----------

The following attributes apply to properties.

``org.gtk.Property.get`` = ``s``
  Defines the getter method for a given property. The value of the attribute is
  the C symbol of the function.

``org.gtk.Property.set`` = ``s``
  Defines the setter method for a given property. The value of the attribute is
  the C symbol of the function.

``org.gtk.Property.default`` = ``s``
  Defines the default value for a given property.

Methods
-------

The following attributes apply to methods of a classed type or interface.

``org.gtk.Method.set_property`` = ``s``
  Defines the property set by the function. The property name must be in
  the same type as the method

``org.gtk.Method.get_property`` = ``s``
  Defines the property retrieved by the function. The property name must
  be in the same type as the method

``org.gtk.Method.signal`` = ``s``
  Defines the signal emitted by the function. The signal name must be
  in the same type as the method
