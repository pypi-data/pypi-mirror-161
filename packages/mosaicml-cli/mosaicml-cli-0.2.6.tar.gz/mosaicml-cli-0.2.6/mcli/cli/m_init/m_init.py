""" m init Entrypoint"""
import logging
import textwrap

from mcli import config
from mcli.config import MCLIConfig
from mcli.utils.utils_logging import OK

logger = logging.getLogger(__name__)


def initialize_mcli_config() -> bool:
    """Initialize the MCLI config directory and file, if necessary

    Returns:
        True if MCLI needed to be initialized. False if initialization was already done.
    """

    initialized = False
    if not config.MCLI_CONFIG_DIR.exists():
        config.MCLI_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        initialized = True
        logger.debug(f'{OK} Created MCLI config directory')
    else:
        logger.debug(f'{OK} MCLI config directory already exists')

    # Generate MCLI Config if not existing
    try:
        mcli_config = MCLIConfig.load_config()
        logger.debug(f'{OK} MCLI config file already exists')
    except Exception as _:  # pylint: disable=broad-except
        mcli_config = MCLIConfig.empty()
        mcli_config.save_config()
        initialized = True
        logger.debug(f'{OK} Created new MCLI config file')

    return initialized


def initialize_mcli(**kwargs) -> int:
    del kwargs

    welcome = """
    ------------------------------------------------------
    Welcome to MCLI
    ------------------------------------------------------
    """
    logger.info(textwrap.dedent(welcome))

    if initialize_mcli_config():
        logger.info(f'{OK} Initialized MCLI!')
    else:
        logger.info(f'{OK} MCLI already initialized. You\'re good to go!')
    logger.info('')

    platform_setup = """
    Before you can run anything, you'll first need to setup your platform access.
    To download your platform credentials, try:

    [bold]mcli init-kube[/]

    And get started launching your runs.

    For more information see the docs at:
    https://mcli.docs.mosaicml.com/getting_started/installation.html#configuring-kubernetes
    """
    logger.info(textwrap.dedent(platform_setup).lstrip())

    logger.info('')

    env_setup = """
    For help getting started with setting up your compute environment, try running:

    [bold]mcli create --help[/]

    or take a look at the docs at:
    https://mcli.docs.mosaicml.com/getting_started/managing_run_environment.html
    """
    logger.info(textwrap.dedent(env_setup).lstrip())

    logger.info('')

    run_text = """
    When you're ready to launch some runs, take a look at:

    [bold]mcli run --help[/]

    or browse the docs at:
    https://mcli.docs.mosaicml.com/launching/run.html
    """
    logger.info(textwrap.dedent(run_text).lstrip())

    return 0
