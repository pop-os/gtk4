# SPDX-FileCopyrightText: 2021 GNOME Foundation
#
# SPDX-License-Identifier: Apache-2.0 OR GPL-3.0-or-later

all: _build

_build: Makefile *.rst */*.rst conf.py
	python3 -m sphinx  -b html . _build

linkcheck:
	python3 -m sphinx  -b linkcheck -n . _build

clean:
	rm -Rf _build
