# SPDX-FileCopyrightText: 2021 GNOME Foundation
# SPDX-License-Identifier: Apache-2.0 OR GPL-3.0-or-later

import sys

if sys.version_info < (3, 6, 0):
    raise SystemExit('ERROR: GI-DocGen requires Python 3.6.0')

from gidocgen.core import version

from distutils.command.build_py import build_py as _build_py
from setuptools import setup


class BuildCommand(_build_py):

    def generate_pkgconfig_file(self):
        lines = []
        with open('gi-docgen.pc.in', 'r') as f:
            for line in f.readlines():
                new_line = line.strip().replace('@VERSION@', version)
                lines.append(new_line)
        with open('gi-docgen.pc', 'w') as f:
            f.write('\n'.join(lines))

    def run(self):
        self.generate_pkgconfig_file()
        return super().run()


def readme_md():
    '''Return the contents of the README.md file'''
    return open('README.md').read()


entries = {
    'console_scripts': ['gi-docgen=gidocgen.gidocmain:main'],
}

packages = [
    'gidocgen',
    'gidocgen.gir',
]

package_data = {
    'gidocgen': [
        "templates/basic/basic.toml",
        "templates/basic/*.css",
        "templates/basic/*.html",
        "templates/basic/*.js",
        "templates/basic/*.png",
        "templates/basic/*.woff2",
        "templates/basic/*.woff",
    ],
}

data_files = [
    ('share/pkgconfig', ['gi-docgen.pc']),
    ('share/man/man1', ['docs/gi-docgen.1']),
]

if __name__ == '__main__':
    setup(
        cmdclass={
            'build_py': BuildCommand,
        },
        name='gi-docgen',
        version=version,
        license='GPL-3.0-or-later AND Apache-2.0 AND CC0-1.0',
        long_description=readme_md(),
        long_description_content_type='text/markdown',
        include_package_data=True,
        packages=packages,
        package_data=package_data,
        entry_points=entries,
        data_files=data_files,
    )
