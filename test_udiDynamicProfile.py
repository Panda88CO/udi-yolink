#!/usr/bin/env python3
"""
Unit test harness for dynamic profile generation, driver name resolution,
and deferred profile loading in udi-yolink.
"""
import sys
import unittest
from unittest.mock import MagicMock, patch
import ast
import glob
import os

# Ensure mock dependencies exist if running in an environment without them installed
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
    mock_udi.LOGGER = MagicMock()
    sys.modules['udi_interface'] = mock_udi

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import udiDynamicProfile


class TestDynamicProfileGeneration(unittest.TestCase):
    """Test dynamic JSON profile payload generation."""

    def test_dynamic_profile_payload_structure(self):
        payload = udiDynamicProfile.get_dynamic_profile_payload()
        self.assertIn('delete', payload)
        self.assertIn('editors', payload)
        self.assertIn('nodedefs', payload)
        self.assertIn('linkdefs', payload)

        self.assertEqual(payload['delete']['editors'], ['*'])
        self.assertEqual(payload['delete']['nodedefs'], ['*'])
        self.assertEqual(payload['delete']['linkdefs'], ['*'])

    def test_dynamic_editors_content(self):
        editors = udiDynamicProfile.get_dynamic_profile_editors()
        self.assertGreaterEqual(len(editors), 100)
        # Check an editor with enum translations
        connect_ed = next((e for e in editors if e.get('id') == 'connect'), None)
        self.assertIsNotNone(connect_ed)
        self.assertTrue(len(connect_ed.get('ranges', [])) > 0)
        self.assertIn('names', connect_ed['ranges'][0])

    def test_dynamic_nodedefs_content(self):
        nodedefs = udiDynamicProfile.get_dynamic_profile_nodedefs()
        self.assertGreaterEqual(len(nodedefs), 70)
        # Check setup nodeDef
        setup_nd = next((nd for nd in nodedefs if nd.get('id') == 'setup'), None)
        self.assertIsNotNone(setup_nd)
        self.assertEqual(setup_nd.get('name'), 'YoLink Setup')
        st_prop = next((p for p in setup_nd.get('properties', []) if p.get('id') == 'ST'), None)
        self.assertIsNotNone(st_prop)
        self.assertEqual(st_prop.get('name'), 'Node Server')


class TestDriverNameResolution(unittest.TestCase):
    """Test resolution and application of driver display names."""

    def test_profile_driver_names_mapping(self):
        names = udiDynamicProfile.get_profile_driver_names()
        self.assertGreaterEqual(len(names), 700)
        # Verify key nodes
        self.assertEqual(names.get(('setup', 'ST')), 'Node Server')
        self.assertEqual(names.get(('setup', 'GV1')), 'Status')
        self.assertEqual(names.get(('setup', 'TIME')), 'LastPoll Time')
        self.assertEqual(names.get(('yoswitch', 'ST')), 'Switch State')
        self.assertEqual(names.get(('yodoorsens', 'ST')), 'Door State')

    def test_apply_profile_driver_names_basic(self):
        class DummyNode:
            id = 'yodoorsens'
            drivers = [
                {'driver': 'ST', 'value': 0, 'uom': 25},
                {'driver': 'GV1', 'value': 99, 'uom': 25},
            ]

        node = DummyNode()
        udiDynamicProfile.apply_profile_driver_names(node)

        st = next(d for d in node.drivers if d['driver'] == 'ST')
        gv1 = next(d for d in node.drivers if d['driver'] == 'GV1')
        self.assertEqual(st['name'], 'Door State')
        self.assertEqual(gv1['name'], 'Sensor Battery Level')

    def test_apply_profile_driver_names_isolates_instances(self):
        class DummyClass:
            id = 'yoswitch'
            drivers = [
                {'driver': 'ST', 'value': 99, 'uom': 25},
            ]

        inst1 = DummyClass()
        inst2 = DummyClass()

        udiDynamicProfile.apply_profile_driver_names(inst1, 'yoswitch')
        self.assertIsNot(inst1.drivers, DummyClass.drivers)
        self.assertIsNot(inst2.drivers, inst1.drivers)

    def test_apply_profile_driver_names_variant_overrides(self):
        class DummyThermostat:
            id = 'yothermostat'
            drivers = [
                {'driver': 'ST', 'value': 0, 'uom': 4},
                {'driver': 'CLISPC', 'value': 22, 'uom': 4},
            ]

        c_node = DummyThermostat()
        udiDynamicProfile.apply_profile_driver_names(c_node, 'yothermostat')

        f_node = DummyThermostat()
        f_node.id = 'yothermostatf'
        udiDynamicProfile.apply_profile_driver_names(f_node, 'yothermostatf')

        self.assertEqual(c_node.drivers[0]['name'], 'Temperature')
        self.assertEqual(f_node.drivers[0]['name'], 'Temperature')

    def test_driver_fallback_labels(self):
        class DummyNode:
            id = 'unknownNode'
            drivers = [
                {'driver': 'GV21', 'value': 0, 'uom': 25},
                {'driver': 'GV22', 'value': 0, 'uom': 25},
                {'driver': 'GV4', 'value': 0, 'uom': 119},
            ]

        node = DummyNode()
        udiDynamicProfile.apply_profile_driver_names(node)
        self.assertEqual(node.drivers[0]['name'], 'On Sec')
        self.assertEqual(node.drivers[1]['name'], 'Off Sec')
        self.assertEqual(node.drivers[2]['name'], 'Energy')


class TestCodebaseDriverIntegrity(unittest.TestCase):
    """Test that all node classes in the codebase define 'name' on all drivers."""

    def test_all_node_classes_have_named_drivers(self):
        node_files = sorted(glob.glob('udiYo*.py') + glob.glob('udi-YoLink.py'))
        total_drivers = 0
        unnamed = []

        for f in node_files:
            if f in ('udiDynamicProfile.py', 'udiYolinkLib.py', 'dynamic_profile_data.py'):
                continue
            with open(f, 'r') as fp:
                tree = ast.parse(fp.read(), filename=f)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    for item in node.body:
                        if isinstance(item, ast.Assign):
                            for target in item.targets:
                                if isinstance(target, ast.Name) and target.id in ('drivers', 'single_press_drivers'):
                                    if isinstance(item.value, ast.List):
                                        for elt in item.value.elts:
                                            if isinstance(elt, ast.Dict):
                                                total_drivers += 1
                                                keys = [k.value for k in elt.keys if isinstance(k, ast.Constant)]
                                                if 'name' not in keys:
                                                    unnamed.append((f, node.name, keys))

        self.assertGreaterEqual(total_drivers, 430)
        self.assertEqual(unnamed, [], f"Found drivers without 'name': {unnamed}")


class TestDeferredProfileLoading(unittest.TestCase):
    """Test update_dynamic_profile deferral behavior."""

    def test_update_dynamic_profile_calls_updateJsonProfile(self):
        controller = MagicMock()
        controller.poly = MagicMock()
        controller.poly.updateJsonProfile = MagicMock()
        controller.poly.updateProfile = MagicMock()

        udiDynamicProfile.update_dynamic_profile(controller)

        controller.poly.updateJsonProfile.assert_called_once()
        args, kwargs = controller.poly.updateJsonProfile.call_args
        self.assertIsInstance(args[0], dict)
        self.assertIn('nodedefs', args[0])
        self.assertEqual(args[1], {"waitResponse": True})

    def test_update_dynamic_profile_fallback_on_json_error(self):
        controller = MagicMock()
        controller.poly = MagicMock()
        controller.poly.updateJsonProfile.side_effect = Exception("updateJsonProfile unsupported")
        controller.poly.updateProfile = MagicMock()

        udiDynamicProfile.update_dynamic_profile(controller)

        controller.poly.updateProfile.assert_called_once()


if __name__ == '__main__':
    unittest.main()

