# SPDX-FileCopyrightText: 2021 GNOME Foundation
# SPDX-License-Identifier: Apache-2.0 OR GPL-3.0-or-later

import argparse
import json
import os
import sys

from . import gir, log, utils


HELP_MSG = "Search terms in the symbol indices"


def _gen_alias_result(symbol, namespace):
    alias = namespace.find_alias(symbol["name"])
    if alias.doc is not None:
        summary = utils.preprocess_docs(alias.doc.content, namespace, summary=True, plain=True)
    else:
        summary = "Missing documentation"

    return {
        "type": "alias",
        "name": alias.name,
        "ctype": alias.base_ctype,
        "summary": summary,
        "link": f"alias.{alias.name}.html",
    }


def _gen_bitfield_result(symbol, namespace):
    enum = namespace.find_bitfield(symbol["name"])
    if enum.doc is not None:
        summary = utils.preprocess_docs(enum.doc.content, namespace, summary=True, plain=True)
    else:
        summary = "Missing documentation"

    return {
        "type": "flags",
        "name": enum.name,
        "ctype": enum.base_ctype,
        "summary": summary.split("\n"),
        "link": f"flags.{enum.name}.html",
    }


def _gen_callback_result(symbol, namespace):
    pass


def _gen_class_result(symbol, namespace):
    cls = namespace.find_class(symbol["name"])
    if cls.doc is not None:
        summary = utils.preprocess_docs(cls.doc.content, namespace, summary=True, plain=True)
    else:
        summary = "Missing documentation"

    return {
        "type": "class",
        "name": cls.name,
        "ctype": cls.base_ctype,
        "summary": summary.split("\n"),
        "link": f"class.{cls.name}.html",
    }


def _gen_class_method_result(symbol, namespace):
    t = namespace.find_real_type(symbol["type_name"])
    cls_name = t.struct_for
    if cls_name is None:
        return None

    methods = getattr(t, "methods", [])
    for m in methods:
        if m.name == symbol["name"]:
            if m.doc is not None:
                summary = utils.preprocess_docs(m.doc.content, namespace, summary=True, plain=True)
            else:
                summary = "Missing documentation"

            return {
                "type": "class method",
                "name": f"{t.name}.{m.name}",
                "ctype": m.identifier,
                "summary": summary.split("\n"),
                "link": f"class_method.{cls_name}.{m.name}.html",
            }

    return None


def _gen_ctor_result(symbol, namespace):
    t = namespace.find_real_type(symbol["type_name"])

    methods = getattr(t, "constructors", [])
    for m in methods:
        if m.name == symbol["name"]:
            if m.doc is not None:
                summary = utils.preprocess_docs(m.doc.content, namespace, summary=True, plain=True)
            else:
                summary = "Missing documentation"

            return {
                "type": "constructor",
                "name": f"{t.name}.{m.name}",
                "ctype": m.identifier,
                "summary": summary.split("\n"),
                "link": f"ctor.{t.name}.{m.name}.html",
            }

    return None


def _gen_domain_result(symbol, namespace):
    enum = namespace.find_error_domain(symbol["name"])
    if enum.doc is not None:
        summary = utils.preprocess_docs(enum.doc.content, namespace, summary=True, plain=True)
    else:
        summary = "Missing documentation"

    return {
        "type": "error",
        "name": enum.name,
        "ctype": enum.base_ctype,
        "summary": summary.split("\n"),
        "link": f"error.{enum.name}.html",
    }


def _gen_enum_result(symbol, namespace):
    enum = namespace.find_enumeration(symbol["name"])
    if enum.doc is not None:
        summary = utils.preprocess_docs(enum.doc.content, namespace, summary=True, plain=True)
    else:
        summary = "Missing documentation"

    return {
        "type": "enum",
        "name": enum.name,
        "ctype": enum.base_ctype,
        "summary": summary.split("\n"),
        "link": f"enum.{enum.name}.html",
    }


def _gen_func_result(symbol, namespace):
    functions = namespace.get_functions()
    for func in functions:
        if func.name == symbol["name"]:
            if func.doc is not None:
                summary = utils.preprocess_docs(func.doc.content, namespace, summary=True, plain=True)
            else:
                summary = "Missing documentation"
            return {
                "type": "function",
                "name": func.name,
                "ctype": func.identifier,
                "summary": summary.split("\n"),
                "link": f"func.{func.name}.html",
            }


def _gen_func_macro_result(symbol, namespace):
    macros = namespace.get_effective_function_macros()
    for func in macros:
        if func.name == symbol["name"]:
            if func.doc is not None:
                summary = utils.preprocess_docs(func.doc.content, namespace, summary=True, plain=True)
            else:
                summary = "Missing documentation"
            return {
                "type": "function macro",
                "name": func.name,
                "ctype": func.identifier,
                "summary": summary.split("\n"),
                "link": f"func.{func.name}.html",
            }


def _gen_interface_result(symbol, namespace):
    iface = namespace.find_interface(symbol["name"])
    if iface.doc is not None:
        summary = utils.preprocess_docs(iface.doc.content, namespace, summary=True, plain=True)
    else:
        summary = "Missing documentation"

    return {
        "type": "interface",
        "name": iface.name,
        "ctype": iface.base_ctype,
        "summary": summary.split("\n"),
        "link": f"iface.{iface.name}.html",
    }


def _gen_method_result(symbol, namespace):
    t = namespace.find_real_type(symbol["type_name"])

    methods = getattr(t, "methods", [])
    for m in methods:
        if m.name == symbol["name"]:
            if m.doc is not None:
                summary = utils.preprocess_docs(m.doc.content, namespace, summary=True, plain=True)
            else:
                summary = "Missing documentation"

            return {
                "type": "method",
                "name": f"{t.name}.{m.name}",
                "ctype": m.identifier,
                "summary": summary.split("\n"),
                "link": f"method.{t.name}.{m.name}.html",
            }

    return None


def _gen_property_result(symbol, namespace):
    t = namespace.find_real_type(symbol["type_name"])

    properties = getattr(t, "properties", {})
    prop = properties.get(symbol["name"], None)
    if prop is None:
        return None

    if prop.doc is not None:
        summary = utils.preprocess_docs(prop.doc.content, namespace, summary=True, plain=True)
    else:
        summary = "Missing documentation"

    return {
        "type": "property",
        "name": f"{t.name}:{prop.name}",
        "ctype": t.base_ctype,
        "summary": summary.split("\n"),
        "link": f"property.{t.name}.{prop.name}.html",
    }


def _gen_record_result(symbol, namespace):
    record = namespace.find_record(symbol["name"])
    if record.doc is not None:
        summary = utils.preprocess_docs(record.doc.content, namespace, summary=True, plain=True)
    else:
        summary = "Missing documentation"

    return {
        "type": "struct",
        "name": record.name,
        "ctype": record.base_ctype,
        "summary": summary.split("\n"),
        "link": f"struct.{record.name}.html",
    }


def _gen_signal_result(symbol, namespace):
    t = namespace.find_real_type(symbol["type_name"])

    signals = getattr(t, "signals", {})
    signal = signals.get(symbol["name"], None)
    if signal is None:
        return None

    if signal.doc is not None:
        summary = utils.preprocess_docs(signal.doc.content, namespace, summary=True, plain=True)
    else:
        summary = "Missing documentation"

    return {
        "type": "signal",
        "name": f"{t.name}::{signal.name}",
        "ctype": t.base_ctype,
        "summary": summary.split("\n"),
        "link": f"signal.{t.name}.{signal.name}.html",
    }


def _gen_type_func_result(symbol, namespace):
    t = namespace.find_real_type(symbol["type_name"])

    functions = getattr(t, "functions", [])
    for f in functions:
        if f.name == symbol["name"]:
            if f.doc is not None:
                summary = utils.preprocess_docs(f.doc.content, namespace, summary=True, plain=True)
            else:
                summary = "Missing documentation"

            return {
                "type": "func",
                "name": f"{t.name}.{f.name}",
                "ctype": f.identifier,
                "summary": summary.split("\n"),
                "link": f"type_func.{t.name}.{f.name}.html",
            }

    return None


def _gen_union_result(symbol, namespace):
    union = namespace.find_union(symbol["name"])
    if union.doc is not None:
        summary = utils.preprocess_docs(union.doc.content, namespace, summary=True, plain=True)
    else:
        summary = "Missing documentation"

    return {
        "type": "union",
        "name": union.name,
        "ctype": union.base_ctype,
        "summary": summary.split("\n"),
        "link": f"union.{union.name}.html",
    }


def _gen_vfunc_result(symbol, namespace):
    t = namespace.find_real_type(symbol["type_name"])

    methods = getattr(t, "virtual_methods", [])
    for m in methods:
        if m.name == symbol["name"]:
            if m.doc is not None:
                summary = utils.preprocess_docs(m.doc.content, namespace, summary=True, plain=True)
            else:
                summary = "Missing documentation"

            return {
                "type": "vfunc",
                "name": f"{t.name}.{m.name}",
                "ctype": t.base_ctype,
                "summary": summary.split("\n"),
                "link": f"vfunc.{t.name}.{m.name}.html",
            }

    return None


def query(repository, terms, index_file):
    if index_file is None:
        index_file = os.path.join(os.getcwd(), "index.json")

    with open(index_file, "r") as f:
        index = json.load(f)

    namespace = repository.namespace

    index_meta = index["meta"]
    index_symbols = index["symbols"]
    index_terms = index["terms"]

    if index_meta["ns"] != namespace.name or index_meta["version"] != namespace.version:
        log.error("Index file does not match the GIR namespace")

    result_types = {
        "alias": _gen_alias_result,
        "bitfield": _gen_bitfield_result,
        "callback": _gen_callback_result,
        "class": _gen_class_result,
        "class_method": _gen_class_method_result,
        "ctor": _gen_ctor_result,
        "domain": _gen_domain_result,
        "enum": _gen_enum_result,
        "function": _gen_func_result,
        "function_macro": _gen_func_macro_result,
        "interface": _gen_interface_result,
        "method": _gen_method_result,
        "property": _gen_property_result,
        "record": _gen_record_result,
        "signal": _gen_signal_result,
        "type_func": _gen_type_func_result,
        "union": _gen_union_result,
        "vfunc": _gen_vfunc_result,
    }

    results = []

    for term in terms:
        docs = index_terms.get(term, [])
        for doc in docs:
            symbol = index_symbols[doc]

            gen_result = result_types.get(symbol["type"])
            if gen_result is None:
                log.warning(f"Unhandled symbol type {symbol['type']} for '{term}'")
                continue

            res = gen_result(symbol, namespace)
            results.append(res)

    prefix = "result:"
    indent = ''.join([' ' for x in range(len(prefix))])

    n_results = len(results)
    terms_str = ", ".join(terms)
    print(f"Found {n_results} results matching '{terms_str}'")

    for res in results:
        lines = [f"{prefix} [{res['type']}] {res['name']} - {res['ctype']}"]
        for chunk in res["summary"]:
            lines.append(f"{indent} {chunk}")
        lines.append(f"{indent} link: {res['link']}")
        print("\n".join(lines))


def add_args(parser):
    parser.add_argument("--add-include-path", action="append", dest="include_paths", default=[],
                        help="include paths for other GIR files")
    parser.add_argument("--index", help="the index file")
    parser.add_argument("--term", action="append", dest="terms", default=[],
                        help="a search term")
    parser.add_argument("infile", metavar="GIRFILE", type=argparse.FileType('r', encoding='UTF-8'),
                        default=sys.stdin, help="the GIR file to parse")


def run(options):
    paths = []
    paths.extend(options.include_paths)
    paths.append(utils.default_search_paths())
    log.debug(f"Search paths: {paths}")

    log.info("Parsing GIR file")
    parser = gir.GirParser(search_paths=paths)
    parser.parse(options.infile)

    log.checkpoint()
    query(parser.get_repository(), options.terms, options.index)

    return 0
