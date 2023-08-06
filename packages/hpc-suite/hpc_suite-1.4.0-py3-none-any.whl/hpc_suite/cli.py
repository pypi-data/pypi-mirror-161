#!/usr/bin/env python3

from argparse import ArgumentParser, ArgumentTypeError, Action, \
        RawDescriptionHelpFormatter  # , BooleanOptionalAction
import re

from . import generate_job
from .store import store_data
from .action import AppendNewline, ParseKwargs, AppendKwargs, \
        BooleanOptionalAction


def generate_job_func(args):
    """Wrapper function for command line interface call to generate_job.

    Parameters
    ----------
        args : argparser namespace
            Command line arguments.

    Returns
    -------
        None

    """

    args_dict = {key: val for key, val in vars(args).items() if key != "func"}
    generate_job.generate_job(**args_dict)


def store_func(args, make_store=None, store_items=None):
    """Wrapper function for command line interface call to store.

    Parameters
    ----------
        args : argparser namespace
            Command line arguments.
        make_store : callable
            Function which generates a store object from an storm item.
        store_items : list of pairs
            List of items to store. All items need to be known to the
            make_store() function.

    Returns
    -------
        None
    """

    data_array = \
        [[make_store(f, item) for item in store_items] for f in args.input]

    if not args.quiet:

        print("Data:")

        for item in store_items:
            print("  - {}".format(item))

        print("{} -> {}".format('|'.join(args.input), args.output or "stdout"))

    store_data(data_array, args.output, filters=args.filter,
               groups=args.group, append=args.append)


# Action for secondary help message
class SecondaryHelp(Action):
    def __init__(self, option_strings, dest=None, const=None, default=None,
                 help=None):
        super().__init__(option_strings=option_strings, dest=dest, const=const,
                         default=default, nargs=0, help=help)

    def __call__(self, parser, namespace, values, option_string=None):
        read_args([self.const, '--help'])


def parse_dict(string):

    # match name and value of a equal sign separated pair
    # capture first and second string, don't capture equal sign
    splt = re.match(r'(.+)(?:=)(.+)?$', string)

    if not splt:
        raise ArgumentTypeError("'" + string + "' is not a valid variable. " +
                                "Expected forms like 'key=value'")

    # extract name and value, if no value is given set to empty string
    name = splt.group(1)
    value = splt.group(2) or ""

    return (name, value)


def parse_dict_key_only(string):

    # match name and value of a equal sign separated pair
    # capture first and alternative second string, don't capture equal sign
    splt = re.match(r'(.+)((?:=)(.+))?$', string)

    if not splt:
        raise ArgumentTypeError("'" + string + "' is not a valid variable. " +
                                "Expected forms like 'key=value' or 'key'")

    # extract name and value, if no value is given set to empty string
    name = splt.group(1)
    value = splt.group(2) or ""

    return (name, value)


def parse_filter(string):
    pair = parse_dict(string)
    return tuple(tuple(int(lab) for lab in item.split('/') if lab)
                 for item in pair)


def parse_occ(string):
    pair = parse_dict(string)
    return (int(pair[0]), tuple(int(lab) for lab in pair[1].split('/') if lab))


def read_args(arg_list=None):

    description = '''
    A package for HPC applications.
    '''

    epilog = '''
    Lorem ipsum.
    '''

    parser = ArgumentParser(
            description=description,
            epilog=epilog,
            formatter_class=RawDescriptionHelpFormatter
            )

    subparsers = parser.add_subparsers()

    job = subparsers.add_parser('generate_job')

    job.set_defaults(func=generate_job_func)

    # arguments for generic job script generation; defaults allowed
    job.add_argument(
        '--profile',
        type=str,
        default='read_hostname',
        choices=["read_hostname", "csf3", "csf4", "cerberus", "medusa"],
        help="Profile specifying job submission system. \
              Default = read_hostname"
    )

    job.add_argument(
        '--submit_file',
        type=str,
        default="submit.sh",
        help='Output jobfile.'
    )

    job.add_argument(
        '--body',
        type=str,
        default="",
        action=AppendNewline,
        help='Body of the script.'
    )

    generic = job.add_argument_group('Basic arguments')

    generic.add_argument(
        '--job_name',
        type=str,
        help='Name of job.')

    generic.add_argument(
        '--env_vars',
        nargs='+',
        default={},
        type=parse_dict,
        action=ParseKwargs,
        help='Enviroment variables to be defined in the job script.',
        metavar='name=value')

    generic.add_argument(
        '--header',
        nargs='+',
        default=[],
        help='Custom header lines.',
        metavar='header line'
    )

    generic.add_argument(
        '--env',
        nargs='+',
        default=[],
        help='Custom environment lines.',
        metavar='env line'
    )

    generic.add_argument(
        '--exit_code',
        nargs='+',
        default=[],
        help='Custom exit code lines.',
        metavar='exit code line'
    )

    generic.add_argument(
        '--shell',
        type=str,
        default='bash',
        help='Shell to run.'
    )

    generic.add_argument(
        '--omp',
        default=1,
        type=int,
        help='Request OpenMP environment with specified number of cores.'
    )

    generic.add_argument(
        '--array',
        default=[],
        nargs='+',
        help='Create job array from list of file stems.'
    )

    generic.add_argument(
        '--verbose',
        default=True,
        action=BooleanOptionalAction,
        help='Print info message.'
    )

    # arguments for non-generic jobs; no defaults allowed
    hpc = job.add_argument_group('Submission scheduler arguments')

    hpc.add_argument(
        '--wait',
        type=bool,
        action=BooleanOptionalAction,
        help='Only return to the shell after completion of the job.'
    )

    hpc.add_argument(
        '--cwd',
        type=bool,
        action=BooleanOptionalAction,
        help='Run in current working directory.'
    )

    hpc.add_argument(
        '--pass_env',
        type=bool,
        action=BooleanOptionalAction,
        help='Pass on the env from the shell.')

    hpc.add_argument(
        '--node_type',
        type=str,
        choices=["normal", "high_mem"],
        help='Type of node to request'
    )

    hpc.add_argument(
        '--hpc_extra',
        nargs='+',
        default={},
        type=parse_dict,
        action=ParseKwargs,
        help='Extra flags passed to the job submission scheduler.',
        metavar='flag=value'
    )

    module = job.add_argument_group('Module arguments')

    module.add_argument(
        '--purge_modules',
        type=bool,
        help='Run "module purge" to remove all pre-loaded modules.'
    )

    module.add_argument(
        '--modules',
        nargs='+',
        default=[],
        help='Modules to load.',
        metavar='module'
    )

    store = subparsers.add_parser('store')

    store.set_defaults(func=store_func)

    store.add_argument(
        '--quiet',
        action='store_true',
        help='disable printing of output file name to screen'
    )

    file = store.add_argument_group('file input parameters')

    file.add_argument(
        '-i', '--input',
        default=None,
        nargs='+',
        required=True,
        help='list of input files'
    )

    output = store.add_argument_group('output parameters')

    output.add_argument(
        '-o', '--output',
        type=str,
        help='name of the output file'
    )

    output.add_argument(
        '--group',
        type=str,
        nargs='+',
        help=('path of the root HDF5 group location where the data will be '
              'stored, one group per input')
    )

    output.add_argument(
        '--append',
        default=False,
        action='store_true',
        help='append to existing database'
    )

    output.add_argument(
        '--filter',
        dest='filter',
        type=parse_filter,
        default=None,
        nargs='+',
        action=AppendKwargs,
        help=('occurrences (src) of "labelled" items to keep and store at a '
              'new location (dest)'),
        metavar='src_label=dest_label'
    )

    output.add_argument(
        '--occ',
        dest='filter',
        type=parse_occ,
        default=None,
        nargs='+',
        action=AppendKwargs,
        help=('occurrences (src) of "order only" items to keep and store at a '
              'new location (dest)'),
        metavar='src_index=dest_label'
    )

    args = parser.parse_args(arg_list)

    return args


def main():
    args = read_args()
    args.func(args)
