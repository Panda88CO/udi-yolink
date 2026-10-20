#!/usr/bin/env python3
"""
Test helper and mocking fixtures for udi-yolink unit tests.
Provides mocks for udi_interface, polyglot, YoAccess, and node instantiation.
"""

import sys
import os
import unittest
from unittest.mock import MagicMock, patch

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
            cls_drivers = getattr(self.__class__, 'drivers', [])
            self.drivers = [dict(d) for d in cls_drivers] if cls_drivers else []
            cls_commands = getattr(self.__class__, 'commands', {})
            self.commands = dict(cls_commands) if cls_commands else {}
            self.id = getattr(self.__class__, 'id', 'mock_id')

        def setDriver(self, *args, **kwargs):
            pass

        def reportCmd(self, *args, **kwargs):
            pass

        def reportDrivers(self):
            pass

    mock_udi.Node = MockNode
    mock_udi.LOGGER = MagicMock()
    sys.modules['udi_interface'] = mock_udi

# Ensure repository root is in sys.path
REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)


class MockPolyglot:
    """Mock Polyglot / PG3 interface."""

    def __init__(self):
        self.nodes = {}
        self.Notices = MagicMock()
        self.Notices.delete = MagicMock()
        self.POLL = 'poll'
        self.START = 'start'
        self.STOP = 'stop'
        self.ADDNODEDONE = 'addnodedone'
        self.CONFIGDONE = 'configdone'
        self.STARTDONE = 'startdone'

    def getValidAddress(self, addr):
        return str(addr)[:14].lower()

    def getValidName(self, name):
        return str(name)

    def getNode(self, addr):
        return self.nodes.get(addr, MagicMock())

    def addNode(self, node, conn_status=None, rename=True):
        self.nodes[node.address] = node
        return node

    def delNode(self, addr):
        if addr in self.nodes:
            del self.nodes[addr]

    def subscribe(self, event, handler, address=None):
        pass

    def updateProfile(self):
        pass

    def updateJsonProfile(self, payload, options=None):
        pass


class MockYoAccess:
    """Mock YoLink API access coordinator."""

    def __init__(self, temp_unit=0, water_unit=0, debug=False, local=False):
        self.temp_unit = temp_unit
        self.water_unit = water_unit
        self.debug = debug
        self.local = local

    def get_temp_unit(self):
        return self.temp_unit

    def set_temp_unit(self, unit):
        self.temp_unit = unit

    def get_water_unit(self):
        return self.water_unit

    def set_water_unit(self, unit):
        self.water_unit = unit

    def get_debug(self):
        return self.debug

    def set_debug(self, debug):
        self.debug = debug


def create_test_node(node_class, model_name='YS5008', dev_type='WaterMeterController',
                     name='TestNode', address='test_addr', temp_unit=0, water_unit=0, **extra_kwargs):
    """
    Factory helper to instantiate any udiYo*.py node class in a fully non-blocking test environment.
    """
    poly = MockPolyglot()
    yo_access = MockYoAccess(temp_unit=temp_unit, water_unit=water_unit)
    dev_info = {
        'modelName': model_name,
        'name': name,
        'type': dev_type,
        'deviceId': 'd88b4c01000001',
        'token': 'mock_token'
    }

    # Patch blocking startup calls
    with patch.object(node_class, 'wait_for_node_done', return_value=None):
        node = node_class(poly, address, address, name, yo_access, dev_info, **extra_kwargs)

    # Set flags so updateData / event handlers don't block
    node.node_ready = True
    node.system_ready = True
    node.configDone = True

    # Assign a mock node object with tracked setDriver calls
    node.node = MagicMock()
    return node, poly, yo_access
