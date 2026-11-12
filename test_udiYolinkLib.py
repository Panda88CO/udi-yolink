#!/usr/bin/env python3
"""
Unit test suite for udiYolinkLib (udiYolinkLib.py).
Tests all utility functions, conversion algorithms, unit normalizations,
meter step factor corrections, and driver updates.
"""

import unittest
from unittest.mock import MagicMock, patch
import os
import sys
import threading
import queue
import time
import tempfile
import xml.etree.ElementTree as ET

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


class TestUdiTssProfileUpdate(unittest.TestCase):
    """Tests for udiTssProfileUpdate handling of MESSAGES editor in editors.xml and en_us.txt."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.orig_cwd = os.getcwd()
        os.chdir(self.temp_dir.name)

        os.makedirs('profile/editor', exist_ok=True)
        os.makedirs('profile/nls', exist_ok=True)

        editors_xml_content = (
            '<editors>\n'
            '  <editor id="STATUS">\n'
            '    <range uom="25" subset="0,1" nls="status" />\n'
            '  </editor>\n'
            '  <editor id="MESSAGES">\n'
            '    <range uom="25" subset="0,1,2,3,4,5" nls="sphtts" />\n'
            '  </editor>\n'
            '</editors>\n'
        )
        with open('profile/editor/editors.xml', 'w') as f:
            f.write(editors_xml_content)

        en_us_content = (
            'status-0 = Off\n'
            'status-1 = On\n'
            'sphtts-0 = Mes1\n'
            'sphtts-1 = Mess2\n'
        )
        with open('profile/nls/en_us.txt', 'w') as f:
            f.write(en_us_content)

    def tearDown(self):
        os.chdir(self.orig_cwd)
        self.temp_dir.cleanup()

    def test_udiTssProfileUpdate_matches_uppercase_messages(self):
        import udiCommonLib
        messages = {0: 'Check sump 1 power', 1: 'Check sump 2 power'}
        changed = udiCommonLib.udiTssProfileUpdate(messages)
        self.assertTrue(changed)

        # Verify editors.xml subset updated
        tree = ET.parse('profile/editor/editors.xml')
        root = tree.getroot()
        msg_editor = [e for e in root if e.attrib.get('id', '').upper() == 'MESSAGES'][0]
        self.assertEqual(msg_editor[0].attrib['subset'], '0-1')

        # Verify en_us.txt updated
        with open('profile/nls/en_us.txt', 'r') as f:
            lines = f.read()
        self.assertIn('sphtts-0 = Check sump 1 power', lines)
        self.assertIn('sphtts-1 = Check sump 2 power', lines)
        self.assertNotIn('sphtts-0 = Mes1', lines)

    def test_udiTssProfileUpdate_no_change_returns_false(self):
        import udiCommonLib
        messages = {0: 'Check sump 1 power', 1: 'Check sump 2 power'}
        udiCommonLib.udiTssProfileUpdate(messages)
        # Calling again with identical messages
        changed = udiCommonLib.udiTssProfileUpdate(messages)
        self.assertFalse(changed)




class TestOfflineNoticesAndResilience(unittest.TestCase):
    """Tests for offline notice management, bounded online checks, and rate-limiting."""

    def test_set_and_clear_offline_notice(self):
        node = MagicMock()
        node.address = 'd88b4c01000001'
        node.name = 'Test Sensor'
        poly = MagicMock()
        notices_dict = {}

        def mock_setitem(key, val):
            notices_dict[key] = val

        def mock_delete(key):
            notices_dict.pop(key, None)

        poly.Notices.__setitem__ = MagicMock(side_effect=mock_setitem)
        poly.Notices.delete = MagicMock(side_effect=mock_delete)
        poly.Notices.__contains__ = MagicMock(side_effect=lambda k: k in notices_dict)
        node.poly = poly

        # Call set_offline_notice
        udiYolinkLib.set_offline_notice(node)
        poly.Notices.__setitem__.assert_called_with('offline_d88b4c01000001', 'Device Test Sensor is offline')
        self.assertEqual(notices_dict.get('offline_d88b4c01000001'), 'Device Test Sensor is offline')

        # Call clear_offline_notice
        udiYolinkLib.clear_offline_notice(node)
        poly.Notices.delete.assert_called_with('offline_d88b4c01000001')
        self.assertNotIn('offline_d88b4c01000001', notices_dict)

    def test_my_setDriver_triggers_offline_notices_on_gv30(self):
        node = MagicMock()
        node.address = 'd88b4c01000002'
        node.name = 'Switch 1'
        node.drivers = [{'driver': 'GV30', 'value': 0, 'uom': 25}]
        node.node = MagicMock()
        node.system_ready = True
        poly = MagicMock()
        notices_dict = {}
        poly.Notices.__setitem__ = MagicMock(side_effect=lambda k, v: notices_dict.update({k: v}))
        poly.Notices.delete = MagicMock(side_effect=lambda k: notices_dict.pop(k, None))
        poly.Notices.__contains__ = MagicMock(side_effect=lambda k: k in notices_dict)
        node.poly = poly

        # When GV30 is set to 0 on a system_ready node, offline notice is set
        udiYolinkLib.my_setDriver(node, 'GV30', 0)
        self.assertEqual(notices_dict.get('offline_d88b4c01000002'), 'Device Switch 1 is offline')

        # When GV30 transitions to 1, offline notice is cleared
        udiYolinkLib.my_setDriver(node, 'GV30', 1)
        self.assertNotIn('offline_d88b4c01000002', notices_dict)

    def test_wait_for_device_online_bounds_and_sets_offline(self):
        node = MagicMock()
        node.address = 'd88b4c01000003'
        node.name = 'Offline TH'
        node.drivers = [{'driver': 'GV30', 'value': 0, 'uom': 25}, {'driver': 'ST', 'value': 0, 'uom': 25}]
        node.node = MagicMock()
        node.my_setDriver = MagicMock()
        mock_dev = MagicMock()
        mock_dev.check_system_online.return_value = False
        poly = MagicMock()
        poly.Notices = MagicMock()
        node.poly = poly

        # Call wait_for_device_online with 2 tries and 0 sleep to verify fast bounding
        is_online = udiYolinkLib.wait_for_device_online(node, mock_dev, max_tries=2, sleep_sec=0)
        self.assertFalse(is_online)
        self.assertEqual(mock_dev.check_system_online.call_count, 2)
        poly.Notices.__setitem__.assert_called_with('offline_d88b4c01000003', 'Device Offline TH is offline')
        node.my_setDriver.assert_any_call('GV30', 0)
        node.my_setDriver.assert_any_call('ST', 0)

    def test_switch_and_dimmer_get_attributes_offline_protection(self):
        from yolinkSwitchV3 import YoLinkSwitch
        from yolinkDimmerV3 import YoLinkDim

        # Test Switch
        mock_switch = MagicMock()
        mock_switch.check_system_online.return_value = False
        YoLinkSwitch.get_attributes(mock_switch)
        mock_switch.setDeviceAttributes.assert_not_called()

        # Test Dimmer
        mock_dimmer = MagicMock()
        mock_dimmer.check_system_online.return_value = False
        YoLinkDim.get_attributes(mock_dimmer)
        mock_dimmer.setDeviceAttributes.assert_not_called()

    def test_time_tracking_scales_and_caps_delay(self):
        import yoLink_init_V4
        import threading
        yoAccess = MagicMock()
        yoAccess.TimeTableLock = threading.Lock()
        yoAccess.time_tracking_dict = {}
        # Simulate 100 devices in mqttList
        yoAccess.mqttList = {f'dev_{i}': {} for i in range(100)}

        # Call time_tracking
        delay = yoLink_init_V4.YoLinkInitPAC.time_tracking(yoAccess, 'dev_1')
        self.assertIsInstance(delay, (int, float))
        # Ensure delay is capped at <= 5.0 seconds
        self.assertLessEqual(delay, 5.0)



class TestMqttResilienceAndTokenManagement(unittest.TestCase):
    def test_update_mqtt_subscription_subscribes_without_unsubscribe(self):
        import yoLink_init_V4
        yoAccess = MagicMock()
        yoAccess.access_mode = ['cloud']
        yoAccess.homeID = 'home123'
        yoAccess.mqtt_str = 'yl-home/'
        yoAccess.QoS = 1
        yoAccess.client = MagicMock()
        yoAccess.mqttList = {
            'dev1': {
                'request': 'yl-home/home123/dev1/request',
                'response': 'yl-home/home123/dev1/response',
                'report': 'yl-home/home123/dev1/report',
            }
        }

        yoLink_init_V4.YoLinkInitPAC.update_mqtt_subscription(yoAccess, 'dev1')

        yoAccess.client.unsubscribe.assert_not_called()
        self.assertEqual(yoAccess.client.subscribe.call_count, 2)
        yoAccess.client.subscribe.assert_any_call('yl-home/home123/dev1/response', 1)
        yoAccess.client.subscribe.assert_any_call('yl-home/home123/dev1/report', 1)

    def test_resubscribe_devices_subscribes_all_without_unsubscribe(self):
        import yoLink_init_V4
        import threading
        yoAccess = MagicMock()
        yoAccess.access_mode = ['cloud']
        yoAccess.connectedToBroker = True
        yoAccess.STOP = threading.Event()
        yoAccess.QoS = 1
        yoAccess.client = MagicMock()
        yoAccess.mqttList = {
            f'dev_{i}': {
                'response': f'yl-home/h1/dev_{i}/response',
                'report': f'yl-home/h1/dev_{i}/report',
            } for i in range(12)
        }

        yoLink_init_V4.YoLinkInitPAC._resubscribe_devices(yoAccess)

        yoAccess.client.unsubscribe.assert_not_called()
        # 12 devices * 2 topics each = 24 calls
        self.assertEqual(yoAccess.client.subscribe.call_count, 24)

    def test_on_connect_success_spawns_resubscribe(self):
        import yoLink_init_V4
        yoAccess = MagicMock()
        yoAccess.access_mode = ['cloud']
        yoAccess.online = False
        yoAccess.connectedToBroker = False
        yoAccess.mqttURL = 'api.yosmart.com'
        yoAccess.mqttList = {'dev1': {}}

        with patch('yoLink_init_V4.Thread') as mock_thread_cls:
            mock_thread_instance = MagicMock()
            mock_thread_cls.return_value = mock_thread_instance

            yoLink_init_V4.YoLinkInitPAC.on_connect(yoAccess, None, None, None, 0)

            self.assertTrue(yoAccess.online)
            self.assertTrue(yoAccess.connectedToBroker)
            mock_thread_cls.assert_called_once_with(target=yoAccess._resubscribe_devices, daemon=True)
            mock_thread_instance.start.assert_called_once()

    def test_on_connect_auth_error_triggers_reconnect_even_if_not_connected(self):
        import yoLink_init_V4
        yoAccess = MagicMock()
        yoAccess.access_mode = ['cloud']
        yoAccess.connectedToBroker = False
        yoAccess.online = True
        yoAccess._reconnecting = False

        with patch('yoLink_init_V4.Thread') as mock_thread_cls:
            mock_thread_instance = MagicMock()
            mock_thread_cls.return_value = mock_thread_instance

            # rc == 2 (Authentication error / Bad Client ID)
            yoLink_init_V4.YoLinkInitPAC.on_connect(yoAccess, None, None, None, 2)

            self.assertFalse(yoAccess.online)
            self.assertFalse(yoAccess.connectedToBroker)
            self.assertTrue(yoAccess._reconnecting)
            mock_thread_cls.assert_called_once_with(target=yoAccess._async_auth_reconnect, daemon=True)
            mock_thread_instance.start.assert_called_once()

    def test_on_disconnect_unintentional_triggers_async_reconnect(self):
        import yoLink_init_V4
        yoAccess = MagicMock()
        yoAccess.access_mode = ['cloud']
        yoAccess.disconnect = False
        yoAccess.connectedToBroker = True
        yoAccess.online = True
        yoAccess._reconnecting = False

        with patch('yoLink_init_V4.Thread') as mock_thread_cls:
            mock_thread_instance = MagicMock()
            mock_thread_cls.return_value = mock_thread_instance

            yoLink_init_V4.YoLinkInitPAC.on_disconnect(yoAccess, None, None, rc=7)

            self.assertFalse(yoAccess.online)
            self.assertFalse(yoAccess.connectedToBroker)
            self.assertTrue(yoAccess.disconnect_occured)
            self.assertTrue(yoAccess._reconnecting)
            mock_thread_cls.assert_called_once_with(target=yoAccess._async_reconnect, daemon=True)
            mock_thread_instance.start.assert_called_once()


class TestPublishDataAndBrokerResilience(unittest.TestCase):
    """Test publish_data bounded wait, transfer_data lock safety, and start() single execution."""

    def test_publish_data_disconnected_times_out(self):
        import yoLink_init_V4
        yoAccess = MagicMock()
        yoAccess.access_mode = ['cloud']
        yoAccess.connectedToBroker = False
        yoAccess.STOP = threading.Event()
        yoAccess.publishQueue = queue.Queue()

        time_values = [0.0, 16.0]
        with patch('time.time', side_effect=lambda: time_values.pop(0) if time_values else 20.0), \
             patch('time.sleep', return_value=None):
            result = yoLink_init_V4.YoLinkInitPAC.publish_data(yoAccess, {'method': 'test', 'targetDevice': 'dev1'})

        self.assertFalse(result)
        self.assertTrue(yoAccess.publishQueue.empty())

    def test_publish_data_stop_event_aborts(self):
        import yoLink_init_V4
        yoAccess = MagicMock()
        yoAccess.access_mode = ['cloud']
        yoAccess.connectedToBroker = False
        yoAccess.STOP = threading.Event()
        yoAccess.STOP.set()
        yoAccess.publishQueue = queue.Queue()

        result = yoLink_init_V4.YoLinkInitPAC.publish_data(yoAccess, {'method': 'test', 'targetDevice': 'dev1'})
        self.assertFalse(result)
        self.assertTrue(yoAccess.publishQueue.empty())

    def test_publish_data_connected_enqueues_and_spawns_thread(self):
        import yoLink_init_V4
        yoAccess = MagicMock()
        yoAccess.access_mode = ['cloud']
        yoAccess.connectedToBroker = True
        yoAccess.STOP = threading.Event()
        yoAccess.publishQueue = queue.Queue()

        with patch('yoLink_init_V4.Thread') as mock_thread_cls:
            mock_thread_instance = MagicMock()
            mock_thread_cls.return_value = mock_thread_instance
            result = yoLink_init_V4.YoLinkInitPAC.publish_data(yoAccess, {'method': 'test', 'targetDevice': 'dev1'})

        self.assertTrue(result)
        self.assertEqual(yoAccess.publishQueue.qsize(), 1)
        mock_thread_cls.assert_called_once_with(target=yoAccess.transfer_data, daemon=True)
        mock_thread_instance.start.assert_called_once()

    def test_transfer_data_empty_queue_releases_lock(self):
        import yoLink_init_V4
        yoAccess = MagicMock()
        yoAccess.access_mode = ['cloud']
        yoAccess.publishQueue = queue.Queue()
        yoAccess.processing_access = threading.Lock()

        res = yoLink_init_V4.YoLinkInitPAC.transfer_data(yoAccess)
        self.assertFalse(res)
        self.assertFalse(yoAccess.processing_access.locked())

    def test_transfer_data_device_not_in_mqtt_list_releases_lock(self):
        import yoLink_init_V4
        yoAccess = MagicMock()
        yoAccess.access_mode = ['cloud']
        yoAccess.publishQueue = queue.Queue()
        yoAccess.processing_access = threading.Lock()
        yoAccess.mqttList = {}
        yoAccess.publishQueue.put({'method': 'test', 'targetDevice': 'unknown_dev'})

        res = yoLink_init_V4.YoLinkInitPAC.transfer_data(yoAccess)
        self.assertFalse(res)
        self.assertFalse(yoAccess.processing_access.locked())

    def test_transfer_data_response_timeout_initiates_retry(self):
        import yoLink_init_V4
        yoAccess = MagicMock()
        yoAccess.access_mode = ['cloud']
        yoAccess.publishQueue = queue.Queue()
        yoAccess.finishQueue = MagicMock()
        yoAccess.finishQueue.get.side_effect = queue.Empty('timed out')
        yoAccess.processing_access = threading.Lock()
        yoAccess.lastPublishTime_ns = 0
        yoAccess.time_tracking = MagicMock(return_value=0)
        yoAccess.QoS = 0
        yoAccess.client = MagicMock()
        pub_result = MagicMock()
        pub_result.rc = 0
        yoAccess.client.publish.return_value = pub_result
        yoAccess.mqttList = {'dev1': {'request': 'topic/req'}}
        yoAccess.lastDataPacket = {}
        yoAccess._enqueue_retry = MagicMock()

        data = {'method': 'test', 'targetDevice': 'dev1'}
        yoAccess.publishQueue.put(data)

        with patch('time.time_ns', return_value=12345000000), patch('time.sleep', return_value=None):
            res = yoLink_init_V4.YoLinkInitPAC.transfer_data(yoAccess)

        self.assertFalse(res)
        self.assertFalse(yoAccess.processing_access.locked())
        yoAccess._enqueue_retry.assert_called_once()
        retried_data = yoAccess._enqueue_retry.call_args[0][0]
        self.assertEqual(retried_data['targetDevice'], 'dev1')
        self.assertEqual(retried_data['retry'], 0)

    def test_transfer_data_rate_limit_010301_initiates_retry_with_code(self):
        import yoLink_init_V4
        yoAccess = MagicMock()
        yoAccess.access_mode = ['cloud']
        yoAccess.publishQueue = queue.Queue()
        yoAccess.finishQueue = MagicMock()
        yoAccess.finishQueue.get.return_value = {'msgid': '12345', 'code': '010301'}
        yoAccess.processing_access = threading.Lock()
        yoAccess.lastPublishTime_ns = 0
        yoAccess.time_tracking = MagicMock(return_value=0)
        yoAccess.QoS = 0
        yoAccess.client = MagicMock()
        pub_result = MagicMock()
        pub_result.rc = 0
        yoAccess.client.publish.return_value = pub_result
        yoAccess.mqttList = {'dev1': {'request': 'topic/req'}}
        yoAccess.lastDataPacket = {}
        yoAccess._enqueue_retry = MagicMock()

        data = {'method': 'test', 'targetDevice': 'dev1', 'time': '12345'}
        yoAccess.publishQueue.put(data)

        with patch('time.time_ns', return_value=12345000000), patch('time.sleep', return_value=None):
            res = yoLink_init_V4.YoLinkInitPAC.transfer_data(yoAccess)

        self.assertTrue(res)
        self.assertFalse(yoAccess.processing_access.locked())
        yoAccess._enqueue_retry.assert_called_once()
        retried_data = yoAccess._enqueue_retry.call_args[0][0]
        self.assertEqual(retried_data['targetDevice'], 'dev1')
        self.assertEqual(retried_data['last_code'], '010301')

    def test_switch_get_attributes_skips_relay_models(self):
        from yolinkSwitchV3 import YoLinkSwitch
        switch = MagicMock()
        switch.check_system_online.return_value = True
        switch.setDeviceAttributes = MagicMock()

        # Model YS5706 (relay)
        switch.deviceInfo = {'modelName': 'YS5706-UC'}
        YoLinkSwitch.get_attributes(switch)
        switch.setDeviceAttributes.assert_not_called()

        # Model YS5708 (in-wall switch with LED)
        switch.deviceInfo = {'modelName': 'YS5708-UC'}
        YoLinkSwitch.get_attributes(switch)
        switch.setDeviceAttributes.assert_called_once_with(None)

    def test_start_reentrancy_guard_prevents_duplicate_initialization(self):
        """udi-YoLink and udiYoLinkLocal start() must execute only once."""
        import importlib
        sys.modules.pop('udi-YoLink', None)
        yolink_mod = importlib.import_module('udi-YoLink')

        ctrl = MagicMock()
        ctrl._started = False
        ctrl._start_lock = threading.Lock()
        ctrl.nodeDefineDone = True
        ctrl.configDone = True
        ctrl.handleParamsDone = True
        ctrl.uaid = 'test_uaid'
        ctrl.secretKey = 'test_secret'
        ctrl.Parameters = {}
        ctrl.updateEpochTime = MagicMock()
        ctrl.my_setDriver = MagicMock()
        ctrl.convert_temp_unit = MagicMock(return_value=0)
        ctrl.convert_water_unit = MagicMock(return_value=0)
        ctrl.sync_tts_parameters = MagicMock()

        with patch('udi-YoLink.YoLinkInitPAC') as mock_pac_cls:
            mock_pac = MagicMock()
            mock_pac.getDeviceList.return_value = []
            mock_pac_cls.return_value = mock_pac

            # First start call
            yolink_mod.YoLinkSetup.start(ctrl)
            self.assertTrue(ctrl._started)
            mock_pac_cls.assert_called_once()

            # Second duplicate start call
            yolink_mod.YoLinkSetup.start(ctrl)
            # Must NOT instantiate YoLinkInitPAC a second time
            mock_pac_cls.assert_called_once()


class TestWaitForNodeDone(unittest.TestCase):
    """Test wait_for_node_done timeout, retry, and non-blocking recovery."""

    def test_wait_for_node_done_success(self):
        import udiYolinkLib
        node = MagicMock()
        node.address = 'test_addr'
        node.n_queue = ['test_addr']

        res = udiYolinkLib.wait_for_node_done(node, timeout=0.1)
        self.assertTrue(res)
        self.assertEqual(node.n_queue, [])

    def test_wait_for_node_done_timeout_retries_and_returns_false(self):
        import udiYolinkLib
        node = MagicMock()
        node.address = 'test_addr'
        node.n_queue = []
        node.poly = MagicMock()

        res = udiYolinkLib.wait_for_node_done(node, timeout=0.05)
        self.assertFalse(res)
        node.poly.addNode.assert_called_once_with(node)

    def test_wait_for_node_done_retry_succeeds(self):
        import udiYolinkLib
        node = MagicMock()
        node.address = 'test_addr'
        node.n_queue = []
        node.poly = MagicMock()

        def simulate_add_node(n):
            n.n_queue.append('test_addr')

        node.poly.addNode.side_effect = simulate_add_node

        res = udiYolinkLib.wait_for_node_done(node, timeout=0.05)
        self.assertTrue(res)
        self.assertEqual(node.n_queue, [])
        node.poly.addNode.assert_called_once_with(node)


if __name__ == '__main__':
    unittest.main()
