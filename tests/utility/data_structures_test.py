import unittest
from pythonequipmentdrivers.utility import AttrDict


class TestAttrDict(unittest.TestCase):
    def test_creation(self):
        d = AttrDict(a=1, b=2)
        self.assertDictEqual(d, {"a": 1, "b": 2})

    def test_getitem(self):
        d = AttrDict(a=1, b=2)
        self.assertEqual(1, d["a"])

    def test_setitem(self):
        d = AttrDict(a=1, b=2)
        d["c"] = 3
        self.assertDictEqual(d, {"a": 1, "b": 2, "c": 3})

    def test_getattr(self):
        d = AttrDict(a=1, b=2)
        self.assertEqual(1, d.a)

    def test_setattr(self):
        d = AttrDict(a=1, b=2)
        d.c = 3
        self.assertDictEqual(d, {"a": 1, "b": 2, "c": 3})

    def test_invalid_setitem(self):
        d = AttrDict(a=1, b=2)
        with self.assertRaises(TypeError):
            d[1] = 3

    def test_invalid_creation(self):
        with self.assertRaises(TypeError):
            d = AttrDict(**{"a": 1, "b": 2, 3: 3})

    def test_repr(self):
        d = AttrDict(a=1, b=2)
        self.assertEqual(repr(d), "AttrDict(a=1, b=2)")

    def test_str(self):
        d = AttrDict(a=1, b=2)
        self.assertEqual(str(d), "AttrDict(a=1, b=2)")
