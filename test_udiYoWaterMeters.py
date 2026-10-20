#!/usr/bin/env python3
"""
Unit test suite for water meter and sprinkler devices:
- udiYoWaterMeterControllerV4 (udiYoWaterMeterController)
- udiYoWaterMeterOnlyV4 (udiYoWaterMeterOnly)
- udiYoWaterMeterMultiControllerV4 (udiYoWaterMeterMulti, udiYoSubWaterMeter)
- udiYoSprinkler2V4 (udiYoSprinkler2)
"""

import unittest
from unittest.mock import MagicMock, patch, call

import test_helper
from udiYoWaterMeterControllerV4 import udiYoWaterMeterController
from udiYoWaterMeterOnlyV4 import udiYoWaterMeterOnly
from udiYoWaterMeterMultiControllerV4 import udiYoWaterMeterMulti, udiYoSubWaterMeter
from udiYoSprinkler2V4 import udiYoSprinkler2


class TestWaterMeterController(unittest.TestCase):
    """Tests for udiYoWaterMeterController (single meter controller)."""

    def setUp(self):
        self.node, self.poly, self.yo_access = test_helper.create_test_node(
            udiYoWaterMeterController,
            model_name='YS5008',
            dev_type='WaterMeterController',
            temp_unit=1,  # Fahrenheit
            water_unit=0  # Gallons
        )
        self.mock_ctrl = MagicMock()
        self.mock_ctrl.check_system_online.return_value = True
        self.mock_ctrl.emptyData.return_value = False
        self.mock_ctrl.get_message_type.return_value = ('Report', 'report')
        self.mock_ctrl.get_report_time.return_value = 1700000000
        self.mock_ctrl.getMeterUnit.return_value = 3  # Hardware reports in Liters
        self.mock_ctrl.get_data.side_effect = self._mock_get_data
        self.mock_ctrl.getWaterTemperature.return_value = 20.0  # 20 C = 68 F
        self.mock_ctrl.getAlarms.return_value = {}
        self.mock_ctrl.getBattery.return_value = ('Battery', 95)
        self.node.yoWaterCtrl = self.mock_ctrl

    def _mock_get_data(self, key, cat=None, idx=None):
        if key == 'meter' and cat == 'state':
            return 3785.41  # 3785.41 Liters = 1000 Gallons
        if key == 'amount' and cat == 'dailyUsage':
            return 378.541  # 378.541 Liters = 100 Gallons
        if key == 'amount' and cat == 'recentUsage':
            return 37.8541  # 37.8541 Liters = 10 Gallons
        if key == 'duration' and cat == 'recentUsage':
            return 15
        if key == 'valve' and cat == 'state':
            return 'open'
        if key == 'waterTemperature' and cat == 'state':
            return 20.0  # 20 C = 68 F
        if key == 'waterFlowing' and cat == 'state':
            return True
        if key == 'meterStepFactor':
            return 1.0
        return None

    def test_initialization_drivers_and_uoms(self):
        self.assertEqual(self.node.id, 'YOWATERMETERCTRL')
        self.assertEqual(self.node.temp_unit, 1)
        self.assertEqual(self.node.water_unit, 0)
        # Check that drivers have been assigned display names and default UOMs
        driver_map = {d['driver']: d for d in self.node.drivers}
        self.assertIn('ST', driver_map)
        self.assertIn('GV1', driver_map)
        self.assertEqual(driver_map['GV1']['uom'], 25)

    def test_update_data_volume_conversions_gallons(self):
        self.node.meter_unit = 3  # Device measures in Liters
        self.node.ISYwater_unit = 0  # User wants Gallons
        self.node.ISYmeter_uom = 69
        self.node.updateData()

        # Check total meter: 3785.41 Liters * 0.264172 = 1000.0 Gallons
        self.node.node.setDriver.assert_any_call('GV1', 1000.0, True, False, uom=69)
        # Daily usage: 378.541 Liters * 0.264172 = 100.0 Gallons
        self.node.node.setDriver.assert_any_call('GV10', 100.0, True, False, uom=69)
        # Recent usage: 37.8541 Liters * 0.264172 = 10.0 Gallons
        self.node.node.setDriver.assert_any_call('GV2', 10.0, True, False, uom=69)
        # Temperature in Fahrenheit: 20 C * 9/5 + 32 = 68.0 F
        self.node.node.setDriver.assert_any_call('CLITEMP', 68.0, True, False, uom=17)

    def test_update_data_volume_conversions_cubic_meters(self):
        self.node.meter_unit = 3  # Device measures in Liters
        self.node.ISYwater_unit = 2  # User wants m^3
        self.node.ISYmeter_uom = 8
        self.node.updateData()

        # Total meter: 3785.41 Liters * 0.001 = 3.8 m^3
        self.node.node.setDriver.assert_any_call('GV1', 3.8, True, False, uom=8)

    def test_set_attributes_leak_limit_and_overrun_limit(self):
        # Setting 100 Gallons leak limit (uom69) on a meter with water_unit = 0
        cmd = {
            'cmd': 'SETATTRIB',
            'query': {
                'LLIMIT.uom69': '100.0',
                'LOFF.uom25': '1',
                'ORLIMIT.uom69': '50.0'
            }
        }
        self.node.water_unit = 0
        self.node.set_attributes(cmd)

        self.mock_ctrl.setAttributes.assert_called_once()
        payload = self.mock_ctrl.setAttributes.call_args[0][0]
        self.assertIn('attributes', payload)
        self.assertEqual(payload['attributes']['leakLimit'], 100.0)
        self.assertTrue(payload['attributes']['autoCloseValve'])
        self.assertEqual(payload['attributes']['overrunAmount'], 50.0)


class TestWaterMeterOnly(unittest.TestCase):
    """Tests for udiYoWaterMeterOnly (meter without valve)."""

    def setUp(self):
        self.node, self.poly, self.yo_access = test_helper.create_test_node(
            udiYoWaterMeterOnly,
            model_name='YS5007',
            dev_type='WaterMeterOnly',
            temp_unit=0,  # Celsius
            water_unit=3  # Liters
        )
        self.mock_ctrl = MagicMock()
        self.mock_ctrl.check_system_online.return_value = True
        self.mock_ctrl.emptyData.return_value = False
        self.mock_ctrl.get_message_type.return_value = ('Report', 'report')
        self.mock_ctrl.get_report_time.return_value = 1700000000
        self.mock_ctrl.getMeterUnit.return_value = 3
        self.mock_ctrl.getWaterTemperature.return_value = 18.5
        self.mock_ctrl.getAlarms.return_value = {}
        self.mock_ctrl.getBattery.return_value = ('Battery', 90)
        self.mock_ctrl.get_data.side_effect = lambda key, cat=None: (
            5000 if key == 'meter' and cat == 'state' else
            500 if key == 'amount' and cat == 'dailyUsage' else
            50 if key == 'amount' and cat == 'recentUsage' else
            10 if key == 'duration' and cat == 'recentUsage' else
            False if key == 'waterFlowing' else None
        )
        self.node.yoWaterCtrl = self.mock_ctrl

    def test_update_data_celsius_and_liters(self):
        self.node.meter_unit = 3
        self.node.ISYwater_unit = 3
        self.node.ISYmeter_uom = 35
        self.node.updateData()

        # In Liters (same unit): 5000.0 Liters
        self.node.node.setDriver.assert_any_call('GV1', 5000.0, True, False, uom=35)
        # Daily: 500.0 Liters
        self.node.node.setDriver.assert_any_call('GV10', 500.0, True, False, uom=35)
        # Temperature in Celsius: 18.5 C
        self.node.node.setDriver.assert_any_call('CLITEMP', 18.5, True, False, uom=4)

    def test_set_attributes_converts_limit_from_other_units(self):
        # User entered 1 CCF (uom6) when water_unit is 3 (Liters)
        cmd = {
            'cmd': 'SETATTRIB',
            'query': {
                'LLIMIT.uom6': '1.0'
            }
        }
        self.node.water_unit = 3  # Liters
        self.node.set_attributes(cmd)

        self.mock_ctrl.setAttributes.assert_called_once()
        payload = self.mock_ctrl.setAttributes.call_args[0][0]
        # 1 CCF = 2831.68 Liters
        self.assertAlmostEqual(payload['attributes']['leakLimit'], 2831.68, places=1)


class TestWaterMeterMultiController(unittest.TestCase):
    """Tests for multi-channel water meters."""

    def test_sub_water_meter_channel_data(self):
        poly = test_helper.MockPolyglot()
        yo_access = test_helper.MockYoAccess(water_unit=0)
        mock_ctrl = MagicMock()
        mock_ctrl.check_system_online.return_value = True
        mock_ctrl.emptyData.return_value = False
        mock_ctrl.get_message_type.return_value = ('Report', 'report')
        mock_ctrl.getMeterUnit.return_value = 3
        mock_ctrl.get_data.side_effect = lambda key, cat=None, idx=None: (
            'open' if key == 'valves' and idx == 0 else
            1000.0 if key == 'meters' and idx == 0 else
            100.0 if key == 'amount' and cat == 'dailyUsage' and idx == 0 else
            True if key == 'waterFlowing' and idx == 0 else None
        )

        with patch.object(udiYoSubWaterMeter, 'wait_for_node_done', return_value=None):
            sub_node = udiYoSubWaterMeter(
                poly, 'primary_addr', 'sub_addr_0', 'Meter CH1', 0, yo_access, mock_ctrl
            )
        sub_node.sub_node_ready = True
        sub_node.system_ready = True
        sub_node.configDone = True
        sub_node.node = MagicMock()
        sub_node.meter_unit = 3
        sub_node.ISYwater_unit = 0
        sub_node.ISYmeter_uom = 69

        sub_node.updateData()
        # 1000 Liters * 0.264172 = 264.2 Gallons (total meter)
        sub_node.node.setDriver.assert_any_call('GV10', 264.2, True, False, uom=69)


class TestSprinkler2(unittest.TestCase):
    """Tests for udiYoSprinkler2."""

    def setUp(self):
        self.node, self.poly, self.yo_access = test_helper.create_test_node(
            udiYoSprinkler2,
            model_name='YS5006',
            dev_type='SprinklerV2',
            temp_unit=1,
            water_unit=0  # Gallons
        )
        self.mock_sprinkler = MagicMock()
        self.mock_sprinkler.check_system_online.return_value = True
        self.mock_sprinkler.emptyData.return_value = False
        self.mock_sprinkler.get_message_type.return_value = ('Report', 'report')
        self.mock_sprinkler.get_report_time.return_value = 1700000000
        self.node.yoSprinkler = self.mock_sprinkler
        self.node.step_factor = 1.0
        self.node.meter_unit = 3  # Liters
        self.node.ISYwater_unit = 0  # Gallons
        self.node.ISYmeter_uom = 69

    def test_update_data_amount_event(self):
        self.mock_sprinkler.get_data.side_effect = lambda key, cat=None: (
            {'events': ['WaterDone'], 'data': {'water': {'type': 'amount', 'value': 100.0}}}
            if key == 'metadata' else
            'amount' if key == 'type' and cat == 'water' else
            100.0 if key == 'value' and cat == 'water' else
            False if key == 'running' else
            False if key == 'noWaterWhenRunning' else None
        )

        self.node.updateData()
        # 100 Liters * 0.264172 = 26.4 Gallons
        self.node.node.setDriver.assert_any_call('GV8', 26.4, True, False, uom=69)


if __name__ == '__main__':
    unittest.main()
