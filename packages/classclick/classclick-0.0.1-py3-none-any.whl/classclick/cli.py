import inspect

import click

from classclick.command import Command


class CLI:
    """
    cli = CLI(main_command=main)
    cli.commands(CertificateGenerator)
    """
    def __init__(self, common_options=None, title="", strict=False):
        def group():
            pass
        self.common_options = common_options or ()
        self.main = click.group(help=title)(group)
        self._strict = strict

    def commands(self, *cmds, **kwargs):
        for command in cmds:
            self.command(command)
        for func_name, (doc, func) in kwargs.items():
            self.command(func, name=func_name, doc=doc)
        return self

    def command(self, cmd, name=None, doc=None):
        def reg(**kwargs):
            cmd(**kwargs)()
        reg = reg if inspect.isclass(cmd) and issubclass(cmd, Command) else cmd
        reg.__name__ = name or getattr(cmd, 'NAME', '') or cmd.__name__.lower()
        reg.__doc__ = doc or cmd.__doc__ or Command.__doc__

        if self._strict and (not reg.__doc__ or reg.__doc__ == Command.__doc__):
            raise RuntimeError(f"Docs missing for command: '{reg.__name__}', while running in strict mode")

        for arg in getattr(cmd, '_Command__click_arg_types', []):
            reg = arg(reg)

        for option in self.common_options:
            reg = option(reg)

        self.main.command(help=reg.__doc__.strip())(reg)
        return self

    def __call__(self):
        return self.main()
