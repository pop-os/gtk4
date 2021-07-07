<!--
SPDX-FileCopyrightText: 2021 GNOME Foundation

SPDX-License-Identifier: Apache-2.0 OR GPL-3.0-or-later
-->

# Contribution guidelines

Thank you for considering contributing to the GI-DocGen project!

These guidelines are meant for new contributors, regardless of their level
of proficiency; following them allows the maintainers of the GI-DocGen project
to more effectively evaluate your contribution, and provide prompt feedback to
you. Additionally, by following these guidelines you clearly communicate
that you respect the time and effort that the people developing this project
put into managing it.

Please, do not use the issue tracker for support questions. If you have
questions on how to use GTK effectively, you can use:

 - the `#gtk` IRC channel on irc.gnome.org
 - the [GNOME Discourse instance](https://discourse.gnome.org/)

The issue tracker is meant to be used for actionable issues only, that is
issues that have a clear conditions towards their resolution.

## Your first contribution

### Prerequisites

If you want to contribute to the GI-DocGen project, you will need to have
the development tools appropriate for your operating system, including:

 - Python 3.x
 - Meson

The GI-DocGen project uses GitLab for code hosting and for tracking issues.
More information about using GitLab can be found [on the GNOME
wiki](https://wiki.gnome.org/GitLab).

### Getting started

You should start by forking the GTK repository from the GitLab web UI, and
cloning from your fork:

```sh
$ git clone https://gitlab.gnome.org/yourusername/gi-docgen.git
$ cd gi-docgen
```

Typically, you should work on your own branch:

```sh
$ git switch -C your-branch
```

You can use Meson to set up GI-DocGen:

```sh
$ meson _build
```

or you can use the `setup.py` script:

```sh
$ python ./setup.py build
```

Once you've finished working on the bug fix or feature, push the branch
to the Git repository and open a new merge request, to let the GI-DocGen
maintainers review your contribution.

### Code reviews

Each contribution is reviewed by the core developers of the GI-DocGen
project.

The [CODEOWNERS](./docs/CODEOWNERS) document contains the list of core
contributors to the project and the areas for which they are responsible;
you should ensure to receive their review and signoff on your changes.

### Commit messages

The expected format for git commit messages is as follows:

```plain
Short explanation of the commit

Longer explanation explaining exactly what's changed, whether any
external or private interfaces changed, what bugs were fixed (with bug
tracker reference if applicable) and so forth. Be concise but not too
brief.

Fixes: #1234
```

 - Always add a brief description of the commit to the _first_ line of
 the commit and terminate by two newlines (it will work without the
 second newline, but that is not nice for the interfaces).

 - First line (the brief description) must only be one sentence and
 should start with a capital letter unless it starts with a lowercase
 symbol or identifier. Don't use a trailing period either. Don't exceed
 72 characters.

 - The main description (the body) is normal prose and should use normal
 punctuation and capital letters where appropriate. Consider the commit
 message as an email sent to the developers (or yourself, six months
 down the line) detailing **why** you changed something. There's no need
 to specify the **how**: the changes can be inlined.

 - When committing code on behalf of others use the `--author` option, e.g.
 `git commit -a --author "Joe Coder <joe@coder.org>"` and `--signoff`.

 - If your commit is addressing an issue, use the
 [GitLab syntax](https://docs.gitlab.com/ce/user/project/issues/automatic_issue_closing.html)
 to automatically close the issue when merging the commit with the upstream
 repository:

```plain
Closes #1234
Fixes #1234
Closes: https://gitlab.gnome.org/GNOME/gtk/issues/1234
```

 - If you have a merge request with multiple commits and none of them
 completely fixes an issue, you should add a reference to the issue in
 the commit message, e.g. `Bug: #1234`, and use the automatic issue
 closing syntax in the description of the merge request.
