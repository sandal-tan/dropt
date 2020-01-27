"""A simple example of Dr. Opt"""
import sys

from dropt import CLICommand, singleton

@singleton
class MyProgram(CLICommand):
    """This is my excellent program's interface!"""

@MyProgram.command
def echo(a_word: str, reverse: bool = False) -> str:
    """Echo whatever word given.

    Args:
        word: The word to echo

    Returns:
        ``word``

    """
    if reverse:
        return reverse_word(a_word)
    return a_word


@MyProgram.subcommand
class Reverse(CLICommand):
    """Provide commands that reverse their output."""

@Reverse.command(name='word')
def reverse_word(a_word: str) -> str:
    """Echo whatever word given, but in reverse.

    Args:
        a_word: The word to echo in reverse

    Returns:
        ``a_word`` in reverse

    """
    return a_word[-1::-1]

@Reverse.command(name='number')
def reverse_number(a_number: int) -> int:
    return int(reverse_word(str(a_number)))

if __name__ == "__main__":
    MyProgram(*sys.argv[1:])
