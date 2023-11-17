"""anotate provides functions, basically decorators
to permit function overloading and arguments typechecking
"""
from inspect import isclass
from typing import Union

class Overload(list):
    """An overload is a list of annotatid functions
    """
    name:str

    def __init__(self, name:str, *functions):
        """def __init__(self, name:str, *functions):
        initializes the Overload with a name and optional initial functions
        """
        self.name = name
        super().__init__(functions)

    def __call__(self, *args, **kw):
        """searches for a function which matches arguments and executes it
        """
        print(self, args, kw)
        for oload in self:
            names = list(oload.__annotations__.keys())
            kw = argstokw(names, args, kw, oload.__kwdefaults__)
            if matchfuction(oload, kw):
                print('find match', args,kw)

                print(
                    (names, args, kw, oload.__kwdefaults__),

                )
                return oload(**argstokw(names, args, kw, oload.__kwdefaults__))

        raise OverloadError(
            f"no overload of {self.name}"
            f" matches types of: {args}, {kw}"
        )

    def __getattr__(self, value:str):
        match value:
            case "__doc__":
                doc = f"{self.name} has overloads"

                for f_overload in self:
                    doc += "\n"+"-"*20
                    doc += f_overload.__doc__
                return doc


Any = Union[list, int, float, object, dict, set, None]


class AnnotationError(ValueError):
    """class AnnotationError(ValueError):
    raisd when annotation type does not matches that of arguments
    """


class OverloadError(ValueError):
    """class OverloadError(ValueError):
    raise when no matching overload for arguments is found
    """


def typematch(value, _type) -> bool:
    """def typematch(value, type) -> bool:
    checks if value: value matches annotation: type
    """
    if _type == Any:

        return True
    if isinstance(_type, (tuple, list, set)):
        for x in _type:
            if x == value:

                return True
    if _type == value:
        return True
    try:
        return isinstance(value, _type)
    except TypeError:
        try:
            return bool(_type(value))
        except TypeError:
            pass
    return False


def argstokw(arg_names, args, kw, defaults={}):
    argkw = {}
    for i, arg in enumerate(args):
        argkw[arg_names[i]] = arg
    # print("arg2kw", argkw, kw, defaults, argkw | kw | defaults)
    return defaults | argkw | kw


def annotati(method=False, _raise=True, **params):
    """def annotati(_raise=True):
    it typechecks arguments based on the function annotations on each call

    import annotati as ann
    @ann.annotati()
    def add(a:int, b:int) -> int:
        return a+b

    can also typecheck a class
    """
    defaults = {}

    for k, v in params.items():
        if k.beginswith("d_"):
            defaults[k[2:]] = v
    def _annotati(func):
        """internal
        """
        if isinstance(func, Overload):
            return func
        nonlocal _raise, method, defaults
        if isclass(func):
            return annotati_class()(func)
        if method and not "self" in func.__annotations__:
            func.__annotations__["self"] = Any
        anno = func.__annotations__

        def _func(*iargs, **ikw):
            """internal
            """
            nonlocal func, method, anno, defaults
            kwargs = argstokw(list(anno.keys()), iargs, ikw, defaults)
            print(kwargs)

            keys = tuple(anno.keys())
            for key, value in kwargs.items():

                annotation = anno[key]
                # print("anno", annotation, "key", key, "value", value)
                if not typematch(value, annotation) and _raise and not key=="self":
                    raise AnnotationError(
                        f"value {value!r} of argument '{key}',"
                        f" does not match annotation {annotation}"
                    )
            ret = func(*iargs, **ikw)
            if not "return" in anno:
                return ret
            if not typematch(ret, anno["return"]) and _raise:
                raise AnnotationError(
                    f"return value {ret!r},"
                    f" does not match annotation {anno['return']}"
                )
            return ret
        _func.__doc__ = func.__doc__
        _func.__annotations__ = func.__annotations__
        return _func
    return _annotati


def overload(name=None, method=False,**params):
    """def overload(name=None):
    creates a new overloads list or append a function to the list 'name',
    default value to function.__module__+function.__qualname__
    >>> from annotati import overload
    >>> @overload()
    ... def devide(a:int|float, b:0) -> None: # division by zero
    ...    raise ZeroDivisionError(f"deviding {a} by {b}")
    ...
    >>> @overload()
    ... def devide(a:int|float, b:int|float) -> int|float:
           # a and b are *int* or *float*
    ...    return a / b
    ...
    >>> @overload()
    ... def devide(a:str, b:str) -> str: # a and b are both *str*
    ...    a, b = float(a), float(b) # convert to *float*
    ...    quotient = a / b # find quotient
    ...    return str(quotient) # convert to *str* and return
    ...
    >>> devide(1, 2)
    0.5
    >>> devide("1", "2")
    '0.5'
    >>> devide(1, 0)
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "C:\\pymodules\\annotati\\__init__.py", line 89, in call
        return oload(*args, **kw)
               ^^^^^^^^^^^^^^^^^^
      File "<stdin>", line 3, in devide
    ZeroDivisionError: deviding 1 by 0
    """

    if isinstance(name, bool):
        method = True
        name = None

    defaults = {}
    for k, v in params.items():
        if k.beginswith("d_"):
            defaults[k[2:]] = v
    def _over(func):
        """internal
        """
        nonlocal defaults, name, method
        if not name:
            name = func.__module__ + "." + func.__qualname__
        else:
            name = "#"+name

        if method:
            func.__annotations__["self"] = Any
        func.__kwdefaults__ = defaults

        if not name in _overloads:
            _overloads[name] = Overload(name)

        call = _overloads[name]

        call.append(func)
        def caller_func(*args, **kw):
            call(*args, **kw)

        caller_func.__doc__ = caller_func.__doc__ or func.__doc__ or ""
        caller_func.__annotations__ |= func.__annotations__
        return caller_func
    return _over


def matchfuction(function, kwargs) -> bool:
    """def matchfuction(function, args, kwargs) -> bool:
    determines if args and kwargs match function's annotations
    """
    anno = function.__annotations__
    keys = sorted(list(anno.keys()))
    if "return" in keys:
        keys.remove("return")


    for key in kwargs:
        if not key in anno:
            break
        annotation = anno[key]
        if not typematch(kwargs[key], annotation):
            break
    else:
        return True
    return False


def annotati_class(methods=True, builtin=True):
    """def annotati_class(bultin=True):
    typechecks values for a class on each assignment

    if builtin is True
    only attributes specified in class annotations are accepted
    other will raise an error
    """
    def _annotati(cls):
        """internal
        """
        nonlocal builtin, methods
        class _cls(cls):
            """internal
            """
            def __getattr__(self, attr):
                match attr:
                    case "__doc__":
                        return super().__doc__
                    case _:
                        return super().__getattr__(attr)
            def __setattr__(self, attr, value):
                if attr in self.__class__.__annotations__:
                    annotation = self.__class__.__annotations__[attr]
                    if not typematch(value, annotation):
                        raise AnnotationError(
                            f"argument {value} for attribute {attr}"
                            f" does not match annotation {annotation}"
                        )
                elif builtin:
                    raise AttributeError(
                        f"object {self} does not have annotation for {attr}"
                    )
                super().__setattr__(attr, value)
        if methods:
            for x in dir(cls):
                try:
                    assert not isclass(f:=getattr(cls, x))
                    setattr(cls, x, annotati(method=True)(f))
                except (AttributeError, AssertionError):
                    pass
        _cls.__doc__ = cls.__doc__
        _cls.__annotations__ = cls.__annotations__
        return _cls
    return _annotati
_overloads = {}












if __name__ == '__main__':
    @annotati()
    class Car:
        year:int

        # __setitem__ =  setattr
        # __getitem__ =  getattr

        @overload(True)
        def __init__(self, year:int) -> None:
            self.year = year
        @overload(True)
        def __init__(self) -> None:
            self.year = 1111
        @overload(True)
        def __init__(self, fall:Any):
            self.year = fall

        def __str__(self) -> str:
            return "year %d" % self.year


    c = Car(23)
    print(c)
