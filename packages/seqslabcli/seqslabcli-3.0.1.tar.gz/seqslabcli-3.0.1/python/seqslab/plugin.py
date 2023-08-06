#!/usr/bin/env python3

import logging
import argparse
import tempfile
from seqslab.context import SQLBContext
from seqslab.statusbar import SQLBStatusBar
from seqslab.usage_logger import SQLBUsageLogger
from seqslab.session_logger import SQLBSessionLogger
from nubia import context
from nubia import PluginInterface, CompletionDataSource
from nubia.internal.blackcmd import CommandBlacklist
from termcolor import cprint
import os


class SQLBPlugin(PluginInterface):
    """
    The PluginInterface class is a way to customize nubia for every customer
    use case. It allows custom argument validation, control over command
    loading, custom context objects, and much more.
    """

    def create_context(self):
        """
        Must create an object that inherits from `Context` parent class.
        The plugin can return a custom context but it has to inherit from the
        correct parent class.
        """
        return SQLBContext()

    def validate_args(self, args):
        """
        This will be executed when starting nubia, the args passed is a
        dict-like object that contains the argparse result after parsing the
        command line arguments. The plugin can choose to update the context
        with the values, and/or decide to raise `ArgsValidationError` with
        the error message.
        """
        if not hasattr(args, "backend") or not args.backend:
            # take out cprint to avoid contaminate stdout content
            # cprint("Platform backend in use", "green", end=" ")
            # cprint("'azure'", "blue")
            logging.warning("Platform backend in use 'azure'")

            setattr(args, "backend", "azure")
            context.get_context().set_args(args)

    def get_opts_parser(self, add_help=True):
        """
        Builds the ArgumentParser that will be passed to , use this to
        build your list of arguments that you want for your shell.
        """
        opts_parser = argparse.ArgumentParser(
            description="Atgenomix SeqsLab CLI",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            add_help=add_help,
        )
        opts_parser.add_argument(
            "--config",
            "-c",
            default="",
            type=str,
            help="Configuration File"
        )
        opts_parser.add_argument(
            "--backend",
            "-b",
            default="",
            type=str,
            help="Platform backend, ex: 'azure'",
        )
        opts_parser.add_argument(
            "--proxy",
            "-p",
            default=None,
            type=str,
            help="Web proxy",
        )
        opts_parser.add_argument(
            "--verbose",
            "-v",
            action="count",
            default=0,
            help="Increase verbosity, can be specified " "multiple times",
        )
        opts_parser.add_argument(
            "--stderr",
            "-s",
            action="store_true",
            help="By default the logging output goes to a "
                 "temporary file. This disables this feature "
                 "by sending the logging output to stderr",
        )
        return opts_parser

    def get_completion_datasource_for_global_argument(self, argument):
        if argument == "--config":
            return ConfigFileCompletionDataSource()
        return None

    def get_status_bar(self, context):
        """
        This returns the StatusBar object that handles the bottom status bar
        and the right-side per-line status
        """
        return SQLBStatusBar(context)

    def getBlacklistPlugin(self):
        blacklister = CommandBlacklist()
        return blacklister

    def create_usage_logger(self, context):
        """
        Override this and return you own usage logger.
        Must be a subtype of UsageLoggerInterface.
        """
        return SQLBUsageLogger(context=context)

    def get_session_logger(self, context):
        """
        Return an instance of SQLBSessionLogger to enable session logging.
        """
        try:
            dir_path = "/var/log/seqslab"
            os.makedirs(dir_path, mode=0o777)
            fileobj = tempfile.NamedTemporaryFile(mode="w+",
                                                  prefix=context.binary_name + "-session-",
                                                  dir=dir_path,
                                                  delete=False)
        except PermissionError:
            fileobj = tempfile.NamedTemporaryFile(mode="w+",
                                                  prefix=context.binary_name + "-session-",
                                                  dir='/var/tmp',
                                                  delete=False)
        except FileExistsError:
            fileobj = tempfile.NamedTemporaryFile(mode="w+",
                                                  prefix=context.binary_name + "-session-",
                                                  dir="/var/log/seqslab",
                                                  delete=False)
        return SQLBSessionLogger(fileobj)

    def setup_logging(self, root_logger, args):
        """
        Configure our own logging setup. Return the root logger.
        """
        return None


class ConfigFileCompletionDataSource(CompletionDataSource):
    def get_all(self):
        return ["/tmp/c1"]
