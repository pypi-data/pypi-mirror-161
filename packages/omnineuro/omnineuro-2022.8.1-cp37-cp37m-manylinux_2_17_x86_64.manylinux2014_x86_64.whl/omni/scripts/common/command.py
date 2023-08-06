#!/usr/bin/env python3
"""
    Adds common command line arguments for omni scripts
"""
import os
import sys
import argparse
import toml
from .arguments import arg_version

# set version
__version__ = "development"


def set_common(
    parser: argparse.ArgumentParser, threads: bool = True, config: bool = True, version: bool = True
) -> None:
    """Adds common arguments for all scripts to parser.

    Parameters
    ----------
    parser: argparse.ArgumentParser
        ArgumentParser to add common arguments to.
    threads: bool
        Boolean flag for adding threads to the argument parser.
    config: bool
        Boolean flag to tell parser whether or not to hide config file options (False = hides the options).
    """
    # EASTER EGG
    if "--easter" in sys.argv[1:]:
        print(
            "\nThis blue eye perceives all things conjoined. \n"
            "The past, the future, and the present. \n"
            "Everything flows and all is connected. \n"
            "This eye is not merely seen reality. \n"
            "It is touching the truth. \n"
            "https://soundcloud.com/driver-beets/the-eye-of-truth\n"
        )
        sys.exit(0)

    # add toml config loader to arguments
    parser.add_argument(
        "--config_file",
        help="A TOML config file that specifies the arguments to use for this program. "
        "This provides an alternative way to specify arguments to the program. Note that "
        "this file follows the TOML standard: https://toml.io/en/. Arguments set for a "
        "particular program should follow under a table heading with the name of the "
        "program (e.g. [{0}]). Alternatively, arguments for multiple programs "
        "can be set using the [Global] table heading. To generate a config file for this "
        "program see the ``--generate_config`` option. Note that arguments in the config "
        "are loaded in BEFORE arguments specified on the command-line. This means when "
        "the same argument is specified in both the command line and the config file, "
        "the program will use the argument value specified on the command-line. In "
        "addition, if the same argument is provided in the [Global] and [{0}] "
        "tables, the argument under [{0}] takes precedence.".format(parser.prog)
        if config
        else argparse.SUPPRESS,
    )

    # add toml config generator
    parser.add_argument(
        "--generate_config",
        help="Path to a location (with .toml extension) to write a config file for this "
        "program. This will generate a TOML file with all options set to their current values. "
        if config
        else argparse.SUPPRESS,
    )

    # set thread use
    if threads:
        parser.add_argument(
            "-n",
            "--number_of_threads",
            default=8,
            type=int,
            help="An integer number representing the number of of threads to use for OpenMP, "
            "OpenBLAS, and ITK based components of the program. Generally a larger number is "
            "better if you can manage it, but past 16 or so there may be diminishing returns.",
        )

    # set version argument
    if version:
        arg_version(parser, "-v")


def parse_common(args: argparse.Namespace, parser: argparse.ArgumentParser) -> None:
    """Reads/Modifies the argparse Namespace object for common arguments

    Currently, this function serves to manipulate the namespace through
    the TOML config file. In addition, if `generate_config` is enabled, it
    generate a config file from the current argument values.

    Parameters
    ----------
    args : argparse.Namespace
        Namespace object to read/manipulate
    parser : argparse.ArgumentParser
        ArgumentParser to read from
    """
    # get program name
    program_name = parser.prog

    # if a toml config was given, read it in
    if args.config_file:
        # get the config arguments
        config_arguments = toml.load(args.config_file)

        # check if [Global] is in the config file
        if "Global" in config_arguments:
            # update any arguments from Global into args dictionary
            for key in config_arguments["Global"]:
                # only if key in args dict and equal to it's default value
                if key in args.__dict__ and args.__dict__[key] == parser.get_default(key):
                    args.__dict__[key] = config_arguments["Global"][key]

        # now check if [program_name] is in the config file
        if program_name in config_arguments:
            # update any arguments from program_name into args dictionary
            for key in config_arguments[program_name]:
                # only if key in args dict and equal to it's default value
                if key in args.__dict__ and args.__dict__[key] == parser.get_default(key):
                    args.__dict__[key] = config_arguments[program_name][key]

    # if generate_config was specified, generate a new config file
    if args.generate_config:
        # get the args as a dictionary
        dargs = vars(args)

        # save the generate_config path before deleting it
        generate_config_path = args.generate_config

        # remove config options from dictionary
        del dargs["config_file"]
        del dargs["generate_config"]

        # now write to disk under program_name heading
        with open(generate_config_path, "w") as f:
            toml.dump({program_name: dargs}, f)

        # force quit the program
        sys.exit(0)


def set_env(args: argparse.Namespace) -> None:
    """Sets environment variables.

    Parameters
    ----------
    args: argparse.Namespace
        A namespace object to set environment variables from.
    """
    # set number of threads to use
    if args.number_of_threads:
        os.environ["OMP_NUM_THREADS"] = str(args.number_of_threads)
        os.environ["OPENBLAS_NUM_THREADS"] = str(args.number_of_threads)
        os.environ["ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS"] = str(args.number_of_threads)
