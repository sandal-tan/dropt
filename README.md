# Dr. Opt

Dr. Opt is a library for programmatically generating a docopt CLI by defining it's linkage to implementation code.

By leveraging Jinja templates, [docopt](https://github.com/docopt/docopt) is generated via your definitions of the
commands API, linking CLI input to the actual implementation code. This ensures that your CLI documenation is always
kept up to date,  with no additional work specifically on docopt. Dr. Opt also allows for dynamic registration of
nested subcommands, which dynamically update parent documentation to reflect their inclusion.

# Examples

    from dropt import Command, command

    @singleton
    class MyProgram(Command):
        """This is my excellent program's interface!"""

    @MyProgram.command
    def echo(word: str, reverse: bool = False) -> str:
        """Echo whatever word given.

        Args:
            word: The word to echo

        Returns:
            ``word``

        """
        if reverse:
            return reverse_word(word)
        return word


    @MyProgram.register_subcommand
    @signleton
    class Reverse(Command):
        """Provide commands that reverse their output."""

    @Reverse.command(name='word')
    def reverse_word(self, a_word: str) -> str:
        """Echo whatever word given, but in reverse.

        Args:
            a_word: The word to echo in reverse

        Returns:
            ``a_word`` in reverse

        """
        return word[-1::-1]

    @Reverse.command(name='number')
    def reverse_number(a_number: int) -> int:
        return int(reverse_word(str(a_number)))

    MyProgram('-h')
    >>> myprogram
    >>>
    >>> This is my excellent program's interface!
    >>>
    >>> Usage:
    >>>   myprogram echo <word>
    >>>   myprogram <subcommand> <args>
    >>>   myprogram [options]
    >>>
    >>> Options:
    >>>   -h --help           Show this screen.
    >>>   --version           Show the version.
    >>>   --list-subcommands  Show the available subcommands.

    MyProgram('reverse', '-h')
    >>> reverse
    >>>
    >>> Provide commands that reverse their output.
    >>>
    >>> Usage:
    >>>   reverse echo <word>
    >>>   reverse [options]
    >>>
    >>> Options:
    >>>  -h --help  Show this screen.
