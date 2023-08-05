""" m delete Entrypoint """
import argparse
import functools
from typing import Callable, List, Optional

from mcli.cli.m_delete.delete import delete_environment_variable, delete_platform, delete_run, delete_secret
from mcli.utils.utils_cli import CLIExample, Description, get_example_text
from mcli.utils.utils_pod_state import PodState

# pylint: disable-next=invalid-name
_description = Description("""
The table below shows the objects that you can delete. For each object below, you can
delete or more of them by name. Each object also supports glob-style selection and --all
to delete all.

To view object-specific additional help, run:

mcli delete <object> --help
""")

_platform_description = Description("""
Remove platform(s) from your setup. This prevents you from launching runs on any of their
instances.
""")
_platform_example_all = CLIExample(example='mcli delete platforms rXzX rXzY', description='Delete multiple platforms')
_platform_examples = [
    _platform_example_all,
    CLIExample(example='mcli delete platforms rXz*', description='Delete platforms that match a pattern'),
    CLIExample(example='mcli delete platforms --all', description='Delete all platforms'),
]

_env_description = Description("""
Delete one or more environment variables from your standard workload setup.
""")
_env_example_all = CLIExample(example='mcli delete env FOO', description='Delete an environment variable FOO')
_env_examples = [
    _env_example_all,
    CLIExample(example='mcli delete envs FOO BAR', description='Delete multiple environment variables'),
    CLIExample(example='mcli delete envs --all', description='Delete all environment variables'),
]

_secret_description = Description("""
Delete one or more secrets from your standard workload setup. These secrets will be
removed completely from the secrets database and no longer added to any subsequent runs.
""")
_secret_example_all = CLIExample(example='mcli delete secrets foo bar', description='Delete secrets foo and bar')
_secret_examples = [
    CLIExample(example='mcli delete secret foo', description='Delete a secret named foo'),
    _secret_example_all,
    CLIExample(example='mcli delete secrets --all', description='Delete all secrets'),
]

_run_description = Description("""
Delete a run or set of runs that match some conditions.
""")
_run_example_simple = CLIExample(example='mcli delete run my-run-1', description='Delete a specific run')
_run_example_status = CLIExample(example='mcli delete runs --status failed,completed',
                                 description='Delete all failed and completed runs')

_run_examples = [
    _run_example_simple,
    CLIExample(example='mcli delete runs --platform rXzX,rXzY',
               description='Delete all runs on platforms rXzX and rXzY'),
    _run_example_status,
    CLIExample(example='mcli delete runs --all', description='Delete all runs (Please be careful!)'),
]
_all_examples = [
    _platform_example_all,
    _env_example_all,
    _secret_example_all,
    _run_example_simple,
    _run_example_status,
]


def delete(parser, **kwargs) -> int:
    del kwargs
    parser.print_help()
    return 0


def add_common_args(parser: argparse.ArgumentParser):
    parser.add_argument('-y',
                        '--force',
                        dest='force',
                        action='store_true',
                        help='Skip confirmation dialog before deleting. Please be careful!')


def comma_separated(arg: str, fun: Optional[Callable[[str], str]] = None) -> List[str]:
    """Get a list of strings from a comma-separated string

    Arg:
        arg: String to process for comma-separated values
        fun: Callable applied to each value in the comma-separated list. Default None.

    Returns:
        List of function outputs
    """
    values = [v.strip() for v in arg.split(',')]
    if fun:
        return [fun(v) for v in values]
    else:
        return values


def configure_argparser(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:

    subparsers = parser.add_subparsers(
        title='MCLI Objects',
        help='DESCRIPTION',
        metavar='OBJECT',
    )
    parser.set_defaults(func=delete, parser=parser)

    # TODO: Delete Projects

    platform_parser = subparsers.add_parser(
        'platform',
        aliases=['platforms'],
        help='Delete one or more platforms',
        description=_platform_description,
        epilog=get_example_text(*_platform_examples),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    platform_parser.add_argument(
        'platform_names',
        nargs='*',
        metavar='PLATFORM',
        help='The name of the platform(s) to delete. Also supports glob-style pattern matching')
    platform_parser.add_argument('-a', '--all', dest='delete_all', action='store_true', help='Delete all platforms')
    platform_parser.set_defaults(func=delete_platform)
    add_common_args(platform_parser)

    environment_parser = subparsers.add_parser(
        'env',
        aliases=['envs'],
        help='Delete one or more environment variables',
        description=_env_description,
        epilog=get_example_text(*_env_examples),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    environment_parser.add_argument(
        'variable_names',
        nargs='*',
        metavar='ENV',
        help='The name(s) of the environment variable(s) to delete. Also supports glob-style pattern matching')
    environment_parser.add_argument('-a',
                                    '--all',
                                    dest='delete_all',
                                    action='store_true',
                                    help='Delete all environment variables')
    environment_parser.set_defaults(func=delete_environment_variable)
    add_common_args(environment_parser)

    secrets_parser = subparsers.add_parser(
        'secret',
        aliases=['secrets'],
        help='Delete one or more secrets',
        description=_secret_description,
        epilog=get_example_text(*_secret_examples),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    secrets_parser.add_argument(
        'secret_names',
        nargs='*',
        metavar='SECRET',
        help='The name(s) of the secret(s) to delete. Also supports glob-style pattern matching.')
    secrets_parser.add_argument('-a', '--all', dest='delete_all', action='store_true', help='Delete all secrets')
    secrets_parser.set_defaults(func=delete_secret)
    add_common_args(secrets_parser)

    run_parser = subparsers.add_parser(
        'run',
        aliases=['runs'],
        help='Delete one or more runs',
        description=_run_description,
        epilog=get_example_text(*_run_examples),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    run_parser.add_argument('name_filter',
                            nargs='*',
                            metavar='RUN',
                            default=None,
                            help='The name(s) of the run(s) to delete')
    run_parser.add_argument('-p',
                            '--platform',
                            dest='platform_filter',
                            metavar='PLATFORM',
                            type=comma_separated,
                            default=None,
                            help='Delete runs on the specified platform(s). If no other arguments are provided, all '
                            'runs on the specified platform(s) will be deleted. Multiple platforms should be specified '
                            'using a comma-separated list, e.g. "platform1,platform2"')

    def _to_status(text: str) -> str:
        return text.title().replace('_', '').lower()

    status_options = [_to_status(state.value) for state in PodState]

    run_parser.add_argument(
        '-s',
        '--status',
        dest='status_filter',
        default=None,
        metavar='STATUS',
        type=functools.partial(comma_separated, fun=_to_status),
        help=f'Delete runs with the specified statuses (choices: {", ".join(status_options)}). '
        'Multiple statuses should be specified using a comma-separated list, e.g. "failed,completed"')
    run_parser.add_argument('-a', '--all', dest='delete_all', action='store_true', help='Delete all runs')
    run_parser.set_defaults(func=delete_run)
    add_common_args(run_parser)

    return parser


def add_delete_argparser(subparser: argparse._SubParsersAction,
                         parents: Optional[List[argparse.ArgumentParser]] = None) -> argparse.ArgumentParser:
    del parents

    delete_parser: argparse.ArgumentParser = subparser.add_parser(
        'delete',
        aliases=['del'],
        help='Delete one or more MCLI objects',
        description=_description,
        epilog=get_example_text(*_all_examples),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    delete_parser = configure_argparser(parser=delete_parser)
    return delete_parser
