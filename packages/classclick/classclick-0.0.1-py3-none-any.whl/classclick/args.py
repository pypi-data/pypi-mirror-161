import click


class CommandType:
    def __init__(self, click_type, *args, **kwargs):
        self.click_type = click_type
        self.args = args
        self.kwargs = kwargs
        self.name = None

    def __set_name__(self, owner, name):
        self.name = name.lstrip("_")

    def __get__(self, obj, objtype=None):
        return obj._click_kwargs[self.name]

    def to_click_type(self, name):
        raise NotImplementedError


class CommandArg(CommandType):
    def __init__(self, *args, **kwargs):
        super().__init__(click_type=click.argument, *args, **kwargs)

    def to_click_type(self, name):
        return self.click_type(name.lstrip("_"), *self.args, **self.kwargs)



class CommandOpt(CommandType):
    def __init__(self, *args, **kwargs):
        super().__init__(click_type=click.option, *args, **kwargs)

    def to_click_type(self, name):
        short_name = self.kwargs.pop('short_name', None)
        if short_name is not None:
            self.args = [short_name] + list(self.args)
        name = f"--{name.lstrip('_').replace('_', '-')}"
        return self.click_type(name, *self.args, **self.kwargs)
