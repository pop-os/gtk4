# SPDX-FileCopyrightText: 2020 GNOME Foundation
# SPDX-License-Identifier: Apache-2.0 OR GPL-3.0-or-later

import typing as T

from .. import log


class Doc:
    """A documentation node, pointing to the source code"""
    def __init__(self, content: str, filename: str, line: int, version: str = None, stability: str = None):
        self.content = content
        self.filename = filename
        self.line = line
        self.version = version
        self.stability = stability

    def __str__(self):
        return self.content


class SourcePosition:
    """A location inside the source code"""
    def __init__(self, filename: str, line: int):
        self.filename = filename
        self.line = line

    def __str__(self):
        return f'{self.filename}:{self.line}'


class Attribute:
    """A user-defined annotation"""
    def __init__(self, name: str, value: T.Optional[str]):
        self.name = name
        self.value = value


class CInclude:
    """A C include header"""
    def __init__(self, name: str):
        self.name = name


class Include:
    """A GIR include"""
    def __init__(self, name: str, version: str = None):
        self.name = name
        self.version = version

    def __str__(self):
        if self.version is not None:
            return f"{self.name}-{self.version}"
        return f"{self.name}"

    def girfile(self) -> str:
        if self.version is not None:
            return f"{self.name}-{self.version}.gir"
        return f"{self.name}.gir"


class Package:
    """Pkg-config containing the library"""
    def __init__(self, name: str):
        self.name = name


class Info:
    """Base information for most types"""
    def __init__(self, introspectable: bool = True, deprecated: T.Optional[str] = None,
                 deprecated_version: T.Optional[str] = None, version: str = None,
                 stability: str = None):
        self.introspectable = introspectable
        self.deprecated_msg = deprecated
        self.deprecated_version = deprecated_version
        self.version = version
        self.stability = stability
        self.attributes: T.Mapping[str, T.Optional[str]] = {}
        self.doc: T.Optional[Doc] = None
        self.source_position: T.Optional[SourcePosition] = None

    def add_attribute(self, name: str, value: T.Optional[str] = None) -> None:
        self.attributes[name] = value


class GIRElement:
    """Base type for elements inside the GIR"""
    def __init__(self, name: T.Optional[str] = None, namespace: T.Optional[str] = None):
        self.name = name
        self.namespace = namespace
        if self.namespace is not None:
            if self.name is not None and '.' in self.name:
                self.namespace = self.name.split('.')[0]
        self.info = Info()

    def set_introspectable(self, introspectable: bool) -> None:
        """Set whether the symbol is introspectable"""
        self.info.introspectable = introspectable

    @property
    def introspectable(self):
        return self.info.introspectable

    def set_version(self, version: str) -> None:
        """Set the version of the symbol"""
        self.info.version = version

    def set_stability(self, stability: str) -> None:
        """Set the stability of the symbol"""
        self.info.stability = stability

    @property
    def stability(self):
        return self.info.stability

    def set_doc(self, doc: Doc) -> None:
        """Set the documentation for the element"""
        self.info.doc = doc

    @property
    def doc(self):
        return self.info.doc

    def set_source_position(self, pos: SourcePosition) -> None:
        """Set the position in the source code for the element"""
        self.info.source_position = pos

    @property
    def source_position(self) -> T.Optional[T.Tuple[str, int]]:
        if self.info.source_position is None:
            return None
        return self.info.source_position.filename, self.info.source_position.line

    def set_deprecated(self, doc: T.Optional[str] = None, since_version: T.Optional[str] = None) -> None:
        """Set the deprecation annotations for the element"""
        self.info.deprecated_msg = doc
        self.info.deprecated_version = since_version

    def set_attributes(self, attrs: T.Mapping[str, T.Optional[str]]) -> None:
        """Add an annotation to the symbol"""
        for name, value in attrs.items():
            self.info.add_attribute(name, value)

    @property
    def attributes(self) -> T.Mapping[str, T.Optional[str]]:
        return self.info.attributes

    @property
    def available_since(self) -> T.Optional[str]:
        return self.info.version

    @property
    def deprecated_since(self) -> T.Optional[T.Tuple[str, str]]:
        if not self.info.deprecated_msg:
            return None
        version = self.info.deprecated_version
        message = self.info.deprecated_msg
        if message is None:
            message = "Please do not use it in newly written code"
        return (version, message)


class Type(GIRElement):
    """Base class for all Type nodes"""
    def __init__(self, name: str, ctype: T.Optional[str] = None, namespace: T.Optional[str] = None):
        super().__init__(name=name, namespace=namespace)
        self.ctype = ctype

    def __eq__(self, other):
        if isinstance(other, Type):
            if self.namespace is not None:
                return self.namespace == other.namespace and self.name == self.name
            elif self.ctype is not None:
                return self.name == other.name and self.ctype == other.ctype
            else:
                return self.name == other.name
        elif isinstance(other, str):
            return self.name == other
        else:
            return False

    def __cmp__(self, other):
        if self.ctype is not None:
            return self.name == other.name and self.ctype == other.ctype
        return self.name == other.name

    def __repr__(self):
        return f"Type({self.fqtn}, {self.ctype})"

    @property
    def resolved(self):
        return self.ctype is not None

    @property
    def base_ctype(self):
        if self.ctype is None:
            return None
        return self.ctype.replace('*', '')

    @property
    def fqtn(self):
        if '.' in self.name:
            return self.name
        elif self.namespace is not None:
            return f"{self.namespace}.{self.name}"
        else:
            return None


class ArrayType(GIRElement):
    """Base class for Array nodes"""
    def __init__(self, name: str, value_type: Type, ctype: str = None, zero_terminated: bool = False,
                 fixed_size: int = -1, length: int = -1):
        super().__init__(name)
        self.ctype = ctype
        self.zero_terminated = zero_terminated
        self.fixed_size = fixed_size
        self.length = length
        self.value_type = value_type


class ListType(GIRElement):
    """Type class for List nodes"""
    def __init__(self, name: str, value_type: Type, ctype: str = None):
        super().__init__(name)
        self.ctype = ctype
        self.value_type = value_type


class MapType(GIRElement):
    """Type class for Map nodes"""
    def __init__(self, name: str, key_type: Type, value_type: Type, ctype: str = None):
        super().__init__(name)
        self.ctype = ctype
        self.key_type = key_type
        self.value_type = value_type


class GType:
    """Base class for GType information"""
    def __init__(self, type_name: str, get_type: str, type_struct: T.Optional[str] = None):
        self.type_name = type_name
        self.get_type = get_type
        self.type_struct = type_struct


class VoidType(Type):
    def __init__(self):
        super().__init__(name='none', ctype='void')

    def __str__(self):
        return "void"


class VarArgs(Type):
    def __init__(self):
        super().__init__(name='none', ctype='')

    def __str__(self):
        return "..."


class Alias(Type):
    """Alias to a Type"""
    def __init__(self, name: str, namespace: str, ctype: str, target: Type):
        super().__init__(name=name, ctype=ctype, namespace=namespace)
        self.target = target


class Constant(Type):
    """A constant"""
    def __init__(self, name: str, namespace: str, ctype: str, target: Type, value: str):
        super().__init__(name=name, ctype=ctype, namespace=namespace)
        self.target = target
        self.value = value


class Parameter(GIRElement):
    """A callable parameter"""
    def __init__(self, name: str, direction: str, transfer: str, target: Type = None, caller_allocates: bool = False,
                 optional: bool = False, nullable: bool = False, closure: int = -1, destroy: int = -1,
                 scope: str = None):
        super().__init__(name)
        self.direction = direction
        self.transfer = transfer
        self.caller_allocates = caller_allocates
        self.optional = optional
        self.nullable = nullable
        self.scope = scope
        self.closure = closure
        self.destroy = destroy
        if target is None:
            self.target: Type = VoidType()
        else:
            self.target = target


class ReturnValue(GIRElement):
    """A callable's return value"""
    def __init__(self, transfer: str, target: Type, nullable: bool = False, closure: int = -1, destroy: int = -1, scope: str = None):
        super().__init__()
        self.transfer = transfer
        self.nullable = nullable
        self.scope = scope
        self.closure = closure
        self.destroy = destroy
        if target is None:
            self.target: Type = VoidType()
        else:
            self.target = target


class Callable(GIRElement):
    """A callable symbol: function, method, function-macro, ..."""
    def __init__(self, name: str, namespace: T.Optional[str], identifier: T.Optional[str], throws: bool = False):
        super().__init__(name=name, namespace=namespace)
        self.identifier = identifier
        self.parameters: T.List[Parameter] = []
        self.return_value: T.Optional[ReturnValue] = None
        self.throws: bool = throws
        self.moved_to: T.Optional[str] = None
        self.shadows: T.Optional[str] = None
        self.shadowed_by: T.Optional[str] = None

    def add_parameter(self, param: Parameter) -> None:
        self.parameters.append(param)

    def set_parameters(self, params: T.List[Parameter]) -> None:
        self.parameters.extend(params)

    def set_return_value(self, res: ReturnValue) -> None:
        self.return_value = res

    def set_shadows(self, func: str) -> None:
        self.shadows = func

    def set_shadowed_by(self, func: str) -> None:
        self.shadowed_by = func

    def set_moved_to(self, func: str) -> None:
        self.moved_to = func

    def __contains__(self, param):
        if isinstance(param, str):
            for p in self.parameters:
                if p.name == param:
                    return True
        elif isinstance(param, Parameter):
            return param in self.parameters
        elif isinstance(param, ReturnValue):
            return param == self.return_value
        return False


class FunctionMacro(Callable):
    def __init__(self, name: str, namespace: T.Optional[str], identifier: str):
        super().__init__(name, namespace, identifier)


class Function(Callable):
    def __init__(self, name: str, namespace: T.Optional[str], identifier: str, throws: bool = False):
        super().__init__(name, namespace, identifier, throws)


class Method(Callable):
    def __init__(self, name: str, identifier: str, instance_param: Parameter, throws: bool = False):
        super().__init__(name, None, identifier, throws)
        self.instance_param = instance_param

    def __contains__(self, param):
        if isinstance(param, Parameter) and param == self.instance_param:
            return True
        return super().__contains__(self, param)


class VirtualMethod(Callable):
    def __init__(self, name: str, identifier: str, invoker: str, instance_param: Parameter, throws: bool = False):
        super().__init__(name, None, identifier, throws)
        self.instance_param = instance_param
        self.invoker = invoker

    def __contains__(self, param):
        if isinstance(param, Parameter) and param == self.instance_param:
            return True
        return super().__contains__(self, param)


class Callback(Callable):
    def __init__(self, name: str, namespace: str, ctype: T.Optional[str], throws: bool = False):
        super().__init__(name=name, namespace=namespace, identifier=None, throws=throws)
        self.ctype = ctype

    @property
    def base_ctype(self):
        if self.ctype is None:
            return None
        return self.ctype.replace('*', '')


class Member(GIRElement):
    """A member in an enumeration, error domain, or bitfield"""
    def __init__(self, name: str, value: str, identifier: str, nick: str):
        super().__init__(name)
        self.value = value
        self.identifier = identifier
        self.nick = nick


class Enumeration(Type):
    """An enumeration type"""
    def __init__(self, name: str, namespace: str, ctype: str, gtype: T.Optional[GType]):
        super().__init__(name=name, ctype=ctype, namespace=namespace)
        self.gtype = gtype
        self.members: T.List[Member] = []
        self.functions: T.List[Function] = []

    def add_member(self, member: Member) -> None:
        self.members.append(member)

    def add_function(self, function: Function) -> None:
        self.functions.append(function)

    def set_members(self, members: T.List[Member]) -> None:
        self.members.extend(members)

    def set_functions(self, functions: T.List[Function]) -> None:
        self.functions.extend(functions)

    def __contains__(self, member):
        if isinstance(member, Member):
            return member in self.members
        return False

    def __iter__(self):
        for member in self.members:
            yield member


class BitField(Enumeration):
    """An enumeration type of bit masks"""
    def __init__(self, name: str, namespace: str, ctype: str, gtype: T.Optional[GType]):
        super().__init__(name, namespace, ctype, gtype)


class ErrorDomain(Enumeration):
    """An error domain for GError"""
    def __init__(self, name: str, namespace: str, ctype: str, gtype: T.Optional[GType], domain: str):
        super().__init__(name, namespace, ctype, gtype)
        self.domain = domain


class Property(GIRElement):
    def __init__(self, name: str, transfer: str, target: Type, writable: bool = True, readable: bool = True, construct: bool = False,
                 construct_only: bool = False):
        super().__init__(name)
        self.transfer = transfer
        self.writable = writable
        self.readable = readable
        self.construct = construct
        self.construct_only = construct_only
        self.target = target


class Signal(GIRElement):
    def __init__(self, name: str, detailed: bool, when: str, action: bool = False, no_hooks: bool = False, no_recurse: bool = False):
        super().__init__(name)
        self.detailed = detailed
        self.when = when
        self.action = action
        self.no_hooks = no_hooks
        self.no_recurse = no_recurse
        self.parameters: T.List[Parameter] = []
        self.return_value: T.Optional[ReturnValue] = None

    def set_parameters(self, params: T.List[Parameter]) -> None:
        self.parameters.extend(params)

    def set_return_value(self, res: ReturnValue) -> None:
        self.return_value = res


class Field(GIRElement):
    """A field in a struct or union"""
    def __init__(self, name: str, target: Type, writable: bool, readable: bool, private: bool = False, bits: int = 0):
        super().__init__(name)
        self.target = target
        self.writable = writable
        self.readable = readable
        self.private = private
        self.bits = bits


class Interface(Type):
    def __init__(self, name: str, namespace: str, ctype: str, symbol_prefix: str, gtype: GType):
        super().__init__(name=name, ctype=ctype, namespace=namespace)
        self.symbol_prefix = symbol_prefix
        self.gtype = gtype
        self.methods: T.List[Method] = []
        self.virtual_methods: T.List[VirtualMethod] = []
        self.properties: T.Mapping[str, Property] = {}
        self.signals: T.Mapping[str, Signal] = {}
        self.functions: T.List[Function] = []
        self.fields: T.List[Field] = []
        self.prerequisite: T.Optional[str] = None

    @property
    def type_struct(self) -> T.Optional[str]:
        if self.gtype is not None:
            return self.gtype.type_struct
        return self.ctype

    @property
    def type_func(self) -> str:
        return self.gtype.get_type

    def set_methods(self, methods: T.List[Method]) -> None:
        self.methods.extend(methods)

    def set_virtual_methods(self, methods: T.List[VirtualMethod]) -> None:
        self.virtual_methods.extend(methods)

    def set_properties(self, properties: T.List[Property]) -> None:
        for p in properties:
            self.properties[p.name] = p

    def set_signals(self, signals: T.List[Signal]) -> None:
        for s in signals:
            self.signals[s.name] = s

    def set_functions(self, functions: T.List[Function]) -> None:
        self.functions.extend(functions)

    def set_fields(self, fields: T.List[Field]) -> None:
        self.fields.extend(fields)

    def set_prerequisite(self, prerequisite: str) -> None:
        self.prerequisite = prerequisite


class Class(Type):
    def __init__(self, name: str, namespace: str, ctype: str, symbol_prefix: str,
                 gtype: GType, parent: T.Optional[Type] = None,
                 abstract: bool = False, fundamental: bool = False,
                 ref_func: T.Optional[str] = None, unref_func: T.Optional[str] = None):
        super().__init__(name=name, ctype=ctype, namespace=namespace)
        self.symbol_prefix = symbol_prefix
        self.parent = parent
        self.abstract = abstract
        self.fundamental = fundamental
        self.ref_func = ref_func
        self.unref_func = unref_func
        self.gtype = gtype
        self.ancestors: T.List[Type] = []
        self.implements: T.List[Type] = []
        self.constructors: T.List[Function] = []
        self.methods: T.List[Method] = []
        self.virtual_methods: T.List[VirtualMethod] = []
        self.properties: T.Mapping[str, Property] = {}
        self.signals: T.Mapping[str, Signal] = {}
        self.functions: T.List[Function] = []
        self.fields: T.List[Field] = []
        self.callbacks: T.List[Callback] = []

    @property
    def type_struct(self) -> T.Optional[str]:
        if self.gtype is not None:
            return self.gtype.type_struct
        return None

    @property
    def type_func(self) -> T.Optional[str]:
        if self.gtype is not None:
            return self.gtype.get_type
        return self.ctype

    def set_constructors(self, ctors: T.List[Function]) -> None:
        self.constructors.extend(ctors)

    def set_methods(self, methods: T.List[Method]) -> None:
        self.methods.extend(methods)

    def set_virtual_methods(self, methods: T.List[VirtualMethod]) -> None:
        self.virtual_methods.extend(methods)

    def set_properties(self, properties: T.List[Property]) -> None:
        for p in properties:
            self.properties[p.name] = p

    def set_signals(self, signals: T.List[Signal]) -> None:
        for s in signals:
            self.signals[s.name] = s

    def set_functions(self, functions: T.List[Function]) -> None:
        self.functions.extend(functions)

    def set_implements(self, ifaces: T.List[Type]) -> None:
        self.implements.extend(ifaces)

    def set_fields(self, fields: T.List[Field]) -> None:
        self.fields.extend(fields)


class Boxed(Type):
    def __init__(self, name: str, namespace: str, symbol_prefix: str, gtype: GType):
        super().__init__(name=name, ctype=None, namespace=namespace)
        self.symbol_prefix = symbol_prefix
        self.gtype = gtype
        self.functions: T.List[Function] = []

    def set_functions(self, functions: T.List[Function]) -> None:
        self.functions.extend(functions)


class Record(Type):
    def __init__(self, name: str, namespace: str, ctype: str, symbol_prefix: str,
                 gtype: T.Optional[GType] = None, struct_for: T.Optional[str] = None,
                 disguised: bool = False):
        super().__init__(name=name, ctype=ctype, namespace=namespace)
        self.symbol_prefix = symbol_prefix
        self.gtype = gtype
        self.struct_for = struct_for
        self.disguised = disguised
        self.constructors: T.List[Function] = []
        self.methods: T.List[Method] = []
        self.functions: T.List[Function] = []
        self.fields: T.List[Field] = []

    @property
    def type_struct(self) -> T.Optional[str]:
        if self.gtype is not None:
            return self.gtype.type_struct
        return self.ctype

    @property
    def type_func(self) -> T.Optional[str]:
        if self.gtype is not None:
            return self.gtype.get_type
        return None

    def set_constructors(self, ctors: T.List[Function]) -> None:
        self.constructors.extend(ctors)

    def set_methods(self, methods: T.List[Method]) -> None:
        self.methods.extend(methods)

    def set_functions(self, functions: T.List[Function]) -> None:
        self.functions.extend(functions)

    def set_fields(self, fields: T.List[Field]) -> None:
        self.fields.extend(fields)


class Union(Type):
    def __init__(self, name: str, namespace: str, ctype: str, symbol_prefix: str, gtype: T.Optional[GType]):
        super().__init__(name=name, ctype=ctype, namespace=namespace)
        self.symbol_prefix = symbol_prefix
        self.gtype = gtype
        self.constructors: T.List[Function] = []
        self.methods: T.List[Method] = []
        self.functions: T.List[Function] = []
        self.fields: T.List[Field] = []

    @property
    def type_struct(self) -> T.Optional[str]:
        if self.gtype is not None:
            return self.gtype.type_struct
        return self.ctype

    @property
    def type_func(self) -> T.Optional[str]:
        if self.gtype is not None:
            return self.gtype.get_type
        return None

    def set_constructors(self, ctors: T.List[Function]) -> None:
        self.constructors.extend(ctors)

    def set_methods(self, methods: T.List[Method]) -> None:
        self.methods.extend(methods)

    def set_functions(self, functions: T.List[Function]) -> None:
        self.functions.extend(functions)

    def set_fields(self, fields: T.List[Field]) -> None:
        self.fields.extend(fields)


class Namespace:
    def __init__(self, name: str, version: str, identifier_prefix: T.List[str] = [], symbol_prefix: T.List[str] = []):
        self.name = name
        self.version = version

        self._shared_libraries: T.List[str] = []

        self._aliases: T.Mapping[str, Alias] = {}
        self._bitfields: T.Mapping[str, BitField] = {}
        self._boxeds: T.Mapping[str, Boxed] = {}
        self._callbacks: T.Mapping[str, Callback] = {}
        self._classes: T.Mapping[str, Class] = {}
        self._constants: T.Mapping[str, Constant] = {}
        self._enumerations: T.Mapping[str, Enumeration] = {}
        self._error_domains: T.Mapping[str, ErrorDomain] = {}
        self._functions: T.Mapping[str, Function] = {}
        self._function_macros: T.Mapping[str, FunctionMacro] = {}
        self._interfaces: T.Mapping[str, Interface] = {}
        self._records: T.Mapping[str, Record] = {}
        self._unions: T.Mapping[str, Union] = {}

        self._symbols: T.Mapping[str, Type] = {}
        self.repository: T.Optional[Repository] = None

        if identifier_prefix:
            self.identifier_prefix = identifier_prefix
        else:
            self.identifier_prefix = [self.name]
        if symbol_prefix:
            self.symbol_prefix = symbol_prefix
        else:
            self.symbol_prefix = [self.name.lower()]

    def __str__(self):
        return f"{self.name}-{self.version}"

    def add_shared_libraries(self, libs: T.List[str]) -> None:
        self._shared_libraries.extend(libs)

    def get_shared_libraries(self) -> T.List[str]:
        return self._shared_libraries

    def add_alias(self, alias: Alias) -> None:
        self._aliases[alias.name] = alias

    def add_enumeration(self, enum: Enumeration) -> None:
        self._enumerations[enum.name] = enum

    def add_error_domain(self, domain: ErrorDomain) -> None:
        self._error_domains[domain.name] = domain

    def add_class(self, cls: Class) -> None:
        self._classes[cls.name] = cls

    def add_constant(self, constant: Constant) -> None:
        self._constants[constant.name] = constant

    def add_interface(self, interface: Interface) -> None:
        self._interfaces[interface.name] = interface

    def add_boxed(self, boxed: Boxed) -> None:
        self._boxeds[boxed.name] = boxed

    def add_record(self, record: Record) -> None:
        self._records[record.name] = record

    def add_union(self, union: Union) -> None:
        self._unions[union.name] = union

    def add_function(self, function: Function) -> None:
        self._functions[function.name] = function

    def add_bitfield(self, bitfield: BitField) -> None:
        self._bitfields[bitfield.name] = bitfield

    def add_function_macro(self, function: FunctionMacro) -> None:
        self._function_macros[function.name] = function

    def add_callback(self, callback: Callback) -> None:
        self._callbacks[callback.name] = callback

    def get_classes(self) -> T.List[Class]:
        return self._classes.values()

    def get_constants(self) -> T.List[Constant]:
        return self._constants.values()

    def get_enumerations(self) -> T.List[Enumeration]:
        return self._enumerations.values()

    def get_error_domains(self) -> T.List[ErrorDomain]:
        return self._error_domains.values()

    def get_aliases(self) -> T.List[Alias]:
        return self._aliases.values()

    def get_interfaces(self) -> T.List[Interface]:
        return self._interfaces.values()

    def get_boxeds(self) -> T.List[Boxed]:
        return self._boxeds.values()

    def get_records(self) -> T.List[Record]:
        return self._records.values()

    def get_effective_records(self) -> T.List[Record]:
        def is_effective(r):
            if "Private" in r.name and r.disguised:
                return False
            if r.struct_for is not None:
                return False
            return True

        return [x for x in self._records.values() if is_effective(x)]

    def get_unions(self) -> T.List[Union]:
        return self._unions.values()

    def get_functions(self) -> T.List[Function]:
        return self._functions.values()

    def get_bitfields(self) -> T.List[BitField]:
        return self._bitfields.values()

    def get_function_macros(self) -> T.List[FunctionMacro]:
        return self._function_macros.values()

    def get_effective_function_macros(self) -> T.List[FunctionMacro]:
        def is_effective(f, ns):
            # Lower-case identifiers are an automatic pass
            if f.name.islower():
                return True
            # Try to eliminate the GObject type macros from the pool
            t = f.name.split('_')
            # Skip "is-a" macros
            if 'IS' in t:
                return False
            # Skip "get class/iface" macros
            if 'GET' in t:
                return False
            # Re-assemble into what most likely is a type name
            s = "".join([x.capitalize() if len(x) > 2 else x for x in t])
            # Skip "cast" macros
            if ns.find_class(s) is not None:
                return False
            if ns.find_interface(s) is not None:
                return False
            if ns.find_record(s) is not None:
                return False
            # Anything that survived at this point is likely a valid function
            # macro
            return True

        return [x for x in self._function_macros.values() if is_effective(x, self)]

    def get_callbacks(self) -> T.List[Callback]:
        return self._callbacks.values()

    def find_class(self, cls: str) -> T.Optional[Class]:
        return self._classes.get(cls)

    def find_record(self, record: str) -> T.Optional[Record]:
        return self._records.get(record)

    def find_interface(self, iface: str) -> T.Optional[Interface]:
        return self._interfaces.get(iface)

    def find_union(self, union: str) -> T.Optional[Union]:
        return self._unions.get(union)

    def find_enumeration(self, enum: str) -> T.Optional[Enumeration]:
        return self._enumerations.get(enum)

    def find_bitfield(self, bitfield: str) -> T.Optional[BitField]:
        return self._bitfields.get(bitfield)

    def find_error_domain(self, domain: str) -> T.Optional[ErrorDomain]:
        return self._error_domains.get(domain)

    def find_alias(self, alias: str) -> T.Optional[Alias]:
        return self._aliases.get(alias)

    def find_function(self, func: str) -> T.Optional[Function]:
        if func in self._functions:
            return self._functions.get(func)
        if func in self._function_macros:
            return self._function_macros.get(func)
        return None

    def find_real_type(self, name: str) -> T.Optional[Type]:
        if name in self._aliases:
            return self._aliases[name]
        if name in self._bitfields:
            return self._bitfields[name]
        if name in self._callbacks:
            return self._callbacks[name]
        if name in self._constants:
            return self._constants[name]
        if name in self._enumerations:
            return self._enumerations[name]
        if name in self._error_domains:
            return self._error_domains[name]
        if name in self._classes:
            return self._classes[name]
        if name in self._interfaces:
            return self._interfaces[name]
        if name in self._records:
            return self._records[name]
        if name in self._unions:
            return self._unions[name]
        return None

    def find_symbol(self, name: str) -> T.Optional[Type]:
        return self._symbols.get(name)

    def find_prerequisite_type(self, name: str) -> T.Optional[Type]:
        if name in self._classes:
            return self._classes[name]
        if name is self._interfaces:
            return self._interfaces[name]
        return None


class Repository:
    def __init__(self):
        self.includes: T.Mapping[str, Repository] = {}
        self.packages: T.List[Package] = []
        self.c_includes: T.List[CInclude] = []
        self.types: T.Mapping[str, T.List[Type]] = {}
        self._namespaces: T.List[Namespace] = []
        self.girfile: T.Optional[str] = None

    def add_namespace(self, ns: Namespace) -> None:
        self._namespaces.append(ns)
        ns.repository = self

    def get_namespace(self, ns: str) -> T.Optional[Namespace]:
        for namespace in self._namespaces:
            if namespace.name == ns:
                return namespace
        return None

    def find_included_namespace(self, ns: str) -> T.Optional[Namespace]:
        for repo_name in self.includes:
            repo = self.includes[repo_name]
            if repo.namespace.name == ns:
                return repo.namespace
        return None

    def resolve_empty_ctypes(self, seen_types: T.Mapping[str, T.List[Type]]) -> None:
        for fqtn in seen_types:
            types = seen_types[fqtn]
            resolved_types = [t for t in types if t.resolved]
            if len(resolved_types) == 0:
                ns, name = fqtn.split('.', 1)
                backstop = f"{self.namespace.identifier_prefix[0]}{name}"
                resolved_types.append(Type(fqtn, backstop))
            self.types[fqtn] = resolved_types
            log.debug(f"Type: {fqtn}: {resolved_types}")

    def resolve_interface_requires(self) -> None:
        def find_prerequisite_type(includes, ns, name):
            for repo in includes.values():
                if repo.namespace.name != ns:
                    continue
                prereq = repo.namespace.find_prerequisite_type(name)
                if prereq is not None:
                    return Type(name=f"{repo.namespace.name}.{prereq.name}", ctype=prereq.ctype)
            return None

        ifaces = self.namespace.get_interfaces()
        for iface in ifaces:
            if iface.prerequisite is None:
                continue
            prerequisite = None
            if '.' in iface.prerequisite.name:
                ns, name = iface.prerequisite.name.split('.', 1)
                if ns == self.namespace.name:
                    prerequisite = self.namespace.find_prerequisite_type(name)
                else:
                    prerequisite = find_prerequisite_type(self.includes, ns, name)
            else:
                prerequisite = self.namespace.find_prerequisite_type(iface.prerequisite.name)
            if prerequisite is not None:
                if prerequisite.ctype is None:
                    t = self.find_type(prerequisite.name)
                    prerequisite.ctype = t.ctype
                iface.prerequisite = prerequisite
                log.debug(f"Prerequisite type for interface {iface}: {iface.prerequisite}")

    def resolve_class_type(self) -> None:
        classes = self.namespace.get_classes()
        for cls in classes:
            if cls.ctype is None:
                if '.' not in cls.name:
                    name = f"{self.namespace.name}.{cls.name}"
                else:
                    name = cls.name
                t = self.find_type(name)
                if t is not None:
                    cls.ctype = t.base_ctype
                else:
                    # This is kind of a kludge, but apparently we can get into
                    # class definitions missing a c:type; if that happens, we
                    # take the identifier prefix of the namespace and append the
                    # class name, because that's the inverse of how g-ir-scanner
                    # determines the class name
                    cls.ctype = f"{self.namespace.identifier_prefix[0]}{cls.name}"
                log.debug(f"Updated C type for {cls}")

    def resolve_class_implements(self) -> None:
        def find_interface_type(includes, ns, name):
            for repo in includes.values():
                if repo.namespace.name != ns:
                    continue
                iface = repo.namespace.find_interface(name)
                if iface is not None:
                    return Type(name=f"{repo.namespace.name}.{iface.name}", ctype=iface.ctype)
            return None

        classes = self.namespace.get_classes()
        for cls in classes:
            if cls.implements is None:
                continue
            implements = cls.implements
            cls.implements = []
            for iface in implements:
                if '.' in iface.name:
                    ns, name = iface.name.split('.', 1)
                    if ns == self.namespace.name:
                        iface_type = self.namespace.find_interface(name)
                    else:
                        iface_type = find_interface_type(self.includes, ns, name)
                else:
                    iface_type = self.namespace.find_interface(iface.name)
                if iface_type is not None:
                    if iface_type.ctype is None:
                        t = self.find_type(iface_type.name)
                        iface_type.ctype = t.ctype
                    cls.implements.append(iface_type)
            log.debug(f"Interfaces implemented by {cls}: {cls.implements}")

    def resolve_class_ancestors(self) -> None:
        def find_parent_class(includes, ns, name):
            repository = includes.get(ns)
            if repository is None:
                return None
            parent_class = repository.namespace.find_class(name)
            # If the parent type is unqualified, then we qualify it here
            if '.' not in parent_class.name:
                parent_class.name = f"{repository.namespace.name}.{parent_class.name}"
            return parent_class

        classes = self.namespace.get_classes()
        for cls in classes:
            if cls.parent is None:
                continue
            ancestors = []
            parent = cls.parent
            while parent is not None:
                if '.' in parent.name:
                    ns, name = parent.name.split('.')
                    if ns == self.namespace.name:
                        real_parent = self.namespace.find_class(name)
                    else:
                        real_parent = find_parent_class(self.includes, ns, name)
                else:
                    real_parent = self.namespace.find_class(parent.name)
                if real_parent is None:
                    break
                if real_parent.parent is not None and real_parent.parent.name == parent.name:
                    log.warning(f"Found a loop in the ancestors for {cls}: {real_parent} matches {parent}")
                    break
                if real_parent.ctype is None:
                    log.debug(f"Looking up C type for {parent.fqtn}")
                    t = self.find_type(parent.name)
                    real_parent.ctype = t.ctype
                log.debug(f"Adding ancestor {real_parent} for {cls}")
                ancestors.append(real_parent)
                parent = real_parent.parent
            cls.ancestors = ancestors
            cls.parent = ancestors[0]
            log.debug(f"Ancestors for {cls}: parent: {cls.parent}, ancestors: {cls.ancestors}")

    def resolve_moved_to(self) -> None:
        functions = list(self.namespace.get_functions())
        old_len = len(functions)
        for func in functions[:]:
            if func.moved_to is None:
                continue
            moved_type, moved_func_name = func.moved_to.split('.')
            real_type = self.namespace.find_real_type(moved_type)
            if real_type is None:
                continue
            self.namespace._functions.pop(func.name)    # XXX: Add accessor
        new_len = len(self.namespace._functions)
        diff = old_len - new_len
        log.debug(f"Removed {old_len} - {new_len} functions: {diff}")

    def resolve_symbols(self) -> None:
        symbols: T.Mapping[str, Type] = {}
        for func in self.namespace.get_functions():
            symbols[func.identifier] = func
        for func in self.namespace.get_function_macros():
            symbols[func.identifier] = func
        for cls in self.namespace.get_classes():
            for m in cls.constructors:
                symbols[m.identifier] = cls
            for m in cls.methods:
                symbols[m.identifier] = cls
            for m in cls.functions:
                symbols[m.identifier] = cls
        for iface in self.namespace.get_interfaces():
            for m in iface.methods:
                symbols[m.identifier] = iface
            for m in iface.functions:
                symbols[m.identifier] = iface
        for record in self.namespace.get_records():
            for m in record.constructors:
                symbols[m.identifier] = record
            for m in record.methods:
                symbols[m.identifier] = record
            for m in record.functions:
                symbols[m.identifier] = record
        for union in self.namespace.get_unions():
            for m in union.constructors:
                symbols[m.identifier] = union
            for m in union.methods:
                symbols[m.identifier] = union
            for m in union.functions:
                symbols[m.identifier] = union
        self.namespace._symbols = symbols

    def get_class_hierarchy(self, root=None):
        flat_tree = []
        seen_types = {}

        def window(iterable, size=2):
            i = iter(iterable)
            win = []
            for e in range(0, size):
                win.append(next(i))
            yield win
            for e in i:
                win = win[1:] + [e]
                yield win

        for cls in self.namespace.get_classes():
            if cls.parent is None:
                flat_tree.append((cls.name, None))
                continue

            if len(cls.ancestors) < 2:
                flat_tree.append((cls.name, cls.ancestors[0].name))
            else:
                flat_tree.append((cls.name, cls.ancestors[0].name))
                for chunk in window(cls.ancestors, size=2):
                    if chunk[0].name in seen_types:
                        continue
                    if len(chunk) == 2:
                        flat_tree.append((chunk[0].name, chunk[1].name))
                    else:
                        flat_tree.append((chunk[0].name, None))
                    seen_types[chunk[0].name] = 1

        def subtree(cls, rel):
            return {
                v: subtree(v, rel)
                for v in [x[0] for x in rel if x[1] == cls]
            }

        return subtree(root, flat_tree)

    @property
    def namespace(self) -> T.Optional[Namespace]:
        return self._namespaces[0]

    def find_type(self, name: str) -> T.Optional[Type]:
        types = self.types.get(name)
        if types is None:
            return None
        for t in types:
            if t.resolved:
                return t
        return types[0]
