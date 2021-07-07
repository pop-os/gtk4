# SPDX-FileCopyrightText: 2020 GNOME Foundation
# SPDX-License-Identifier: Apache-2.0 OR GPL-3.0-or-later

import argparse
import sys

from . import gir, log, utils


HELP_MSG = "Generates an index of all the symbols"


def add_args(parser):
    parser.add_argument("--add-include-path", action="append", dest="include_paths", default=[],
                        help="include paths for other GIR files")
    parser.add_argument("infile", metavar="GIRFILE", type=argparse.FileType('r', encoding='UTF-8'),
                        default=sys.stdin, help="the GIR file to parse")


def _print_function(function):
    return_val = f" -> {log.color(function.return_value.target.ctype, 40)}"
    func_name = f"{log.color(function.name, 220)}"

    params = []
    for param in function.parameters:
        params += [f"{param.name}: {log.color(param.target.ctype, 40)}"]

    params = ', '.join(params)

    return f"{func_name}({params}){return_val}"


def _print_method(method):
    return_val = f" -> {log.color(method.return_value.target.ctype, 40)}"
    method_name = f"{log.color(method.name, 220)}"

    params = ['self']
    for param in method.parameters:
        params += [f"{param.name}: {log.color(param.target.ctype, 40)}"]

    params = ', '.join(params)

    return f"{method_name}({params}){return_val}"


def _print_property(prop):
    flags = []
    if prop.readable:
        flags += [log.color('readable', 196)]
    if prop.writable:
        flags += [log.color('writable', 196)]
    if prop.construct:
        flags += [log.color('construct', 196)]
    if prop.construct_only:
        flags += [log.color('construct-only', 196)]

    flags = ', '.join(flags)

    return f"{log.color(prop.name, 220)}: {flags} -> {log.color(prop.target.name, 40)}"


def _print_signal(signal):
    return_val = f" -> {log.color(signal.return_value.target.ctype, 40)}"
    signal_name = f"{log.color(signal.name, 220)}"

    params = ['self']
    for param in signal.parameters:
        params += [f"{param.name}: {log.color(param.target.ctype, 40)}"]

    params = ', '.join(params)

    return f"{signal_name}({params}){return_val}"


def _print_enum_member(member):
    return f"{log.color(member.name.upper(), 220)} = {member.value} ({member.nick})"


def _print_enum_members(enum, sections=[], is_last_enum=False, is_last_branch=False):
    if is_last_branch:
        root_branch = ' '
    else:
        root_branch = '│'

    if is_last_enum:
        enum_branch = ' '
    else:
        enum_branch = '│'

    if not sections:
        sect_branch = '└──'
        member_branch = ' '
    else:
        sect_branch = '├──'
        member_branch = '│'

    title = str(log.color('Members', 36))
    log.log(f'    {root_branch}   {enum_branch}   {sect_branch} {title}')

    for i, member in enumerate(enum.members):
        is_last_member = i == len(enum.members) - 1
        enum_str = _print_enum_member(member)

        if is_last_member:
            leaf = '└──'
        else:
            leaf = '├──'

        log.log(f'    {root_branch}   {enum_branch}   {member_branch}   {leaf} {enum_str}')


def _print_enum_functions(enum, sections=[], is_last_enum=False, is_last_branch=False):
    if not enum.functions:
        return

    if is_last_branch:
        root_branch = ' '
    else:
        root_branch = '│'

    if is_last_enum:
        enum_branch = ' '
    else:
        enum_branch = '│'

    if not sections:
        sect_branch = '└──'
        member_branch = ' '
    else:
        sect_branch = '├──'
        member_branch = '│'

    title = str(log.color('Functions', 36))
    log.log(f'    {root_branch}   {enum_branch}   {sect_branch} {title}')

    for i, function in enumerate(enum.functions):
        is_last_function = i == len(enum.functions) - 1
        func_str = _print_function(function)

        if is_last_function:
            leaf = '└──'
        else:
            leaf = '├──'

        log.log(f'    {root_branch}   {enum_branch}   {member_branch}   {leaf} {func_str}')


def _print_class_implements(cls, sections=[], is_last_class=False):
    if not cls.implements:
        return

    root_branch = '│'

    if is_last_class:
        ifaces_branch = ' '
    else:
        ifaces_branch = '│'

    if not sections:
        sect_branch = '└──'
        iface_branch = ' '
    else:
        sect_branch = '├──'
        iface_branch = '│'

    title = str(log.color('Implements', 36))
    log.log(f'    {root_branch}   {ifaces_branch}   {sect_branch} {title}')

    for i, iface in enumerate(cls.implements):
        is_last_iface = i == len(cls.implements) - 1
        if is_last_iface:
            leaf = '└──'
        else:
            leaf = '├──'

        log.log(f'    {root_branch}   {ifaces_branch}   {iface_branch}   {leaf} {iface}')


def _print_class_properties(cls, sections=[], is_last_class=False):
    if not cls.properties:
        return

    root_branch = '│'

    if is_last_class:
        props_branch = ' '
    else:
        props_branch = '│'

    if not sections:
        sect_branch = '└──'
        prop_branch = ' '
    else:
        sect_branch = '├──'
        prop_branch = '│'

    title = str(log.color('Properties', 36))
    log.log(f'    {root_branch}   {props_branch}   {sect_branch} {title}')

    for i, prop in enumerate(cls.properties.values()):
        is_last_prop = i == len(cls.properties) - 1
        prop_str = _print_property(prop)
        if is_last_prop:
            leaf = '└──'
        else:
            leaf = '├──'

        log.log(f'    {root_branch}   {props_branch}   {prop_branch}   {leaf} {prop_str}')


def _print_class_signals(cls, sections=[], is_last_class=False):
    if not cls.signals:
        return

    root_branch = '│'

    if is_last_class:
        signals_branch = ' '
    else:
        signals_branch = '│'

    if not sections:
        sect_branch = '└──'
        signal_branch = ' '
    else:
        sect_branch = '├──'
        signal_branch = '│'

    title = str(log.color('Signals', 36))
    log.log(f'    {root_branch}   {signals_branch}   {sect_branch} {title}')

    for i, signal in enumerate(cls.signals.values()):
        is_last_signal = i == len(cls.signals) - 1
        signal_str = _print_signal(signal)
        if is_last_signal:
            leaf = '└──'
        else:
            leaf = '├──'

        log.log(f'    {root_branch}   {signals_branch}   {signal_branch}   {leaf} {signal_str}')


def _print_class_constructors(cls, sections=[], is_last_class=False):
    if not cls.constructors:
        return

    root_branch = '│'

    if is_last_class:
        ctors_branch = ' '
    else:
        ctors_branch = '│'

    if not sections:
        sect_branch = '└──'
        ctor_branch = ' '
    else:
        sect_branch = '├──'
        ctor_branch = '│'

    title = str(log.color('Constructors', 36))
    log.log(f'    {root_branch}   {ctors_branch}   {sect_branch} {title}')

    for i, ctor in enumerate(cls.constructors):
        is_last_ctor = i == len(cls.constructors) - 1
        ctor_str = _print_function(ctor)
        if is_last_ctor:
            leaf = '└──'
        else:
            leaf = '├──'

        log.log(f'    {root_branch}   {ctors_branch}   {ctor_branch}   {leaf} {ctor_str}')


def _print_class_methods(cls, sections=[], is_last_class=False):
    if not cls.methods:
        return

    root_branch = '│'

    if is_last_class:
        methods_branch = ' '
    else:
        methods_branch = '│'

    if not sections:
        sect_branch = '└──'
        method_branch = ' '
    else:
        sect_branch = '├──'
        method_branch = '│'

    title = str(log.color('Methods', 36))
    log.log(f'    {root_branch}   {methods_branch}   {sect_branch} {title}')

    for i, method in enumerate(cls.methods):
        is_last_method = i == len(cls.methods) - 1
        method_str = _print_method(method)
        if is_last_method:
            leaf = '└──'
        else:
            leaf = '├──'

        log.log(f'    {root_branch}   {methods_branch}   {method_branch}   {leaf} {method_str}')


def _print_class_functions(cls, sections=[], is_last_class=False):
    if not cls.functions:
        return

    root_branch = '│'

    if is_last_class:
        functions_branch = ' '
    else:
        functions_branch = '│'

    if not sections:
        sect_branch = '└──'
        function_branch = ' '
    else:
        sect_branch = '├──'
        function_branch = '│'

    title = str(log.color('Functions', 36))
    log.log(f'    {root_branch}   {functions_branch}   {sect_branch} {title}')

    for i, function in enumerate(cls.functions):
        is_last_func = i == len(cls.functions) - 1
        func_str = _print_function(function)
        if is_last_func:
            leaf = '└──'
        else:
            leaf = '├──'

        log.log(f'    {root_branch}   {functions_branch}   {function_branch}   {leaf} {func_str}')


def gen_tree(repository):
    includes = ', '.join([str(repository.includes[r]) for r in repository.includes])
    c_includes = ', '.join(repository.c_includes)
    packages = ', '.join(repository.packages)

    title = str(log.color('Repository', 12))
    log.log(f'{title}')
    log.log(f'├── Includes:  {includes}')
    log.log(f'├── C headers: {c_includes}')
    log.log(f'├── Packages:  {packages}')

    namespace = repository.namespace
    shlibs = ', '.join(namespace.get_shared_libraries())

    aliases = sorted(namespace.get_aliases(), key=lambda alias: alias.name.lower())
    classes = sorted(namespace.get_classes(), key=lambda cls: cls.name.lower())
    constants = sorted(namespace.get_constants(), key=lambda const: const.name.lower())
    domains = sorted(namespace.get_error_domains(), key=lambda domain: domain.name.lower())
    enums = sorted(namespace.get_enumerations(), key=lambda enum: enum.name.lower())
    functions = sorted(namespace.get_functions(), key=lambda func: func.name.lower())
    interfaces = sorted(namespace.get_interfaces(), key=lambda interface: interface.name.lower())
    records = sorted(namespace.get_records(), key=lambda record: record.name.lower())
    unions = sorted(namespace.get_unions(), key=lambda union: union.name.lower())

    title = str(log.color('Namespace', 36))
    log.log(f'└── {title}: {namespace.name}, version: {namespace.version}')
    log.log(f'    ├── Shared libraries: {shlibs}')

    title = str(log.color('Classes', 36))
    log.log(f'    ├── {title}')

    if len(classes) == 0:
        log.log('    │   └── None')
    else:
        for i, cls in enumerate(classes):
            is_last_class = i == len(classes) - 1
            if is_last_class:
                log.log(f'    │   └── {cls.name} - parent: {cls.parent}, abstract: {log.color(cls.abstract, 196)}')
            else:
                log.log(f'    │   ├── {cls.name} - parent: {cls.parent}, abstract: {log.color(cls.abstract, 196)}')

            sections = []
            if cls.implements:
                sections += ['implements']
            if cls.properties:
                sections += ['properties']
            if cls.signals:
                sections += ['signals']
            if cls.constructors:
                sections += ['constructors']
            if cls.methods:
                sections += ['methods']
            if cls.functions:
                sections += ['functions']

            if 'implements' in sections:
                sections.remove('implements')
                _print_class_implements(cls, sections, is_last_class)
            if 'properties' in sections:
                sections.remove('properties')
                _print_class_properties(cls, sections, is_last_class)
            if 'signals' in sections:
                sections.remove('signals')
                _print_class_signals(cls, sections, is_last_class)
            if 'constructors' in sections:
                sections.remove('constructors')
                _print_class_constructors(cls, sections, is_last_class)
            if 'methods' in sections:
                sections.remove('methods')
                _print_class_methods(cls, sections, is_last_class)
            if 'functions' in sections:
                sections.remove('functions')
                _print_class_functions(cls, sections, is_last_class)

    title = str(log.color('Interfaces', 36))
    log.log(f'    ├── {title}')

    if len(interfaces) == 0:
        log.log('    │   └── None')
    else:
        for i, iface in enumerate(interfaces):
            is_last_iface = i == len(interfaces) - 1
            if is_last_iface:
                log.log(f'    │   └── {iface.name}, prerequisite: {iface.prerequisite}')
            else:
                log.log(f'    │   ├── {iface.name}, prerequisite: {iface.prerequisite}')

            sections = []
            if iface.properties:
                sections += ['properties']
            if iface.signals:
                sections += ['signals']
            if iface.methods:
                sections += ['methods']
            if iface.functions:
                sections += ['functions']

            if 'properties' in sections:
                sections.remove('properties')
                _print_class_properties(iface, sections, is_last_iface)
            if 'signals' in sections:
                sections.remove('signals')
                _print_class_signals(iface, sections, is_last_iface)
            if 'methods' in sections:
                sections.remove('methods')
                _print_class_methods(iface, sections, is_last_iface)
            if 'functions' in sections:
                sections.remove('functions')
                _print_class_functions(iface, sections, is_last_iface)

    title = str(log.color('Records', 36))
    log.log(f'    ├── {title}')

    if len(records) == 0:
        log.log('    │   └── None')
    else:
        for i, record in enumerate(records):
            is_last_record = i == len(records) - 1
            if is_last_record:
                log.log(f'    │   └── {record.name}')
            else:
                log.log(f'    │   ├── {record.name}')

            sections = []
            if record.constructors:
                sections += ['constructors']
            if record.methods:
                sections += ['methods']
            if record.functions:
                sections += ['functions']

            if 'constructors' in sections:
                sections.remove('constructors')
                _print_class_constructors(record, sections, is_last_record)
            if 'methods' in sections:
                sections.remove('methods')
                _print_class_methods(record, sections, is_last_record)
            if 'functions' in sections:
                sections.remove('functions')
                _print_class_functions(record, sections, is_last_record)

    title = str(log.color('Unions', 36))
    log.log(f'    ├── {title}')

    if len(unions) == 0:
        log.log('    │   └── None')
    else:
        for i, union in enumerate(unions):
            is_last_union = i == len(unions) - 1
            if is_last_union:
                log.log(f'    │   └── {union.name}')
            else:
                log.log(f'    │   ├── {union.name}')

            sections = []
            if union.constructors:
                sections += ['constructors']
            if union.methods:
                sections += ['methods']
            if union.functions:
                sections += ['functions']

            if 'constructors' in sections:
                sections.remove('constructors')
                _print_class_constructors(union, sections, is_last_union)
            if 'methods' in sections:
                sections.remove('methods')
                _print_class_methods(union, sections, is_last_union)
            if 'functions' in sections:
                sections.remove('functions')
                _print_class_functions(union, sections, is_last_union)

    title = str(log.color('Functions', 36))
    log.log(f'    ├── {title}')

    if len(aliases) == 0:
        log.log('    │   └── None')
    else:
        for i, func in enumerate(functions):
            is_last_func = i == len(functions) - 1
            func_str = _print_function(func)
            if is_last_func:
                log.log(f'    │   ├── {func_str}')
            else:
                log.log(f'    │   └── {func_str}')

    title = str(log.color('Aliases', 36))
    log.log(f'    ├── {title}')

    if len(aliases) == 0:
        log.log('    │   └── None')
    else:
        for i in range(len(aliases)):
            alias = aliases[i]
            if i < len(aliases) - 1:
                log.log(f'    │   ├── {log.color(alias.name, 220)} → {alias.target.name} ({log.color(alias.target.ctype, 40)})')
            else:
                log.log(f'    │   └── {log.color(alias.name, 220)} → {alias.target.name} ({log.color(alias.target.ctype, 40)})')

    title = str(log.color('Constants', 36))
    log.log(f'    ├── {title}')

    if len(constants) == 0:
        log.log('    │   └── None')
    else:
        for i in range(len(constants)):
            const = constants[i]
            if i < len(constants) - 1:
                log.log(f'    │   ├── {log.color(const.name, 220)} = {const.value} ({log.color(const.target.ctype, 40)})')
            else:
                log.log(f'    │   └── {log.color(const.name, 220)} = {const.value} ({log.color(const.target.ctype, 40)})')

    title = str(log.color('Enumerations', 36))
    log.log(f'    ├── {title}')

    if len(enums) == 0:
        log.log('    │   └── None')
    else:
        for i, enum in enumerate(enums):
            is_last_enum = i == len(enums) - 1
            if is_last_enum:
                log.log(f'    │   └── {enum.name}')
            else:
                log.log(f'    │   ├── {enum.name}')

            sections = []
            if enum.members:
                sections += ['members']
            if enum.functions:
                sections += ['functions']

            if 'members' in sections:
                sections.remove('members')
                _print_enum_members(enum, sections, is_last_enum)
            if 'functions' in sections:
                sections.remove('functions')
                _print_enum_functions(enum, sections, is_last_enum)

    title = str(log.color('Error domains', 36))
    log.log(f'    └── {title}')

    if len(domains) == 0:
        log.log('        └── None')
    else:
        for i, domain in enumerate(domains):
            is_last_domain = i == len(domains) - 1
            if is_last_domain:
                log.log(f'        └── {domain.name} - domain: {domain.domain}')
            else:
                log.log(f'        ├── {domain.name} - domain: {domain.domain}')

            sections = []
            if domain.members:
                sections += ['members']
            if domain.functions:
                sections += ['functions']

            if 'members' in sections:
                sections.remove('members')
                _print_enum_members(domain, sections, is_last_domain, True)
            if 'functions' in sections:
                sections.remove('functions')
                _print_enum_functions(domain, sections, is_last_domain, True)


def run(options):
    paths = []
    paths.extend(options.include_paths)
    paths.extend(utils.default_search_paths())
    log.info(f"Search paths: {paths}")

    parser = gir.GirParser(search_paths=paths)
    parser.parse(options.infile)

    log.checkpoint()
    gen_tree(parser.get_repository())

    return 0
