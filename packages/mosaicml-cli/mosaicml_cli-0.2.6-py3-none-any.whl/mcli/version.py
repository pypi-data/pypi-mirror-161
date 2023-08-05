""" MCLI Versioning """
from __future__ import annotations

import logging
from typing import NamedTuple

__version_major__ = 0
__version_minor__ = 2
__version_patch__ = 6
__version_extras__ = ''
__version__ = f'v{__version_major__}.{__version_minor__}.{__version_patch__}{__version_extras__}'

logger = logging.getLogger(__name__)


class Version(NamedTuple):
    """ An Easier to work with Version Encapsulation"""
    major: int
    minor: int
    patch: int
    extras: str = ''

    def __lt__(self, o: object) -> bool:
        assert isinstance(o, Version)
        if self.major != o.major:
            return self.major < o.major
        if self.minor != o.minor:
            return self.minor < o.minor
        if self.patch != o.patch:
            return self.patch < o.patch
        if self.extras and not o.extras:
            return True
        if not self.extras and o.extras:
            return False

        if self.extras and o.extras:
            # alphas check
            # TODO: maybe more version semantics but for now lets only support alphas
            try:
                return int(self.extras.split('a')[1]) < int(o.extras.split('a')[1])
            # pylint: disable-next=bare-except
            except:
                return True
        return False

    def __eq__(self, o: object) -> bool:
        assert isinstance(o, Version)
        return self.major == o.major \
            and  self.minor == o.minor \
            and self.patch == o.patch \
            and self.extras == o.extras

    def __gt__(self, o: object) -> bool:
        assert isinstance(o, Version)
        return o < self

    @classmethod
    def from_string(cls, text: str) -> Version:
        """Parses a semantic version of the form X.Y.Z[a0-9*]?

        Does not use `v` prefix and only supports optional alpha version tags

        Args:
            text: The text to parse

        Returns:
            Returns a Version object
        """
        text = text.lstrip('v')
        major, minor, patch = text.split('.')
        extras = ''
        if not patch.isdigit():
            if 'a' in patch:
                extras = patch[patch.index('a'):]
                patch = patch[:patch.index('a')]
        return Version(
            major=int(major),
            minor=int(minor),
            patch=int(patch),
            extras=extras,
        )

    def __str__(self) -> str:
        return f'v{self.major}.{self.minor}.{self.patch}{self.extras}'

    @property
    def is_alpha(self) -> bool:
        return self.extras != ''


def print_version(**kwargs) -> int:
    # pylint: disable=import-outside-toplevel
    from mcli.config import FeatureFlag, MCLIConfig
    from mcli.utils.utils_pypi import get_latest_alpha_package_version, get_latest_package_version

    del kwargs
    print(__version__)

    current_version = Version.from_string(__version__)
    conf = MCLIConfig.load_config(safe=True)
    is_alpha = current_version.is_alpha or conf.feature_enabled(FeatureFlag.ALPHA_TESTER)
    try:
        if is_alpha:
            latest_version = get_latest_alpha_package_version()
        else:
            latest_version = get_latest_package_version()
    except Exception:  # pylint: disable=broad-except
        logger.error('\nFailed to fetch current version from PyPI\n')
        return 1

    logger.info('')
    if latest_version > current_version:
        logger.info(f'A new version ({latest_version}) is available, please upgrade with:\n'
                    f'[bold]pip install --upgrade mosaicml-cli=={str(latest_version).lstrip("v")}[/]')
    else:
        logger.info('Your version is up to date.')
    logger.info('')
    return 0
