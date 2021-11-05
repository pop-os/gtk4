# SPDX-FileCopyrightText: 2021 GNOME Foundation <https://gnome.org>
# SPDX-License-Identifier: Apache-2.0 OR GPL-3.0-or-later

from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor

import re


SIGNAL_SIGIL_RE = re.compile(r"(^|\W)#([A-Z][A-Za-z0-9]+)::([a-z0-9_-]+)\b")

PROP_SIGIL_RE = re.compile(r"(^|\W)#([A-Z][A-Za-z0-9]+):([a-z0-9_-]+)\b")

TYPE_SIGIL_RE = re.compile(r"(^|\W)#([A-Z][A-Za-z0-9]+)\b")

ARG_SIGIL_RE = re.compile(r"(^|\W)@([A-Za-z0-9_]+)\b")

CONST_SIGIL_RE = re.compile(r"(^|\W)%([A-Z0-9_]+)\b")

FUNCTION_RE = re.compile(r"(^|\s+)([a-z][a-z0-9_]*)\(\)(\s+|$)")


class GtkDocPreprocessor(Preprocessor):
    """Remove all gtk-doc sigils from the Markdown text"""
    def run(self, lines):
        new_lines = []
        inside_code_block = False
        for line in lines:
            if line.startswith("```"):
                if not inside_code_block:
                    inside_code_block = True
                else:
                    inside_code_block = False

            new_line = line

            # Never transform code blocks
            if not inside_code_block:
                # XXX: The order is important; signals and properties have
                # higher precedence than types

                # Signal sigil
                new_line = re.sub(SIGNAL_SIGIL_RE, r"\g<1>`\g<2>::\g<3>`", new_line)

                # Property sigil
                new_line = re.sub(PROP_SIGIL_RE, r"\g<1>`\g<2>:\g<3>`", new_line)

                # Type sigil
                new_line = re.sub(TYPE_SIGIL_RE, r"\g<1>`\g<2>`", new_line)

                # Constant sygil
                new_line = re.sub(CONST_SIGIL_RE, r"\g<1>`\g<2>`", new_line)

                # Argument sygil
                new_line = re.sub(ARG_SIGIL_RE, r"\g<1>`\g<2>`", new_line)

                # Function
                new_line = re.sub(FUNCTION_RE, r"\g<1>`\g<2>()`\g<3>", new_line)

            new_lines.append(new_line)
        return new_lines


class GtkDocExtension(Extension):
    """Markdown extension for gtk-doc"""
    def extendMarkdown(self, md):
        """Add extensions"""
        md.preprocessors.register(GtkDocPreprocessor(md), 'gtkdoc', 27)
