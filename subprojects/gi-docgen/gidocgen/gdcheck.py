# SPDX-FileCopyrightText: 2021 GNOME Foundation
# SPDX-License-Identifier: Apache-2.0 OR GPL-3.0-or-later

import argparse
import sys

from . import config, gir, log, utils


HELP_MSG = "Checks introspection data for valid documentation"


def _check_doc_element(path, symbol, results):
    name = '.'.join(path + [symbol.name])

    if symbol.source_position is not None:
        filename = symbol.source_position[0]
        line = symbol.source_position[1]
    else:
        filename = "<unknown>"
        line = 0

    if symbol.doc is None:
        results.append(f"Symbol '{name}' at {filename}:{line} is not documented")


def _check_arg_docs(path, arguments, results):
    symbol = '.'.join(path)
    for arg in arguments:
        if arg.doc is None:
            results.append(f"Parameter '{arg.name}' of symbol '{symbol}' is not documented")


def _check_retval_docs(path, retval, results):
    if retval is None:
        return

    if isinstance(retval.target, gir.VoidType):
        return

    symbol = '.'.join(path)
    if retval.doc is None:
        results.append(f"Return value for symbol '{symbol}' is not documented")


def _check_aliases(config, repository, symbols, results):
    for alias in symbols:
        if config.is_skipped(alias.name):
            log.debug(f"Skipping hidden alias {alias.name}")
            continue
        _check_doc_element([repository.namespace.name], alias, results)


def _check_bitfields(config, repository, symbols, results):
    for bitfield in symbols:
        if config.is_skipped(bitfield.name):
            log.debug(f"Skipping hidden bitfield {bitfield.name}")
            continue

        _check_doc_element([repository.namespace.name], bitfield, results)

        for member in bitfield.members:
            _check_doc_element([repository.namespace.name, bitfield.name], member, results)

        for func in bitfield.functions:
            if config.is_skipped(bitfield.name, 'function', func.name):
                continue
            _check_doc_element([repository.namespace.name, bitfield.name], func, results)
            _check_arg_docs([repository.namespace.name, bitfield.name, func.name], func.parameters, results)
            _check_retval_docs([repository.namespace.name, bitfield.name, func.name], func.return_value, results)


def _check_callbacks(config, repository, symbols, results):
    for cb in symbols:
        if config.is_skipped(cb.name):
            log.debug(f"Skipping hidden callback {cb.name}")
            continue

        _check_doc_element([repository.namespace.name], cb, results)
        _check_arg_docs([repository.namespace.name, cb.name], cb.parameters, results)
        _check_retval_docs([repository.namespace.name, cb.name], cb.return_value, results)


def _check_classes(config, repository, symbols, results):
    for cls in symbols:
        if config.is_skipped(cls.name):
            log.debug(f"Skipping hidden class {cls.name}")
            continue

        _check_doc_element([repository.namespace.name], cls, results)

        for ctor in cls.constructors:
            if config.is_skipped(cls.name, 'constructor', ctor.name):
                continue
            _check_doc_element([repository.namespace.name, cls.name], ctor, results)
            _check_arg_docs([repository.namespace.name, cls.name, ctor.name], ctor.parameters, results)
            _check_retval_docs([repository.namespace.name, cls.name, ctor.name], ctor.return_value, results)

        for method in cls.methods:
            if config.is_skipped(cls.name, 'method', method.name):
                continue
            _check_doc_element([repository.namespace.name, cls.name], method, results)
            _check_arg_docs([repository.namespace.name, cls.name, method.name], method.parameters, results)
            _check_retval_docs([repository.namespace.name, cls.name, method.name], method.return_value, results)

        for func in cls.functions:
            if config.is_skipped(cls.name, 'function', func.name):
                continue
            _check_doc_element([repository.namespace.name, cls.name], func, results)
            _check_arg_docs([repository.namespace.name, cls.name, func.name], func.parameters, results)
            _check_retval_docs([repository.namespace.name, cls.name, func.name], func.return_value, results)

        for prop in cls.properties.values():
            if config.is_skipped(cls.name, 'property', prop.name):
                continue
            _check_doc_element([repository.namespace.name, cls.name], prop, results)

        for signal in cls.signals.values():
            if config.is_skipped(cls.name, 'signal', signal.name):
                continue
            _check_doc_element([repository.namespace.name, cls.name], signal, results)
            _check_arg_docs([repository.namespace.name, cls.name, signal.name], signal.parameters, results)
            _check_retval_docs([repository.namespace.name, cls.name, signal.name], signal.return_value, results)


def _check_constants(config, repository, symbols, results):
    for constant in symbols:
        if config.is_skipped(constant.name):
            log.debug(f"Skipping hidden constant {constant.name}")
            continue

        _check_doc_element([repository.namespace.name], constant, results)


def _check_domains(config, repository, symbols, results):
    for domain in symbols:
        if config.is_skipped(domain.name):
            log.debug(f"Skipping hidden error domain {domain.name}")
            continue

        _check_doc_element([repository.namespace.name], domain, results)

        for member in domain.members:
            _check_doc_element([repository.namespace.name, domain.name], member, results)

        for func in domain.functions:
            if config.is_skipped(domain.name, 'function', func.name):
                continue
            _check_doc_element([repository.namespace.name, domain.name], func, results)
            _check_arg_docs([repository.namespace.name, domain.name, func.name], func.parameters, results)
            _check_retval_docs([repository.namespace.name, domain.name, func.name], func.return_value, results)


def _check_enums(config, repository, symbols, results):
    for enum in symbols:
        if config.is_skipped(enum.name):
            log.debug(f"Skipping hidden enumeration {enum.name}")
            continue

        _check_doc_element([repository.namespace.name], enum, results)

        for member in enum.members:
            _check_doc_element([repository.namespace.name, enum.name], member, results)

        for func in enum.functions:
            if config.is_skipped(enum.name, 'function', func.name):
                continue
            _check_doc_element([repository.namespace.name, enum.name], func, results)
            _check_arg_docs([repository.namespace.name, enum.name, func.name], func.parameters, results)
            _check_retval_docs([repository.namespace.name, enum.name, func.name], func.return_value, results)


def _check_functions(config, repository, symbols, results):
    for func in symbols:
        if config.is_skipped(func.name):
            log.debug(f"Skipping hidden function {func.name}")
            continue

        _check_doc_element([repository.namespace.name], func, results)
        _check_arg_docs([repository.namespace.name, func.name], func.parameters, results)
        _check_retval_docs([repository.namespace.name, func.name], func.return_value, results)


def _check_function_macros(config, repository, symbols, results):
    for func in symbols:
        if config.is_skipped(func.name):
            log.debug(f"Skipping hidden function macro {func.name}")
            continue

        _check_doc_element([repository.namespace.name], func, results)
        _check_arg_docs([repository.namespace.name, func.name], func.parameters, results)
        _check_retval_docs([repository.namespace.name, func.name], func.return_value, results)


def _check_interfaces(config, repository, symbols, results):
    for iface in symbols:
        if config.is_skipped(iface.name):
            log.debug(f"Skipping hidden interface {iface.name}")
            continue

        _check_doc_element([repository.namespace.name], iface, results)

        for method in iface.methods:
            if config.is_skipped(iface.name, 'method', method.name):
                continue
            _check_doc_element([repository.namespace.name, iface.name], method, results)
            _check_arg_docs([repository.namespace.name, iface.name, method.name], method.parameters, results)
            _check_retval_docs([repository.namespace.name, iface.name, method.name], method.return_value, results)

        for func in iface.functions:
            if config.is_skipped(iface.name, 'function', func.name):
                continue
            _check_doc_element([repository.namespace.name, iface.name], func, results)
            _check_arg_docs([repository.namespace.name, iface.name, func.name], func.parameters, results)
            _check_retval_docs([repository.namespace.name, iface.name, func.name], func.return_value, results)

        for prop in iface.properties.values():
            if config.is_skipped(iface.name, 'property', prop.name):
                continue
            _check_doc_element([repository.namespace.name, iface.name], prop, results)

        for signal in iface.signals.values():
            if config.is_skipped(iface.name, 'signal', signal.name):
                continue
            _check_doc_element([repository.namespace.name, iface.name], signal, results)
            _check_arg_docs([repository.namespace.name, iface.name, signal.name], signal.parameters, results)
            _check_retval_docs([repository.namespace.name, iface.name, signal.name], signal.return_value, results)


def _check_records(config, repository, symbols, results):
    for struct in symbols:
        if config.is_skipped(struct.name):
            log.debug(f"Skipping hidden record {struct.name}")
            continue

        _check_doc_element([repository.namespace.name], struct, results)

        for ctor in struct.constructors:
            if config.is_skipped(struct.name, 'constructor', ctor.name):
                continue
            _check_doc_element([repository.namespace.name, struct.name], ctor, results)
            _check_arg_docs([repository.namespace.name, struct.name, ctor.name], ctor.parameters, results)
            _check_retval_docs([repository.namespace.name, struct.name, ctor.name], ctor.return_value, results)

        for method in struct.methods:
            if config.is_skipped(struct.name, 'method', method.name):
                continue
            _check_doc_element([repository.namespace.name, struct.name], method, results)
            _check_arg_docs([repository.namespace.name, struct.name, method.name], method.parameters, results)
            _check_retval_docs([repository.namespace.name, struct.name, method.name], method.return_value, results)

        for func in struct.functions:
            if config.is_skipped(struct.name, 'function', func.name):
                continue
            _check_doc_element([repository.namespace.name, struct.name], func, results)
            _check_arg_docs([repository.namespace.name, struct.name, func.name], func.parameters, results)
            _check_retval_docs([repository.namespace.name, struct.name, func.name], func.return_value, results)


def _check_unions(config, repository, symbols, results):
    for union in symbols:
        if config.is_skipped(union.name):
            log.debug(f"Skipping hidden union {union.name}")
            continue

        _check_doc_element([repository.namespace.name], union, results)

        for ctor in union.constructors:
            if config.is_skipped(union.name, 'constructor', ctor.name):
                continue
            _check_doc_element([repository.namespace.name, union.name], ctor, results)
            _check_arg_docs([repository.namespace.name, union.name, ctor.name], ctor.parameters, results)
            _check_retval_docs([repository.namespace.name, union.name, ctor.name], ctor.return_value, results)

        for method in union.methods:
            if config.is_skipped(union.name, 'method', method.name):
                continue
            _check_doc_element([repository.namespace.name, union.name], method, results)
            _check_arg_docs([repository.namespace.name, union.name, method.name], method.parameters, results)
            _check_retval_docs([repository.namespace.name, union.name, method.name], method.return_value, results)

        for func in union.functions:
            if config.is_skipped(union.name, 'function', func.name):
                continue
            _check_doc_element([repository.namespace.name, union.name], func, results)
            _check_arg_docs([repository.namespace.name, union.name, func.name], func.parameters, results)
            _check_retval_docs([repository.namespace.name, union.name, func.name], func.return_value, results)


def check(repository, config):
    namespace = repository.namespace

    symbols = {
        "aliases": sorted(namespace.get_aliases(), key=lambda alias: alias.name.lower()),
        "bitfields": sorted(namespace.get_bitfields(), key=lambda bitfield: bitfield.name.lower()),
        "callbacks": sorted(namespace.get_callbacks(), key=lambda callback: callback.name.lower()),
        "classes": sorted(namespace.get_classes(), key=lambda cls: cls.name.lower()),
        "constants": sorted(namespace.get_constants(), key=lambda const: const.name.lower()),
        "domains": sorted(namespace.get_error_domains(), key=lambda domain: domain.name.lower()),
        "enums": sorted(namespace.get_enumerations(), key=lambda enum: enum.name.lower()),
        "functions": sorted(namespace.get_functions(), key=lambda func: func.name.lower()),
        "function_macros": sorted(namespace.get_effective_function_macros(), key=lambda func: func.name.lower()),
        "interfaces": sorted(namespace.get_interfaces(), key=lambda interface: interface.name.lower()),
        "structs": sorted(namespace.get_effective_records(), key=lambda record: record.name.lower()),
        "unions": sorted(namespace.get_unions(), key=lambda union: union.name.lower()),
    }

    all_indices = {
        "aliases": _check_aliases,
        "bitfields": _check_bitfields,
        "callbacks": _check_callbacks,
        "classes": _check_classes,
        "constants": _check_constants,
        "domains": _check_domains,
        "enums": _check_enums,
        "functions": _check_functions,
        "function_macros": _check_function_macros,
        "interfaces": _check_interfaces,
        "structs": _check_records,
        "unions": _check_unions,
    }

    results = []

    # Each section is isolated, so we run it into a thread pool
    for section in all_indices:
        checker = all_indices.get(section, None)
        if checker is None:
            log.error(f"No checker for section {section}")
            continue

        s = symbols.get(section, None)
        if s is None:
            log.debug(f"No symbols for section {section}")
            continue

        log.debug(f"Checking symbols for section {section}")
        checker(config, repository, s, results)

    for res in results:
        log.warning(res)

    if len(results) == 0:
        return 0
    else:
        return 1


def add_args(parser):
    parser.add_argument("-C", "--config", metavar="FILE", help="the configuration file")
    parser.add_argument("--add-include-path", action="append", dest="include_paths", default=[],
                        help="include paths for other GIR files")
    parser.add_argument("infile", metavar="GIRFILE", type=argparse.FileType('r', encoding='UTF-8'),
                        default=sys.stdin, help="the GIR file to parse")


def run(options):
    log.info(f"Loading config file: {options.config}")

    conf = config.GIDocConfig(options.config)

    paths = []
    paths.extend(options.include_paths)
    paths.extend(utils.default_search_paths())
    log.info(f"Search paths: {paths}")

    parser = gir.GirParser(search_paths=paths)
    parser.parse(options.infile)

    log.checkpoint()
    return check(parser.get_repository(), conf)
