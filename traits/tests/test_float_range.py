# -----------------------------------------------------------------------------
#
#  Copyright (c) 2019, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in /LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
# -----------------------------------------------------------------------------
"""
Tests for the Range trait with value type float.
"""

import unittest

from traits.api import (
    BaseRange,
    Either,
    HasTraits,
    Instance,
    Range,
    TraitError,
)
from traits.testing.optional_dependencies import numpy, requires_numpy


class Impossible(object):
    """
    Type that never gets instantiated.
    """

    def __init__(self):
        raise TypeError("Cannot instantiate this class")


def ModelFactory(name, RangeFactory):
    """
    Helper function to create various similar model classes.

    Parameters
    ----------
    name : str
        Name to give the created class.
    RangeFactory : callable(*range_args, **range_kwargs) -> TraitType
        Callable with the same signature as Range; this will be used
        to create the model traits.

    Returns
    -------
    HasTraits subclass
        Subclass containing various Range-like traits, for testing.

    """

    class ModelWithRanges(HasTraits):
        """
        Model containing various Range-like traits.
        """

        # Simple floating-point range trait.
        percentage = RangeFactory(0.0, 100.0)

        # Traits that exercise the various possiblities for inclusion
        # or exclusion of the endpoints.
        open_closed = RangeFactory(0.0, 100.0, exclude_low=True)

        closed_open = RangeFactory(0.0, 100.0, exclude_high=True)

        open = RangeFactory(0.0, 100.0, exclude_low=True, exclude_high=True)

        closed = RangeFactory(0.0, 100.0)

        unbounded = RangeFactory()

        unbounded_with_default = RangeFactory(value=50.0)

        # Traits for one-sided intervals
        steam_temperature = RangeFactory(low=100.0)

        ice_temperature = Range(high=0.0)

    ModelWithRanges.__name__ = name

    return ModelWithRanges


# A trait type that has a fast validator but doesn't accept any values.
impossible = Instance(Impossible, allow_none=False)


def RangeCompound(*args, **kwargs):
    """
    Compound trait including a Range.
    """
    return Either(impossible, Range(*args, **kwargs))


def BaseRangeCompound(*args, **kwargs):
    """
    Compound trait including a BaseRange.
    """
    return Either(impossible, BaseRange(*args, **kwargs))


ModelWithRange = ModelFactory("ModelWithRange", RangeFactory=Range)

ModelWithBaseRange = ModelFactory("ModelWithBaseRange", RangeFactory=BaseRange)

ModelWithRangeCompound = ModelFactory(
    "ModelWithRangeCompound", RangeFactory=RangeCompound,
)

ModelWithBaseRangeCompound = ModelFactory(
    "ModelWithBaseRangeCompound", RangeFactory=BaseRangeCompound,
)


class InheritsFromFloat(float):
    """
    Object that's float-like by virtue of inheriting from float.
    """

    pass


class FloatLike(object):
    """
    Object that's float-like by virtue of providing a __float__ method.

    Also participates in comparisons with floats.
    """

    def __init__(self, value):
        self._value = value

    def __float__(self):
        return self._value

    def __le__(self, other):
        return float(self) <= other

    def __lt__(self, other):
        return float(self) < other

    def __ge__(self, other):
        return float(self) >= other

    def __gt__(self, other):
        return float(self) > other

    def __eq__(self, other):
        return float(self) == other

    def __ne__(self, other):
        return float(self) != other


class BadFloatLike(object):
    """
    Object whose __float__ method raises something other than TypeError.
    """

    def __float__(self):
        raise ZeroDivisionError("bogus error")


class CommonRangeTests(object):
    def test_accepts_float(self):
        self.model.percentage = 35.0
        self.assertIs(type(self.model.percentage), float)
        self.assertEqual(self.model.percentage, 35.0)
        with self.assertRaises(TraitError):
            self.model.percentage = -0.5
        with self.assertRaises(TraitError):
            self.model.percentage = 100.5

    def test_accepts_int(self):
        self.model.percentage = 35
        self.assertIs(type(self.model.percentage), float)
        self.assertEqual(self.model.percentage, 35.0)
        with self.assertRaises(TraitError):
            self.model.percentage = -1
        with self.assertRaises(TraitError):
            self.model.percentage = 101

    def test_accepts_bool(self):
        self.model.percentage = False
        self.assertIs(type(self.model.percentage), float)
        self.assertEqual(self.model.percentage, 0.0)

        self.model.percentage = True
        self.assertIs(type(self.model.percentage), float)
        self.assertEqual(self.model.percentage, 1.0)

    def test_rejects_bad_types(self):
        # A selection of things that don't count as float-like.
        non_floats = [
            "not a number",
            "\N{GREEK CAPITAL LETTER SIGMA}",
            b"not a number",
            "3.5",
            "3",
            3 + 4j,
            0j,
            [1],
            (1,),
            [1.2],
            (1.2,),
            None,
        ]

        for non_float in non_floats:
            with self.assertRaises(TraitError):
                self.model.percentage = non_float

    @requires_numpy
    def test_accepts_numpy_types(self):
        numpy_values = [
            numpy.uint8(25),
            numpy.uint16(25),
            numpy.uint32(25),
            numpy.uint64(25),
            numpy.int8(25),
            numpy.int16(25),
            numpy.int32(25),
            numpy.int64(25),
            numpy.float16(25),
            numpy.float32(25),
            numpy.float64(25),
        ]
        for numpy_value in numpy_values:
            self.model.percentage = numpy_value
            self.assertIs(type(self.model.percentage), float)
            self.assertEqual(self.model.percentage, 25.0)

    def test_accepts_float_subclass(self):
        self.model.percentage = InheritsFromFloat(44.0)
        self.assertIs(type(self.model.percentage), float)
        self.assertEqual(self.model.percentage, 44.0)
        with self.assertRaises(TraitError):
            self.model.percentage = InheritsFromFloat(-0.5)
        with self.assertRaises(TraitError):
            self.model.percentage = InheritsFromFloat(100.5)

    def test_accepts_float_like(self):
        self.model.percentage = FloatLike(35.0)
        self.assertIs(type(self.model.percentage), float)
        self.assertEqual(self.model.percentage, 35.0)
        with self.assertRaises(TraitError):
            self.model.percentage = FloatLike(-0.5)
        with self.assertRaises(TraitError):
            self.model.percentage = FloatLike(100.5)

    def test_bad_float_like(self):
        with self.assertRaises(ZeroDivisionError):
            self.model.percentage = BadFloatLike()

    def test_endpoints(self):
        # point within the interior of the range
        self.model.open = self.model.closed = 50.0
        self.model.open_closed = self.model.closed_open = 50.0
        self.assertEqual(self.model.open, 50.0)
        self.assertEqual(self.model.closed, 50.0)
        self.assertEqual(self.model.open_closed, 50.0)
        self.assertEqual(self.model.closed_open, 50.0)

        # low endpoint
        self.model.closed = self.model.closed_open = 0.0
        self.assertEqual(self.model.closed, 0.0)
        self.assertEqual(self.model.closed_open, 0.0)
        with self.assertRaises(TraitError):
            self.model.open = 0.0
        with self.assertRaises(TraitError):
            self.model.open_closed = 0.0

        # high endpoint
        self.model.closed = self.model.open_closed = 100.0
        self.assertEqual(self.model.closed, 100.0)
        self.assertEqual(self.model.open_closed, 100.0)
        with self.assertRaises(TraitError):
            self.model.open = 100.0
        with self.assertRaises(TraitError):
            self.model.closed_open = 100.0

    def test_half_infinite(self):
        ice_temperatures = [-273.15, -273.0, -100.0, -1.0, -0.1, -0.001]
        water_temperatures = [0.001, 0.1, 1.0, 50.0, 99.0, 99.9, 99.999]
        steam_temperatures = [100.001, 100.1, 101.0, 1000.0, 1e100]

        for temperature in steam_temperatures:
            self.model.steam_temperature = temperature
            self.assertEqual(self.model.steam_temperature, temperature)

        for temperature in ice_temperatures + water_temperatures:
            self.model.steam_temperature = 1729.0
            with self.assertRaises(TraitError):
                self.model.steam_temperature = temperature
            self.assertEqual(self.model.steam_temperature, 1729.0)

        for temperature in ice_temperatures:
            self.model.ice_temperature = temperature
            self.assertEqual(self.model.ice_temperature, temperature)

        for temperature in water_temperatures + steam_temperatures:
            self.model.ice_temperature = -1729.0
            with self.assertRaises(TraitError):
                self.model.ice_temperature = temperature
            self.assertEqual(self.model.ice_temperature, -1729.0)

    def test_float_like_limits(self):
        class Model(HasTraits):
            temperature = self.range_factory(
                low=FloatLike(10.0), high=FloatLike(30.0),
            )

        model = Model()
        model.temperature = 15.5
        self.assertIsExactFloat(model.temperature, 15.5)
        model.temperature = FloatLike(25.7)
        self.assertIsExactFloat(model.temperature, 25.7)
        model.temperature = 13
        self.assertIsExactFloat(model.temperature, 13.0)

        # Out-of-range values.
        model.temperature = 27.0

        with self.assertRaises(TraitError):
            model.temperature = 5.0
        self.assertIsExactFloat(model.temperature, 27.0)

        with self.assertRaises(TraitError):
            model.temperature = 35.0
        self.assertIsExactFloat(model.temperature, 27.0)

    def test_unbounded_range_with_default(self):
        # For compound traits, default is None.
        if self.compound:
            self.assertIsNone(self.model.unbounded_with_default)
            return

        self.assertIsExactFloat(self.model.unbounded_with_default, 50.0)

    def test_unbounded_range_no_default(self):
        # For compound traits, default is None.
        if self.compound:
            self.assertIsNone(self.model.unbounded)
            return

        self.assertIsExactFloat(self.model.unbounded, 0.0)

    def assertIsExactFloat(self, actual, expected):
        self.assertIs(type(actual), float)
        self.assertEqual(actual, expected)


class TestFloatRange(CommonRangeTests, unittest.TestCase):
    def setUp(self):
        self.range_factory = Range
        self.model = ModelWithRange()
        self.compound = False


class TestFloatBaseRange(CommonRangeTests, unittest.TestCase):
    def setUp(self):
        self.range_factory = BaseRange
        self.model = ModelWithBaseRange()
        self.compound = False


class TestFloatRangeCompound(CommonRangeTests, unittest.TestCase):
    def setUp(self):
        self.range_factory = RangeCompound
        self.model = ModelWithRangeCompound()
        self.compound = True


class TestFloatBaseRangeCompound(CommonRangeTests, unittest.TestCase):
    def setUp(self):
        self.range_factory = BaseRangeCompound
        self.model = ModelWithBaseRangeCompound()
        self.compound = True


# XXX Move me to a different file?


class TestRange(unittest.TestCase):
    def test_low_or_high_invalid(self):
        with self.assertRaises(TraitError):
            Range(low=None, high=1j)
        with self.assertRaises(TraitError):
            Range(low=[2.3], high=4.5)

    def test_static_integer_like(self):
        int_like = Range(low=None, high=3)
        self.assertAccepts(int_like, 2, 2)
        self.assertRejects(int_like, 2.0)

        int_like = Range(low=0, high=None)
        self.assertAccepts(int_like, 2, 2)
        self.assertRejects(int_like, 2.0)

        int_like = Range(low=0, high=3)
        self.assertAccepts(int_like, 2, 2)
        self.assertRejects(int_like, 2.0)

    def test_static_float_like(self):
        float_like = Range(low=None, high=3.0)
        self.assertAccepts(float_like, 2, 2.0)
        self.assertAccepts(float_like, 2.0, 2.0)

        float_like = Range(low=0.0, high=None)
        self.assertAccepts(float_like, 2, 2.0)
        self.assertAccepts(float_like, 2.0, 2.0)

        float_like = Range(low=0.0, high=3.0)
        self.assertAccepts(float_like, 2, 2.0)
        self.assertAccepts(float_like, 2.0, 2.0)

        # Mixed types for low and high
        float_like = Range(low=0.0, high=3)
        self.assertAccepts(float_like, 2, 2.0)
        self.assertAccepts(float_like, 2.0, 2.0)

        float_like = Range(low=0, high=3.0)
        self.assertAccepts(float_like, 2, 2.0)
        self.assertAccepts(float_like, 2.0, 2.0)

    def assertAccepts(self, trait, value, expected):
        obj = HasTraits()
        new_value = trait.validate(obj, "name", value)
        self.assertIs(type(new_value), type(expected))
        self.assertEqual(new_value, expected)

    def assertRejects(self, trait, value):
        obj = HasTraits()
        with self.assertRaises(TraitError):
            trait.validate(obj, "name", value)
