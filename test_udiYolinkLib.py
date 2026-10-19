#!/usr/bin/env python3
"""
Unit test suite for udiYolinkLib (udiYolinkLib.py).
Tests all utility functions, conversion algorithms, unit normalizations,
meter step factor corrections, and driver updates.
"""

import unittest
from unittest.mock import MagicMock, patch
import os
import time

import test_helper
import udiYolinkLib


class TestUdiYolinkLibConversions(unittest.TestCase):
    """Tests for unit conversions (water volume, temp, UOMs)."""

    def test_calculate_water_volume_all_pairs(self):
        calc = lambda vol, vu, tu: udiYolinkLib.calculate_water_volume(None, vol, vu, tu)

        # 0 = Gallon, 1 = CCF, 2 = m^3, 3 = Liter
        # Gallon -> others
        self.assertAlmostEqual(calc(100, 0, 1), 0.133681, places=5)
        self.assertAlmostEqual(calc(1000, 0, 2), 3.78541, places=4)
        self.assertAlmostEqual(calc(10, 0, 3), 37.8541, places=3)
        self.assertEqual(calc(25, 0, 0), 25)

        # CCF -> others
        self.assertAlmostEqual(calc(1, 1, 0), 748.052, places=3)
        self.assertAlmostEqual(calc(1, 1, 2), 2.83168, places=4)
        self.assertAlmostEqual(calc(1, 1, 3), 2831.68, places=2)
        self.assertEqual(calc(25, 1, 1), 25)

        # m^3 -> others
        self.assertAlmostEqual(calc(1, 2, 0), 264.172, places=3)
        self.assertAlmostEqual(calc(1, 2, 1), 0.353147, places=5)
        self.assertAlmostEqual(calc(1, 2, 3), 1000.0, places=1)
        self.assertEqual(calc(25, 2, 2), 25)

        # Liter -> others
        self.assertAlmostEqual(calc(1000, 3, 0), 264.172, places=3)
        self.assertAlmostEqual(calc(1000, 3, 1), 0.353147, places=5)
        self.assertAlmostEqual(calc(1000, 3, 2), 1.0, places=4)
        self.assertEqual(calc(25, 3, 3), 25)

    def test_calculate_water_volume_string_inputs(self):
        calc = lambda vol, vu, tu: udiYolinkLib.calculate_water_volume(None, vol, vu, tu)
        self.assertAlmostEqual(calc('500', 'L', 'G'), 500 * 0.264172, places=3)
        self.assertAlmostEqual(calc('2', 'm3', 'Liter'), 2000.0, places=1)
        self.assertAlmostEqual(calc('10', 'CCF', 'Gallon'), 7480.52, places=2)
        self.assertAlmostEqual(calc('100', 'Gallon', 'CCF'), 0.133681, places=5)

    def test_calculate_water_volume_edge_cases(self):
        calc = lambda vol, vu, tu: udiYolinkLib.calculate_water_volume(None, vol, vu, tu)
        self.assertEqual(calc(None, 0, 3), 0)
        self.assertEqual(calc('invalid', 0, 3), 'invalid')
        self.assertEqual(calc(0, 0, 1), 0.0)

    def test_convert_water_unit(self):
        conv = lambda u: udiYolinkLib.convert_water_unit(None, u)
        # Numbers
        self.assertEqual(conv(0), 0)
        self.assertEqual(conv(1), 1)
        self.assertEqual(conv(2), 2)
        self.assertEqual(conv(3), 3)
        # String representations
        self.assertEqual(conv('G'), 0)
        self.assertEqual(conv('Gallon'), 0)
        self.assertEqual(conv('C'), 1)
        self.assertEqual(conv('CCF'), 1)
        self.assertEqual(conv('M'), 2)
        self.assertEqual(conv('m3'), 2)
        self.assertEqual(conv('L'), 3)
        self.assertEqual(conv('Liter'), 3)
        self.assertEqual(conv('0'), 0)
        self.assertEqual(conv('1'), 1)
        self.assertEqual(conv('2'), 2)
        self.assertEqual(conv('3'), 3)
        # Fallback
        self.assertEqual(conv(None), 0)
        self.assertEqual(conv('unknown'), 0)

    def test_convert_temp_unit(self):
        conv = lambda s: udiYolinkLib.convert_temp_unit(None, s)
        self.assertEqual(conv('Fahrenheit'), 1)
        self.assertEqual(conv('f'), 1)
        self.assertEqual(conv('Kelvin'), 2)
        self.assertEqual(conv('k'), 2)
        self.assertEqual(conv('Celsius'), 0)
        self.assertEqual(conv('c'), 0)
        self.assertEqual(conv('anything_else'), 0)

    def test_water_meter_unit2uom(self):
        uom_fn = lambda u: udiYolinkLib.water_meter_unit2uom(None, u)
        self.assertEqual(uom_fn(0), 69)
        self.assertEqual(uom_fn(1), 6)
        self.assertEqual(uom_fn(2), 8)
        self.assertEqual(uom_fn(3), 35)
        self.assertEqual(uom_fn('0'), 69)
        self.assertEqual(uom_fn('1'), 6)
        self.assertEqual(uom_fn('2'), 8)
        self.assertEqual(uom_fn('3'), 35)
        self.assertEqual(uom_fn('G'), 69)
        self.assertEqual(uom_fn('C'), 6)
        self.assertEqual(uom_fn('M'), 8)
        self.assertEqual(uom_fn('L'), 35)
        self.assertEqual(uom_fn(99), 69)


class TestUdiYolinkLibMeterCorrection(unittest.TestCase):
    """Tests for meter step-factor and correction logic."""

    def test_get_meter_correction_factor_default(self):
        # None device
        self.assertEqual(udiYolinkLib.get_meter_correction_factor(None, None), 1.0)

        # Device without step factor
        mock_ctrl = MagicMock()
        mock_ctrl.get_data.return_value = None
        self.assertEqual(udiYolinkLib.get_meter_correction_factor(None, mock_ctrl), 1.0)

    def test_get_meter_correction_factor_single_channel(self):
        mock_ctrl = MagicMock()
        mock_ctrl.get_data.return_value = 1000
        factor = udiYolinkLib.get_meter_correction_factor(None, mock_ctrl)
        self.assertEqual(factor, 1000.0)

    def test_get_meter_correction_factor_indexed(self):
        mock_ctrl = MagicMock()
        mock_ctrl.get_data.side_effect = lambda key, cat, idx=None: 500 if idx == 1 else 1000
        factor = udiYolinkLib.get_meter_correction_factor(None, mock_ctrl, wm_index=1)
        self.assertEqual(factor, 500.0)

    def test_apply_meter_correction(self):
        # Numeric values
        self.assertEqual(udiYolinkLib.apply_meter_correction(None, 5000, 1000), 5.0)
        self.assertEqual(udiYolinkLib.apply_meter_correction(None, 100, 1.0), 100.0)

        # Zero or invalid factor should default to 1.0
        self.assertEqual(udiYolinkLib.apply_meter_correction(None, 100, 0), 100.0)
        self.assertEqual(udiYolinkLib.apply_meter_correction(None, 100, None), 100.0)

        # Non-numeric passthrough
        self.assertIsNone(udiYolinkLib.apply_meter_correction(None, None, 1000))
        self.assertEqual(udiYolinkLib.apply_meter_correction(None, 'string_val', 1000), 'string_val')


class TestUdiYolinkLibStateHelpers(unittest.TestCase):
    """Tests for bool, state, and schedule conversions."""

    def test_bool2ISY_and_bool2Nbr(self):
        self.assertEqual(udiYolinkLib.bool2ISY(None, True), 1)
        self.assertEqual(udiYolinkLib.bool2ISY(None, False), 0)
        self.assertIsNone(udiYolinkLib.bool2ISY(None, 'not_bool'))

        self.assertEqual(udiYolinkLib.bool2Nbr(None, True), 1)
        self.assertEqual(udiYolinkLib.bool2Nbr(None, False), 0)
        self.assertIsNone(udiYolinkLib.bool2Nbr(None, None))

    def test_state2ISY(self):
        # Open / closed
        self.assertEqual(udiYolinkLib.state2ISY(None, 'open'), 1)
        self.assertEqual(udiYolinkLib.state2ISY(None, 'closed'), 0)
        self.assertEqual(udiYolinkLib.state2ISY(None, 'on'), 1)
        self.assertEqual(udiYolinkLib.state2ISY(None, 'off'), 0)
        self.assertEqual(udiYolinkLib.state2ISY(None, 'normal'), 0)
        self.assertEqual(udiYolinkLib.state2ISY(None, 'alert'), 1)
        self.assertEqual(udiYolinkLib.state2ISY(None, True), 1)
        self.assertEqual(udiYolinkLib.state2ISY(None, False), 0)

    def test_state2Nbr(self):
        self.assertEqual(udiYolinkLib.state2Nbr(None, 'alert'), 1)
        self.assertEqual(udiYolinkLib.state2Nbr(None, 'normal'), 0)
        self.assertIsNone(udiYolinkLib.state2Nbr(None, 'other'))

    def test_mask2key(self):
        self.assertEqual(udiYolinkLib.mask2key(None, 0), 0)
        self.assertEqual(udiYolinkLib.mask2key(None, 1), 0)
        self.assertEqual(udiYolinkLib.mask2key(None, 2), 1)
        self.assertEqual(udiYolinkLib.mask2key(None, 4), 2)
        self.assertEqual(udiYolinkLib.mask2key(None, 8), 3)
        self.assertEqual(udiYolinkLib.mask2key(None, 16), 4)
        self.assertEqual(udiYolinkLib.mask2key(None, 32), 5)
        self.assertEqual(udiYolinkLib.mask2key(None, 64), 6)

    def test_convert_timestr_to_epoch(self):
        # Test standard ISO timestamp parsing
        iso_str = '2026-01-01T12:00:00.000Z'
        epoch = udiYolinkLib.convert_timestr_to_epoch(None, iso_str)
        self.assertGreater(epoch, 1700000000)

        # Invalid string returns 0
        self.assertEqual(udiYolinkLib.convert_timestr_to_epoch(None, 'invalid-date'), 0)


class TestMySetDriver(unittest.TestCase):
    """Tests for my_setDriver driver updates and event handling."""

    def setUp(self):
        self.mock_node_obj = MagicMock()
        self.node = MagicMock()
        self.node.node = self.mock_node_obj
        self.node.address = 'test_addr'
        self.node.drivers = [
            {'driver': 'ST', 'value': 0, 'uom': 25},
            {'driver': 'GV1', 'value': 0, 'uom': 69},
            {'driver': 'GV20', 'value': 0, 'uom': 25},
        ]
        self.node.yoAccess = MagicMock()
        self.node.yoAccess.local = False

    def test_my_setDriver_updates_valid_driver(self):
        udiYolinkLib.my_setDriver(self.node, 'ST', 1)
        self.mock_node_obj.setDriver.assert_called_with('ST', 1, True, False)

    def test_my_setDriver_passes_uom(self):
        udiYolinkLib.my_setDriver(self.node, 'GV1', 123.4, UOM=69)
        self.mock_node_obj.setDriver.assert_called_with('GV1', 123.4, True, False, uom=69)

    def test_my_setDriver_ignores_missing_driver(self):
        udiYolinkLib.my_setDriver(self.node, 'UNKNOWN_DRIVER', 50)
        self.mock_node_obj.setDriver.assert_not_called()

    def test_my_setDriver_preserves_event_on_none_value(self):
        udiYolinkLib.my_setDriver(self.node, 'ST', None, type='event')
        self.mock_node_obj.setDriver.assert_not_called()

    def test_my_setDriver_local_offset_on_gv20(self):
        self.node.yoAccess.local = True
        udiYolinkLib.my_setDriver(self.node, 'GV20', 1)
        # In local mode, value 1 + 3 = 4
        self.mock_node_obj.setDriver.assert_called_with('GV20', 4, True, False)


if __name__ == '__main__':
    unittest.main()
