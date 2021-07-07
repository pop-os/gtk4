#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2020 GNOME Foundation
# SPDX-License-Identifier: Apache-2.0 OR GPL-3.0-or-later

import sys
from pathlib import Path

# Handle running uninstalled
gidocgen_bin = Path(sys.argv[0]).resolve()
if (gidocgen_bin.parent / 'gidocgen').is_dir():
    sys.path.insert(0, str(gidocgen_bin.parent))

from gidocgen import gidocmain

if __name__ == '__main__':
    """Main entry point. Instantiates the GIDocGen application and runs it."""
    if sys.version_info < (3, 6):  # pragma: no cover
        print(
            "GIDocGen requires Python >= 3.6, but you have version " + sys.version_info
        )
        print("Please update your environment to use GIDocGen.")
        sys.exit(1)
    app = gidocmain.GIDocGenApp()
    sys.exit(app.run(sys.argv[1:]))
