"""Creators for docker secrets"""
from typing import Callable, Optional

from mcli.models import SecretType
from mcli.objects.secrets import MCLIDockerRegistrySecret
from mcli.objects.secrets.create.base import SecretCreator, SecretValidationError
from mcli.utils.utils_interactive import secret_prompt, simple_prompt
from mcli.utils.utils_string_validation import validate_email_address, validate_url


class DockerSecretFiller():
    """Interactive filler for docker secret data
    """

    @staticmethod
    def fill_str(prompt: str, default: Optional[str] = None, validate: Optional[Callable[[str], bool]] = None):
        return simple_prompt(prompt, default=default, validate=validate)

    @classmethod
    def fill_username(cls) -> str:
        return cls.fill_str('What is your username?')

    @classmethod
    def fill_password(cls) -> str:
        return secret_prompt('What is your password/API token?')

    @classmethod
    def fill_server(cls, validate: Callable[[str], bool]) -> str:
        return cls.fill_str('What is the URL for this registry?',
                            validate=validate,
                            default='https://index.docker.io/v1/')


class DockerSecretValidator():
    """Validation methods for docker secret data

    Raises:
        SecretValidationError: Raised for any validation error for secret data
    """

    @staticmethod
    def validate_email(email: str) -> bool:
        is_valid_email = validate_email_address(email)
        if not is_valid_email:
            raise SecretValidationError(f'{email} does not appear to be a valid email address.')
        return True

    @staticmethod
    def validate_server(url: str) -> bool:
        is_valid_url = validate_url(url)
        if not is_valid_url:
            raise SecretValidationError(f'{url} does not appear to be a valid URL.')
        return True


class DockerSecretCreator(DockerSecretFiller, DockerSecretValidator):
    """Creates docker secrets for the CLI
    """

    def create(self,
               name: Optional[str] = None,
               username: Optional[str] = None,
               password: Optional[str] = None,
               email: Optional[str] = None,
               server: Optional[str] = None,
               **kwargs) -> MCLIDockerRegistrySecret:
        del kwargs

        if server:
            self.validate_server(server)

        if email:
            self.validate_email(email)

        # Get base secret
        base_creator = SecretCreator()
        secret = base_creator.create(SecretType.docker_registry, name)
        assert isinstance(secret, MCLIDockerRegistrySecret)

        secret.server = server or self.fill_server(self.validate_server)
        secret.username = username or self.fill_username()
        secret.password = password or self.fill_password()
        secret.email = email

        return secret
