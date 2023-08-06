from .args import CommandType


class CommandMeta(type):
    def __new__(mcs, clsname, bases, attrs):
        inherited_args = tuple((
            click_arg
            for cls in bases if issubclass(cls, Command)
            for click_arg in cls.get_click_args()
        ))
        attrs['_Command__click_arg_types'] = tuple((
            obj.to_click_type(attr)
            for attr, obj in attrs.items()
            if isinstance(obj, CommandType)
        )) + inherited_args

        docs = attrs.get('__doc__', '')
        attrs['__doc__'] = docs or bases[0].__doc__
        attrs['_Command__has_own_docs'] = bool(docs)

        return super().__new__(mcs, clsname, bases, attrs)


class Command(metaclass=CommandMeta):
    """
    Undocumented subcommand.
    """
    NAME = None
    __click_arg_types = ()
    __has_own_docs = False

    def __init__(self, **kwargs):
        self._click_kwargs = kwargs

    @classmethod
    def get_click_args(cls) -> tuple:
        return cls.__click_arg_types

    @classmethod
    def has_docs(cls) -> bool:
        return cls.__has_own_docs

    def __call__(self) -> None:
        raise NotImplementedError
