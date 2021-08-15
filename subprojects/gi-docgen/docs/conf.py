# SPDX-FileCopyrightText: 2021 GNOME Foundation
#
# SPDX-License-Identifier: Apache-2.0 OR GPL-3.0-or-later

project = 'gi-docgen'
copyright = '2021, Emmanuele Bassi'
author = 'Emmanuele Bassi'

release = '2021.1'

extensions = [
    'sphinx.ext.extlinks',
]

source_suffix = '.rst'
master_doc = 'index'

exclude_patterns = ['_build']

html_theme = 'sphinx_rtd_theme'
html_show_copyright = False
html_title = project

html_theme_options = {
    'display_version': False,
}

html_static_path = ['extra.css']

html_context = {
    'extra_css_files': [
        '_static/extra.css',
    ],
}

extlinks = {
    'commit': ('https://gitlab.gnome.org/GNOME/gobject-introspection/commit/%s', ''),
    'issue': ('https://gitlab.gnome.org/GNOME/gobject-introspection/issues/%s', '#'),
    'mr': ('https://gitlab.gnome.org/GNOME/gobject-introspection/merge_requests/%s', '!'),
}
