# SPDX-FileCopyrightText: 2021 GNOME Foundation
# SPDX-License-Identifier: Apache-2.0 OR GPL-3.0-or-later

import argparse
import os
import sys

from . import config, gir, log, utils


HELP_MSG = "Generates the build dependencies"


def _gen_content_files(config, content_dirs):
    content_files = []
    for file_name in config.content_files:
        content_files.append(utils.find_extra_content_file(content_dirs, file_name))
    return content_files


def _gen_content_images(config, content_dirs):
    content_images = []
    for image_file in config.content_images:
        content_images.append(utils.find_extra_content_file(content_dirs, image_file))
    return content_images


def gen_dependencies(repository, config, options):
    outfile = options.outfile

    outfile.write(options.config)
    outfile.write("\n")

    for name in repository.includes:
        include = repository.includes[name]
        if include.girfile is not None:
            outfile.write(include.girfile)
            outfile.write("\n")

    outfile.write(repository.girfile)
    outfile.write("\n")

    content_dirs = options.content_dirs
    if content_dirs == []:
        content_dirs = [os.getcwd()]

    content_files = _gen_content_files(config, content_dirs)
    for f in content_files:
        outfile.write(f)
        outfile.write("\n")

    content_images = _gen_content_images(config, content_dirs)
    for f in content_images:
        outfile.write(f)
        outfile.write("\n")


def add_args(parser):
    parser.add_argument("--add-include-path", action="append", dest="include_paths", default=[],
                        help="include paths for other GIR files")
    parser.add_argument("-C", "--config", metavar="FILE", help="the configuration file")
    parser.add_argument("--content-dir", action="append", dest="content_dirs", default=[],
                        help="the base directories with the extra content")
    parser.add_argument("--dry-run", action="store_true", help="parses the GIR file without generating files")
    parser.add_argument("infile", metavar="GIRFILE", type=argparse.FileType('r', encoding='UTF-8'),
                        default=sys.stdin, help="the GIR file to parse")
    parser.add_argument("outfile", metavar="DEPFILE", type=argparse.FileType('w', encoding='UTF-8'),
                        default=sys.stdout, help="the dependencies file to generate")


def run(options):
    # If we're sending output to stdout, we disable logging
    if options.outfile.name == "<stdout>":
        log.set_quiet(True)

    log.info(f"Loading config file: {options.config}")
    conf = config.GIDocConfig(options.config)

    paths = []
    paths.extend(options.include_paths)
    paths.extend(utils.default_search_paths())
    log.info(f"Search paths: {paths}")

    log.info("Parsing GIR file")
    parser = gir.GirParser(search_paths=paths)
    parser.parse(options.infile)

    if not options.dry_run:
        gen_dependencies(parser.get_repository(), conf, options)

    return 0
