# SPDX-FileCopyrightText: 2020 GNOME Foundation
# SPDX-License-Identifier: Apache-2.0 OR GPL-3.0-or-later

import argparse
import json
import os
import sys

from . import config, core, gir, log, porter, utils


HELP_MSG = "Generates the symbol indices for search"

MISSING_DESCRIPTION = "No description available."


def add_index_terms(index, terms, docid):
    for term in terms:
        docs = index.setdefault(term, [])
        if docid not in docs:
            docs.append(docid)


def _gen_aliases(config, stemmer, index, repository, symbols):
    index_symbols = index["symbols"]
    index_terms = index["terms"]

    for alias in symbols:
        if config.is_hidden(alias.name):
            log.debug(f"Skipping hidden type {alias.name}")
            continue
        idx = len(index_symbols)
        if alias.doc is not None:
            description = alias.doc.content
        else:
            description = MISSING_DESCRIPTION
        index_symbols.append({
            "type": "alias",
            "name": alias.name,
            "ctype": alias.base_ctype,
            "summary": utils.preprocess_docs(description, repository.namespace, summary=True, plain=True),
        })
        add_index_terms(index_terms, [alias.base_ctype.lower()], idx)
        add_index_terms(index_terms, utils.index_identifier(alias.name, stemmer), idx)
        add_index_terms(index_terms, utils.index_description(description, stemmer), idx)


def _gen_bitfields(config, stemmer, index, repository, symbols):
    index_symbols = index["symbols"]
    index_terms = index["terms"]

    for bitfield in symbols:
        if config.is_hidden(bitfield.name):
            log.debug(f"Skipping hidden type {bitfield.name}")
            continue
        idx = len(index_symbols)
        if bitfield.doc is not None:
            description = bitfield.doc.content
        else:
            description = MISSING_DESCRIPTION
        index_symbols.append({
            "type": "bitfield",
            "name": bitfield.name,
            "ctype": bitfield.base_ctype,
            "summary": utils.preprocess_docs(description, repository.namespace, summary=True, plain=True),
        })
        add_index_terms(index_terms, [bitfield.base_ctype.lower()], idx)
        add_index_terms(index_terms, utils.index_identifier(bitfield.name, stemmer), idx)
        add_index_terms(index_terms, utils.index_description(description, stemmer), idx)

        for member in bitfield.members:
            add_index_terms(index_terms, [member.name], idx)
            if member.doc is not None:
                add_index_terms(index_terms, utils.index_description(member.doc.content, stemmer), idx)

        for func in bitfield.functions:
            func_idx = len(index_symbols)
            if func.doc is not None:
                func_desc = func.doc.content
            else:
                func_desc = MISSING_DESCRIPTION
            index_symbols.append({
                "type": "type_func",
                "name": func.name,
                "type_name": bitfield.name,
                "ident": func.identifier,
                "summary": utils.preprocess_docs(func_desc, repository.namespace, summary=True, plain=True)
            })
            add_index_terms(index_terms, [func.identifier], func_idx)
            add_index_terms(index_terms, utils.index_symbol(func.name, stemmer), func_idx)
            add_index_terms(index_terms, utils.index_description(func_desc, stemmer), func_idx)


def _gen_callbacks(config, stemmer, index, repository, symbols):
    index_symbols = index["symbols"]
    index_terms = index["terms"]

    for callback in symbols:
        if config.is_hidden(callback.name):
            log.debug(f"Skipping hidden callback {callback.name}")
            continue
        idx = len(index_symbols)
        if callback.doc is not None:
            cb_desc = callback.doc.content
        else:
            cb_desc = MISSING_DESCRIPTION
        index_symbols.append({
            "type": "callback",
            "name": callback.name,
            "ctype": callback.base_ctype,
            "summary": utils.preprocess_docs(cb_desc, repository.namespace, summary=True, plain=True),
        })
        add_index_terms(index_terms, [callback.base_ctype.lower()], idx)
        add_index_terms(index_terms, utils.index_identifier(callback.name, stemmer), idx)
        add_index_terms(index_terms, utils.index_description(cb_desc, stemmer), idx)


def _gen_classes(config, stemmer, index, repository, symbols):
    namespace = repository.namespace

    index_symbols = index["symbols"]
    index_terms = index["terms"]

    for cls in symbols:
        if config.is_hidden(cls.name):
            log.debug(f"Skipping hidden type {cls.name}")
            continue
        idx = len(index_symbols)
        if cls.doc is not None:
            cls_desc = cls.doc.content
        else:
            cls_desc = MISSING_DESCRIPTION
        index_symbols.append({
            "type": "class",
            "name": cls.name,
            "ctype": cls.base_ctype,
            "summary": utils.preprocess_docs(cls_desc, repository.namespace, summary=True, plain=True),
        })
        add_index_terms(index_terms, [cls.base_ctype.lower()], idx)
        add_index_terms(index_terms, utils.index_identifier(cls.name, stemmer), idx)
        add_index_terms(index_terms, utils.index_description(cls_desc, stemmer), idx)

        for ctor in cls.constructors:
            ctor_idx = len(index_symbols)
            if ctor.doc is not None:
                ctor_desc = ctor.doc.content
            else:
                ctor_desc = MISSING_DESCRIPTION
            index_symbols.append({
                "type": "ctor",
                "name": ctor.name,
                "type_name": cls.name,
                "ident": ctor.identifier,
                "summary": utils.preprocess_docs(ctor_desc, repository.namespace, summary=True, plain=True),
            })
            add_index_terms(index_terms, [ctor.identifier], ctor_idx)
            add_index_terms(index_terms, utils.index_symbol(ctor.name, stemmer), ctor_idx)
            add_index_terms(index_terms, utils.index_description(ctor_desc, stemmer), ctor_idx)

        for method in cls.methods:
            method_idx = len(index_symbols)
            if method.doc is not None:
                method_desc = method.doc.content
            else:
                method_desc = MISSING_DESCRIPTION
            index_symbols.append({
                "type": "method",
                "name": method.name,
                "type_name": cls.name,
                "ident": method.identifier,
                "summary": utils.preprocess_docs(method_desc, repository.namespace, summary=True, plain=True),
            })
            add_index_terms(index_terms, [method.identifier], method_idx)
            add_index_terms(index_terms, utils.index_symbol(method.name, stemmer), method_idx)
            add_index_terms(index_terms, utils.index_description(method_desc, stemmer), method_idx)

        for func in cls.functions:
            func_idx = len(index_symbols)
            if func.doc is not None:
                func_desc = func.doc.content
            else:
                func_desc = MISSING_DESCRIPTION
            index_symbols.append({
                "type": "type_func",
                "name": func.name,
                "type_name": cls.name,
                "ident": func.identifier,
                "summary": utils.preprocess_docs(func_desc, repository.namespace, summary=True, plain=True),
            })
            add_index_terms(index_terms, [func.identifier], func_idx)
            add_index_terms(index_terms, utils.index_symbol(func.name, stemmer), func_idx)
            add_index_terms(index_terms, utils.index_description(func_desc, stemmer), func_idx)

        for prop_name, prop in cls.properties.items():
            if config.is_hidden(cls.name, 'property', prop_name):
                log.debug(f"Skipping hidden property {cls.name}.{prop_name}")
                continue
            prop_idx = len(index_symbols)
            if prop.doc is not None:
                prop_desc = prop.doc.content
            else:
                prop_desc = MISSING_DESCRIPTION
            index_symbols.append({
                "type": "property",
                "name": prop.name,
                "type_name": cls.name,
                "summary": utils.preprocess_docs(prop_desc, repository.namespace, summary=True, plain=True),
            })
            add_index_terms(index_terms, utils.index_symbol(prop.name, stemmer), prop_idx)
            add_index_terms(index_terms, utils.index_description(prop_desc, stemmer), prop_idx)

        for signal_name, signal in cls.signals.items():
            if config.is_hidden(cls.name, 'signal', signal_name):
                log.debug(f"Skipping hidden signal {cls.name}.{signal_name}")
                continue
            signal_idx = len(index_symbols)
            if signal.doc is not None:
                signal_desc = signal.doc.content
            else:
                signal_desc = MISSING_DESCRIPTION
            index_symbols.append({
                "type": "signal",
                "name": signal.name,
                "type_name": cls.name,
                "summary": utils.preprocess_docs(signal_desc, repository.namespace, summary=True, plain=True),
            })
            add_index_terms(index_terms, utils.index_symbol(signal.name, stemmer), signal_idx)
            add_index_terms(index_terms, utils.index_description(signal_desc, stemmer), signal_idx)

        for vfunc in cls.virtual_methods:
            vfunc_idx = len(index_symbols)
            if vfunc.doc is not None:
                vfunc_desc = vfunc.doc.content
            else:
                vfunc_desc = MISSING_DESCRIPTION
            index_symbols.append({
                "type": "vfunc",
                "name": vfunc.name,
                "type_name": cls.name,
                "summary": utils.preprocess_docs(vfunc_desc, repository.namespace, summary=True, plain=True),
            })
            add_index_terms(index_terms, utils.index_symbol(vfunc.name, stemmer), vfunc_idx)
            add_index_terms(index_terms, utils.index_description(vfunc_desc, stemmer), vfunc_idx)

        if cls.type_struct is not None:
            cls_struct = namespace.find_record(cls.type_struct)
            for cls_method in cls_struct.methods:
                cls_method_idx = len(index_symbols)
                if cls_method.doc is not None:
                    cls_method_desc = cls_method.doc.content
                else:
                    cls_method_desc = MISSING_DESCRIPTION
                index_symbols.append({
                    "type": "class_method",
                    "name": cls_method.name,
                    "type_name": cls_struct.name,
                    "struct_for": cls_struct.struct_for,
                    "ident": cls_method.identifier,
                    "summary": utils.preprocess_docs(cls_method_desc, repository.namespace, summary=True, plain=True),
                })
                add_index_terms(index_terms, [cls_method.identifier], cls_method_idx)
                add_index_terms(index_terms, utils.index_symbol(cls_method.name, stemmer), cls_method_idx)
                add_index_terms(index_terms, utils.index_description(cls_method_desc, stemmer), cls_method_idx)


def _gen_constants(config, stemmer, index, repository, symbols):
    index_symbols = index["symbols"]
    index_terms = index["terms"]

    for const in symbols:
        if config.is_hidden(const.name):
            log.debug(f"Skipping hidden const {const.name}")
            continue
        idx = len(index_symbols)
        if const.doc is not None:
            const_desc = const.doc.content
        else:
            const_desc = MISSING_DESCRIPTION
        index_symbols.append({
            "type": "constant",
            "name": const.name,
            "ident": const.ctype,
            "summary": utils.preprocess_docs(const_desc, repository.namespace, summary=True, plain=True),
        })
        add_index_terms(index_terms, [const.ctype.lower()], idx)
        add_index_terms(index_terms, utils.index_symbol(const.name, stemmer), idx)
        add_index_terms(index_terms, utils.index_description(const_desc, stemmer), idx)


def _gen_domains(config, stemmer, index, repository, symbols):
    index_symbols = index["symbols"]
    index_terms = index["terms"]

    for domain in symbols:
        if config.is_hidden(domain.name):
            log.debug(f"Skipping hidden type {domain.name}")
            continue
        idx = len(index_symbols)
        if domain.doc is not None:
            domain_desc = domain.doc.content
        else:
            domain_desc = MISSING_DESCRIPTION
        index_symbols.append({
            "type": "domain",
            "name": domain.name,
            "ctype": domain.base_ctype,
            "summary": utils.preprocess_docs(domain_desc, repository.namespace, summary=True, plain=True),
        })
        add_index_terms(index_terms, [domain.base_ctype.lower()], idx)
        add_index_terms(index_terms, utils.index_identifier(domain.name, stemmer), idx)
        add_index_terms(index_terms, utils.index_description(domain_desc, stemmer), idx)

        for member in domain.members:
            add_index_terms(index_terms, [member.name], idx)
            if member.doc is not None:
                add_index_terms(index_terms, utils.index_description(member.doc.content, stemmer), idx)

        for func in domain.functions:
            func_idx = len(index_symbols)
            if func.doc is not None:
                func_desc = func.doc.content
            else:
                func_desc = MISSING_DESCRIPTION
            index_symbols.append({
                "type": "type_func",
                "name": func.name,
                "type_name": domain.name,
                "ident": func.identifier,
                "summary": utils.preprocess_docs(func_desc, repository.namespace, summary=True, plain=True),
            })
            add_index_terms(index_terms, [func.identifier], func_idx)
            add_index_terms(index_terms, utils.index_symbol(func.name, stemmer), func_idx)
            add_index_terms(index_terms, utils.index_description(func_desc, stemmer), func_idx)


def _gen_enums(config, stemmer, index, repository, symbols):
    index_symbols = index["symbols"]
    index_terms = index["terms"]

    for enum in symbols:
        if config.is_hidden(enum.name):
            log.debug(f"Skipping hidden type {enum.name}")
            continue
        idx = len(index_symbols)
        if enum.doc is not None:
            enum_desc = enum.doc.content
        else:
            enum_desc = MISSING_DESCRIPTION
        index_symbols.append({
            "type": "enum",
            "name": enum.name,
            "ctype": enum.base_ctype,
            "summary": utils.preprocess_docs(enum_desc, repository.namespace, summary=True, plain=True),
        })
        add_index_terms(index_terms, [enum.base_ctype.lower()], idx)
        add_index_terms(index_terms, utils.index_identifier(enum.name, stemmer), idx)
        add_index_terms(index_terms, utils.index_description(enum_desc, stemmer), idx)

        for member in enum.members:
            add_index_terms(index_terms, [member.name], idx)
            if member.doc is not None:
                add_index_terms(index_terms, utils.index_description(member.doc.content, stemmer), idx)

        for func in enum.functions:
            func_idx = len(index_symbols)
            if func.doc is not None:
                func_desc = func.doc.content
            else:
                func_desc = MISSING_DESCRIPTION
            index_symbols.append({
                "type": "type_func",
                "name": func.name,
                "type_name": enum.name,
                "ident": func.identifier,
                "summary": utils.preprocess_docs(func_desc, repository.namespace, summary=True, plain=True),
            })
            add_index_terms(index_terms, [func.identifier], func_idx)
            add_index_terms(index_terms, utils.index_symbol(func.name, stemmer), func_idx)
            add_index_terms(index_terms, utils.index_description(func_desc, stemmer), func_idx)


def _gen_functions(config, stemmer, index, repository, symbols):
    index_symbols = index["symbols"]
    index_terms = index["terms"]

    for func in symbols:
        if config.is_hidden(func.name):
            log.debug(f"Skipping hidden function {func.name}")
            continue
        idx = len(index_symbols)
        if func.doc is not None:
            func_desc = func.doc.content
        else:
            func_desc = MISSING_DESCRIPTION
        index_symbols.append({
            "type": "function",
            "name": func.name,
            "ident": func.identifier,
            "summary": utils.preprocess_docs(func_desc, repository.namespace, summary=True, plain=True),
        })
        add_index_terms(index_terms, [func.identifier], idx)
        add_index_terms(index_terms, utils.index_symbol(func.name, stemmer), idx)
        add_index_terms(index_terms, utils.index_description(func_desc, stemmer), idx)


def _gen_function_macros(config, stemmer, index, repository, symbols):
    index_symbols = index["symbols"]
    index_terms = index["terms"]

    for func in symbols:
        if config.is_hidden(func.name):
            log.debug(f"Skipping hidden macro {func.name}")
            continue
        idx = len(index_symbols)
        if func.doc is not None:
            func_desc = func.doc.content
        else:
            func_desc = MISSING_DESCRIPTION
        index_symbols.append({
            "type": "function_macro",
            "name": func.name,
            "ident": func.identifier,
            "summary": utils.preprocess_docs(func_desc, repository.namespace, summary=True, plain=True),
        })
        add_index_terms(index_terms, [func.identifier], idx)
        add_index_terms(index_terms, utils.index_symbol(func.name, stemmer), idx)
        add_index_terms(index_terms, utils.index_description(func_desc, stemmer), idx)


def _gen_interfaces(config, stemmer, index, repository, symbols):
    index_symbols = index["symbols"]
    index_terms = index["terms"]

    for iface in symbols:
        if config.is_hidden(iface.name):
            log.debug(f"Skipping hidden type {iface.name}")
            continue
        idx = len(index_symbols)
        if iface.doc is not None:
            iface_desc = iface.doc.content
        else:
            iface_desc = MISSING_DESCRIPTION
        index_symbols.append({
            "type": "interface",
            "name": iface.name,
            "ctype": iface.base_ctype,
            "summary": utils.preprocess_docs(iface_desc, repository.namespace, summary=True, plain=True),
        })
        add_index_terms(index_terms, [iface.base_ctype.lower()], idx)
        add_index_terms(index_terms, utils.index_identifier(iface.name, stemmer), idx)
        add_index_terms(index_terms, utils.index_description(iface_desc, stemmer), idx)

        for method in iface.methods:
            method_idx = len(index_symbols)
            if method.doc is not None:
                method_desc = method.doc.content
            else:
                method_desc = MISSING_DESCRIPTION
            index_symbols.append({
                "type": "method",
                "name": method.name,
                "type_name": iface.name,
                "ident": method.identifier,
                "summary": utils.preprocess_docs(method_desc, repository.namespace, summary=True, plain=True),
            })
            add_index_terms(index_terms, [method.identifier], method_idx)
            add_index_terms(index_terms, utils.index_symbol(method.name, stemmer), method_idx)
            add_index_terms(index_terms, utils.index_description(method_desc, stemmer), method_idx)

        for func in iface.functions:
            func_idx = len(index_symbols)
            if func.doc is not None:
                func_desc = func.doc.content
            else:
                func_desc = MISSING_DESCRIPTION
            index_symbols.append({
                "type": "type_func",
                "name": func.name,
                "type_name": iface.name,
                "ident": func.identifier,
                "summary": utils.preprocess_docs(func_desc, repository.namespace, summary=True, plain=True),
            })
            add_index_terms(index_terms, [func.identifier], func_idx)
            add_index_terms(index_terms, utils.index_symbol(func.name, stemmer), func_idx)
            add_index_terms(index_terms, utils.index_description(func_desc, stemmer), func_idx)

        for prop_name, prop in iface.properties.items():
            if config.is_hidden(iface.name, 'property', prop_name):
                log.debug(f"Skipping hidden property {iface.name}.{prop_name}")
                continue
            prop_idx = len(index_symbols)
            if prop.doc is not None:
                prop_desc = prop.doc.content
            else:
                prop_desc = MISSING_DESCRIPTION
            index_symbols.append({
                "type": "property",
                "name": prop.name,
                "type_name": iface.name,
                "summary": utils.preprocess_docs(prop_desc, repository.namespace, summary=True, plain=True),
            })
            add_index_terms(index_terms, utils.index_symbol(prop.name, stemmer), prop_idx)
            add_index_terms(index_terms, utils.index_description(prop_desc, stemmer), prop_idx)

        for signal_name, signal in iface.signals.items():
            if config.is_hidden(iface.name, 'signal', signal_name):
                log.debug(f"Skipping hidden signal {iface.name}.{signal_name}")
                continue
            signal_idx = len(index_symbols)
            if signal.doc is not None:
                signal_desc = signal.doc.content
            else:
                signal_desc = MISSING_DESCRIPTION
            index_symbols.append({
                "type": "signal",
                "name": signal.name,
                "type_name": iface.name,
                "summary": utils.preprocess_docs(signal_desc, repository.namespace, summary=True, plain=True),
            })
            add_index_terms(index_terms, utils.index_symbol(signal.name, stemmer), signal_idx)
            add_index_terms(index_terms, utils.index_description(signal_desc, stemmer), signal_idx)

        for vfunc in iface.virtual_methods:
            vfunc_idx = len(index_symbols)
            if vfunc.doc is not None:
                vfunc_desc = vfunc.doc.content
            else:
                vfunc_desc = MISSING_DESCRIPTION
            index_symbols.append({
                "type": "vfunc",
                "name": vfunc.name,
                "type_name": iface.name,
                "summary": utils.preprocess_docs(vfunc_desc, repository.namespace, summary=True, plain=True),
            })
            add_index_terms(index_terms, utils.index_symbol(vfunc.name, stemmer), vfunc_idx)
            add_index_terms(index_terms, utils.index_description(vfunc_desc, stemmer), vfunc_idx)


def _gen_records(config, stemmer, index, repository, symbols):
    index_symbols = index["symbols"]
    index_terms = index["terms"]

    for record in symbols:
        if config.is_hidden(record.name):
            log.debug(f"Skipping hidden type {record.name}")
            continue
        idx = len(index_symbols)
        if record.doc is not None:
            desc = record.doc.content
        else:
            desc = MISSING_DESCRIPTION
        index_symbols.append({
            "type": "record",
            "name": record.name,
            "ctype": record.base_ctype,
            "summary": utils.preprocess_docs(desc, repository.namespace, summary=True, plain=True),
        })
        add_index_terms(index_terms, [record.base_ctype.lower()], idx)
        add_index_terms(index_terms, utils.index_identifier(record.name, stemmer), idx)
        add_index_terms(index_terms, utils.index_description(desc, stemmer), idx)

        for ctor in record.constructors:
            ctor_idx = len(index_symbols)
            if ctor.doc is not None:
                ctor_desc = ctor.doc.content
            else:
                ctor_desc = MISSING_DESCRIPTION
            index_symbols.append({
                "type": "ctor",
                "name": ctor.name,
                "type_name": record.name,
                "ident": ctor.identifier,
                "summary": utils.preprocess_docs(ctor_desc, repository.namespace, summary=True, plain=True),
            })
            add_index_terms(index_terms, [ctor.identifier], ctor_idx)
            add_index_terms(index_terms, utils.index_symbol(ctor.name, stemmer), ctor_idx)
            add_index_terms(index_terms, utils.index_description(ctor_desc, stemmer), ctor_idx)

        for method in record.methods:
            method_idx = len(index_symbols)
            if method.doc is not None:
                method_desc = method.doc.content
            else:
                method_desc = MISSING_DESCRIPTION
            index_symbols.append({
                "type": "method",
                "name": method.name,
                "type_name": record.name,
                "ident": method.identifier,
                "summary": utils.preprocess_docs(method_desc, repository.namespace, summary=True, plain=True),
            })
            add_index_terms(index_terms, [method.identifier], method_idx)
            add_index_terms(index_terms, utils.index_symbol(method.name, stemmer), method_idx)
            add_index_terms(index_terms, utils.index_description(method_desc, stemmer), method_idx)

        for func in record.functions:
            func_idx = len(index_symbols)
            if func.doc is not None:
                func_desc = func.doc.content
            else:
                func_desc = MISSING_DESCRIPTION
            index_symbols.append({
                "type": "type_func",
                "name": func.name,
                "type_name": record.name,
                "ident": func.identifier,
                "summary": utils.preprocess_docs(func_desc, repository.namespace, summary=True, plain=True),
            })
            add_index_terms(index_terms, [func.identifier], func_idx)
            add_index_terms(index_terms, utils.index_symbol(func.name, stemmer), func_idx)
            add_index_terms(index_terms, utils.index_description(func_desc, stemmer), func_idx)


def _gen_unions(config, stemmer, index, repository, symbols):
    index_symbols = index["symbols"]
    index_terms = index["terms"]

    for union in symbols:
        if config.is_hidden(union.name):
            log.debug(f"Skipping hidden type {union.name}")
            continue
        idx = len(index_symbols)
        if union.doc is not None:
            desc = union.doc.content
        else:
            desc = MISSING_DESCRIPTION
        index_symbols.append({
            "type": "union",
            "name": union.name,
            "ctype": union.base_ctype,
            "summary": utils.preprocess_docs(desc, repository.namespace, summary=True, plain=True),
        })
        add_index_terms(index_terms, [union.base_ctype.lower()], idx)
        add_index_terms(index_terms, utils.index_identifier(union.name, stemmer), idx)
        add_index_terms(index_terms, utils.index_description(desc, stemmer), idx)

        for ctor in union.constructors:
            ctor_idx = len(index_symbols)
            if ctor.doc is not None:
                ctor_desc = ctor.doc.content
            else:
                ctor_desc = MISSING_DESCRIPTION
            index_symbols.append({
                "type": "ctor",
                "name": ctor.name,
                "type_name": union.name,
                "ident": ctor.identifier,
                "summary": utils.preprocess_docs(ctor_desc, repository.namespace, summary=True, plain=True),
            })
            add_index_terms(index_terms, [ctor.identifier], ctor_idx)
            add_index_terms(index_terms, utils.index_symbol(ctor.name, stemmer), ctor_idx)
            add_index_terms(index_terms, utils.index_description(ctor_desc, stemmer), ctor_idx)

        for method in union.methods:
            method_idx = len(index_symbols)
            if method.doc is not None:
                method_desc = method.doc.content
            else:
                method_desc = MISSING_DESCRIPTION
            index_symbols.append({
                "type": "method",
                "name": method.name,
                "type_name": union.name,
                "ident": method.identifier,
                "summary": utils.preprocess_docs(method_desc, repository.namespace, summary=True, plain=True),
            })
            add_index_terms(index_terms, [method.identifier], method_idx)
            add_index_terms(index_terms, utils.index_symbol(method.name, stemmer), method_idx)
            add_index_terms(index_terms, utils.index_description(method_desc, stemmer), method_idx)

        for func in union.functions:
            func_idx = len(index_symbols)
            if func.doc is not None:
                func_desc = func.doc.content
            else:
                func_desc = MISSING_DESCRIPTION
            index_symbols.append({
                "type": "type_func",
                "name": func.name,
                "type_name": union.name,
                "ident": func.identifier,
                "summary": utils.preprocess_docs(func_desc, repository.namespace, summary=True, plain=True),
            })
            add_index_terms(index_terms, [func.identifier], func_idx)
            add_index_terms(index_terms, utils.index_symbol(func.name, stemmer), func_idx)
            add_index_terms(index_terms, utils.index_description(func_desc, stemmer), func_idx)


def _gen_content_files(config, stemmer, index, repository, content_dirs):
    index_symbols = index["symbols"]
    index_terms = index["terms"]

    for file_name in config.content_files:
        src_file = utils.find_extra_content_file(content_dirs, file_name)

        src_data = ""
        with open(src_file, encoding='utf-8') as infile:
            source = []
            header = True
            title = None
            for line in infile:
                if header:
                    if line.startswith("Title: "):
                        title = line.replace("Title: ", "").strip()
                    if line == "\n":
                        header = False

                if not header:
                    source.append(line)
            src_data = "".join(source)

        if title is None:
            title = f"Untitled document '{file_name}'"

        index_symbols.append({
            "type": "content",
            "name": title,
            "href": file_name.replace(".md", ".html"),
            "summary": utils.preprocess_docs(src_data, repository.namespace, summary=True, plain=True),
        })

        content_idx = len(index_symbols)
        add_index_terms(index_terms, utils.index_description(src_data, stemmer), content_idx)


def gen_indices(config, repository, content_dirs, output_dir):
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
        "aliases": _gen_aliases,
        "bitfields": _gen_bitfields,
        "callbacks": _gen_callbacks,
        "classes": _gen_classes,
        "constants": _gen_constants,
        "domains": _gen_domains,
        "enums": _gen_enums,
        "functions": _gen_functions,
        "function_macros": _gen_function_macros,
        "interfaces": _gen_interfaces,
        "structs": _gen_records,
        "unions": _gen_unions,
    }

    index = {
        "meta": {
            "ns": namespace.name,
            "version": namespace.version,
            "generator": "gi-docgen",
            "generator-version": core.version,
        },
        "symbols": [],
        "terms": {},
    }

    stemmer = porter.PorterStemmer()

    # Each section is isolated, so we run it into a thread pool
    for section in all_indices:
        generator = all_indices.get(section, None)
        if generator is None:
            log.error(f"No generator for section {section}")
            continue

        s = symbols.get(section, None)
        if s is None:
            log.debug(f"No symbols for section {section}")
            continue

        log.debug(f"Generating symbols for section {section}")
        generator(config, stemmer, index, repository, s)

    _gen_content_files(config, stemmer, index, repository, content_dirs)

    # Ensure iteration order is reproducible by sorting symbols by type/name,
    # and terms by key. This has no overhead since values are not copied.
    index["symbols"].sort(key=lambda s: (s["type"], s["name"]))
    index["terms"] = dict(sorted(index["terms"].items()))

    data = json.dumps(index, separators=(',', ':'))
    index_file = os.path.join(output_dir, "index.json")
    log.info(f"Creating index file for {namespace.name}-{namespace.version}: {index_file}")
    with open(index_file, "w") as out:
        out.write(data)


def add_args(parser):
    parser.add_argument("--add-include-path", action="append", dest="include_paths", default=[],
                        help="include paths for other GIR files")
    parser.add_argument("-C", "--config", metavar="FILE", help="the configuration file")
    parser.add_argument("--content-dir", action="append", dest="content_dirs", default=[],
                        help="the base directories with the extra content")
    parser.add_argument("--dry-run", action="store_true", help="parses the GIR file without generating files")
    parser.add_argument("--output-dir", default=None, help="the output directory for the index files")
    parser.add_argument("infile", metavar="GIRFILE", type=argparse.FileType('r', encoding='UTF-8'),
                        default=sys.stdin, help="the GIR file to parse")


def run(options):
    log.info(f"Loading config file: {options.config}")

    conf = config.GIDocConfig(options.config)

    output_dir = options.output_dir or os.getcwd()
    log.info(f"Output directory: {output_dir}")

    content_dirs = options.content_dirs
    if content_dirs == []:
        content_dirs = [os.getcwd()]

    paths = []
    paths.extend(options.include_paths)
    paths.extend(utils.default_search_paths())
    log.debug(f"Search paths: {paths}")

    log.info("Parsing GIR file")
    parser = gir.GirParser(search_paths=paths)
    parser.parse(options.infile)

    if not options.dry_run:
        log.checkpoint()
        gen_indices(conf, parser.get_repository(), content_dirs, output_dir)

    return 0
