from typing import Any


class AttrDict(dict):
    """
    An extension of Dict that allows access to its values via attributes where
    the key is the attribute name. In order to accomplish this keys can only
    be of the str type.
    """

    def __init__(self, **kwargs):
        for key in kwargs:
            if not isinstance(key, str):
                raise TypeError("keywords must be strings")
        super().__init__(self, **kwargs)

    def __setitem__(self, __k: str, v: Any) -> None:
        if not isinstance(__k, str):
            raise TypeError("keywords must be strings")
        return super().__setitem__(__k, v)

    def __setattr__(self, __name: str, __value: Any) -> None:
        #self[__name] = __value
        self.__setitem__(__name, __value)

    def __getattr__(self, __name: str) -> None:
        # return self[__name]
        return self.__getitem__(__name)

    def __repr__(self) -> str:
        s = f"{self.__class__.__name__}("
        s += ", ".join(f"{k}={v}" for k, v in self.items())
        s += ")"
        return s
