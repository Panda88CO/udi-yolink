#!/usr/bin/env python3
"""
Unit test harness for udiYoSpeakerHub (udiYoSpeakerHubV4.py) and yolinkSpeakerHubV3.py.
Tests driver definitions, state updates, command processing (PLAY, MUTE, BEEP),
and dynamic profile TTS message generation.
"""

import sys
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
from udiYoSpeakerHubV4 import udiYoSpeakerHub
from yolinkSpeakerHubV3 import YoLinkSpeakerH
from udiDynamicProfile import get_dynamic_profile_editors, get_dynamic_profile_payload


class TestSpeakerHubDrivers(unittest.TestCase):
    """Test driver definitions and configuration for SpeakerHub node."""

    def test_driver_definitions(self):
        """Verify driver definitions match nodedefs and editors specifications."""
        self.assertEqual(udiYoSpeakerHub.id, 'YOSPEAKERH')
        driver_map = {d['driver']: d for d in udiYoSpeakerHub.drivers}

        # GV4 (Message index) MUST have UOM 25 to match MESSAGES editor (uom="25")
        self.assertIn('GV4', driver_map)
        self.assertEqual(driver_map['GV4']['uom'], 25)
        self.assertEqual(driver_map['GV4']['name'], 'Message')

        # ST (Nodeserver Status) MUST have UOM 25 to match STATUS editor
        self.assertIn('ST', driver_map)
        self.assertEqual(driver_map['ST']['uom'], 25)

        # GV0 (Volume) has UOM 56 (raw number)
        self.assertIn('GV0', driver_map)
        self.assertEqual(driver_map['GV0']['uom'], 56)

        # GV1 (Beep), GV2 (Mute), GV3 (Tone) have UOM 25
        self.assertEqual(driver_map['GV1']['uom'], 25)
        self.assertEqual(driver_map['GV2']['uom'], 25)
        self.assertEqual(driver_map['GV3']['uom'], 25)

        # GV5 (Repeat) has UOM 56
        self.assertEqual(driver_map['GV5']['uom'], 56)


class TestUdiYoSpeakerHubOperations(unittest.TestCase):
    """Test runtime operations and commands of udiYoSpeakerHub."""

    def setUp(self):
        self.poly = MagicMock()
        self.poly.getValidAddress.side_effect = lambda a: str(a)[:14]
        self.poly.getValidName.side_effect = lambda n: str(n)
        self.poly.getNode.return_value = MagicMock()

        self.yoAccess = MagicMock()
        self.yoAccess.TtsMessages = {
            0: 'Garage Door Opened',
            1: 'Entry through Garage',
            2: 'Garage Door Bell Pressed'
        }

        self.devInfo = {
            'modelName': 'YS1604-UC',
            'name': 'SY Speaker Hub',
            'type': 'SpeakerHub',
            'deviceId': 'd88b4c1604000b5c',
            'token': 'TEST_TOKEN'
        }

        with patch.object(udiYoSpeakerHub, 'wait_for_node_done', lambda self: None), \
             patch.object(udiYoSpeakerHub, 'apply_profile_driver_names', lambda self, nid: None):
            self.node = udiYoSpeakerHub(self.poly, 'test_addr', 'test_addr', 'SY Speaker Hub', self.yoAccess, self.devInfo)

        self.node.node_ready = True
        self.node.system_ready = True
        self.node.configDone = True

        # Mock internal yoSpeakerHub
        self.mock_speaker_hub = MagicMock()
        self.mock_speaker_hub.volume = 12
        self.mock_speaker_hub.beepEnabled = True
        self.mock_speaker_hub.mute = False
        self.mock_speaker_hub.suspended = False
        self.mock_speaker_hub.getLastUpdateTime.return_value = 1793851354
        self.mock_speaker_hub.get_message_type.return_value = ('method', 'getState')
        self.node.yoSpeakerHub = self.mock_speaker_hub

    def test_update_data_online_does_not_overwrite_st_with_message_number(self):
        """updateData must set ST to 1 when online, not overwrite it with messageNbr."""
        self.mock_speaker_hub.check_system_online.return_value = True
        self.node.messageNbr = 2  # Message index 2

        with patch.object(self.node, 'my_setDriver') as mock_set:
            self.node.updateData()

            # Inspect all driver updates sent
            st_calls = [c for c in mock_set.call_args_list if c[0][0] == 'ST']
            # ST should ONLY be set to 1, never to 2 (messageNbr)
            self.assertEqual(len(st_calls), 1)
            self.assertEqual(st_calls[0][0][1], 1)

            # Check that GV4 received the messageNbr
            gv4_calls = [c for c in mock_set.call_args_list if c[0][0] == 'GV4']
            self.assertEqual(len(gv4_calls), 1)
            self.assertEqual(gv4_calls[0][0][1], 2)

            # Check that volume, beep, mute were synced from speaker_hub
            self.assertEqual(self.node.volume, 12)
            self.assertEqual(self.node.beepEnabled, True)
            self.assertEqual(self.node.mute, False)

    def test_update_data_offline(self):
        """updateData must set ST to 0 and GV30 to 0 when offline."""
        self.mock_speaker_hub.check_system_online.return_value = False

        with patch.object(self.node, 'my_setDriver') as mock_set:
            self.node.updateData()
            calls = {c[0][0]: c[0][1] for c in mock_set.call_args_list}
            self.assertEqual(calls.get('ST'), 0)
            self.assertEqual(calls.get('GV30'), 0)
            self.assertEqual(calls.get('GV20'), 2)

    def test_play_message_new_with_uom_query(self):
        """playMessageNew should parse standard IoX query parameters and invoke speaker_hub.playAudio."""
        command = {
            'cmd': 'PLAY',
            'query': {
                'message.uom25': '1',
                'volume.uom56': '14',
                'tone.uom25': '2',
                'repeat.uom56': '3'
            }
        }

        with patch.object(self.node, 'my_setDriver') as mock_set:
            self.node.playMessageNew(command)

            self.mock_speaker_hub.playAudio.assert_called_once_with(
                'Entry through Garage', 'Alert', 14, 3
            )
            self.assertEqual(self.node.messageNbr, 1)
            self.assertEqual(self.node.volume, 14)
            self.assertEqual(self.node.tone, 'Alert')
            self.assertEqual(self.node.repeat, 3)

            # Verify driver updates to preserve last played settings in Admin Console
            calls = {c[0][0]: c[0][1] for c in mock_set.call_args_list}
            self.assertEqual(calls.get('GV4'), 1)
            self.assertEqual(calls.get('GV0'), 14)
            self.assertEqual(calls.get('GV3'), 2)
            self.assertEqual(calls.get('GV5'), 3)

    def test_play_message_new_resilient_to_missing_and_invalid_params(self):
        """playMessageNew should safely handle missing query parameters and unknown message indices."""
        # Query with non-existent message index
        command = {
            'cmd': 'PLAY',
            'query': {
                'message': '99',
                'volume': '8',
                'tone': '99',  # Out of range tone
                'repeat': '0'
            }
        }

        self.node.playMessageNew(command)
        # Should fall back to f"Message 99" and tone 'none' without crashing
        self.mock_speaker_hub.playAudio.assert_called_once_with(
            'Message 99', 'none', 8, 0
        )

        # None command
        self.mock_speaker_hub.reset_mock()
        self.node.playMessageNew(None)
        self.mock_speaker_hub.playAudio.assert_called_once()

    def test_set_mute_and_beep(self):
        """setMute and setBeepEnable should update drivers and call speaker_hub."""
        with patch.object(self.node, 'my_setDriver') as mock_set:
            self.node.setMute({'cmd': 'MUTE', 'value': '1'})
            self.assertTrue(self.node.mute)
            self.mock_speaker_hub.setMute.assert_called_once_with(True)

            self.node.setBeepEnable({'cmd': 'BEEP', 'value': '0'})
            self.assertFalse(self.node.beepEnabled)
            self.mock_speaker_hub.setBeepEnable.assert_called_once_with(False)


class TestYoLinkSpeakerHubV3(unittest.TestCase):
    """Test YoLinkSpeakerH communication class."""

    def test_play_audio_omits_none_tone(self):
        """playAudio should not send 'tone': 'none' to YoLink cloud."""
        yoAccess = MagicMock()
        yoAccess.publish_data.return_value = True
        devInfo = {'name': 'test_hub', 'type': 'SpeakerHub', 'deviceId': 'test_dev', 'token': 'test_tok'}

        with patch.object(YoLinkSpeakerH, 'timezoneOffsetSec', return_value=0):
            sh = YoLinkSpeakerH(yoAccess, devInfo, MagicMock())

        # Tone 'none'
        sh.playAudio('Test alert', 'none', 10, 0)
        published_payload = yoAccess.publish_data.call_args[0][0]
        self.assertNotIn('tone', published_payload['params'])
        self.assertEqual(published_payload['params']['message'], 'Test alert')

        # Tone 'Emergency'
        sh.playAudio('Fire alarm', 'Emergency', 16, 2)
        published_payload = yoAccess.publish_data.call_args[0][0]
        self.assertEqual(published_payload['params']['tone'], 'Emergency')

    def test_play_audio_truncates_long_message(self):
        """playAudio should truncate messages exceeding 200 characters."""
        yoAccess = MagicMock()
        yoAccess.publish_data.return_value = True
        devInfo = {'name': 'test_hub', 'type': 'SpeakerHub', 'deviceId': 'test_dev', 'token': 'test_tok'}

        with patch.object(YoLinkSpeakerH, 'timezoneOffsetSec', return_value=0):
            sh = YoLinkSpeakerH(yoAccess, devInfo, MagicMock())
        long_msg = 'A' * 300
        sh.playAudio(long_msg, 'Alert', 8, 0)
        published_payload = yoAccess.publish_data.call_args[0][0]
        self.assertEqual(len(published_payload['params']['message']), 200)

    def test_update_status_parses_options(self):
        """updateStatus should parse options on getState response."""
        yoAccess = MagicMock()
        devInfo = {'name': 'test_hub', 'type': 'SpeakerHub', 'deviceId': 'test_dev', 'token': 'test_tok'}
        with patch.object(YoLinkSpeakerH, 'timezoneOffsetSec', return_value=0):
            sh = YoLinkSpeakerH(yoAccess, devInfo, MagicMock())

        data = {
            'code': '000000',
            'method': 'SpeakerHub.getState',
            'data': {
                'options': {
                    'volume': 14,
                    'mute': True,
                    'enableBeep': False
                }
            }
        }
        sh.updateStatus(data)
        self.assertEqual(sh.volume, 14)
        self.assertTrue(sh.mute)
        self.assertFalse(sh.beepEnabled)


class TestDynamicProfileTtsIntegration(unittest.TestCase):
    """Test dynamic profile generation with custom TTS messages."""

    def test_dynamic_editors_populates_tts_messages(self):
        """get_dynamic_profile_editors should dynamically format MESSAGES editor."""
        messages = {
            0: 'Check sump 1 power',
            1: 'Check sump 2 power'
        }
        editors = get_dynamic_profile_editors(tts_messages=messages)
        msg_editor = next((e for e in editors if e.get('id') == 'MESSAGES'), None)
        self.assertIsNotNone(msg_editor)

        ranges = msg_editor.get('ranges', [])
        self.assertEqual(len(ranges), 1)
        r = ranges[0]
        self.assertEqual(r.get('uom'), '25')
        self.assertEqual(r.get('subset'), '0-1')
        self.assertEqual(r.get('names'), {
            '0': 'Check sump 1 power',
            '1': 'Check sump 2 power'
        })

    def test_dynamic_payload_resolves_tts_from_controller(self):
        """get_dynamic_profile_payload should extract TtsMessages from controller.yoAccess."""
        mock_controller = MagicMock()
        mock_controller.yoAccess.TtsMessages = {
            0: 'Front Gate Opened'
        }
        mock_controller.temp_unit = 0
        mock_controller.water_unit = 0

        payload = get_dynamic_profile_payload(controller=mock_controller)
        editors = payload.get('editors', [])
        msg_editor = next((e for e in editors if e.get('id') == 'MESSAGES'), None)
        self.assertIsNotNone(msg_editor)

        r = msg_editor['ranges'][0]
        self.assertEqual(r['subset'], '0')
        self.assertEqual(r['names'], {'0': 'Front Gate Opened'})


class TestSpeakerHubTtsParameters(unittest.TestCase):
    """Test dynamic synchronization of TTS parameter input lines matching NBR_TTS."""

    class MockCustomParams(dict):
        def delete(self, key):
            if key in self:
                del self[key]

    def setUp(self):
        self.patch_update = patch('udiCommonLib.udiTssProfileUpdate', return_value=False)
        self.patch_dyn = patch('udiCommonLib.update_dynamic_profile', return_value=None)
        self.mock_update = self.patch_update.start()
        self.mock_dyn = self.patch_dyn.start()
        self.addCleanup(self.patch_update.stop)
        self.addCleanup(self.patch_dyn.stop)

        self.controller = MagicMock()
        self.controller.poly = MagicMock()
        self.controller.poly.Notices = {}
        self.controller.yoAccess = MagicMock()
        self.controller.yoAccess.TtsMessages = {}
        self.controller.yoLocal = MagicMock()
        self.controller.yoLocal.TtsMessages = {}
        self.controller.TTSstr = 'TTS'
        self.controller.Parameters = self.MockCustomParams()

    def test_sync_tts_parameters_creates_single_input_line_when_nbr_tts_is_one(self):
        """When NBR_TTS = 1, exactly 1 input line (TTS0) should be created."""
        from udiCommonLib import sync_tts_parameters

        self.controller.Parameters['NBR_TTS'] = '1'
        sync_tts_parameters(self.controller)

        self.assertEqual(self.controller.nbrTTS, 1)
        self.assertIn('TTS0', self.controller.Parameters)
        self.assertEqual(self.controller.Parameters['TTS0'], 'Message 0')
        self.assertEqual(self.controller.yoAccess.TtsMessages, {0: 'Message 0'})
        self.assertEqual(self.controller.yoLocal.TtsMessages, {0: 'Message 0'})

    def test_sync_tts_parameters_creates_multiple_input_lines(self):
        """When NBR_TTS = 2, exactly 2 input lines (TTS0, TTS1) should be created."""
        from udiCommonLib import sync_tts_parameters

        self.controller.Parameters['NBR_TTS'] = '2'
        sync_tts_parameters(self.controller)

        self.assertEqual(self.controller.nbrTTS, 2)
        self.assertEqual(self.controller.Parameters['TTS0'], 'Message 0')
        self.assertEqual(self.controller.Parameters['TTS1'], 'Message 1')
        self.assertNotIn('TTS2', self.controller.Parameters)
        self.assertEqual(self.controller.yoAccess.TtsMessages, {0: 'Message 0', 1: 'Message 1'})

    def test_sync_tts_parameters_preserves_custom_messages(self):
        """Existing custom message text must be preserved when new lines are added."""
        from udiCommonLib import sync_tts_parameters

        self.controller.Parameters['NBR_TTS'] = '2'
        self.controller.Parameters['TTS0'] = 'Front door opened'
        sync_tts_parameters(self.controller)

        self.assertEqual(self.controller.Parameters['TTS0'], 'Front door opened')
        self.assertEqual(self.controller.Parameters['TTS1'], 'Message 1')
        self.assertEqual(self.controller.yoAccess.TtsMessages, {0: 'Front door opened', 1: 'Message 1'})

    def test_sync_tts_parameters_removes_excess_lines_when_nbr_tts_decreases(self):
        """When NBR_TTS is reduced from 3 to 1, extra lines TTS1 and TTS2 must be deleted."""
        from udiCommonLib import sync_tts_parameters

        self.controller.Parameters['NBR_TTS'] = '1'
        self.controller.Parameters['TTS0'] = 'Keep this'
        self.controller.Parameters['TTS1'] = 'Remove this'
        self.controller.Parameters['TTS2'] = 'Remove this too'
        sync_tts_parameters(self.controller)

        self.assertEqual(self.controller.nbrTTS, 1)
        self.assertEqual(self.controller.Parameters['TTS0'], 'Keep this')
        self.assertNotIn('TTS1', self.controller.Parameters)
        self.assertNotIn('TTS2', self.controller.Parameters)
        self.assertEqual(self.controller.yoAccess.TtsMessages, {0: 'Keep this'})

    def test_sync_tts_parameters_zero_removes_all_tts(self):
        """When NBR_TTS is 0, all TTS parameter lines should be removed."""
        from udiCommonLib import sync_tts_parameters

        self.controller.Parameters['NBR_TTS'] = '0'
        self.controller.Parameters['TTS0'] = 'Old message'
        sync_tts_parameters(self.controller)

        self.assertEqual(self.controller.nbrTTS, 0)
        self.assertNotIn('TTS0', self.controller.Parameters)
        self.assertEqual(self.controller.yoAccess.TtsMessages, {})

    def test_sync_tts_parameters_normalizes_case(self):
        """Keys like 'tts0' should be normalized to 'TTS0' and preserve user content."""
        from udiCommonLib import sync_tts_parameters

        self.controller.Parameters['NBR_TTS'] = '1'
        self.controller.Parameters['tts0'] = 'Custom case'
        sync_tts_parameters(self.controller)

        self.assertEqual(self.controller.Parameters['TTS0'], 'Custom case')
        self.assertNotIn('tts0', self.controller.Parameters)


if __name__ == '__main__':
    unittest.main()
