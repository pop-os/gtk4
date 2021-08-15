# SPDX-FileCopyrightText: 2021 GNOME Foundation
# SPDX-License-Identifier: Apache-2.0 OR GPL-3.0-or-later

import markdown
import os
import re
import subprocess
import sys

from markupsafe import Markup
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
from typogrify.filters import typogrify

from . import gir, log, mdext, porter


# The beginning of a gtk-doc code block:
#
# |[ (optional language identifier)
#
CODEBLOCK_START_RE = re.compile(
    r'''
    ^
    \s*
    \|\[
    \s*
    (?P<language>\<\!-- \s* language="\w+" \s* --\>)?
    \s*
    $
    ''',
    re.UNICODE | re.VERBOSE)

# The optional language identifier for a gtk-doc code block:
#
# <!-- language="..." -->
#
LANGUAGE_RE = re.compile(
    r'''
    ^
    \s*
    <!--
    \s*
    language="(?P<language>\w+)"
    \s*
    -->
    \s*
    $
    ''',
    re.UNICODE | re.VERBOSE)

# The ending of a gtk-doc code block:
#
# ]|
#
CODEBLOCK_END_RE = re.compile(
    r'''
    ^
    \s*
    \]\|
    \s*
    $
    ''',
    re.UNICODE | re.VERBOSE)

LINK_RE = re.compile(
    r'''
    \[
    (`)?
    (?P<fragment>[\w]+)
    @
    (?P<endpoint>[\w\-_:\.]+)
    (`)?
    \]
    ''',
    re.VERBOSE)

TYPE_RE = re.compile(
    r'''
    (?P<ns>[\w]+\.)?            # namespace (optional)
    (?P<name>[\w]+)             # type name
    ''',
    re.VERBOSE)

PROPERTY_RE = re.compile(
    r'''
    (?P<ns>[\w]+\.)?            # namespace (optional)
    (?P<name>[\w]+)             # type name
    :{1}                        # delimiter
    (?P<property>[\w-]*\w)      # property name
    ''',
    re.VERBOSE)

SIGNAL_RE = re.compile(
    r'''
    (?P<ns>[\w]+\.)?            # namespace (optional)
    (?P<name>[\w]+)             # type name
    :{2}                        # delimiter
    (?P<signal>[\w-]*\w)        # signal name
    ''',
    re.VERBOSE)

METHOD_RE = re.compile(
    r'''
    (?P<ns>[\w]+\.)?            # namespace (optional)
    (?P<name>[\w]+)             # type name
    \.                          # delimiter
    (?P<method>[\w_]*\w)        # method name
    ''',
    re.VERBOSE)

CAMEL_CASE_START_RE = re.compile(r"([A-Z]+)([A-Z][a-z])")

CAMEL_CASE_CHUNK_RE = re.compile(r"([a-z\d])([A-Z])")

LANGUAGE_MAP = {
    'c': 'c',
    'css': 'css',
    'plain': 'plain',
    'xml': 'xml',
}

MD_EXTENSIONS = [
    # Standard extensions
    'codehilite',
    'def_list',
    'fenced_code',
    'meta',
    'tables',
    'toc',

    # Local extensions
    mdext.GtkDocExtension(),
]

MD_EXTENSIONS_CONF = {
    'codehilite': {'guess_lang': False},
    'toc': {'permalink_class': 'md-anchor', 'permalink': ''},
}

EN_STOPWORDS = set("""
a  and  are  as  at
be  but  by
for
if  in  into  is  it
near  no  not
of  on  or
such
that  the  their  then  there  these  they  this  to
was  will  with
""".split())


def process_language(lang):
    if lang is None:
        return "plain"

    res = LANGUAGE_RE.match(lang)
    if res:
        language = res.group("language") or "plain"
    else:
        language = "plain"

    return LANGUAGE_MAP[language.lower()]


class LinkParseError:
    def __init__(self, line=None, start=0, end=0, fragment=None, rest=None, message="Unable to parse link"):
        self.line = line
        self.start = start
        self.end = end
        self.fragment = fragment
        self.rest = rest
        self.message = message

    def __str__(self):
        if self.line is not None:
            msg = [self.message]
            msg.append(self.line)
            err_line = ['^'.rjust(self.start + 1, ' ')]
            err_line += [''.join(['~' for x in range(self.end - self.start - 1)])]
            msg.append("".join(err_line))
            return "\n".join(msg)
        else:
            return f"{self.message}: [{self.fragment}@{self.rest}]"


class LinkGenerator:
    def __init__(self, **kwargs):
        self._line = kwargs.get('line')
        self._start = kwargs.get('start', 0)
        self._end = kwargs.get('end', 0)
        self._namespace = kwargs.get('namespace')
        self._fragment = kwargs.get('fragment', '')
        self._endpoint = kwargs.get('endpoint', '')
        self._no_link = kwargs.get('no_link', False)

        assert self._namespace is not None

        self._repository = self._namespace.repository
        self._valid_namespaces = [n for n in self._repository.includes]
        self._external = False

        fragment_parsers = {
            "alias": self._parse_type,
            "callback": self._parse_type,
            "class": self._parse_type,
            "const": self._parse_type,
            "ctor": self._parse_method,
            "enum": self._parse_type,
            "error": self._parse_type,
            "flags": self._parse_type,
            "func": self._parse_func,
            "id": self._parse_id,
            "iface": self._parse_type,
            "method": self._parse_method,
            "property": self._parse_property,
            "signal": self._parse_signal,
            "struct": self._parse_type,
            "type": self._parse_type,
            "vfunc": self._parse_method,
        }

        parser_method = fragment_parsers.get(self._fragment)
        if parser_method is not None:
            res = parser_method(self._fragment)
            if res is not None:
                self._fragment = None
                log.warning(str(res))
        else:
            self._fragment = None
            log.warning(str(LinkParseError(self._line, self._start, self._end,
                                           self._fragment, self._endpoint,
                                           "Unable to parse link")))

    def _parse_id(self, fragment):
        t = self._namespace.find_symbol(self._endpoint)
        if isinstance(t, gir.Class) or \
           isinstance(t, gir.Interface) or \
           isinstance(t, gir.Record):
            self._fragment = 'method'
            self._symbol_name = f"{self._endpoint}()"
            self._name = t.name
            self._method_name = self._endpoint.replace(self._namespace.symbol_prefix[0] + '_', '')
            self._method_name = self._method_name.replace(t.symbol_prefix + '_', '')
            return None
        elif isinstance(t, gir.Function):
            self._fragment = 'func'
            self._symbol_name = f"{self._endpoint}()"
            self._name = None
            self._func_name = self._endpoint.replace(self._namespace.symbol_prefix[0] + '_', '')
            return None
        else:
            return LinkParseError(self._line, self._start, self._end,
                                  self._fragment, self._endpoint,
                                  f"Unable to find symbol {self._endpoint}")

    def _parse_type(self, fragment):
        res = TYPE_RE.match(self._endpoint)
        if res:
            ns = res.group('ns')
            name = res.group('name')
            if ns is not None:
                ns = ns[:len(ns) - 1]   # Drop the trailing dot
            else:
                ns = self._namespace.name
                # Accept FooBar in place of Foo.Bar
                if name.startswith(tuple(self._namespace.identifier_prefix)):
                    for prefix in self._namespace.identifier_prefix:
                        name = name.replace(prefix, '')
        else:
            return LinkParseError(self._line, self._start, self._end,
                                  self._fragment, self._endpoint,
                                  "Invalid type link")
        if ns == self._namespace.name:
            namespace = self._namespace
            self._external = False
            self._ns = ns
        else:
            repository = self._namespace.repository
            namespace = repository.find_included_namespace(ns)
            if namespace is not None:
                self._external = True
                self._ns = namespace.name
            else:
                self._fragment = None
                return None
        t = namespace.find_real_type(name)
        if t is not None and t.base_ctype is not None:
            if fragment == 'type':
                if isinstance(t, gir.Alias):
                    self._fragment = 'alias'
                elif isinstance(t, gir.BitField):
                    self._fragment = 'flags'
                elif isinstance(t, gir.Callback):
                    self._fragment = 'callback'
                elif isinstance(t, gir.Class):
                    self._fragment = 'class'
                elif isinstance(t, gir.Constant):
                    self._fragment = 'const'
                elif isinstance(t, gir.Enumeration):
                    self._fragment = 'enum'
                elif isinstance(t, gir.ErrorDomain):
                    self._fragment = 'error'
                elif isinstance(t, gir.Interface):
                    self._fragment = 'iface'
                elif isinstance(t, gir.Record) or isinstance(t, gir.Union):
                    self._fragment = 'struct'
                else:
                    return LinkParseError(self._line, self._start, self._end,
                                          self._fragment, self._endpoint,
                                          f"Invalid type {t} for '{ns}.{name}'")
            self._name = name
            self._type = t.base_ctype
            return None
        else:
            return LinkParseError(self._line, self._start, self._end,
                                  self._fragment, self._endpoint,
                                  f"Unable to find type '{ns}.{name}'")

    def _parse_property(self, fragment):
        res = PROPERTY_RE.match(self._endpoint)
        if res:
            ns = res.group('ns')
            name = res.group('name')
            pname = res.group('property')
            if ns is not None:
                ns = ns[:len(ns) - 1]   # Drop the trailing dot
            else:
                ns = self._namespace.name
                # Accept FooBar in place of Foo.Bar
                if name.startswith(tuple(self._namespace.identifier_prefix)):
                    for prefix in self._namespace.identifier_prefix:
                        name = name.replace(prefix, '')
            # Canonicalize the property name
            pname = pname.replace('_', '-')
        else:
            return LinkParseError(self._line, self._start, self._end,
                                  self._fragment, self._endpoint,
                                  "Invalid property link")
        if ns == self._namespace.name:
            namespace = self._namespace
            self._external = False
            self._ns = ns
        else:
            repository = self._namespace.repository
            namespace = repository.find_included_namespace(ns)
            if namespace is not None:
                self._external = True
                self._ns = ns
            else:
                self._fragment = None
                return None
        t = namespace.find_real_type(name)
        if t is not None and t.base_ctype is not None:
            self._type = t.base_ctype
            self._name = name
        else:
            return LinkParseError(self._line, self._start, self._end,
                                  self._fragment, self._endpoint,
                                  f"Unable to find type '{ns}.{name}'")
        if (isinstance(t, gir.Class) or isinstance(t, gir.Interface)) and pname in t.properties:
            self._property_name = pname
        else:
            return LinkParseError(self._line, self._start, self._end,
                                  self._fragment, self._endpoint,
                                  f"Invalid property '{pname}' for type '{ns}.{name}'")

    def _parse_signal(self, fragment):
        res = SIGNAL_RE.match(self._endpoint)
        if res:
            ns = res.group('ns')
            name = res.group('name')
            sname = res.group('signal')
            if ns is not None:
                ns = ns[:len(ns) - 1]   # Drop the trailing dot
            else:
                ns = self._namespace.name
                # Accept FooBar in place of Foo.Bar
                if name.startswith(tuple(self._namespace.identifier_prefix)):
                    for prefix in self._namespace.identifier_prefix:
                        name = name.replace(prefix, '')
            # Canonicalize the signal name
            sname = sname.replace('_', '-')
        else:
            return LinkParseError(self._line, self._start, self._end,
                                  self._fragment, self._endpoint,
                                  "Invalid signal link")
        if ns == self._namespace.name:
            namespace = self._namespace
            self._external = False
            self._ns = ns
        else:
            repository = self._namespace.repository
            namespace = repository.find_included_namespace(ns)
            if namespace is not None:
                self._external = True
                self._ns = namespace.name
            else:
                self._fragment = None
                return None
        t = namespace.find_real_type(name)
        if t is not None and t.base_ctype is not None:
            self._type = t.base_ctype
            self._name = name
        else:
            return LinkParseError(self._line, self._start, self._end,
                                  self._fragment, self._endpoint,
                                  f"Unable to find type '{ns}.{name}'")
        if (isinstance(t, gir.Class) or isinstance(t, gir.Interface)) and sname in t.signals:
            self._signal_name = sname
        else:
            return LinkParseError(self._line, self._start, self._end,
                                  self._fragment, self._endpoint,
                                  f"Invalid signal name '{sname}' for type '{ns}.{name}'")

    def _parse_method(self, fragment):
        res = METHOD_RE.match(self._endpoint)
        if res:
            ns = res.group('ns')
            name = res.group('name')
            method = res.group('method')
            if ns is not None:
                ns = ns[:len(ns) - 1]   # Drop the trailing dot
            else:
                ns = self._namespace.name
                # Accept FooBar in place of Foo.Bar
                if name.startswith(tuple(self._namespace.identifier_prefix)):
                    for prefix in self._namespace.identifier_prefix:
                        name = name.replace(prefix, '')
        else:
            return LinkParseError(self._line, self._start, self._end,
                                  self._fragment, self._endpoint,
                                  "Invalid method link")
        if ns == self._namespace.name:
            namespace = self._namespace
            self._external = False
            self._ns = ns
        else:
            repository = self._namespace.repository
            namespace = repository.find_included_namespace(ns)
            if namespace is not None:
                self._ns = namespace.name
                self._external = True
            else:
                self._fragment = None
                return None
        t = namespace.find_real_type(name)
        if t is not None and t.base_ctype is not None:
            self._type = t.base_ctype
            self._method_name = method
            # method@Foo.BarClass.add_name -> class_method.Bar.add_name.html
            if isinstance(t, gir.Record) and t.struct_for is not None:
                self._name = t.struct_for
                self._fragment = "class_method"
            elif fragment == "vfunc" and t.type_struct is not None:
                self._name = name
                self._type = t.type_struct
            else:
                self._name = name
        else:
            return LinkParseError(self._line, self._start, self._end,
                                  self._fragment, self._endpoint,
                                  f"Unable to find type '{ns}.{name}'")
        if fragment == "ctor":
            methods = getattr(t, "constructors", [])
        elif fragment in ["method", "class_method"]:
            methods = getattr(t, "methods", [])
        elif fragment == "vfunc":
            methods = getattr(t, "virtual_methods", [])
        else:
            methods = []
        for m in methods:
            if m.name == method:
                if fragment == "vfunc":
                    self._vfunc_name = m.name
                else:
                    self._symbol_name = f"{m.identifier}()"
                return None
        return LinkParseError(self._line, self._start, self._end,
                              self._fragment, self._endpoint,
                              f"Unable to find method '{ns}.{name}.{method}'")

    def _parse_func(self, fragment):
        tokens = self._endpoint.split('.')
        # Case 1: [func@init] => gtk_init()
        if len(tokens) == 1:
            ns = self._namespace.name
            name = None
            func_name = tokens[0]
        # Case 2: [func@Gtk.Foo.bar] => gtk_foo_bar()
        elif len(tokens) == 3:
            ns = tokens[0]
            name = tokens[1]
            func_name = tokens[2]
        # Case 3: either [func@Gtk.init] or [func@Foo.bar]
        elif len(tokens) == 2:
            if tokens[0] == self._namespace.name:
                ns = tokens[0]
                name = None
                func_name = tokens[1]
            elif tokens[0] in self._valid_namespaces:
                ns = tokens[0]
                name = None
                func_name = tokens[1]
            else:
                ns = self._namespace.name
                name = tokens[0]
                func_name = tokens[1]
        else:
            return LinkParseError(self._line, self._start, self._end,
                                  self._fragment, self._endpoint,
                                  "Invalid function link")
        if ns == self._namespace.name:
            namespace = self._namespace
            self._external = False
            self._ns = ns
        else:
            repository = self._namespace.repository
            namespace = repository.find_included_namespace(ns)
            if namespace is not None:
                self._external = True
                self._ns = namespace.name
            else:
                self._fragment = None
                log.warning(f"Namespace {ns} not found for link {self._endpoint}")
                return None
        if name is None:
            t = namespace.find_function(func_name)
            if t is not None:
                self._name = None
                self._func_name = func_name
                self._symbol_name = f"{t.identifier}()"
                return None
            else:
                return LinkParseError(self._line, self._start, self._end,
                                      self._fragment, self._endpoint,
                                      f"Unable to find function '{ns}.{func_name}'")
        else:
            t = namespace.find_real_type(name)
            if t is None:
                return LinkParseError(self._line, self._start, self._end,
                                      self._fragment, self._endpoint,
                                      f"Unable to find type '{ns}.{name}'")
            for func in t.functions:
                if func.name == func_name:
                    self._name = name
                    self._func_name = func.name
                    self._symbol_name = f"{func.identifier}()"
                    return None
            return LinkParseError(self._line, self._start, self._end,
                                  self._fragment, self._endpoint,
                                  f"Unable to find function '{ns}.{name}.{func_name}'")

    @property
    def text(self):
        if self._fragment in ['alias', 'class', 'const', 'enum', 'error', 'flags', 'iface', 'struct']:
            return f"<code>{self._type}</code>"
        elif self._fragment == 'property':
            return f"<code>{self._type}:{self._property_name}</code>"
        elif self._fragment == 'signal':
            return f"<code>{self._type}::{self._signal_name}</code>"
        elif self._fragment in ['ctor', 'func', 'method', 'class_method']:
            return f"{self._symbol_name}"
        elif self._fragment == 'vfunc':
            return f"<code>{self._ns}.{self._type}.{self._vfunc_name}</code>"
        else:
            return f"{self._endpoint}"

    @property
    def href(self):
        if self._fragment in ['alias', 'class', 'const', 'enum', 'error', 'flags', 'iface', 'struct']:
            return f"{self._fragment}.{self._name}.html"
        elif self._fragment == 'property':
            return f"property.{self._name}.{self._property_name}.html"
        elif self._fragment == 'signal':
            return f"signal.{self._name}.{self._signal_name}.html"
        elif self._fragment in ['ctor', 'method', 'class_method', 'vfunc']:
            return f"{self._fragment}.{self._name}.{self._method_name}.html"
        elif self._fragment == 'func':
            if self._name is not None:
                return f"type_func.{self._name}.{self._func_name}.html"
            else:
                return f"func.{self._func_name}.html"
        else:
            return None

    def __str__(self):
        text = self.text
        if self._no_link:
            return text
        link = self.href
        if link is None:
            return text
        if self._external:
            data_namespace = f"data-namespace=\"{self._ns}\""
            data_link = f"data-link=\"{link}\""
            href = "href=\"javascript:void(0)\""
            css = "class=\"external\""
            return f"<a {href} {data_namespace} {data_link} {css}>{text}</a>"
        else:
            return f"<a href=\"{link}\">{text}</a>"


def preprocess_docs(text, namespace, summary=False, md=None, extensions=[], plain=False, max_length=10):
    if plain:
        text = text.replace('\n', ' ')
        text = re.sub(r'<[^<]+?>', '', text)
        if max_length > 0:
            words = text.split(' ')
            if len(words) > max_length:
                words = words[:max_length - 1]
                words.append('...')
                text = ' '.join(words)
        return text

    processed_text = []

    code_block_text = []
    code_block_language = None
    inside_code_block = False

    for line in text.split("\n"):
        # If we're in "summary" mode, we bail out at the first empty line
        # after a paragraph
        if summary and line == '' and len(processed_text) > 0:
            break

        res = CODEBLOCK_START_RE.match(line)
        if res:
            code_block_language = process_language(res.group("language"))
            inside_code_block = True
            continue

        res = CODEBLOCK_END_RE.match(line)
        if res and inside_code_block:
            if code_block_language == "plain":
                processed_text += ["```"]
                processed_text.extend(code_block_text)
                processed_text += ["```"]
            else:
                lexer = get_lexer_by_name(code_block_language)
                formatter = HtmlFormatter()
                code_block = highlight("\n".join(code_block_text), lexer, formatter)
                processed_text += [""]
                processed_text.extend(code_block.split("\n"))
                processed_text += [""]

            code_block_language = None
            code_block_text = []
            inside_code_block = False
            continue

        if inside_code_block:
            code_block_text.append(line)
        else:
            new_line = []
            idx = 0
            for m in LINK_RE.finditer(line, idx):
                fragment = m.group('fragment')
                endpoint = m.group('endpoint')
                start = m.start()
                end = m.end()
                link = LinkGenerator(line=line, start=start, end=end,
                                     namespace=namespace,
                                     fragment=fragment, endpoint=endpoint,
                                     no_link=summary)
                left_pad = line[idx:start]
                replacement = re.sub(LINK_RE, str(link), line[start:end])
                new_line.append(left_pad)
                new_line.append(replacement)
                idx = end
            new_line.append(line[idx:])

            if len(new_line) == 0:
                processed_text.append(line)
            else:
                processed_text.append("".join(new_line))

    if len(processed_text) == 0:
        return ''

    # Capitalize the first character of the first line, but only if it does not
    # start with a link or a gtk-doc marker, to avoid messing up the rest of
    # the string
    first_line = processed_text[0]
    if first_line and first_line[0].isalpha():
        processed_text[0] = ''.join([first_line[0:1].upper(), first_line[1:]])

    # Append a period, if one isn't there already
    last_line = processed_text[-1]
    if last_line and last_line[-1] != '.':
        processed_text[-1] = ''.join([last_line, '.'])

    if md is None:
        md_ext = extensions.copy()
        md_ext.extend(MD_EXTENSIONS)
        text = markdown.markdown("\n".join(processed_text),
                                 extensions=md_ext,
                                 extension_configs=MD_EXTENSIONS_CONF)
    else:
        text = md.reset().convert("\n".join(processed_text))

    return Markup(typogrify(text, ignore_tags=['h1', 'h2', 'h3', 'h4']))


def stem(word, stemmer=None):
    if stemmer is None:
        stemmer = porter.PorterStemmer()
    return stemmer.stem(word, 0, len(word) - 1)


def index_description(text, stemmer=None):
    processed_text = []

    inside_code_block = False
    for line in text.split("\n"):
        if not inside_code_block and (line.startswith('```') or line.startswith('|[')):
            inside_code_block = True
            continue

        if inside_code_block and (line.startswith('```') or line.startswith(']|')):
            inside_code_block = False
            continue

        if not inside_code_block:
            processed_text.append(line)

    data = " ".join(processed_text)
    terms = set()
    for chunk in data.split(" "):
        chunk = chunk.lower()
        if chunk in ["\n", "\r", "\r\n"]:
            continue
        # Skip gtk-doc sygils
        if chunk.startswith('%') or chunk.startswith('#') or chunk.startswith('@') or chunk.endswith('()'):
            continue
        # Skip gi-docgen links
        if chunk.startswith('[') and chunk.endswith(']') and '@' in chunk:
            continue
        # Skip images
        if chunk.startswith('!['):
            continue
        if chunk in EN_STOPWORDS:
            continue
        chunk = re.sub(r"`(\w+)`", r"\g<1>", chunk)
        chunk = re.sub(r"[,\.:;`]$", '', chunk)
        chunk = re.sub(r"[\(\)]+", '', chunk)
        terms.add(stem(chunk, stemmer))
    return terms


def canonicalize(symbol):
    return symbol.replace('-', '_')


def index_identifier(symbol, stemmer=None):
    """Chunks an identifier (e.g. EventControllerClik) into terms useful for indexing."""
    symbol = re.sub(CAMEL_CASE_START_RE, r"\g<1>_\g<2>", symbol)
    symbol = re.sub(CAMEL_CASE_CHUNK_RE, r"\g<1>_\g<2>", symbol)
    symbol = symbol.replace('-', '_')
    symbol = symbol.lower()
    terms = set()
    for chunk in symbol.split('_'):
        if chunk in EN_STOPWORDS:
            continue
        terms.add(stem(chunk, stemmer))
    return terms


def index_symbol(symbol, stemmer=None):
    """Chunks a symbol (e.g. set_layout_manager) into terms useful for indexing."""
    terms = set()
    for chunk in canonicalize(symbol).split('_'):
        if chunk in EN_STOPWORDS:
            continue
        terms.add(stem(chunk, stemmer))
    return terms


def code_highlight(text, language='c'):
    lexer = get_lexer_by_name(language)
    formatter = HtmlFormatter()
    return Markup(highlight(text, lexer, formatter))


def render_dot(dot, output_format="svg"):
    if output_format not in ["svg", "png"]:
        log.error("Invalid output format for render_dot(): {output_format}")

    args = ["dot", f"-T{output_format}"]

    try:
        proc = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        proc.stdin.write(dot.encode("utf-8"))
        output, err = proc.communicate()
        if err:
            log.warning(f"Unable to process dot data: {err}")
            return None
        if output_format == "svg":
            return output.decode("utf-8")
    except Exception as e:
        log.warning(f"Unable to process dot data: {e}")
        return None


found_programs = {}


def find_program(bin_name, path=None):
    """Finds a program @bin_name inside the given @path, and returns
    its full path if found, or None if the program could not be found.

    The @bin_name will automatically get an extension depending on the
    platform.
    """
    global found_programs

    if path is None and bin_name in found_programs:
        return found_programs[bin_name]

    if path is None:
        search_paths = os.environ['PATH'].split(os.pathsep)
    else:
        search_paths = path.split(os.pathsep)

    bin_extensions = ['']

    if sys.platform == 'win32':
        pathext = os.environ['PATHEXT'].lower().split(os.pathsep)
        (basename, extension) = os.path.splitext(bin_name)
        if extension.lower() not in pathext:
            bin_extensions = pathext
        search_paths.insert(0, '')

    for ext in bin_extensions:
        executable = bin_name + ext

        for p in search_paths:
            full_path = os.path.join(p, executable)
            if os.path.isfile(full_path):
                # Memoize the result with the default PATH, so we can
                # call this multiple times at no additional cost
                if path is None:
                    found_programs[bin_name] = full_path
                return full_path

    return None


def default_search_paths():
    if not sys.platform == 'win32':
        xdg_data_dirs = os.environ.get("XDG_DATA_DIRS", "/usr/share:/usr/local/share").split(":")
        xdg_data_home = os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))
    else:
        xdg_data_dirs = None
        xdg_data_home = None

    paths = []
    paths.append(os.getcwd())
    # Add sys.base_prefix when using MSYS2
    if sys.platform == 'win32' and 'GCC' in sys.version:
        paths.append(os.path.join(sys.base_prefix, 'share', 'gir-1.0'))
    if xdg_data_home is not None:
        paths.append(os.path.join(xdg_data_home, "gir-1.0"))
    if xdg_data_dirs is not None:
        paths.extend([os.path.join(x, "gir-1.0") for x in xdg_data_dirs])

    return paths
