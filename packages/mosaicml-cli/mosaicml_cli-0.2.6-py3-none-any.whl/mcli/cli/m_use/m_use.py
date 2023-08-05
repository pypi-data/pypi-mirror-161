""" mcli use Entrypoint """
import argparse
from typing import Optional

from mcli import config
from mcli.utils.utils_interactive import choose_one


def use(**kwargs):
    del kwargs
    mock_parser = configure_argparser(parser=argparse.ArgumentParser())
    mock_parser.print_help()
    return 0


def use_feature_flag(feature: Optional[str], activate: bool = True, **kwargs) -> int:
    del kwargs
    conf = config.MCLIConfig.load_config()
    available_features = list(config.FeatureFlag)
    available_features_str = [x.value for x in available_features]
    feature_flag: Optional[config.FeatureFlag] = None
    if feature:
        if feature not in available_features_str:
            print(f'Unable to find feature flag: {feature}')
        else:
            feature_flag = config.FeatureFlag[feature]
    if feature_flag is None:
        feature_flag = choose_one(
            'What feature would you like to enable?',
            options=available_features,
            formatter=lambda x: x.value,
        )

    assert feature_flag is not None
    if activate:
        print(f'Activating Feature: {feature_flag.value}')
    else:
        print(f'Deactivating Feature: {feature_flag.value}')
    conf.feature_flags[feature_flag.value] = activate
    conf.save_config()

    return 0


def configure_argparser(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    subparsers = parser.add_subparsers()
    parser.set_defaults(func=use)

    feature_parser = subparsers.add_parser('feature', help='Activate or Deactivate feature flag')
    feature_parser.add_argument('feature', nargs='?', help='The name of the Feature Flag')
    feature_parser.add_argument('--deactivate', action='store_false', dest='activate', help='Deactivate a feature flag')
    feature_parser.add_argument('--activate',
                                action='store_true',
                                default=True,
                                dest='activate',
                                help='Activate a feature flag')
    feature_parser.set_defaults(func=use_feature_flag)
    return parser


def add_use_argparser(subparser: argparse._SubParsersAction,) -> argparse.ArgumentParser:
    """Adds the use parser to a subparser

    Args:
        subparser: the Subparser to add the Use parser to
    """
    use_parser: argparse.ArgumentParser = subparser.add_parser(
        'use',
        aliases=['u'],
        help='Configure your local project',
    )
    use_parser = configure_argparser(parser=use_parser)
    return use_parser
