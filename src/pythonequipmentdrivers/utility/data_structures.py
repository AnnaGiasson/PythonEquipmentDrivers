from typing import Any


class AttrDict(dict):
    """
    AttrDict() -> new empty dictionary
    AttrDict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    AttrDict(iterable) -> new dictionary initialized as if via:
        d = AttrDict()
        for k, v in iterable:
            d[k] = v
    AttrDict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  AttrDict(one=1, two=2)

    An extension of Dict that allows access to its values via attributes where
    the key is the attribute name. In order to accomplish this keys can only
    be of the str type.

    from this with dict:
    datum['eff'] = datum['pout'] * datum['pin']
    to this with AttrDict:
    datum.eff = datum.pout * datum.pin
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not all(isinstance(key, str) for key in self):
            raise TypeError("keys must be strings")

    def __setitem__(self, __k: str, v: Any) -> None:
        if not isinstance(__k, str):
            raise TypeError("keys must be strings")
        return super().__setitem__(__k, v)

    def __setattr__(self, __name: str, __value: Any) -> None:
        # self[__name] = __value
        self.__setitem__(__name, __value)

    def __getattr__(self, __name: str) -> None:
        # return self[__name]
        return self.__getitem__(__name)

    def __repr__(self) -> str:
        s = f"{self.__class__.__name__}("
        s += ", ".join(f"{k}={v}" for k, v in self.items())
        s += ")"
        return s
