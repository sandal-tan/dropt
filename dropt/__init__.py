"""Dr. Opt: programmatic docopt generation."""

import inspect
import sys
from typing import Any, Callable

import docopt
import jinja2

_COMMAND_DOC_TEMPLATE = jinja2.Template(
"""{{ name | lower }}

{{ desc }}

Usage:
{%- for command, args in commands.items() %}
  {{ name | lower }} {{ command }} {{ args }}
{%- endfor %}
{%- for subcommand, args in subcommands.items() %}
  {{ name | lower }} {{ subcommand | replace('_', ' ') }} {{ args }}
{%- endfor %}
  {{ name | lower }} [options]

Options:
    -h --help     Show this screen.
    -v --version  Show the version.
"""
)

def format_signature(sig: inspect.Signature) -> str:
    """Format a function signature as a docopt command.

    Args:
        sig: The signature to format

    Returns:
        The docopt command string

    """

    params = []
    repeatable = False
    for name, param in sig.parameters.items():
        param: inspect.Parameter
        if param.kind is param.VAR_POSITIONAL:
            repeatable = True
        params.append(f'<{name}>{"..." if repeatable else ""}')
    return ' '.join(params)

class OutputHandler:

    def write(self, value: str, level: int):
        raise NotImplementedError(
            f'Subclass `{self.__class__.__name__}` of `OutputHandler` must implement `write`.'
        )

def singleton(cls: Any = None, **kwargs) -> Any:
    """Create an instance of ``cls`` and replace it's definition with an instance.

    Args:
        cls: The class to make a singleton
        kwargs: Keyword argument passed to ``cls.__init__``

    Returns:
        An instance of ``cls``

    Raises:
        RuntimeError: If no input is given

    """

    if cls is None: # Then they must have given us kwargs
        if not kwargs:
            raise RuntimeError('singleton must be called directly with a class or with keyword arugments.')
        def _wrap_class(cls: Any) -> Any:
            return cls(**kwargs)
        return _wrap_class

    return cls()


class CLICommand:
    """A CLICommand is a container for a CLI command's definition, argument parsing, and definition.

    Args:
        output_handler: The output handler to use for the command
        template: The Jinja template to use to render the DocOpt

    """


    def __init__(
        self,
        output_handler: OutputHandler = None,
        template: jinja2.Template = _COMMAND_DOC_TEMPLATE
    ):
        self.output_handler = output_handler
        self.commands = {}
        self.template = template
        self.desc = self.__doc__
        self.subcommands = {}

    def make_docs(self):
        """Render the underlying template with the current definition.

        This updates ``self.__doc__``.

        """
        self.__doc__ = self.template.render(
            name=self.__class__.__name__,
            desc=self.desc,
            commands={
                k.lower(): format_signature(inspect.signature(v)) for k, v in self.commands.items()
            },
            subcommands={
                f'{x}_{k}': format_signature(inspect.signature(v))
                for x, y in self.subcommands.items() for k, v in y.commands.items()
            }
        )

    def __call__(self, *args) -> Any:
        """Call this program.

        Args:
            args: The arguemnts to parse for the program.

        Returns:
            The return of the program execution

        """
        self.make_docs()
        res = docopt.docopt(self.__doc__, args, options_first=True)

        # Commands > Subcommands
        # Commands
        for command_name, command in {**self.commands, **self.subcommands}.items():
            if res.get(command_name, False):
                params = list(inspect.signature(command).parameters.keys())
                return command(*[res.get(f'<{param}>') for param in params])

        self('-h') # Call for help

    def subcommand(self, cls: 'CLICommand' = None, **kwargs) -> 'CLICommand':
        """Add a subcommand for ``self``.

        Args:
            cls: The command class to register as a subclass
            kwargs: Keyword args for adding the subcommand to ``self``

        Returns:
            The registered class

        """
        if cls is None:

            if not kwargs:
                raise RuntimeError()

            def _subcommand(cls: 'CLICommand') -> 'CLICommand':

                name = kwargs.get('name', cls.__class__.__name__.lower())

                cls = singleton(cls, output_handler=self.output_handler)
                self.subcommands[name] = cls
                return cls
            return _subcommand

        cls = singleton(cls, output_handler=self.output_handler)
        self.subcommands[cls.__class__.__name__.lower()] = cls
        return cls

    def command(self, a_command: Callable = None, **kwargs) -> Callable:
        """Add a command for ``self``.

        Args:
            a_command: The command to add to ``self``
            kwargs: Keyword arguments passed to ``a_command``

        Returns:
            ``a_command``

        """

        if a_command is None:

            if not kwargs:
                raise RuntimeError()

            def _command(a_command: Callable) -> Callable:

                name = kwargs.get('name', a_command.__name__.lower())
                self.commands[name] = a_command
                return a_command
            return _command
        self.commands[a_command.__name__.lower()] = a_command
        return a_command
