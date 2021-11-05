# SPDX-FileCopyrightText: 2020 GNOME Foundation
# SPDX-License-Identifier: Apache-2.0 OR GPL-3.0-or-later

import argparse
import shutil
import sys
import traceback

from . import core, log
from . import gdindex, gdgenerate, gdgenindices, gdgendeps, gdsearch, gdcheck


class GIDocGenApp:
    """
    The main GIDocGen application, working as a multiplexer for different
    commands.
    """
    def __init__(self):
        self.term_width = shutil.get_terminal_size().columns
        self.formatter = lambda prog: argparse.HelpFormatter(prog, max_help_position=int(self.term_width / 2), width=self.term_width)

        self.quiet = False
        self.commands = {}
        self.parser = argparse.ArgumentParser(prog='gi-docgen', formatter_class=self.formatter)

        self.subparser = self.parser.add_subparsers(title='Commands',
                                                    description='If no command is specified, default to help')

        self.add_command('help',
                         add_args_func=self.add_help_args,
                         run_func=self.run_help_cmd,
                         help_msg='Show the help for gi-docgen or a sub-command')
        self.add_command('index',
                         add_args_func=gdindex.add_args,
                         run_func=gdindex.run,
                         help_msg=gdindex.HELP_MSG)
        self.add_command('generate',
                         add_args_func=gdgenerate.add_args,
                         run_func=gdgenerate.run,
                         help_msg=gdgenerate.HELP_MSG)
        self.add_command('gen-index',
                         add_args_func=gdgenindices.add_args,
                         run_func=gdgenindices.run,
                         help_msg=gdgenindices.HELP_MSG)
        self.add_command('gen-deps',
                         add_args_func=gdgendeps.add_args,
                         run_func=gdgendeps.run,
                         help_msg=gdgendeps.HELP_MSG)
        self.add_command('search',
                         add_args_func=gdsearch.add_args,
                         run_func=gdsearch.run,
                         help_msg=gdsearch.HELP_MSG)
        self.add_command('check',
                         add_args_func=gdcheck.add_args,
                         run_func=gdcheck.run,
                         help_msg=gdcheck.HELP_MSG)

    def run(self, args):
        """
        Run the main application.
        """
        known_commands = list(self.commands.keys()) + ['-h', '--help']
        if not args or args[0] not in known_commands:
            args = ['help'] + args

        options = self.parser.parse_args(args)

        # Set up the logging system
        log.set_quiet(options.quiet)
        log.set_fatal_warnings(options.fatal_warnings)
        log.set_log_epoch()

        try:
            res = options.run_func(options)
            if 'help' not in args:
                report_res = log.report()
            else:
                report_res = 0
            if res == 0:
                return report_res
            return res

        except Exception:
            traceback.print_exc()
            return 1

    def add_command(self, name, add_args_func, run_func, help_msg, aliases=[]):
        """
        Add a command to the application.

        @name (str): the name of the command
        @add_args_func (callable): a function to be called to add the arguments
        @run_func (callable): a function to be called when running the command
        @help_msg (str): short help message for the command
        @aliases (array): a list of aliases for the command
        """
        p = self.subparser.add_parser(name, help=help_msg, aliases=aliases, formatter_class=self.formatter)

        # Add shared commands
        p.add_argument("-q", "--quiet", action="store_true", help="suppress messages except warnings")
        p.add_argument("--fatal-warnings", action="store_true", help="whether warnings are fatal")

        if add_args_func:
            add_args_func(p)
        p.set_defaults(run_func=run_func)
        for i in [name] + aliases:
            self.commands[i] = p

    def add_help_args(self, parser):
        parser.add_argument("-v", "--version", action="store_true", help="show the version of gi-docgen")
        parser.add_argument('command', nargs='?')

    def run_help_cmd(self, options):
        if options.version:
            print(core.version)
        elif options.command:
            known_commands = list(self.commands.keys())
            if options.command not in known_commands:
                log.error(f'Unknown command {options.command}.')
                return 1
            self.commands[options.command].print_help()
        else:
            self.parser.print_help()
        return 0


def main():
    """The entry point expected by setuptools"""
    return GIDocGenApp().run(sys.argv[1:])
