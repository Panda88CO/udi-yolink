#!/usr/bin/env python3
"""
Unit test harness for udiYoSwitch (udiYoSwitchV4.py).
Tests device model initialization, state updates, command processing,
and ghost-trigger protection / press-event deduplication for dual switch models (YS5708/YS5709).
"""

import sys
import unittest
from unittest.mock import MagicMock, patch, call

# Ensure mock dependencies exist if running in an environment without them installed
from datetime import timezone
for mod in [
    'dateutil', 'dateutil.tz', 'dateutil.parser',
    'requests', 'paho', 'paho.mqtt', 'paho.mqtt.client'
]:
    if mod not in sys.modules:
        sys.modules[mod] = MagicMock()
sys.modules['dateutil.tz'].tzlocal = lambda: timezone.utc
sys.modules['dateutil.tz'].tzutc = lambda: timezone.utc

if 'udi_interface' not in sys.modules:
    mock_udi = MagicMock()
    class MockNode:
        def __init__(self, polyglot=None, primary=None, address=None, name=None):
            self.poly = polyglot
            self.primary = primary
            self.address = address
            self.name = name
            self.drivers = [dict(d) for d in getattr(self.__class__, 'drivers', [])]
            self.node = MagicMock()
        def setDriver(self, *args, **kwargs):
            pass
        def reportCmd(self, *args, **kwargs):
            pass
        def reportDrivers(self):
            pass
    mock_udi.Node = MockNode
    sys.modules['udi_interface'] = mock_udi

# Ensure repository root is on sys.path
sys.path.insert(0, '.')
from udiYoSwitchV4 import udiYoSwitch


class TestUdiYoSwitchBase(unittest.TestCase):
    """Base setup helper for udiYoSwitch test cases."""

    def create_switch_node(self, model_name='YS5708-EC', dev_type='Switch', name='TestSwitch', address='test_addr'):
        poly = MagicMock()
        poly.getValidAddress.side_effect = lambda a: str(a)[:14]
        poly.getValidName.side_effect = lambda n: str(n)
        poly.getNode.return_value = MagicMock()

        dev_info = {
            'modelName': model_name,
            'name': name,
            'type': dev_type,
            'deviceId': 'd88b4c01000001'
        }
        dev_access = MagicMock()

        # Prevent wait_for_node_done from blocking during unit tests
        with patch.object(udiYoSwitch, 'wait_for_node_done', return_value=None):
            node = udiYoSwitch(poly, address, address, name, dev_access, dev_info)

        node.node_ready = True
        node.system_ready = True
        node.configDone = True

        # Attach a mock YoLinkSwitch device
        mock_yo_switch = MagicMock()
        mock_yo_switch.check_system_online.return_value = True
        mock_yo_switch.suspended = False
        mock_yo_switch.get_report_time.return_value = 1700000000
        mock_yo_switch.lastUpdate.return_value = 1700000000
        node.yoSwitch = mock_yo_switch

        return node, poly, mock_yo_switch


class TestModelConfiguration(TestUdiYoSwitchBase):
    """Tests model identification and driver configuration."""

    def test_dual_switch_ys5708_configuration(self):
        node, poly, _ = self.create_switch_node(model_name='YS5708')
        self.assertEqual(node.id, 'yoswitch')
        self.assertEqual(node.nbr_keys, 2)
        self.assertEqual(node.max_remote_keys, 8)
        self.assertFalse(node.support_power)
        self.assertFalse(node.support_battery)

    def test_dual_switch_ys5709_battery_configuration(self):
        node, poly, _ = self.create_switch_node(model_name='YS5709')
        self.assertEqual(node.id, 'yoswitchBat')
        self.assertEqual(node.nbr_keys, 2)
        self.assertEqual(node.max_remote_keys, 8)
        self.assertTrue(node.support_battery)
        self.assertFalse(node.support_power)

    def test_power_switch_ys5716_configuration(self):
        node, poly, _ = self.create_switch_node(model_name='YS5716')
        self.assertEqual(node.id, 'yoswitchPwr')
        self.assertEqual(node.nbr_keys, 0)
        self.assertTrue(node.support_power)
        self.assertFalse(node.support_battery)

    def test_standard_switch_configuration(self):
        node, poly, _ = self.create_switch_node(model_name='YS5705')
        self.assertEqual(node.id, 'yoswitch')
        self.assertEqual(node.nbr_keys, 0)
        self.assertFalse(node.support_power)
        self.assertFalse(node.support_battery)


class TestGhostTriggerProtection(TestUdiYoSwitchBase):
    """Tests ghost-trigger prevention, baseline capture, Report filtering, and deduplication for YS5708/YS5709."""

    def setUp(self):
        self.node, self.poly, self.mock_switch = self.create_switch_node(model_name='YS5708')
        # Setup mock child key nodes
        self.mock_key0 = MagicMock()
        self.mock_key1 = MagicMock()
        self.node.keys = {0: self.mock_key0, 1: self.mock_key1}

    def test_startup_baseline_capture_ignores_stale_event(self):
        """Historical event snapshot present at startup must be captured as baseline and ignored."""
        startup_packet = {
            'event': 'Switch.getState',
            'time': 1000,
            'msgid': 'msg_init',
            'data': {
                'event': {'keyMask': 1, 'type': 'Press'},
                'state': 'closed'
            }
        }
        self.node._last_status_packet = startup_packet
        self.node._capture_press_baseline(self.mock_switch)

        self.assertIsNotNone(self.node._last_processed_press_signature)
        self.assertEqual(self.node._last_processed_press_signature, (1000, 'msg_init', 1, 'Press'))

        # When getState or initial update runs, no command should be dispatched
        self.mock_switch.get_message_type.return_value = ('method', 'getState')
        self.mock_switch.get_data.side_effect = lambda *args: 'closed' if args[0] == 'state' else None
        self.node.updateData()

        self.mock_key0.send_command.assert_not_called()
        self.mock_key1.send_command.assert_not_called()

    def test_report_packet_is_ignored(self):
        """Switch.Report heartbeat packets containing event payloads must NEVER dispatch commands."""
        report_packet = {
            'event': 'Switch.Report',
            'time': 2000,
            'msgid': 'msg_report_123',
            'data': {
                'event': {'keyMask': 1, 'type': 'Press'},
                'state': 'closed'
            }
        }
        self.node._last_status_packet = report_packet
        self.mock_switch.get_message_type.return_value = ('event', 'Report')
        self.mock_switch.get_data.side_effect = lambda *args: 'closed' if args[0] == 'state' else None

        self.node.updateData()

        self.mock_key0.send_command.assert_not_called()
        self.mock_key1.send_command.assert_not_called()

    def test_valid_short_press_event_dispatched_and_deduplicated(self):
        """Live Switch.Alert packet triggers send_command and deduplicates repeated calls."""
        alert_packet = {
            'event': 'Switch.Alert',
            'time': 3000,
            'msgid': 'msg_alert_key0',
            'data': {
                'event': {'keyMask': 1, 'type': 'Press'},  # keyMask 1 -> key 0
                'state': 'open'
            }
        }
        self.node._last_status_packet = alert_packet
        self.mock_switch.get_message_type.return_value = ('event', 'Alert')
        self.mock_switch.get_data.side_effect = lambda *args: 'open' if args[0] == 'state' else None

        self.node.updateData()

        # Key 0 receives the short press
        self.mock_key0.send_command.assert_called_once_with('Press')
        self.mock_key1.send_command.assert_not_called()
        self.assertEqual(self.node._last_processed_press_signature, (3000, 'msg_alert_key0', 1, 'Press'))

        # Duplicate delivery / poll should NOT fire again
        self.mock_key0.reset_mock()
        self.node.updateData()
        self.mock_key0.send_command.assert_not_called()

    def test_valid_long_press_on_second_key(self):
        """Live LongPress on key 1 (keyMask=2) triggers key 1 correctly."""
        alert_packet = {
            'event': 'Switch.Alert',
            'time': 4000,
            'msgid': 'msg_alert_key1',
            'data': {
                'event': {'keyMask': 2, 'type': 'LongPress'},  # keyMask 2 -> key 1
                'state': 'open'
            }
        }
        self.node._last_status_packet = alert_packet
        self.mock_switch.get_message_type.return_value = ('event', 'Alert')
        self.mock_switch.get_data.side_effect = lambda *args: 'open' if args[0] == 'state' else None

        self.node.updateData()

        self.mock_key1.send_command.assert_called_once_with('LongPress')
        self.mock_key0.send_command.assert_not_called()
        self.assertEqual(self.node._last_processed_press_signature, (4000, 'msg_alert_key1', 2, 'LongPress'))

    def test_invalid_or_zero_keymask_handled_safely(self):
        """A keyMask of 0 or invalid type should not cause math errors or fire commands."""
        packet = {
            'event': 'Switch.Alert',
            'time': 5000,
            'msgid': 'msg_zero',
            'data': {
                'event': {'keyMask': 0, 'type': 'Press'},
                'state': 'closed'
            }
        }
        self.node._last_status_packet = packet
        self.mock_switch.get_message_type.return_value = ('event', 'Alert')
        self.mock_switch.get_data.side_effect = lambda *args: 'closed' if args[0] == 'state' else None

        self.node.updateData()

        self.mock_key0.send_command.assert_not_called()
        self.mock_key1.send_command.assert_not_called()


class TestStateReporting(TestUdiYoSwitchBase):
    """Tests driver updates and ISY reportCmd on switch state changes."""

    def setUp(self):
        self.node, self.poly, self.mock_switch = self.create_switch_node(model_name='YS5708')
        self.mock_switch.get_message_type.return_value = ('event', 'StatusChange')

    def test_switch_state_transition_reports_command(self):
        """Initial state sets baseline; subsequent state transitions report DON or DOF."""
        # Initial turn on sets baseline (no spurious DON)
        self.mock_switch.get_data.side_effect = lambda *args: 'open' if args[0] == 'state' else None
        self.node.updateData()
        self.assertEqual(self.node._last_reported_state, 'on')
        self.node.node.reportCmd.assert_not_called()

        # Transition to closed (off) reports DOF
        self.mock_switch.get_data.side_effect = lambda *args: 'closed' if args[0] == 'state' else None
        self.node.updateData()
        self.node.node.reportCmd.assert_called_with('DOF')
        self.assertEqual(self.node._last_reported_state, 'off')

        # Duplicate closed state should NOT report DOF again
        self.node.node.reportCmd.reset_mock()
        self.node.updateData()
        self.node.node.reportCmd.assert_not_called()

        # Transition back to open (on) reports DON
        self.mock_switch.get_data.side_effect = lambda *args: 'open' if args[0] == 'state' else None
        self.node.updateData()
        self.node.node.reportCmd.assert_called_with('DON')
        self.assertEqual(self.node._last_reported_state, 'on')

    def test_offline_reporting(self):
        """When device is offline, GV30 is set to 0 and GV20 is set to 2."""
        self.mock_switch.check_system_online.return_value = False
        with patch.object(self.node, 'my_setDriver') as mock_set_driver:
            self.node.updateData()
            mock_set_driver.assert_any_call('GV30', 0)
            mock_set_driver.assert_any_call('GV20', 2)


class TestSwitchCommands(TestUdiYoSwitchBase):
    """Tests ISY control commands dispatching to YoLinkSwitch API."""

    def setUp(self):
        self.node, self.poly, self.mock_switch = self.create_switch_node(model_name='YS5708')

    def test_don_command(self):
        self.node.set_switch_on()
        self.mock_switch.setState.assert_called_once_with('ON')

    def test_dof_command(self):
        self.node.set_switch_off()
        self.mock_switch.setState.assert_called_once_with('OFF')

    def test_switch_control_toggle(self):
        # When currently 'open' (on), toggle (value 2) turns OFF
        self.mock_switch.get_data.side_effect = lambda *args: 'open' if args[0] == 'state' else None
        self.node.switchControl({'value': 2})
        self.mock_switch.setState.assert_called_with('OFF')

        # When currently 'closed' (off), toggle (value 2) turns ON
        self.mock_switch.get_data.side_effect = lambda *args: 'closed' if args[0] == 'state' else None
        self.node.switchControl({'value': 2})
        self.mock_switch.setState.assert_called_with('ON')

    def test_update_command(self):
        self.node.update()
        self.mock_switch.refreshDevice.assert_called_once()


class TestEventDrivenStartup(TestUdiYoSwitchBase):
    """Tests the event-driven node start sequence (Phase 1 optimization)."""

    def test_online_event_set_by_update_status(self):
        """updateStatus signals _online_event upon packet arrival."""
        node, poly, mock_switch = self.create_switch_node(model_name='YS5708')
        self.assertFalse(node._online_event.is_set())

        packet = {
            'event': 'Switch.Report',
            'time': 1000,
            'msgid': 'msg_test',
            'data': {'state': 'closed'}
        }
        node.updateStatus(packet)
        self.assertTrue(node._online_event.is_set())

    @patch('udiYoSwitchV4.YoLinkSwitch')
    @patch('udiYoSwitchV4.udiRemoteKey')
    def test_start_unblocks_immediately_when_online_event_signals(self, mock_key_cls, mock_yoswitch_cls):
        """start() unblocks without sleep delay when _online_event is signaled."""
        node, poly, _ = self.create_switch_node(model_name='YS5708')
        mock_switch_instance = MagicMock()
        mock_yoswitch_cls.return_value = mock_switch_instance

        def simulate_mqtt_response():
            node.updateStatus({'event': 'Switch.Report', 'data': {'state': 'open'}})
        mock_switch_instance.initNode.side_effect = simulate_mqtt_response

        with patch.object(node, 'my_setDriver'):
            node.start()

        mock_switch_instance.initNode.assert_called_once()
        self.assertTrue(node._online_event.is_set())
        mock_switch_instance.get_attributes.assert_called_once()
        self.assertTrue(node.system_ready)

    @patch('udiYoSwitchV4.YoLinkSwitch')
    @patch('udiYoSwitchV4.udiRemoteKey')
    def test_start_handles_timeout_gracefully(self, mock_key_cls, mock_yoswitch_cls):
        """start() proceeds cleanly and marks device offline if _online_event times out."""
        node, poly, _ = self.create_switch_node(model_name='YS5708')
        mock_switch_instance = MagicMock()
        mock_yoswitch_cls.return_value = mock_switch_instance

        with patch.object(node._online_event, 'wait', return_value=False) as mock_wait:
            with patch.object(node, 'my_setDriver') as mock_set_driver:
                node.start()
            mock_wait.assert_called_once_with(timeout=4.0)
            mock_set_driver.assert_any_call('GV30', 0)
            mock_set_driver.assert_any_call('GV20', 2)

        mock_switch_instance.get_attributes.assert_called_once()
        self.assertTrue(node.system_ready)

    def test_yolink_switch_get_attributes_does_not_publish(self):
        """YoLinkSwitch.get_attributes must not burn an API call by publishing empty packets."""
        from yolinkSwitchV3 import YoLinkSwitch
        dev_info = {'modelName': 'YS5708', 'type': 'Switch', 'name': 'TestSwitch', 'deviceId': 'd123', 'token': 'tok123'}
        mock_access = MagicMock()
        switch = YoLinkSwitch(mock_access, dev_info, MagicMock())
        switch.get_attributes()
        mock_access.publish_data.assert_not_called()


class TestTimeDriverValidation(TestUdiYoSwitchBase):
    """Tests TIME driver updates: only valid telemetry updates TIME, error/offline/empty packets are rejected."""

    def setUp(self):
        self.node, self.poly, self.mock_switch = self.create_switch_node(model_name='YS5708')
        self.mock_switch.get_message_type.return_value = ('event', 'Report')

    def test_time_driver_default_is_zero(self):
        """TIME driver must be initialized to 0 at node creation, not host boot time."""
        time_driver = next((item for item in self.node.drivers if item.get('driver') == 'TIME'), None)
        self.assertIsNotNone(time_driver)
        self.assertEqual(time_driver['value'], 0)

    def test_time_driver_not_updated_when_offline(self):
        """When device is offline, TIME driver must NEVER be updated."""
        self.mock_switch.check_system_online.return_value = False
        self.mock_switch.get_report_time.return_value = 1782388800
        with patch.object(self.node, 'my_setDriver') as mock_set_driver:
            self.node.updateData()
            time_calls = [c for c in mock_set_driver.call_args_list if c[0][0] == 'TIME']
            self.assertEqual(len(time_calls), 0)

    def test_time_driver_not_updated_on_error_code(self):
        """When an error packet arrives (e.g. 020401 Busy), TIME must NOT be updated."""
        self.mock_switch.check_system_online.return_value = False
        self.mock_switch.data = {'code': '020401', 'desc': 'Service busy', 'time': 1782388800000}
        self.mock_switch.get_report_time.return_value = None
        with patch.object(self.node, 'my_setDriver') as mock_set_driver:
            self.node.updateData()
            time_calls = [c for c in mock_set_driver.call_args_list if c[0][0] == 'TIME']
            self.assertEqual(len(time_calls), 0)

    def test_time_driver_not_updated_on_empty_data(self):
        """When emptyData is flagged, TIME must NOT be updated."""
        self.mock_switch.check_system_online.return_value = True
        self.mock_switch.data = {'code': '000000', 'emptyData': True}
        self.mock_switch.get_report_time.return_value = None
        with patch.object(self.node, 'my_setDriver') as mock_set_driver:
            self.node.updateData()
            time_calls = [c for c in mock_set_driver.call_args_list if c[0][0] == 'TIME']
            self.assertEqual(len(time_calls), 0)

    def test_time_driver_updated_only_on_valid_telemetry(self):
        """When device is online and valid telemetry with reportAt arrives, TIME is updated."""
        self.mock_switch.check_system_online.return_value = True
        self.mock_switch.data = {'code': '000000', 'data': {'state': 'open', 'reportAt': '2026-06-25T12:00:00.000Z'}}
        self.mock_switch.get_report_time.return_value = 1782388800
        self.mock_switch.get_data.side_effect = lambda *args: 'open' if args[0] == 'state' else None
        with patch.object(self.node, 'my_setDriver') as mock_set_driver:
            self.node.updateData()
            mock_set_driver.assert_any_call('TIME', 1782388800, 151)

    def test_my_set_driver_central_guard_rejects_none_and_non_positive_time(self):
        """my_setDriver central guard must reject None, 0, or negative TIME values."""
        self.node.node.setDriver = MagicMock()
        self.node.my_setDriver('TIME', None, 151)
        self.node.node.setDriver.assert_not_called()
        self.node.my_setDriver('TIME', 0, 151)
        self.node.node.setDriver.assert_not_called()
        self.node.my_setDriver('TIME', -100, 151)
        self.node.node.setDriver.assert_not_called()

        # Valid positive epoch updates successfully
        self.node.my_setDriver('TIME', 1782388800, 151)
        self.node.node.setDriver.assert_called_once_with('TIME', 1782388800, True, False, uom=151)

    def test_yolink_mqtt_class_time_and_online_guards(self):
        """Test yolink_mqtt_classV4 error code handling, check_system_online, and lastUpdate."""
        from yolink_mqtt_classV4 import YoLinkMQTTDevice
        dev = YoLinkMQTTDevice.__new__(YoLinkMQTTDevice)
        dev.type = 'Switch'
        dev.name = 'Test'
        dev.dData = 'data'
        dev.online = True
        dev.messageTime = 'time'
        dev.lastUpd = 'lastUpdTime'
        dev.deviceInfo = {'name': 'Test', 'deviceId': 'd123'}
        dev._lastOfflineLogSig = None
        dev._lastOfflineLogTime = 0
        dev.offlineLogThrottleSec = 300

        # Error code 020401 (busy) -> check_system_online returns False
        dev.data = {'code': '020401', 'desc': 'Service busy', 'time': 1782388800000}
        self.assertFalse(dev.check_system_online())
        self.assertEqual(dev.lastUpdate(), 0)
        self.assertIsNone(dev.get_report_time('reportAt'))

        # Empty data -> check_system_online returns False
        dev.data = {'code': '000000', 'emptyData': True, 'time': 1782388800000}
        self.assertFalse(dev.check_system_online())
        self.assertEqual(dev.lastUpdate(), 0)
        self.assertIsNone(dev.get_report_time('reportAt'))


if __name__ == '__main__':
    unittest.main()

