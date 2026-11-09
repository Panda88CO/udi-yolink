#!/usr/bin/env python3
"""
Unit test suite for Garage Door Controller & Sensor Integration.
Tests udiYoGarageDoor, udiYoGarageFinger, and udiYoDoorSensor.
Covers:
- Driver integrity and command mapping
- Paired door sensor discovery (config, parentDeviceId, heuristic, single sensor)
- State machine transitions (Closed, Open, Opening, Closing, Half-Open, Half-Closed, Unknown)
- 1-pulse vs 3-pulse sequences (open from half-open, close from half-closed)
- Toggle transitions and midway stopping
- Real-time sensor synchronization and external open detection
- Travel timer handling
"""

import sys
import unittest
from unittest.mock import MagicMock, patch, call
import threading
import time

for mod in [
    'dateutil', 'dateutil.tz', 'dateutil.parser',
    'requests', 'paho', 'paho.mqtt', 'paho.mqtt.client'
]:
    if mod not in sys.modules:
        sys.modules[mod] = MagicMock()

if 'udi_interface' not in sys.modules:
    mock_udi = MagicMock()
    class MockNode:
        def __init__(self, polyglot=None, primary=None, address=None, name=None):
            self.poly = polyglot
            self.primary = primary
            self.address = address
            self.name = name
            self.drivers = []
        def setDriver(self, *args, **kwargs):
            pass
        def reportCmd(self, *args, **kwargs):
            pass
        def reportDrivers(self):
            pass
    mock_udi.Node = MockNode
    sys.modules['udi_interface'] = mock_udi

sys.path.insert(0, '.')

from udiYoGarageDoorCtrlV4 import (
    udiYoGarageDoor,
    STATE_CLOSED,
    STATE_OPEN,
    STATE_OPENING,
    STATE_CLOSING,
    STATE_HALF_OPEN,
    STATE_HALF_CLOSED,
    STATE_UNKNOWN,
)
from udiYoGarageFingerCtrlV4 import udiYoGarageFinger
from udiYoDoorSensorV4 import udiYoDoorSensor


class TestGarageDoorDriverIntegrity(unittest.TestCase):
    """Test driver configurations and command maps for Garage Door nodes."""

    def test_garage_door_drivers(self):
        drivers_by_id = {d['driver']: d for d in udiYoGarageDoor.drivers}
        self.assertIn('ST', drivers_by_id)
        self.assertEqual(drivers_by_id['ST']['name'], 'Door State')
        self.assertEqual(drivers_by_id['ST']['uom'], 25)
        self.assertEqual(drivers_by_id['ST']['value'], 99)

        self.assertIn('GV30', drivers_by_id)
        self.assertEqual(drivers_by_id['GV30']['name'], 'Online State')
        self.assertIn('GV20', drivers_by_id)
        self.assertEqual(drivers_by_id['GV20']['name'], 'Connection State')

    def test_garage_finger_drivers(self):
        drivers_by_id = {d['driver']: d for d in udiYoGarageFinger.drivers}
        self.assertIn('ST', drivers_by_id)
        self.assertEqual(drivers_by_id['ST']['name'], 'State')
        self.assertEqual(drivers_by_id['ST']['uom'], 25)
        self.assertEqual(drivers_by_id['ST']['value'], 0)
        self.assertEqual(udiYoGarageFinger.id, 'YOFINGER')

    def test_garage_commands_mapping(self):
        self.assertIn('DON', udiYoGarageDoor.commands)
        self.assertIn('DOF', udiYoGarageDoor.commands)
        self.assertIn('TOGGLE', udiYoGarageDoor.commands)
        self.assertEqual(udiYoGarageDoor.commands['DON'], udiYoGarageDoor.openDoor)
        self.assertEqual(udiYoGarageDoor.commands['DOF'], udiYoGarageDoor.closeDoor)
        self.assertEqual(udiYoGarageDoor.commands['TOGGLE'], udiYoGarageDoor.toggleDoor)


class TestGarageDoorBase(unittest.TestCase):
    """Base helper to instantiate mock garage door controllers and sensors."""

    def setUp(self):
        self.poly = MagicMock()
        self.poly.getValidAddress.side_effect = lambda a: str(a)[:14]
        self.poly.getValidName.side_effect = lambda n: str(n)
        self.node_mock = MagicMock()
        self.poly.getNode.return_value = self.node_mock
        self.poly.getNodes.return_value = {}

    def create_garage_door(self, name='Garage Door', address='garage01', device_id='d88b4c01000001', parent_id=None):
        dev_info = {
            'name': name,
            'deviceId': device_id,
            'type': 'GarageDoor',
            'parentDeviceId': parent_id,
        }
        yo_access = MagicMock()
        with patch.object(udiYoGarageDoor, 'wait_for_node_done', return_value=None), \
             patch.object(udiYoGarageDoor, 'apply_profile_driver_names', return_value=None):
            node = udiYoGarageDoor(self.poly, 'controller', address, name, yo_access, dev_info)
            node.my_setDriver = MagicMock()
            node.yoDoorControl = MagicMock()
            return node

    def create_garage_finger(self, name='Garage Finger', address='finger01', device_id='d88b4c03000001', parent_id=None):
        dev_info = {
            'name': name,
            'deviceId': device_id,
            'type': 'Finger',
            'parentDeviceId': parent_id,
        }
        yo_access = MagicMock()
        with patch.object(udiYoGarageFinger, 'wait_for_node_done', return_value=None), \
             patch.object(udiYoGarageFinger, 'apply_profile_driver_names', return_value=None):
            node = udiYoGarageFinger(self.poly, 'controller', address, name, yo_access, dev_info)
            node.my_setDriver = MagicMock()
            node.yoDoorControl = MagicMock()
            return node

    def create_door_sensor(self, name='Garage Door Sensor', address='sensor01', device_id='d88b4c02000001', parent_id=None):
        dev_info = {
            'name': name,
            'deviceId': device_id,
            'type': 'DoorSensor',
            'parentDeviceId': parent_id,
        }
        yo_access = MagicMock()
        with patch.object(udiYoDoorSensor, 'wait_for_node_done', return_value=None), \
             patch.object(udiYoDoorSensor, 'apply_profile_driver_names', return_value=None), \
             patch.object(udiYoDoorSensor, 'retrieve_cmd_state', return_value=0), \
             patch.object(udiYoDoorSensor, 'save_cmd_state', return_value=None):
            sensor = udiYoDoorSensor(self.poly, 'controller', address, name, yo_access, dev_info)
            sensor.my_setDriver = MagicMock()
            sensor.yoDoorSensor = MagicMock()
            return sensor


class TestGarageDoorSensorDiscovery(TestGarageDoorBase):
    """Test automatic discovery and pairing between Garage Door and Door Sensor."""

    def test_pair_via_controller_parent_id(self):
        controller = self.create_garage_door(parent_id='d88b4c02000001')
        sensor = self.create_door_sensor(device_id='d88b4c02000001')
        sensor.doorState = MagicMock(return_value=0)

        self.poly.getNodes.return_value = {
            controller.address: controller,
            sensor.address: sensor,
        }

        paired = controller.find_paired_sensor()
        self.assertEqual(paired, sensor)
        self.assertEqual(controller.state, STATE_CLOSED)
        controller.my_setDriver.assert_called_with('ST', STATE_CLOSED)

    def test_pair_via_sensor_parent_id(self):
        controller = self.create_garage_door(device_id='d88b4c01000001')
        sensor = self.create_door_sensor(parent_id='d88b4c01000001')
        sensor.doorState = MagicMock(return_value=1)

        self.poly.getNodes.return_value = {
            controller.address: controller,
            sensor.address: sensor,
        }

        paired = controller.find_paired_sensor()
        self.assertEqual(paired, sensor)
        self.assertEqual(controller.state, STATE_OPEN)
        controller.my_setDriver.assert_called_with('ST', STATE_OPEN)

    def test_pair_via_custom_param(self):
        controller = self.create_garage_door()
        sensor = self.create_door_sensor(address='custom_sensor_addr')
        sensor.doorState = MagicMock(return_value=0)

        self.poly.getNodes.return_value = {
            controller.address: controller,
            sensor.address: sensor,
        }

        # Mock custom params returning sensor address
        controller._get_param = MagicMock(side_effect=lambda k, d=None: 'custom_sensor_addr' if 'GARAGE_SENSOR' in k else d)

        paired = controller.find_paired_sensor()
        self.assertEqual(paired, sensor)

    def test_pair_via_name_heuristic(self):
        controller = self.create_garage_door(name='Main Garage Door')
        sensor = self.create_door_sensor(name='Garage Door Contact Sensor')
        sensor.doorState = MagicMock(return_value=0)

        self.poly.getNodes.return_value = {
            controller.address: controller,
            sensor.address: sensor,
        }

        paired = controller.find_paired_sensor()
        self.assertEqual(paired, sensor)

    def test_pair_single_sensor_fallback(self):
        controller = self.create_garage_door(name='Front Door Opener')
        sensor = self.create_door_sensor(name='Side Sensor')
        sensor.doorState = MagicMock(return_value=0)

        self.poly.getNodes.return_value = {
            controller.address: controller,
            sensor.address: sensor,
        }

        paired = controller.find_paired_sensor()
        self.assertEqual(paired, sensor)


class TestGarageDoorStateMachine(TestGarageDoorBase):
    """Test state machine commands, multi-pulse sequences, and transitions."""

    @patch('time.sleep', return_value=None)
    def test_open_from_closed_sends_single_pulse(self, mock_sleep):
        controller = self.create_garage_door()
        controller.state = STATE_CLOSED

        controller.openDoor()
        if controller._pulse_thread:
            controller._pulse_thread.join(timeout=1.0)

        controller.yoDoorControl.toggleDevice.assert_called_once()
        self.assertEqual(controller.state, STATE_OPENING)
        controller.my_setDriver.assert_any_call('ST', STATE_OPENING)
        self.node_mock.reportCmd.assert_called_with('DON')

    @patch('time.sleep', return_value=None)
    def test_open_when_already_open_or_opening_is_ignored(self, mock_sleep):
        controller = self.create_garage_door()
        controller.state = STATE_OPEN

        controller.openDoor()
        self.assertEqual(controller.yoDoorControl.toggleDevice.call_count, 0)

        controller.state = STATE_OPENING
        controller.openDoor()
        self.assertEqual(controller.yoDoorControl.toggleDevice.call_count, 0)

    @patch('time.sleep', return_value=None)
    def test_open_from_half_open_sends_three_pulses(self, mock_sleep):
        controller = self.create_garage_door()
        controller.state = STATE_HALF_OPEN

        controller.openDoor()
        if controller._pulse_thread:
            controller._pulse_thread.join(timeout=1.0)

        self.assertEqual(controller.yoDoorControl.toggleDevice.call_count, 3)
        self.assertEqual(controller.state, STATE_OPENING)
        controller.my_setDriver.assert_any_call('ST', STATE_OPENING)
        self.node_mock.reportCmd.assert_called_with('DON')

    @patch('time.sleep', return_value=None)
    def test_close_from_open_sends_single_pulse(self, mock_sleep):
        controller = self.create_garage_door()
        controller.state = STATE_OPEN

        controller.closeDoor()
        if controller._pulse_thread:
            controller._pulse_thread.join(timeout=1.0)

        controller.yoDoorControl.toggleDevice.assert_called_once()
        self.assertEqual(controller.state, STATE_CLOSING)
        controller.my_setDriver.assert_any_call('ST', STATE_CLOSING)
        self.node_mock.reportCmd.assert_called_with('DOF')

    @patch('time.sleep', return_value=None)
    def test_close_when_already_closed_or_closing_is_ignored(self, mock_sleep):
        controller = self.create_garage_door()
        controller.state = STATE_CLOSED

        controller.closeDoor()
        self.assertEqual(controller.yoDoorControl.toggleDevice.call_count, 0)

        controller.state = STATE_CLOSING
        controller.closeDoor()
        self.assertEqual(controller.yoDoorControl.toggleDevice.call_count, 0)

    @patch('time.sleep', return_value=None)
    def test_close_from_half_closed_sends_three_pulses(self, mock_sleep):
        controller = self.create_garage_door()
        controller.state = STATE_HALF_CLOSED

        controller.closeDoor()
        if controller._pulse_thread:
            controller._pulse_thread.join(timeout=1.0)

        self.assertEqual(controller.yoDoorControl.toggleDevice.call_count, 3)
        self.assertEqual(controller.state, STATE_CLOSING)
        controller.my_setDriver.assert_any_call('ST', STATE_CLOSING)
        self.node_mock.reportCmd.assert_called_with('DOF')

    def test_toggle_transitions_and_stopping(self):
        controller = self.create_garage_door()

        # From Closed -> Toggle -> Opening
        controller.state = STATE_CLOSED
        controller.toggleDoor()
        self.assertEqual(controller.state, STATE_OPENING)
        controller.my_setDriver.assert_called_with('ST', STATE_OPENING)
        self.node_mock.reportCmd.assert_called_with('DON')

        # From Opening -> Toggle -> Half-Open (stopped midway)
        controller.toggleDoor()
        self.assertEqual(controller.state, STATE_HALF_OPEN)
        controller.my_setDriver.assert_called_with('ST', STATE_HALF_OPEN)

        # From Half-Open -> Toggle -> Closing
        controller.toggleDoor()
        self.assertEqual(controller.state, STATE_CLOSING)
        controller.my_setDriver.assert_called_with('ST', STATE_CLOSING)
        self.node_mock.reportCmd.assert_called_with('DOF')

        # From Closing -> Toggle -> Half-Closed (stopped midway)
        controller.toggleDoor()
        self.assertEqual(controller.state, STATE_HALF_CLOSED)
        controller.my_setDriver.assert_called_with('ST', STATE_HALF_CLOSED)

        # From Half-Closed -> Toggle -> Opening
        controller.toggleDoor()
        self.assertEqual(controller.state, STATE_OPENING)
        controller.my_setDriver.assert_called_with('ST', STATE_OPENING)
        self.node_mock.reportCmd.assert_called_with('DON')


class TestGarageDoorSensorCallbacks(TestGarageDoorBase):
    """Test real-time sensor updates communicating with garage door controller."""

    def test_sensor_closed_sets_door_closed_and_reports_dof(self):
        controller = self.create_garage_door()
        controller.state = STATE_CLOSING

        controller.on_sensor_state_change(0)

        self.assertEqual(controller.state, STATE_CLOSED)
        controller.my_setDriver.assert_called_with('ST', STATE_CLOSED)
        self.node_mock.reportCmd.assert_called_with('DOF')

    def test_sensor_opened_from_closed_detects_external_open(self):
        controller = self.create_garage_door()
        controller.state = STATE_CLOSED

        controller.on_sensor_state_change(1)

        self.assertEqual(controller.state, STATE_OPENING)
        controller.my_setDriver.assert_called_with('ST', STATE_OPENING)
        self.node_mock.reportCmd.assert_called_with('DON')

    def test_travel_timer_expiration_opening_to_open(self):
        controller = self.create_garage_door()
        controller.state = STATE_OPENING

        controller._on_travel_timer_expired(STATE_OPEN)

        self.assertEqual(controller.state, STATE_OPEN)
        controller.my_setDriver.assert_called_with('ST', STATE_OPEN)

    def test_travel_timer_expiration_closing_with_sensor_open(self):
        controller = self.create_garage_door()
        controller.state = STATE_CLOSING
        mock_sensor = MagicMock()
        mock_sensor.doorState.return_value = 1  # Sensor is still open!
        controller.paired_sensor = mock_sensor

        controller._on_travel_timer_expired(STATE_CLOSED)

        self.assertEqual(controller.state, STATE_HALF_CLOSED)
        controller.my_setDriver.assert_called_with('ST', STATE_HALF_CLOSED)


class TestDoorSensorCallbackSystem(TestGarageDoorBase):
    """Test callback registration and invocation on udiYoDoorSensor."""

    def test_register_and_notify_callbacks(self):
        sensor = self.create_door_sensor()
        sensor.node = self.node_mock
        sensor.node_ready = True
        sensor.system_ready = True
        sensor.configDone = True

        mock_cb = MagicMock()
        sensor.register_state_callback(mock_cb)

        sensor.yoDoorSensor.check_system_online.return_value = True
        sensor.yoDoorSensor.get_message_type.return_value = ['report']
        sensor.yoDoorSensor.get_report_time.return_value = 1600000000
        sensor.yoDoorSensor.getBattery.return_value = 4
        def mock_get_data(key, group=None):
            if key == 'state':
                return 'closed'
            elif key == 'stateChangedAt':
                return 1600000000000
            return None

        sensor.yoDoorSensor.get_data.side_effect = mock_get_data
        sensor.yoDoorSensor.suspended = False

        sensor.updateData()

        mock_cb.assert_called_with(0)


class TestGarageFingerControl(TestGarageDoorBase):
    """Test udiYoGarageFinger state machine, 3-pulse sequences, and paired sensor integration."""

    @patch('time.sleep', return_value=None)
    def test_finger_open_and_close_from_half_states(self, mock_sleep):
        finger = self.create_garage_finger()

        # Open from Half-Open sends 3 pulses
        finger.state = STATE_HALF_OPEN
        finger.openDoor()
        if finger._pulse_thread:
            finger._pulse_thread.join(timeout=1.0)
        self.assertEqual(finger.yoDoorControl.toggleDevice.call_count, 3)
        self.assertEqual(finger.state, STATE_OPENING)

        finger.yoDoorControl.toggleDevice.reset_mock()

        # Close from Half-Closed sends 3 pulses
        finger.state = STATE_HALF_CLOSED
        finger.closeDoor()
        if finger._pulse_thread:
            finger._pulse_thread.join(timeout=1.0)
        self.assertEqual(finger.yoDoorControl.toggleDevice.call_count, 3)
        self.assertEqual(finger.state, STATE_CLOSING)


class TestGarageDynamicProfileIntegration(TestGarageDoorBase):
    """Test dynamic JSON profile adaptation based on presence of paired door sensors."""

    def test_dynamic_profile_prunes_open_close_when_no_sensor(self):
        import udiDynamicProfile

        mock_controller = MagicMock()
        mock_controller.temp_unit = 0
        mock_controller.water_unit = 0
        mock_controller.poly.getNodes.return_value = {
            'garage1': MagicMock(id='YOGARAGE', paired_sensor=None)
        }
        mock_controller.yolink_nodes = {}
        mock_controller.deviceList = [{'type': 'GarageDoor', 'name': 'Garage'}]

        payload = udiDynamicProfile.get_dynamic_profile_payload(controller=mock_controller)
        garage_nd = next((nd for nd in payload['nodedefs'] if nd.get('id') == 'YOGARAGE'), None)
        self.assertIsNotNone(garage_nd)

        accepted_cmd_ids = [c['id'] for c in garage_nd['cmds']['accepts']]
        self.assertEqual(accepted_cmd_ids, ['TOGGLE'])
        self.assertEqual(garage_nd['cmds']['sends'], [])

        st_prop = next((p for p in garage_nd['properties'] if p.get('id') == 'ST'), None)
        self.assertEqual(st_prop['editor'], 'STATUS')

    def test_dynamic_profile_retains_open_close_when_sensor_paired(self):
        import udiDynamicProfile

        mock_controller = MagicMock()
        mock_controller.temp_unit = 0
        mock_controller.water_unit = 0
        mock_controller.poly.getNodes.return_value = {
            'garage1': MagicMock(id='YOGARAGE', paired_sensor=MagicMock())
        }
        mock_controller.yolink_nodes = {}
        mock_controller.deviceList = [{'type': 'GarageDoor'}, {'type': 'DoorSensor'}]

        payload = udiDynamicProfile.get_dynamic_profile_payload(controller=mock_controller)
        garage_nd = next((nd for nd in payload['nodedefs'] if nd.get('id') == 'YOGARAGE'), None)
        self.assertIsNotNone(garage_nd)

        accepted_cmd_ids = [c['id'] for c in garage_nd['cmds']['accepts']]
        self.assertIn('DON', accepted_cmd_ids)
        self.assertIn('DOF', accepted_cmd_ids)
        self.assertIn('TOGGLE', accepted_cmd_ids)

        st_prop = next((p for p in garage_nd['properties'] if p.get('id') == 'ST'), None)
        self.assertEqual(st_prop['editor'], 'GARAGESTATE')

    def test_yofinger_nodedef_is_toggle_only(self):
        import udiDynamicProfile

        payload = udiDynamicProfile.get_dynamic_profile_payload()
        finger_nd = next((nd for nd in payload['nodedefs'] if nd.get('id') == 'YOFINGER'), None)
        self.assertIsNotNone(finger_nd)

        accepted_cmd_ids = [c['id'] for c in finger_nd['cmds']['accepts']]
        self.assertEqual(accepted_cmd_ids, ['TOGGLE'])
        self.assertEqual(finger_nd['cmds']['sends'], [])


if __name__ == '__main__':
    unittest.main()
