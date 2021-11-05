<!--
SPDX-FileCopyrightText: 2021 GNOME Foundation

SPDX-License-Identifier: Apache-2.0 OR GPL-3.0-or-later
-->

Release check list
==================

- [ ] Collect all changes since the previous tag
- [ ] Tag the release, using `git tag -s YYYY.N`
- [ ] Write down all the noteworthy changes in the tag message
- [ ] Update `twine`: `pip install --upgrade --user twine`
- [ ] Build a Python dist: `python -m build`
- [ ] Upload the dist to PyPI: `python -m twine upload dist/*`
- [ ] Build a Meson dist: `meson setup _build . && meson dist -C _build`
- [ ] Upload the Meson dist to gnome.org
- [ ] Clean up the repository: `git clean -xdf`
- [ ] Bump the version in `meson.build` and `gidocgen/core.py` to `YYYY.N+1`
- [ ] Push the changes to the repository: `git push origin HEAD`
- [ ] Push the release tag to the repository: `git push origin YYYY.N`
