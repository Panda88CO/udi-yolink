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
import json
import xml.etree.ElementTree as ET

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
import udiYolinkLib


class TestDynamicProfileGeneration(unittest.TestCase):
    """Test dynamic JSON profile payload generation."""

    def test_dynamic_profile_payload_structure(self):
        payload = udiDynamicProfile.get_dynamic_profile_payload()
        self.assertNotIn('delete', payload)
        self.assertIn('editors', payload)
        self.assertIn('nodedefs', payload)
        self.assertIn('linkdefs', payload)

        # Optional delete section can be provided if explicitly requested
        custom_delete = {'editors': ['OLD_EDITOR']}
        del_payload = udiDynamicProfile.get_dynamic_profile_payload(delete=custom_delete)
        self.assertIn('delete', del_payload)
        self.assertEqual(del_payload['delete'], custom_delete)

    def test_dynamic_editors_content(self):
        editors = udiDynamicProfile.get_dynamic_profile_editors()
        self.assertGreaterEqual(len(editors), 100)
        # Check an editor with enum translations
        connect_ed = next((e for e in editors if e.get('id') == 'CONNECT'), None)
        self.assertIsNotNone(connect_ed)
        self.assertTrue(len(connect_ed.get('ranges', [])) > 0)
        self.assertIn('names', connect_ed['ranges'][0])

    def test_dynamic_nodedefs_content(self):
        nodedefs_unified = udiDynamicProfile.get_dynamic_profile_nodedefs(include_variants=False)
        self.assertEqual(len(nodedefs_unified), 58)
        # All variant IDs should be excluded
        unified_ids = {nd['id'] for nd in nodedefs_unified}
        for var_id in udiDynamicProfile.VARIANT_TO_BASE_NODEDEF:
            self.assertNotIn(var_id, unified_ids)

        # Full profile with variants retained
        nodedefs_all = udiDynamicProfile.get_dynamic_profile_nodedefs(include_variants=True)
        self.assertEqual(len(nodedefs_all), 73)

        # Check setup nodeDef
        setup_nd = next((nd for nd in nodedefs_unified if nd.get('id') == 'SETUP'), None)
        self.assertIsNotNone(setup_nd)
        self.assertEqual(setup_nd.get('name'), 'YoLink Setup')
        st_prop = next((p for p in setup_nd.get('properties', []) if p.get('id') == 'ST'), None)
        self.assertIsNotNone(st_prop)
        self.assertEqual(st_prop.get('name'), 'Node Server')

        # Check yowatermeterSub has full properties
        sub_nd = next((nd for nd in nodedefs_unified if nd.get('id') == 'YOWATERMETERSUB'), None)
        self.assertIsNotNone(sub_nd)
        sub_prop_ids = {p['id'] for p in sub_nd.get('properties', [])}
        self.assertIn('GV22', sub_prop_ids)
        self.assertIn('GV28', sub_prop_ids)
        self.assertIn('GV20', sub_prop_ids)

    def test_dynamic_nodedefs_parameters_have_valid_ids(self):
        """All command parameters in dynamic nodedefs must have non-empty alphanumeric string ID, editor, and name."""
        for nd in udiDynamicProfile.get_dynamic_profile_nodedefs(include_variants=True):
            for cmd in nd.get('cmds', {}).get('accepts', []):
                for p in cmd.get('parameters', []):
                    self.assertIn('id', p)
                    self.assertIsInstance(p['id'], str)
                    self.assertTrue(len(p['id']) > 0, f"Parameter ID empty in node {nd['id']} cmd {cmd['id']}")
                    self.assertTrue(p['id'].isalnum(), f"Parameter ID '{p['id']}' not alphanumeric in node {nd['id']} cmd {cmd['id']}")
                    self.assertIn('editor', p)
                    self.assertIn('name', p)
                    self.assertNotIn('init', p)

    def test_dynamic_editors_numeric_ranges(self):
        """All range min, max, prec values must be numbers (int/float), never strings."""
        for ed in udiDynamicProfile.get_dynamic_profile_editors():
            for r in ed.get('ranges', []):
                for k in ['min', 'max']:
                    if k in r:
                        self.assertIsInstance(r[k], (int, float), f"{ed['id']} {k} must be numeric, got {type(r[k])}")
                if 'prec' in r:
                    self.assertIsInstance(r['prec'], int, f"{ed['id']} prec must be int, got {type(r['prec'])}")

    def test_sends_commands_have_no_name_attribute(self):
        """Commands under 'sends' must not contain 'name' attribute in dynamic profile."""
        for nd in udiDynamicProfile.get_dynamic_profile_nodedefs(include_variants=True):
            for cmd in nd.get('cmds', {}).get('sends', []):
                self.assertNotIn('name', cmd, f"Nodedef '{nd['id']}' send command '{cmd['id']}' has 'name'")

    def test_server_json_manifest_valid(self):
        """server.json must be a valid manifest with profile_version."""
        import json
        manifest_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'server.json')
        self.assertTrue(os.path.exists(manifest_path), "server.json must exist")
        with open(manifest_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.assertIn('name', data)
        self.assertIn('profile_version', data)
        self.assertTrue(len(data['profile_version']) > 0)
        self.assertIn('executable', data)

    def test_dynamic_editors_fahrenheit_and_gallons(self):
        editors = udiDynamicProfile.get_dynamic_profile_editors(temp_unit=1, water_unit=0)
        by_id = {e['id']: e for e in editors}

        # Temperature editors parameterized to Fahrenheit (UOM 17)
        self.assertEqual(by_id['CELSIUS']['ranges'][0]['uom'], '17')
        self.assertEqual(by_id['CELSIUS']['ranges'][0]['max'], 221)
        self.assertEqual(by_id['FARENHEIT']['ranges'][0]['uom'], '17')
        self.assertEqual(by_id['CELSIUSSET']['ranges'][0]['uom'], '17')
        self.assertEqual(by_id['CELSIUSSET']['ranges'][0]['min'], 40)
        self.assertEqual(by_id['ECOSET']['ranges'][0]['uom'], '17')
        self.assertEqual(by_id['ECOSET']['ranges'][0]['max'], 9)

        # Water editors parameterized to Gallons (UOM 69)
        self.assertEqual(by_id['LITER']['ranges'][0]['uom'], '69')
        self.assertEqual(by_id['GALLON']['ranges'][0]['uom'], '69')
        self.assertEqual(by_id['LITERSET']['ranges'][0]['uom'], '69')

    def test_dynamic_editors_celsius_and_liters(self):
        editors = udiDynamicProfile.get_dynamic_profile_editors(temp_unit=0, water_unit=3)
        by_id = {e['id']: e for e in editors}

        # Temperature editors parameterized to Celsius (UOM 4)
        self.assertEqual(by_id['CELSIUS']['ranges'][0]['uom'], '4')
        self.assertEqual(by_id['CELSIUS']['ranges'][0]['max'], 105)
        self.assertEqual(by_id['FARENHEIT']['ranges'][0]['uom'], '4')
        self.assertEqual(by_id['CELSIUSSET']['ranges'][0]['uom'], '4')
        self.assertEqual(by_id['CELSIUSSET']['ranges'][0]['max'], 38)
        self.assertEqual(by_id['ECOSET']['ranges'][0]['uom'], '4')
        self.assertEqual(by_id['ECOSET']['ranges'][0]['max'], 5)

        # Water editors parameterized to Liters (UOM 35)
        self.assertEqual(by_id['LITER']['ranges'][0]['uom'], '35')
        self.assertEqual(by_id['GALLON']['ranges'][0]['uom'], '35')
        self.assertEqual(by_id['LITERSET']['ranges'][0]['uom'], '35')
        self.assertEqual(by_id['LITER']['ranges'][0]['max'], 100000)

    def test_dynamic_editors_ccf_and_m3(self):
        ed_ccf = {e['id']: e for e in udiDynamicProfile.get_dynamic_profile_editors(water_unit=1)}
        self.assertEqual(ed_ccf['LITER']['ranges'][0]['uom'], '6')
        self.assertEqual(ed_ccf['GALLON']['ranges'][0]['uom'], '6')

        ed_m3 = {e['id']: e for e in udiDynamicProfile.get_dynamic_profile_editors(water_unit=2)}
        self.assertEqual(ed_m3['LITER']['ranges'][0]['uom'], '8')
        self.assertEqual(ed_m3['GALLON']['ranges'][0]['uom'], '8')
        self.assertEqual(ed_m3['LITER']['ranges'][0]['prec'], 2)

    def test_dynamic_profile_payload_resolves_controller_units(self):
        mock_controller = MagicMock()
        mock_controller.temp_unit = 1  # Fahrenheit
        mock_controller.water_unit = 3  # Liters

        payload = udiDynamicProfile.get_dynamic_profile_payload(controller=mock_controller)
        by_id = {e['id']: e for e in payload['editors']}
        self.assertEqual(by_id['CELSIUS']['ranges'][0]['uom'], '17')
        self.assertEqual(by_id['LITER']['ranges'][0]['uom'], '35')
        self.assertEqual(len(payload['nodedefs']), 58)

    def test_normalize_units(self):
        # Temp unit normalizer
        self.assertEqual(udiDynamicProfile.normalize_temp_unit(None), 0)
        self.assertEqual(udiDynamicProfile.normalize_temp_unit(0), 0)
        self.assertEqual(udiDynamicProfile.normalize_temp_unit(1), 1)
        self.assertEqual(udiDynamicProfile.normalize_temp_unit('0'), 0)
        self.assertEqual(udiDynamicProfile.normalize_temp_unit('1'), 1)
        self.assertEqual(udiDynamicProfile.normalize_temp_unit('C'), 0)
        self.assertEqual(udiDynamicProfile.normalize_temp_unit('Celsius'), 0)
        self.assertEqual(udiDynamicProfile.normalize_temp_unit('F'), 1)
        self.assertEqual(udiDynamicProfile.normalize_temp_unit('Fahrenheit'), 1)
        self.assertEqual(udiDynamicProfile.normalize_temp_unit('unknown'), 0)

        # Water unit normalizer
        self.assertEqual(udiDynamicProfile.normalize_water_unit(None), 0)
        self.assertEqual(udiDynamicProfile.normalize_water_unit(0), 0)
        self.assertEqual(udiDynamicProfile.normalize_water_unit(1), 1)
        self.assertEqual(udiDynamicProfile.normalize_water_unit(2), 2)
        self.assertEqual(udiDynamicProfile.normalize_water_unit(3), 3)
        self.assertEqual(udiDynamicProfile.normalize_water_unit('0'), 0)
        self.assertEqual(udiDynamicProfile.normalize_water_unit('1'), 1)
        self.assertEqual(udiDynamicProfile.normalize_water_unit('2'), 2)
        self.assertEqual(udiDynamicProfile.normalize_water_unit('3'), 3)
        self.assertEqual(udiDynamicProfile.normalize_water_unit('G'), 0)
        self.assertEqual(udiDynamicProfile.normalize_water_unit('Gallon'), 0)
        self.assertEqual(udiDynamicProfile.normalize_water_unit('C'), 1)
        self.assertEqual(udiDynamicProfile.normalize_water_unit('CCF'), 1)
        self.assertEqual(udiDynamicProfile.normalize_water_unit('M'), 2)
        self.assertEqual(udiDynamicProfile.normalize_water_unit('m3'), 2)
        self.assertEqual(udiDynamicProfile.normalize_water_unit('L'), 3)
        self.assertEqual(udiDynamicProfile.normalize_water_unit('Liter'), 3)
        self.assertEqual(udiDynamicProfile.normalize_water_unit('invalid'), 0)


class TestDriverNameResolution(unittest.TestCase):
    """Test resolution and application of driver display names."""

    def test_profile_driver_names_mapping(self):
        names = udiDynamicProfile.get_profile_driver_names()
        self.assertGreaterEqual(len(names), 700)
        # Verify key nodes
        self.assertEqual(names.get(('SETUP', 'ST')), 'Node Server')
        self.assertEqual(names.get(('SETUP', 'GV1')), 'Status')
        self.assertEqual(names.get(('SETUP', 'TIME')), 'LastPoll Time')
        self.assertEqual(names.get(('YOSWITCH', 'ST')), 'Switch State')
        self.assertEqual(names.get(('YODOORSENS', 'ST')), 'Door State')

    def test_apply_profile_driver_names_basic(self):
        class DummyNode:
            id = 'YODOORSENS'
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
            id = 'YOSWITCH'
            drivers = [
                {'driver': 'ST', 'value': 99, 'uom': 25},
            ]

        inst1 = DummyClass()
        inst2 = DummyClass()

        udiDynamicProfile.apply_profile_driver_names(inst1, 'YOSWITCH')
        self.assertIsNot(inst1.drivers, DummyClass.drivers)
        self.assertIsNot(inst2.drivers, inst1.drivers)

    def test_apply_profile_driver_names_variant_overrides(self):
        class DummyThermostat:
            id = 'YOTHERMOSTAT'
            drivers = [
                {'driver': 'ST', 'value': 0, 'uom': 4},
                {'driver': 'CLISPC', 'value': 22, 'uom': 4},
            ]

        c_node = DummyThermostat()
        udiDynamicProfile.apply_profile_driver_names(c_node, 'YOTHERMOSTAT')

        f_node = DummyThermostat()
        f_node.id = 'YOTHERMOSTATF'
        udiDynamicProfile.apply_profile_driver_names(f_node, 'YOTHERMOSTATF')

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

    def test_apply_profile_driver_names_dynamic_uom(self):
        class DummyTempNode:
            id = 'YOTHSENS'
            temp_unit = 1  # Fahrenheit
            drivers = [
                {'driver': 'CLITEMP', 'value': 0, 'uom': 4},
            ]

        f_node = DummyTempNode()
        udiDynamicProfile.apply_profile_driver_names(f_node)
        self.assertEqual(f_node.drivers[0]['uom'], 17)

        class DummyWaterNode:
            id = 'YOWATERMETERSUB'
            water_unit = 0  # Gallons
            drivers = [
                {'driver': 'GV1', 'value': 0, 'uom': 35},
                {'driver': 'GV2', 'value': 0, 'uom': 35},
            ]

        g_node = DummyWaterNode()
        udiDynamicProfile.apply_profile_driver_names(g_node)
        self.assertEqual(g_node.drivers[0]['uom'], 69)
        self.assertEqual(g_node.drivers[1]['uom'], 69)


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
        # Static profile upload should NOT be called when dynamic JSON update succeeds
        controller.poly.updateProfile.assert_not_called()

    def test_update_dynamic_profile_fallback_on_json_error(self):
        controller = MagicMock()
        controller.poly = MagicMock()
        controller.poly.updateJsonProfile.side_effect = Exception("updateJsonProfile unsupported")
        controller.poly.updateProfile = MagicMock()

        udiDynamicProfile.update_dynamic_profile(controller)

        controller.poly.updateProfile.assert_called_once()

    def test_update_dynamic_profile_fallback_when_pruned_exceeds_safe_limit(self):
        """When active-node pruned profile exceeds MAX_SAFE_PROFILE_BYTES, fall back directly to updateProfile."""
        controller = MagicMock()
        controller.poly = MagicMock()
        controller.poly.updateJsonProfile = MagicMock()
        controller.poly.updateProfile = MagicMock()

        with patch.object(udiDynamicProfile, 'get_active_nodedef_ids', return_value={'SETUP', 'YOTHSENS'}), \
             patch.object(udiDynamicProfile, 'get_dynamic_profile_payload') as mock_payload:
            # Return a payload that serializes to > 60KB
            mock_payload.return_value = {'nodedefs': [{'id': 'BIG'}], 'editors': [{'id': 'ED', 'desc': 'x' * 65000}]}
            udiDynamicProfile.update_dynamic_profile(controller)

        controller.poly.updateJsonProfile.assert_not_called()
        controller.poly.updateProfile.assert_called_once()

    def test_get_active_nodedef_ids_extraction(self):
        """Test extraction of active nodeDef IDs from mock controller with live nodes."""
        controller = MagicMock()
        node_setup = MagicMock()
        node_setup.id = 'SETUP'
        node_th = MagicMock()
        node_th.id = 'YOTHSENS'
        node_sw = MagicMock()
        node_sw.id = 'YOSWITCH'
        controller.poly.getNodes.return_value = {
            'setup': node_setup,
            'th1': node_th,
            'sw1': node_sw,
        }
        controller.yolink_nodes = None
        controller.nodes_in_db = None
        controller.deviceList = None

        active_ids = udiDynamicProfile.get_active_nodedef_ids(controller)
        self.assertIsNotNone(active_ids)
        self.assertIn('SETUP', active_ids)
        self.assertIn('YOTHSENS', active_ids)
        self.assertIn('YOTHSENSF', active_ids)  # Expanded variant
        self.assertIn('YOSWITCH', active_ids)
        self.assertIn('YOSWITCHPWR', active_ids)  # Family expansion
        self.assertIn('YOSCHEDULE', active_ids)   # Schedule expansion for switch

    def test_active_only_payload_reduces_size(self):
        """Active-only dynamic profile payload must be well below 60KB and retain required editors."""
        controller = MagicMock()
        node_setup = MagicMock()
        node_setup.id = 'SETUP'
        node_th = MagicMock()
        node_th.id = 'YOTHSENS'
        node_outlet = MagicMock()
        node_outlet.id = 'YOOUTLETPWR'
        controller.poly.getNodes.return_value = {
            'setup': node_setup,
            'th1': node_th,
            'out1': node_outlet,
        }
        controller.yolink_nodes = None
        controller.nodes_in_db = None
        controller.deviceList = None
        controller.temp_unit = 1
        controller.water_unit = 0

        # Full payload
        full_payload = udiDynamicProfile.get_dynamic_profile_payload(controller=controller, active_only=False)
        full_bytes = len(json.dumps(full_payload).encode('utf-8'))
        self.assertGreater(full_bytes, 60000)

        # Active-only pruned payload
        pruned_payload = udiDynamicProfile.get_dynamic_profile_payload(controller=controller, active_only=True)
        pruned_bytes = len(json.dumps(pruned_payload).encode('utf-8'))
        self.assertLess(pruned_bytes, 60000)
        self.assertLess(pruned_bytes, full_bytes)

        # NodeDefs in pruned payload must include active nodes
        pruned_nids = {nd['id'] for nd in pruned_payload['nodedefs']}
        self.assertIn('SETUP', pruned_nids)
        self.assertIn('YOTHSENS', pruned_nids)
        self.assertIn('YOOUTLETPWR', pruned_nids)

        # All editors used by pruned nodeDefs must be present in pruned editors
        pruned_eids = {ed['id'] for ed in pruned_payload['editors']}
        for nd in pruned_payload['nodedefs']:
            for prop in nd.get('properties', []):
                if prop.get('editor'):
                    self.assertIn(prop['editor'], pruned_eids)

    def test_update_dynamic_profile_writes_debug_dump_files(self):
        """update_dynamic_profile must write debug json file and log size metrics."""
        controller = MagicMock()
        controller.poly = MagicMock()
        controller.poly.updateJsonProfile = MagicMock()
        controller.poly.updateProfile = MagicMock()

        udiDynamicProfile.update_dynamic_profile(controller)

        base_dir = os.path.dirname(os.path.abspath(__file__))
        debug_path = os.path.join(base_dir, 'profile_payload_debug.json')
        self.assertTrue(os.path.exists(debug_path))
        with open(debug_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.assertIn('editors', data)
        self.assertIn('nodedefs', data)


class TestWaterUnitConversions(unittest.TestCase):
    """Test full 4x4 matrix and helper conversions for water units."""

    def test_calculate_water_volume_full_matrix(self):
        # 0 = Gallon, 1 = CCF, 2 = m^3, 3 = Liter
        calc = lambda vol, vu, tu: udiYolinkLib.calculate_water_volume(None, vol, vu, tu)

        # Gallon (0) conversions
        self.assertAlmostEqual(calc(100, 0, 1), 0.133681, places=5)
        self.assertAlmostEqual(calc(1000, 0, 2), 3.78541, places=4)
        self.assertAlmostEqual(calc(10, 0, 3), 37.8541, places=3)
        self.assertEqual(calc(50, 0, 0), 50)

        # CCF (1) conversions
        self.assertAlmostEqual(calc(1, 1, 0), 748.052, places=3)
        self.assertAlmostEqual(calc(1, 1, 2), 2.83168, places=4)
        self.assertAlmostEqual(calc(1, 1, 3), 2831.68, places=2)
        self.assertEqual(calc(50, 1, 1), 50)

        # m^3 (2) conversions
        self.assertAlmostEqual(calc(1, 2, 0), 264.172, places=3)
        self.assertAlmostEqual(calc(1, 2, 1), 0.353147, places=5)
        self.assertAlmostEqual(calc(1, 2, 3), 1000.0, places=1)
        self.assertEqual(calc(50, 2, 2), 50)

        # Liter (3) conversions
        self.assertAlmostEqual(calc(1000, 3, 0), 264.172, places=3)
        self.assertAlmostEqual(calc(1000, 3, 1), 0.353147, places=5)
        self.assertAlmostEqual(calc(1000, 3, 2), 1.0, places=4)
        self.assertEqual(calc(50, 3, 3), 50)

    def test_calculate_water_volume_string_and_edge_inputs(self):
        calc = lambda vol, vu, tu: udiYolinkLib.calculate_water_volume(None, vol, vu, tu)

        # String units
        self.assertAlmostEqual(calc('1000', 'Liter', 'Gallon'), 264.172, places=3)
        self.assertAlmostEqual(calc('1000', 'L', 'G'), 264.172, places=3)
        self.assertAlmostEqual(calc('1000', '3', '0'), 264.172, places=3)
        self.assertAlmostEqual(calc('1', 'm3', 'Liter'), 1000.0, places=1)
        self.assertAlmostEqual(calc('1', 'CCF', 'Gallon'), 748.052, places=3)

        # Edge cases
        self.assertEqual(calc(None, 0, 3), 0)
        self.assertEqual(calc('invalid', 0, 3), 'invalid')

    def test_convert_water_unit_mappings(self):
        conv = lambda s: udiYolinkLib.convert_water_unit(None, s)
        self.assertEqual(conv(0), 0)
        self.assertEqual(conv(1), 1)
        self.assertEqual(conv(2), 2)
        self.assertEqual(conv(3), 3)
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
        self.assertEqual(conv(None), 0)
        self.assertEqual(conv('unknown'), 0)

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

    def test_dynamic_profile_all_four_water_units(self):
        for unit_val, expected_uom in [(0, '69'), (1, '6'), (2, '8'), (3, '35')]:
            editors = udiDynamicProfile.get_dynamic_profile_editors(water_unit=unit_val)
            by_id = {e['id']: e for e in editors}
            self.assertEqual(by_id['LITER']['ranges'][0]['uom'], expected_uom)
            self.assertEqual(by_id['GALLON']['ranges'][0]['uom'], expected_uom)
            self.assertEqual(by_id['LITERSET']['ranges'][0]['uom'], expected_uom)
            self.assertEqual(by_id['GALLONSET']['ranges'][0]['uom'], expected_uom)

    def test_apply_profile_driver_names_all_four_water_units(self):
        for unit_val, expected_uom in [(0, 69), (1, 6), (2, 8), (3, 35)]:
            mock_node = MagicMock()
            mock_node.id = 'YOWATERMETERSUB'
            mock_node.water_unit = unit_val
            mock_node.temp_unit = 0
            mock_node.drivers = [
                {'driver': 'GV1', 'value': 0, 'uom': 69},
                {'driver': 'GV10', 'value': 0, 'uom': 35},
                {'driver': 'GV2', 'value': 0, 'uom': 6},
            ]
            udiDynamicProfile.apply_profile_driver_names(mock_node)
            for d in mock_node.drivers:
                self.assertEqual(d['uom'], expected_uom)


class TestProfileSchemaAndValidation(unittest.TestCase):
    """Test schema validity and integrity of static and dynamic profile definitions."""

    def test_nodedefs_xml_no_cmd_editor_attribute(self):
        """IoX schema violation: <cmd> in accepts/sends must not have an 'editor' attribute."""
        xml_path = os.path.join(os.path.dirname(__file__), 'profile', 'nodedef', 'nodedefs.xml')
        self.assertTrue(os.path.exists(xml_path), f"File not found: {xml_path}")
        tree = ET.parse(xml_path)
        violations = []
        for nd in tree.findall('.//nodeDef'):
            nid = nd.get('id')
            for cmd in nd.findall('.//cmds/accepts/cmd') + nd.findall('.//cmds/sends/cmd'):
                if 'editor' in cmd.attrib:
                    violations.append((nid, cmd.get('id'), cmd.attrib))
        self.assertEqual(violations, [], f"Illegal editor attribute found on <cmd> elements: {violations}")

    def test_dynamic_nodedefs_no_cmd_editor_attribute(self):
        """Dynamic JSON profile commands must not contain an 'editor' attribute."""
        dynamic_nodedefs = udiDynamicProfile.get_dynamic_profile_nodedefs(include_variants=True)
        violations = []
        for nd in dynamic_nodedefs:
            nid = nd.get('id')
            for cmd in nd.get('cmds', {}).get('accepts', []) + nd.get('cmds', {}).get('sends', []):
                if 'editor' in cmd:
                    violations.append((nid, cmd.get('id'), cmd))
        self.assertEqual(violations, [], f"Illegal editor key found in dynamic nodeDef cmds: {violations}")

    def test_onoff_devices_nodedef_structure(self):
        """On/off devices (switches, outlets, manipulators) must have valid ST drivers and commands."""
        dynamic_nodedefs = {nd['id']: nd for nd in udiDynamicProfile.get_dynamic_profile_nodedefs(include_variants=True)}
        expected_editors = {
            'YOSWITCH': ('ST', 'SWSTATE', ['DON', 'DOF']),
            'YOOUTLET': ('ST', 'SWSTATE', ['DON', 'DOF']),
            'YOOUTLETPWR': ('ST', 'SWSTATE', ['DON', 'DOF']),
            'YOSUBOUT': ('ST', 'SWSTATE', ['DON', 'DOF']),
            'YOSUBUSB': ('ST', 'USBSTATE', ['DON', 'DOF']),
            'YOMANIPU': ('ST', 'MANSTATE', ['MOPEN', 'MCLOSE']),
        }
        for node_id, (st_prop, expected_editor, expected_cmds) in expected_editors.items():
            self.assertIn(node_id, dynamic_nodedefs, f"Missing nodeDef {node_id}")
            nd = dynamic_nodedefs[node_id]
            props = {p.get('id'): p.get('editor') for p in nd.get('properties', [])}
            self.assertIn(st_prop, props, f"NodeDef {node_id} missing property {st_prop}")
            self.assertEqual(props[st_prop], expected_editor, f"NodeDef {node_id} property {st_prop} editor mismatch")
            accept_cmds = [c.get('id') for c in nd.get('cmds', {}).get('accepts', [])]
            for cmd in expected_cmds:
                self.assertIn(cmd, accept_cmds, f"NodeDef {node_id} missing command {cmd}")

    def test_all_editor_nls_keys_exist_in_en_us(self):
        """Every editor subset entry in editors.xml must have a corresponding NLS key in en_us.txt."""
        base_dir = os.path.dirname(__file__)
        nls_path = os.path.join(base_dir, 'profile', 'nls', 'en_us.txt')
        ed_path = os.path.join(base_dir, 'profile', 'editor', 'editors.xml')

        nls_keys = set()
        with open(nls_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    nls_keys.add(line.split('=', 1)[0].strip())

        tree = ET.parse(ed_path)
        missing_keys = []
        for ed in tree.findall('.//editor'):
            for r in ed.findall('range'):
                nls = r.get('nls')
                subset = r.get('subset')
                if nls and subset:
                    for part in subset.split(','):
                        part = part.strip()
                        if '-' in part and not part.startswith('-'):
                            start, end = part.split('-', 1)
                            for i in range(int(start), int(end) + 1):
                                k = f"{nls}-{i}"
                                if k not in nls_keys:
                                    missing_keys.append(k)
                        else:
                            k = f"{nls}-{part}"
                            if k not in nls_keys:
                                missing_keys.append(k)
        self.assertEqual(missing_keys, [], f"Missing NLS keys in en_us.txt: {missing_keys}")

    def test_dynamic_profile_compact_size(self):
        """Dynamic profile pruned payload with typical devices should stay comfortably under 60KB."""
        class MockController:
            temp_unit = 1
            water_unit = 0
            deviceList = [
                {'type': 'THSensor'}, {'type': 'Switch'}, {'type': 'Outlet'},
                {'type': 'MultiOutlet'}, {'type': 'SpeakerHub'}, {'type': 'LeakSensor'},
                {'type': 'MotionSensor'}, {'type': 'DoorSensor'}, {'type': 'Manipulator'}
            ]
        c = MockController()
        pruned = udiDynamicProfile.get_dynamic_profile_payload(controller=c, active_only=True)
        compact_json = json.dumps(pruned, separators=(',', ':'))
        byte_len = len(compact_json.encode('utf-8'))
        self.assertLess(byte_len, 60000, f"Pruned dynamic profile size {byte_len} exceeds 60KB limit")


if __name__ == '__main__':
    unittest.main()

