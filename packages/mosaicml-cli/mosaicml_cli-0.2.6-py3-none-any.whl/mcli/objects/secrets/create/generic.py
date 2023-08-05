"""Creators for generic secrets"""
import re
import uuid
from pathlib import Path
from typing import Callable, Optional, Set, Tuple

from mcli.cli.m_create.env_var import EnvVarValidator
from mcli.models.mcli_secret import SECRET_MOUNT_PATH_PARENT, MCLIGenericSecret, SecretType
from mcli.objects.secrets import MCLIEnvVarSecret, MCLIMountedSecret, MCLIS3Secret
from mcli.objects.secrets.create.base import SecretCreator, SecretValidationError, SecretValidator
from mcli.utils.utils_interactive import file_prompt, secret_prompt, simple_prompt
from mcli.utils.utils_string_validation import (KEY_VALUE_PATTERN, ensure_rfc1123_compatibility, validate_absolute_path,
                                                validate_existing_filename)


class GenericSecretFiller():
    """Interactive filler for secret data
    """

    @staticmethod
    def fill_value() -> str:
        return secret_prompt('What data would you like to store?')


class GenericSecretValidator():
    """Validation methods for generic secret data
    """
    pass


class GenericSecretCreator(GenericSecretFiller, GenericSecretValidator):
    """Creates base generic secrets for the CLI
    """

    def create(self,
               name: Optional[str] = None,
               value: Optional[str] = None,
               make_name_unique: bool = False) -> MCLIGenericSecret:

        base_creator = SecretCreator()
        secret = base_creator.create(SecretType.generic, name=name, make_name_unique=make_name_unique)
        assert isinstance(secret, MCLIGenericSecret)

        if not secret.value:
            secret.value = value or self.fill_value()

        return secret


class EnvVarSecretFiller():
    """Interactive filler for secret data
    """

    @staticmethod
    def fill_key(validate: Callable[[str], bool]) -> str:
        return simple_prompt('If an environment variable is KEY=VALUE, what should be the KEY?', validate=validate)


class EnvVarSecretValidator(SecretValidator, EnvVarValidator):
    """Validation methods for env var secret data

    Raises:
        SecretValidationError: Raised for any validation error for secret data
    """


class EnvVarSecretCreator(EnvVarSecretFiller, EnvVarSecretValidator):
    """Creates env var secrets for the CLI
    """

    @staticmethod
    def get_env(env_pair: str) -> Tuple[str, str]:
        m = re.fullmatch(KEY_VALUE_PATTERN, env_pair)
        assert m is not None
        key, value = m.groups()
        return key, value

    def create(
        self,
        env_pair: Optional[str] = None,
        name: Optional[str] = None,
        value: Optional[str] = None,
        key: Optional[str] = None,
    ) -> MCLIEnvVarSecret:

        if env_pair:
            self.validate_env_pair(env_pair)
            key, value = self.get_env(env_pair)

        # Validate key
        if key:
            self.validate_env_key_available(key)

        # Fill key
        if not key:
            key = self.fill_key(self.validate_key)

        # Make a name if not provided
        make_name_unique = False
        if not name:
            name = ensure_rfc1123_compatibility(key)
            make_name_unique = True

        # Make and fill generic secret
        generic_creator = GenericSecretCreator()
        generic_secret = generic_creator.create(name, value, make_name_unique=make_name_unique)

        return MCLIEnvVarSecret.from_generic_secret(generic_secret, key=key)


class FileSecretFiller():
    """Interactive filler for secret data
    """

    @staticmethod
    def fill_secret_path(validate: Callable[[str], bool]) -> str:
        del validate
        return file_prompt('Which file would you like to store as a secret?')


class FileSecretValidator(SecretValidator):
    """Validation methods for mounted secret data

    Raises:
        SecretValidationError: Raised for any validation error for secret data
    """

    def __init__(self):
        super().__init__()
        self.existing_mounts = self.get_existing_mounts()

    def get_existing_mounts(self) -> Set[str]:
        secret_paths = {
            s.mount_path for s in self.existing_secrets if isinstance(s, MCLIMountedSecret) and s.mount_path
        }
        s3_mounts = {
            s.mount_directory for s in self.existing_secrets if isinstance(s, MCLIS3Secret) and s.mount_directory
        }
        return secret_paths | s3_mounts

    def get_valid_mount_path(self, name: str, unique: bool = False) -> str:
        if not unique:
            proposed = str(SECRET_MOUNT_PATH_PARENT / name)
        else:
            proposed = str(SECRET_MOUNT_PATH_PARENT / name / f'-{str(uuid.uuid4())[:6]}')

        try:
            self.validate_mount_available(proposed, self.existing_mounts)
        except SecretValidationError:
            if not unique:
                # Try getting a unique path
                proposed = self.get_valid_mount_path(name, True)
            else:
                # If that fails for some reason, just fail
                raise
        return proposed

    @staticmethod
    def validate_mount_absolute(path: str) -> bool:
        is_valid = validate_absolute_path(path)
        if not is_valid:
            raise SecretValidationError('Invalid mount point. Mount must be an absolute path, '
                                        f'not {path}.')
        return True

    @staticmethod
    def validate_mount_available(path: str, existing_paths: Set[str]) -> bool:
        if path in existing_paths:
            path_str = '\n'.join(sorted(list(existing_paths)))
            raise SecretValidationError(f'Duplicate path. Mount path {path} already in use.'
                                        f'Please choose something not in: {path_str}.')
        return True

    def validate_mount(self, path: str) -> bool:
        return self.validate_mount_absolute(path) and self.validate_mount_available(path, self.existing_mounts)

    @staticmethod
    def validate_path_exists(path: str) -> bool:
        if not validate_existing_filename(path):
            raise SecretValidationError(f'File does not exist. File path {path} does not exist or is not a file.')
        return True


class FileSecretCreator(FileSecretFiller, FileSecretValidator):
    """Creates mounted secrets for the CLI
    """

    def create(
        self,
        name: Optional[str] = None,
        secret_path: Optional[str] = None,
        mount_path: Optional[str] = None,
    ) -> MCLIMountedSecret:

        if secret_path:
            self.validate_path_exists(secret_path)

        # Validate mount path
        if mount_path:
            self.validate_mount(mount_path)

        # Fill secret file
        if not secret_path:
            secret_path = self.fill_secret_path(self.validate_path_exists)

        secret_file = Path(secret_path).expanduser().absolute()

        # Default name based on secret path
        make_name_unique = False
        if not name:
            name = ensure_rfc1123_compatibility(secret_file.stem)
            make_name_unique = True

        # Read secret value
        with open(secret_file, 'r', encoding='utf8') as fh:
            value = fh.read()

        # Create generic secret
        generic_creator = GenericSecretCreator()
        generic_secret = generic_creator.create(name, value, make_name_unique=make_name_unique)

        # Get a mount path based on the secret's name
        if mount_path is None:
            mount_path = self.get_valid_mount_path(generic_secret.name)
        return MCLIMountedSecret.from_generic_secret(generic_secret, mount_path=mount_path)
