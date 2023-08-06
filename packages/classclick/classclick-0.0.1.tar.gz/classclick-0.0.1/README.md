### classclick
Class based approach for writing command line interfaces with Click. 
Made for more modular code structure that is grouped under one script name. 

### Usage

```python
# example_module.py
import click
from classclick import Command, CLI, clickargs, helpers


class Example(Command):
    """Command help, which will be presented in CLI."""

    _example_arg: str = clickargs.CommandArg()  # arg have truncated leading '_' chars
    example_option: str = clickargs.CommandOpt(short_name="-o", default="option")

    def __call__(self):
        """
        The only required method to implement by a command.
        """
        print(f"Arg: {self._example_arg}, option: {self.example_option}")


class Example2(Example):
    """Example docstring"""
    option_3: str = clickargs.CommandArg()

    def __call__(self):
        print(self._example_arg, self.option_3)


def version():
    """Docstring"""
    print("0.0.1")


@click.option("--count", default=1, help="Number")
def hello(count):
    """Hello here!"""
    for _ in range(count):
        click.echo("Hello!")


# script
cli = CLI(title="My first CLI", strict=True)
cli.commands(
    Example, # class based command
    Example2, # works command inheritance
    version, # simple function-based command without args
    hello,  # compatible with native click-decorated functions
    version2=("Print version", helpers.echo("0.0.1")),  # kwargs-based interface, where keyword would be command name,
)                                                       # first element of tuple docstring, second element - function

if __name__ == "__main__":
    cli()
```

Result:
```
Usage: main.py [OPTIONS] COMMAND [ARGS]...

  My first CLI

Options:
  --help  Show this message and exit.

Commands:
  example   Command help, which will be presented in CLI.
  example2  Example docstring
  hello     Hello here!
  version   Docstring
  version2  Print version

```