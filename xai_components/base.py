from argparse import Namespace
from typing import TypeVar, Generic, Tuple, NamedTuple, Callable, List

T = TypeVar('T')

class InArg(Generic[T]):
    def __init__(self, value: T = None, getter: Callable[[T], any] = lambda x: x) -> None:
        self._value = value
        self._getter = getter

    @property
    def value(self):
        return self._getter(self._value)

    @value.setter
    def value(self, value: T):
        self._value = value

class OutArg(Generic[T]):
    def __init__(self, value: T = None, *args, **kwargs) -> None:
        self.value = value

class InCompArg(Generic[T]):
    def __init__(self, value: T = None, *args, **kwargs) -> None:
        self.value = value

def xai_component(*args, **kwargs):
    # Passthrough element without any changes.
    # This is used for parser metadata only.
    if len(args) == 1 and callable(args[0]):
        # @xai_components form
        return args[0]
    else:
        # @xai_components(...) form
        def passthrough(f):
            return f
        return passthrough

class ExecutionContext:
    args: Namespace

    def __init__(self, args: Namespace):
        self.args = args

class BaseComponent:
    def __init__(self):
        all_ports = self.__annotations__
        for key, type_arg in all_ports.items():
            port_class = type_arg.__origin__
            port_type = type_arg.__args__[0]
            if port_class in (InArg, InCompArg, OutArg):
                if hasattr(port_type, 'initial_value'):
                    port_value = port_type.initial_value()
                else:
                    port_value = None

                if hasattr(port_type, 'getter'):
                    port_getter = port_type.getter
                else:
                    port_getter = lambda x: x
                setattr(self, key, port_class(port_value, port_getter))
            else:
                setattr(self, key, None)

    @classmethod
    def set_execution_context(cls, context: ExecutionContext) -> None:
        cls.execution_context = context

    def execute(self, ctx) -> None:
        pass

    def do(self, ctx) -> Tuple[bool, 'BaseComponent']:
        pass

class Component(BaseComponent):
    next: BaseComponent

    def do(self, ctx) -> Tuple[bool, BaseComponent]:
        print(f"\nExecuting: {self.__class__.__name__}")
        self.execute(ctx)

        return self.next

    def debug_repr(self) -> str:
        return "<h1>Component</h1>"


class SubGraphExecutor:
    
    def __init__(self, component):
        self.comp = component
        
    def do(self, ctx):
        comp = self.comp
        
        while comp is not None:
            comp = comp.do(ctx)
        return None


def execute_graph(args: Namespace, start: BaseComponent, ctx) -> None:
    BaseComponent.set_execution_context(ExecutionContext(args))

    if 'debug' in args and args['debug']:
        import pdb
        pdb.set_trace()

        current_component = start
        next_component = current_component.do(ctx)
        while next_component:
            current_component = next_component
            next_component = current_component.do(ctx)
    else:
        next_component = start.do(ctx)
        while next_component:
            next_component = next_component.do(ctx)
            

class secret:

    def __init__(self, value):
        self.__value = value

    def get_value(self):
        return self.__value
    
class message(NamedTuple):
    role: str
    content: str

class chat(NamedTuple):
    messages: List[message]
    
class dynalist:
    @staticmethod
    def initial_value():
        return []

    @staticmethod
    def getter(x):
        return [item.value if isinstance(item, (InArg, OutArg)) else item for item in x]

class dynatuple:
    def __init__(self, value):
        self.value = value

    @staticmethod
    def initial_value():
        return tuple()

    @staticmethod
    def getter(x):
        def resolve(item):
            if isinstance(item, (InArg, OutArg)):
                return item.value
            elif isinstance(item, str):
                return item
            else:
                return item

        return tuple(resolve(item) for item in x)
    
class dynadict:
    def __init__(self, value):
        self.value = value

    @staticmethod
    def initial_value():
        return {}

    @staticmethod
    def getter(x):
        # Check for InArg and OutArg instances in the dictionary and extract their values
        return {key: (val.value if isinstance(val, (InArg, OutArg)) else val) for key, val in x.items()}