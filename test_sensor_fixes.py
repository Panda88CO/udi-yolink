#!/usr/bin/env python3
"""
Unit tests for Motion Sensor, Vibration Sensor, Door Sensor, PowerFail Alarm,
Command State Persistence, and Heartbeat fixes.
"""

import sys
import os
import json
import unittest
from unittest.mock import MagicMock, patch

from test_helper import create_test_node, MockPolyglot, MockYoAccess
from udiYoMotionSensorV4 import udiYoMotionSensor
from udiYoVibrationSensorV4 import udiYoVibrationSensor
from udiYoDoorSensorV4 import udiYoDoorSensor
from udiYoPowerFailV4 import udiYoPowerFailSenor
import udiYolinkLib
import udiCommonLib


class TestMotionSensorFixes(unittest.TestCase):
    """Test udiYoMotionSensor command setting logic and alert/normal cycling."""

    def setUp(self):
        with patch.object(udiYoMotionSensor, 'retrieve_cmd_state', return_value=0), \
             patch.object(udiYoMotionSensor, 'save_cmd_state', return_value=None):
            self.node, self.poly, self.yo_access = create_test_node(
                udiYoMotionSensor, dev_type='MotionSensor', name='Motion Sensor'
            )
        self.mock_sensor = MagicMock()
        self.mock_sensor.check_system_online.return_value = True
        self.mock_sensor.get_message_type.return_value = ['event']
        self.mock_sensor.get_report_time.return_value = 1600000000
        self.mock_sensor.suspended = False
        self.mock_sensor.get_data.side_effect = lambda key, *args: {
            'state': 'normal',
            'battery': 3,
            'devTemperature': 21.0
        }.get(key)
        self.node.yoMotionsSensor = self.mock_sensor

    def test_motion_on_only_repeats_don(self):
        """When cmd_state is 1 (DON Only), subsequent motion alerts MUST report DON."""
        self.node.cmd_state = 1
        self.node.last_state = 99

        # 1st motion alert
        self.mock_sensor.get_data.side_effect = lambda key, *args: 'alert' if key == 'state' else 3
        self.node.updateData()
        self.node.node.reportCmd.assert_called_with('DON')
        self.assertEqual(self.node.last_state, 1)

        # Motion clears (normal) -> DOF must NOT be reported, but last_state MUST reset to 0
        self.node.node.reportCmd.reset_mock()
        self.mock_sensor.get_data.side_effect = lambda key, *args: 'normal' if key == 'state' else 3
        self.node.updateData()
        self.node.node.reportCmd.assert_not_called()
        self.assertEqual(self.node.last_state, 0)

        # 2nd motion alert -> DON MUST be reported again
        self.node.node.reportCmd.reset_mock()
        self.mock_sensor.get_data.side_effect = lambda key, *args: 'alert' if key == 'state' else 3
        self.node.updateData()
        self.node.node.reportCmd.assert_called_with('DON')
        self.assertEqual(self.node.last_state, 1)

        # 2nd motion clears
        self.node.node.reportCmd.reset_mock()
        self.mock_sensor.get_data.side_effect = lambda key, *args: 'normal' if key == 'state' else 3
        self.node.updateData()
        self.node.node.reportCmd.assert_not_called()
        self.assertEqual(self.node.last_state, 0)

        # 3rd motion alert -> DON MUST be reported again
        self.node.node.reportCmd.reset_mock()
        self.mock_sensor.get_data.side_effect = lambda key, *args: 'alert' if key == 'state' else 3
        self.node.updateData()
        self.node.node.reportCmd.assert_called_with('DON')

    def test_motion_off_only_repeats_dof(self):
        """When cmd_state is 2 (DOF Only), clearing motion reports DOF repeatedly."""
        self.node.cmd_state = 2
        self.node.last_state = 99

        # Alert -> DON suppressed, last_state becomes 1
        self.mock_sensor.get_data.side_effect = lambda key, *args: 'alert' if key == 'state' else 3
        self.node.updateData()
        self.node.node.reportCmd.assert_not_called()
        self.assertEqual(self.node.last_state, 1)

        # Normal -> DOF reported, last_state becomes 0
        self.mock_sensor.get_data.side_effect = lambda key, *args: 'normal' if key == 'state' else 3
        self.node.updateData()
        self.node.node.reportCmd.assert_called_with('DOF')
        self.assertEqual(self.node.last_state, 0)

        # Cycle 2: Alert -> DON suppressed, Normal -> DOF reported again
        self.node.node.reportCmd.reset_mock()
        self.mock_sensor.get_data.side_effect = lambda key, *args: 'alert' if key == 'state' else 3
        self.node.updateData()
        self.node.node.reportCmd.assert_not_called()
        self.assertEqual(self.node.last_state, 1)

        self.mock_sensor.get_data.side_effect = lambda key, *args: 'normal' if key == 'state' else 3
        self.node.updateData()
        self.node.node.reportCmd.assert_called_with('DOF')
        self.assertEqual(self.node.last_state, 0)


class TestVibrationSensorFixes(unittest.TestCase):
    """Test udiYoVibrationSensor command setting logic and alert/normal cycling."""

    def setUp(self):
        with patch.object(udiYoVibrationSensor, 'retrieve_cmd_state', return_value=0), \
             patch.object(udiYoVibrationSensor, 'save_cmd_state', return_value=None):
            self.node, self.poly, self.yo_access = create_test_node(
                udiYoVibrationSensor, dev_type='VibrationSensor', name='Vibration Sensor'
            )
        self.mock_sensor = MagicMock()
        self.mock_sensor.check_system_online.return_value = True
        self.mock_sensor.get_message_type.return_value = ['event']
        self.mock_sensor.get_report_time.return_value = 1600000000
        self.mock_sensor.suspended = False
        self.mock_sensor.get_data.side_effect = lambda key, *args: {
            'state': 'normal',
            'battery': 3,
            'devTemperature': 'NA'
        }.get(key)
        self.node.yoVibrationSensor = self.mock_sensor

    def test_vibration_on_only_repeats_don(self):
        """When cmd_state is 1 (DON Only), subsequent vibration alerts MUST report DON."""
        self.node.cmd_state = 1
        self.node.last_state = 99

        # 1st vibration alert
        self.mock_sensor.get_data.side_effect = lambda key, *args: 'alert' if key == 'state' else 3
        self.node.updateData()
        self.node.node.reportCmd.assert_called_with('DON')
        self.assertEqual(self.node.last_state, 1)

        # Vibration clears (normal) -> last_state must reset to 0 without DOF
        self.node.node.reportCmd.reset_mock()
        self.mock_sensor.get_data.side_effect = lambda key, *args: 'normal' if key == 'state' else 3
        self.node.updateData()
        self.node.node.reportCmd.assert_not_called()
        self.assertEqual(self.node.last_state, 0)

        # 2nd vibration alert -> DON MUST be reported again
        self.node.node.reportCmd.reset_mock()
        self.mock_sensor.get_data.side_effect = lambda key, *args: 'alert' if key == 'state' else 3
        self.node.updateData()
        self.node.node.reportCmd.assert_called_with('DON')


class TestDoorSensorFixes(unittest.TestCase):
    """Test udiYoDoorSensor state parsing and command reporting."""

    def setUp(self):
        with patch.object(udiYoDoorSensor, 'retrieve_cmd_state', return_value=0), \
             patch.object(udiYoDoorSensor, 'save_cmd_state', return_value=None):
            self.node, self.poly, self.yo_access = create_test_node(
                udiYoDoorSensor, dev_type='DoorSensor', name='Door Sensor'
            )
        self.mock_sensor = MagicMock()
        self.mock_sensor.check_system_online.return_value = True
        self.mock_sensor.get_message_type.return_value = ['event']
        self.mock_sensor.get_report_time.return_value = 1600000000
        self.mock_sensor.getBattery.return_value = 3
        self.mock_sensor.suspended = False
        self.node.yoDoorSensor = self.mock_sensor

    def test_door_state_parser_variations(self):
        """doorState() must recognize closed/open across string case, bool, and int formats."""
        for closed_val in ['closed', 'Closed', 'CLOSED', 'close', '0', 0, False]:
            self.mock_sensor.get_data.return_value = closed_val
            self.assertEqual(self.node.doorState(), 0, f"Failed for closed value: {closed_val}")

        for open_val in ['open', 'Open', 'OPEN', '1', 1, True]:
            self.mock_sensor.get_data.return_value = open_val
            self.assertEqual(self.node.doorState(), 1, f"Failed for open value: {open_val}")

        for invalid_val in [None, 'unknown', 99, {}]:
            self.mock_sensor.get_data.return_value = invalid_val
            self.assertIsNone(self.node.doorState(), f"Failed for invalid value: {invalid_val}")

    def test_door_sensor_cmd_setting_open_only(self):
        """When cmd_state is 1 (Open Only), door open reports DON, close suppresses DOF, and last_state tracks."""
        self.node.cmd_state = 1
        self.node.last_state = 0

        # Open door -> DON reported
        self.mock_sensor.get_data.side_effect = lambda key, *args: 'open' if key == 'state' else 1600000000
        self.node.updateData()
        self.node.node.reportCmd.assert_called_with('DON')
        self.assertEqual(self.node.last_state, 1)

        # Close door -> DOF suppressed, last_state becomes 0
        self.node.node.reportCmd.reset_mock()
        self.mock_sensor.get_data.side_effect = lambda key, *args: 'closed' if key == 'state' else 1600000000
        self.node.updateData()
        self.node.node.reportCmd.assert_not_called()
        self.assertEqual(self.node.last_state, 0)

        # Reopen door -> DON reported again
        self.node.node.reportCmd.reset_mock()
        self.mock_sensor.get_data.side_effect = lambda key, *args: 'open' if key == 'state' else 1600000000
        self.node.updateData()
        self.node.node.reportCmd.assert_called_with('DON')


class TestPowerFailSensorFixes(unittest.TestCase):
    """Test udiYoPowerFailSenor alertType numeric conversion and driver setting."""

    def setUp(self):
        with patch.object(udiYoPowerFailSenor, 'retrieve_cmd_state', return_value=0), \
             patch.object(udiYoPowerFailSenor, 'save_cmd_state', return_value=None):
            self.node, self.poly, self.yo_access = create_test_node(
                udiYoPowerFailSenor, dev_type='PowerFailureAlarm', name='Power Fail Alarm'
            )
        self.mock_sensor = MagicMock()
        self.mock_sensor.check_system_online.return_value = True
        self.mock_sensor.get_message_type.return_value = ['event']
        self.mock_sensor.get_report_time.return_value = 1600000000
        self.mock_sensor.suspended = False
        self.node.yoPowerFail = self.mock_sensor

    def test_alert_type_numeric_mapping(self):
        """alertType string 'remind' or 'alert' must map to numeric 1, 'normal' to 0, unknown to 99."""
        test_cases = [
            ('remind', 1),
            ('alert', 1),
            ('normal', 0),
            (None, 0),
            (0, 0),
            (1, 1),
            ('unexpected', 99)
        ]

        for alert_input, expected_numeric in test_cases:
            def mock_get_data(key, *args):
                if key == 'alertType':
                    return alert_input
                if key == 'state':
                    return 'normal'
                if key == 'battery':
                    return 3
                if key in ['powerSupply', 'mute']:
                    return True
                return None

            self.mock_sensor.get_data.side_effect = mock_get_data
            self.node.node.reset_mock()

            with patch.object(self.node, 'my_setDriver') as mock_my_setDriver:
                self.node.updateData()
                mock_my_setDriver.assert_any_call('GV2', expected_numeric, type='event')

    def test_powerfail_command_emission_and_gv7_update(self):
        """Power Failure Alarm must update GV7 with int(cmd_state) and emit DON/DOF on power alerts."""
        self.node.cmd_state = 1  # DON Only
        self.node.last_state = 0

        # Power failure alert
        self.mock_sensor.get_data.side_effect = lambda key, *args: {
            'state': 'alert',
            'battery': 3,
            'alertType': 'alert',
            'powerSupply': False,
            'mute': False
        }.get(key)

        with patch.object(self.node, 'my_setDriver') as mock_setDriver:
            self.node.updateData()
            self.node.node.reportCmd.assert_called_with('DON')
            mock_setDriver.assert_any_call('GV7', 1)
            self.assertEqual(self.node.last_state, 1)

        # Power restored -> DOF suppressed with cmd_state=1, last_state updated to 0
        self.node.node.reportCmd.reset_mock()
        self.mock_sensor.get_data.side_effect = lambda key, *args: {
            'state': 'normal',
            'battery': 3,
            'alertType': 'normal',
            'powerSupply': True,
            'mute': False
        }.get(key)

        with patch.object(self.node, 'my_setDriver') as mock_setDriver:
            self.node.updateData()
            self.node.node.reportCmd.assert_not_called()
            mock_setDriver.assert_any_call('GV7', 1)
            self.assertEqual(self.node.last_state, 0)


class TestCmdStatePersistenceAndDBFallback(unittest.TestCase):
    """Test retrieve_cmd_state and save_cmd_state fallback sequence."""

    def setUp(self):
        self.test_addr = 'test_cmd_addr'
        self.json_file = f'{self.test_addr}.json'
        if os.path.exists(self.json_file):
            os.remove(self.json_file)

    def tearDown(self):
        if os.path.exists(self.json_file):
            try:
                os.remove(self.json_file)
            except Exception:
                pass

    def test_retrieve_from_local_file(self):
        """When JSON file exists, cmd_state is read from file."""
        with open(self.json_file, 'w') as f:
            json.dump({'cmd_state': 2}, f)

        mock_self = MagicMock()
        mock_self.address = self.test_addr
        res = udiYolinkLib.retrieve_cmd_state(mock_self)
        self.assertEqual(res, 2)

    def test_retrieve_from_customdata_when_file_missing(self):
        """When JSON file is missing, cmd_state falls back to get_node_custom."""
        mock_self = MagicMock()
        mock_self.address = self.test_addr

        with patch('udiYolinkLib.get_node_custom', return_value=1), \
             patch('udiYolinkLib.save_cmd_state'):
            res = udiYolinkLib.retrieve_cmd_state(mock_self)
            self.assertEqual(res, 1)

    def test_retrieve_from_pg3_db_when_file_and_customdata_missing(self):
        """When JSON file and customdata are missing, cmd_state falls back to PG3 DB driver."""
        mock_self = MagicMock()
        mock_self.address = self.test_addr
        mock_self.drivers = [{'driver': 'GV2', 'value': 0, 'uom': 25, 'name': 'Command Setting'}]
        mock_poly = MagicMock()
        mock_poly.db_getNodeDriver.return_value = {'driver': 'GV2', 'value': '1'}
        mock_self.poly = mock_poly

        with patch('udiYolinkLib.get_node_custom', return_value=None), \
             patch('udiYolinkLib.set_node_custom'):
            res = udiYolinkLib.retrieve_cmd_state(mock_self)
            self.assertEqual(res, 1)
            # File should now exist with restored setting
            self.assertTrue(os.path.exists(self.json_file))
            with open(self.json_file, 'r') as f:
                saved = json.load(f)
                self.assertEqual(saved.get('cmd_state'), 1)

    def test_save_cmd_state_writes_both_file_and_customdata(self):
        """save_cmd_state writes both the local file and the customdata store."""
        mock_self = MagicMock()
        mock_self.address = self.test_addr

        with patch('udiYolinkLib.set_node_custom') as mock_set_custom:
            udiYolinkLib.save_cmd_state(mock_self, 1)
            mock_set_custom.assert_called_with(mock_self, 'cmd_state', 1)

        self.assertTrue(os.path.exists(self.json_file))
        with open(self.json_file, 'r') as f:
            data = json.load(f)
            self.assertEqual(data.get('cmd_state'), 1)


from udiYoLeakSensorV4 import udiYoLeakSensor
from udiYoTHsensorV4 import udiYoTHsensor
from udiYoSoilSensorV4 import udiYoSoilSensor
from udiYoCOSmokeSensorV4 import udiYoCOSmokeSensor


class TestLeakSensorFixes(unittest.TestCase):
    """Test udiYoLeakSensor state normalization, command reporting, and timestamp parsing."""

    def setUp(self):
        with patch.object(udiYoLeakSensor, 'retrieve_cmd_state', return_value=0), \
             patch.object(udiYoLeakSensor, 'save_cmd_state', return_value=None):
            self.node, self.poly, self.yo_access = create_test_node(
                udiYoLeakSensor, dev_type='LeakSensor', name='Leak Sensor'
            )
        self.mock_sensor = MagicMock()
        self.mock_sensor.check_system_online.return_value = True
        self.mock_sensor.get_message_type.return_value = ['event']
        self.mock_sensor.get_report_time.return_value = 1600000000
        self.mock_sensor.suspended = False
        self.node.yoLeakSensor = self.mock_sensor

    def test_startup_dry_suppresses_spurious_dof(self):
        """When leak sensor starts up in dry state (last_state=99), DOF must not be emitted."""
        self.node.cmd_state = 0
        self.node.last_state = 99
        self.mock_sensor.get_data.side_effect = lambda key, *args: {
            'state': 'normal',
            'battery': 3,
            'stateChangedAt': 1600000000000,
            'devTemperature': 20.0,
            'beep': 'off',
            'sensorMode': 'WaterLeak',
            'sensitivity': 'Low'
        }.get(key)

        self.node.updateData()
        self.node.node.reportCmd.assert_not_called()
        self.assertEqual(self.node.last_state, 0)

    def test_alert_wet_state_normalization_and_cycling(self):
        """Transitioning from alert to wet while leaking must not repeat DON; clearing to dry reports DOF."""
        self.node.cmd_state = 0
        self.node.last_state = 0

        # Leak detected with 'alert'
        self.mock_sensor.get_data.side_effect = lambda key, *args: {
            'state': 'alert',
            'battery': 3,
            'stateChangedAt': 1600000000000,
            'devTemperature': 20.0,
            'beep': 'off',
            'sensorMode': 'WaterLeak',
            'sensitivity': 'Low'
        }.get(key)
        self.node.updateData()
        self.node.node.reportCmd.assert_called_with('DON')
        self.assertEqual(self.node.last_state, 1)

        # Subsequent packet with 'wet' must not re-emit DON
        self.node.node.reportCmd.reset_mock()
        self.mock_sensor.get_data.side_effect = lambda key, *args: {
            'state': 'wet',
            'battery': 3,
            'stateChangedAt': 1600000000000,
            'devTemperature': 20.0,
            'beep': 'off',
            'sensorMode': 'WaterLeak',
            'sensitivity': 'Low'
        }.get(key)
        self.node.updateData()
        self.node.node.reportCmd.assert_not_called()
        self.assertEqual(self.node.last_state, 1)

        # Leak dries up to 'dry'
        self.mock_sensor.get_data.side_effect = lambda key, *args: {
            'state': 'dry',
            'battery': 3,
            'stateChangedAt': 1600000000000,
            'devTemperature': 20.0,
            'beep': 'off',
            'sensorMode': 'WaterLeak',
            'sensitivity': 'Low'
        }.get(key)
        self.node.updateData()
        self.node.node.reportCmd.assert_called_with('DOF')
        self.assertEqual(self.node.last_state, 0)

    def test_alert_only_command_setting(self):
        """When cmd_state is 1 (Alert Only), DOF is suppressed on clearing, but last_state resets."""
        self.node.cmd_state = 1
        self.node.last_state = 0

        # Alert
        self.mock_sensor.get_data.side_effect = lambda key, *args: {
            'state': 'alert', 'battery': 3, 'stateChangedAt': 1600000000000, 'devTemperature': 20.0,
            'beep': 'off', 'sensorMode': 'WaterLeak', 'sensitivity': 'Low'
        }.get(key)
        self.node.updateData()
        self.node.node.reportCmd.assert_called_with('DON')
        self.assertEqual(self.node.last_state, 1)

        # Clear -> DOF suppressed, last_state becomes 0
        self.node.node.reportCmd.reset_mock()
        self.mock_sensor.get_data.side_effect = lambda key, *args: {
            'state': 'normal', 'battery': 3, 'stateChangedAt': 1600000000000, 'devTemperature': 20.0,
            'beep': 'off', 'sensorMode': 'WaterLeak', 'sensitivity': 'Low'
        }.get(key)
        self.node.updateData()
        self.node.node.reportCmd.assert_not_called()
        self.assertEqual(self.node.last_state, 0)

        # Alert again -> DON emitted again
        self.node.node.reportCmd.reset_mock()
        self.mock_sensor.get_data.side_effect = lambda key, *args: {
            'state': 'alert', 'battery': 3, 'stateChangedAt': 1600000000000, 'devTemperature': 20.0,
            'beep': 'off', 'sensorMode': 'WaterLeak', 'sensitivity': 'Low'
        }.get(key)
        self.node.updateData()
        self.node.node.reportCmd.assert_called_with('DON')


class TestThermalAndSmokeSensorFixes(unittest.TestCase):
    """Test udiYoTHsensor, udiYoSoilSensor, and udiYoCOSmokeSensor driver updates and commands."""

    def test_th_sensor_gv9_persistent_and_command_emission(self):
        """THSensor must always update GV9 (Command Setting) and emit DON/DOF when alarm transitions."""
        with patch.object(udiYoTHsensor, 'retrieve_cmd_state', return_value=1), \
             patch.object(udiYoTHsensor, 'save_cmd_state', return_value=None):
            node, poly, yo_access = create_test_node(
                udiYoTHsensor, dev_type='THSensor', name='Temp Humidity Sensor'
            )
        mock_sensor = MagicMock()
        mock_sensor.check_system_online.return_value = True
        mock_sensor.get_message_type.return_value = ['event']
        mock_sensor.get_report_time.return_value = 1600000000
        mock_sensor.suspended = False
        mock_sensor.getAlarms.return_value = None
        mock_sensor.getLimits.return_value = None
        mock_sensor.bool2Nbr.side_effect = lambda b: 1 if b else 0
        mock_sensor.update_data_24_hours.return_value = (18.0, 26.0, 30.0, 60.0)

        def make_th_getter(alarm_active=False):
            def _th_get(key, group=None, *args):
                if group in ['alarm', 'alarms']:
                    if key == 'highTemp':
                        return alarm_active
                    return False
                if group == 'tempLimit':
                    return 18.0 if key == 'min' else 26.0
                if group == 'humidityLimit':
                    return 30.0 if key == 'min' else 60.0
                if group == 'state':
                    if key == 'temperature':
                        return 35.0 if alarm_active else 22.0
                    if key == 'humidity':
                        return 45.0
                    if key == 'battery':
                        return 3
                return None
            return _th_get

        mock_sensor.get_data.side_effect = make_th_getter(alarm_active=False)
        node.yoTHsensor = mock_sensor
        node.cmd_state = 1
        node.alarm_state = False

        with patch.object(node, 'my_setDriver') as mock_setDriver:
            node.updateData()
            # GV9 must be updated on normal update
            mock_setDriver.assert_any_call('GV9', 1)

        # Alarm occurs
        mock_sensor.get_data.side_effect = make_th_getter(alarm_active=True)
        node.updateData()
        node.node.reportCmd.assert_called_with('DON')
        self.assertTrue(node.alarm_state)

        # Alarm clears -> with cmd_state=1, DOF suppressed, alarm_state reset to False
        node.node.reportCmd.reset_mock()
        mock_sensor.get_data.side_effect = make_th_getter(alarm_active=False)
        node.updateData()
        node.node.reportCmd.assert_not_called()
        self.assertFalse(node.alarm_state)

    def test_soil_sensor_gv9_persistent_and_command_emission(self):
        """SoilSensor must update GV9 on normal poll and emit commands on alert."""
        with patch.object(udiYoSoilSensor, 'retrieve_cmd_state', return_value=0), \
             patch.object(udiYoSoilSensor, 'save_cmd_state', return_value=None):
            node, poly, yo_access = create_test_node(
                udiYoSoilSensor, dev_type='SoilThcSensor', name='Soil Sensor'
            )
        mock_sensor = MagicMock()
        mock_sensor.check_system_online.return_value = True
        mock_sensor.get_message_type.return_value = ['event']
        mock_sensor.get_report_time.return_value = 1600000000
        mock_sensor.suspended = False
        mock_sensor.getAlarms.return_value = None
        mock_sensor.getLimits.return_value = None
        mock_sensor.bool2Nbr.side_effect = lambda b: 1 if b else 0
        mock_sensor.get_data.side_effect = lambda key, *args: {
            'conductivity': 500,
            'lowConductivity': False,
            'highConductivity': False,
            'temperature': 20.0,
            'lowTemp': False,
            'highTemp': False,
            'humidity': 50.0,
            'lowHumidity': False,
            'highHumidity': False,
            'period': False,
            'battery': 3
        }.get(key)
        node.yoSoilSensor = mock_sensor
        node.cmd_state = 0
        node.alarm_state = False

        with patch.object(node, 'my_setDriver') as mock_setDriver:
            node.updateData()
            mock_setDriver.assert_any_call('GV9', 0)

        # Trigger alarm
        mock_sensor.get_data.side_effect = lambda key, *args: {
            'conductivity': 500,
            'lowConductivity': False,
            'highConductivity': False,
            'temperature': 20.0,
            'lowTemp': True,
            'highTemp': False,
            'humidity': 50.0,
            'lowHumidity': False,
            'highHumidity': False,
            'period': False,
            'battery': 3
        }.get(key)
        node.updateData()
        node.node.reportCmd.assert_called_with('DON')

    def test_smoke_co_sensor_command_emission(self):
        """COSmokeSensor emits DON on smoke/CO alert and DOF on normal."""
        with patch.object(udiYoCOSmokeSensor, 'retrieve_cmd_state', return_value=0), \
             patch.object(udiYoCOSmokeSensor, 'save_cmd_state', return_value=None):
            node, poly, yo_access = create_test_node(
                udiYoCOSmokeSensor, dev_type='COSmokeSensor', name='Smoke Sensor'
            )
        mock_sensor = MagicMock()
        mock_sensor.check_system_online.return_value = True
        mock_sensor.get_message_type.return_value = ['event']
        mock_sensor.get_report_time.return_value = 1600000000
        mock_sensor.suspended = False
        mock_sensor.get_data.side_effect = lambda key, *args: {
            'smoke': False,
            'CO': False,
            'high_temp': False,
            'sLowBattery': False,
            'battery': 3,
            'inspect': False,
            'devTemperature': 'NA'
        }.get(key)
        node.yoCOSmokeSensor = mock_sensor
        node.cmd_state = 0
        node.last_alert = False

        # Alert triggered
        mock_sensor.get_data.side_effect = lambda key, *args: {
            'smoke': True,
            'CO': False,
            'high_temp': False,
            'sLowBattery': False,
            'battery': 3,
            'inspect': False,
            'devTemperature': 'NA'
        }.get(key)
        node.updateData()
        node.node.reportCmd.assert_called_with('DON')
        self.assertTrue(node.last_alert)

        # Alert cleared
        node.node.reportCmd.reset_mock()
        mock_sensor.get_data.side_effect = lambda key, *args: {
            'smoke': False,
            'CO': False,
            'high_temp': False,
            'sLowBattery': False,
            'battery': 3,
            'inspect': False,
            'devTemperature': 'NA'
        }.get(key)
        node.updateData()
        node.node.reportCmd.assert_called_with('DOF')
        self.assertFalse(node.last_alert)


class TestHeartbeatFix(unittest.TestCase):
    """Test heartbeat() calls reportCmd('DON') and reportCmd('DOF') without extra parameters."""

    def test_heartbeat_calls_don_dof_without_params(self):
        mock_setup = MagicMock()
        mock_setup.yoAccess.online = True
        mock_setup.hb = 0
        mock_setup.my_setDriver = MagicMock()
        mock_setup.reportCmd = MagicMock()

        # First pulse (hb=0 -> sends DON)
        udiCommonLib.heartbeat(mock_setup)
        mock_setup.reportCmd.assert_called_once_with('DON')
        self.assertEqual(mock_setup.hb, 1)

        # Second pulse (hb=1 -> sends DOF)
        mock_setup.reportCmd.reset_mock()
        udiCommonLib.heartbeat(mock_setup)
        mock_setup.reportCmd.assert_called_once_with('DOF')
        self.assertEqual(mock_setup.hb, 0)


if __name__ == '__main__':
    unittest.main()

