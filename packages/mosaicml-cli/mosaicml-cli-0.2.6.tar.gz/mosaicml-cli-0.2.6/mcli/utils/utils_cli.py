"""Utility functions for the CLI and CLI testing"""
import sys
import textwrap
from contextlib import contextmanager
from typing import List, NamedTuple


@contextmanager
def set_argv(args: List[str]):
    """Temporarily override sys.argv

    Args:
        args (List[str]): List of new args
    """
    original_argv = sys.argv
    sys.argv = args
    yield
    sys.argv = original_argv


class CLIExample(NamedTuple):
    example: str
    description: str

    def __str__(self) -> str:
        message = f"""
        # {self.description}
        {self.example}
        """
        return textwrap.dedent(message).strip()


def get_example_text(*examples: CLIExample) -> str:

    message = '\n'.join(f'\n{ex}\n' for ex in examples)
    message = f"""
    Examples:
    {message}
    """

    return textwrap.dedent(message).strip()


def extract_first_examples(*example_lists: List[CLIExample]) -> str:

    message = '\n'.join(f'\n{items[0]}\n' for items in example_lists)
    message = f"""
    Examples:
    {message}
    """

    return textwrap.dedent(message).strip()


class Description(str):
    """Simple string wrapper that formats a description nicely from triple-quote strings

    This can be used for argparse descriptions.
    """

    def __new__(cls, text: str):
        text = textwrap.dedent(text).strip()
        return super().__new__(cls, text)
