# -*- coding: utf-8 -*-

##########################################################################
# OpenLP - Open Source Lyrics Projection                                 #
# ---------------------------------------------------------------------- #
# Copyright (c) 2008-2024 OpenLP Developers                              #
# ---------------------------------------------------------------------- #
# This program is free software: you can redistribute it and/or modify   #
# it under the terms of the GNU General Public License as published by   #
# the Free Software Foundation, either version 3 of the License, or      #
# (at your option) any later version.                                    #
#                                                                        #
# This program is distributed in the hope that it will be useful,        #
# but WITHOUT ANY WARRANTY; without even the implied warranty of         #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          #
# GNU General Public License for more details.                           #
#                                                                        #
# You should have received a copy of the GNU General Public License      #
# along with this program.  If not, see <https://www.gnu.org/licenses/>. #
##########################################################################
"""
Test the choice of the audio output for videos and background audio, e.g. live to Dante and preview to headphones.
"""
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from openlp.core.ui.media.mediatab import MediaTab
from openlp.core.ui.media.vlcplayer import enumerate_audio_output_devices, set_audio_output_device


DANTE_ID = '{0.0.0.00000000}.{11111111-2222-3333-4444-555555555555}'
SPEAKERS_ID = '{0.0.0.00000000}.{0754aa56-f799-44a2-b435-b184764e49eb}'


def make_device_list(devices):
    """
    Build a linked list like the one libvlc_audio_output_device_list_get() returns
    """
    item = None
    for device_id, name in reversed(devices):
        item = SimpleNamespace(contents=SimpleNamespace(device=device_id.encode('utf-8'),
                                                        description=name.encode('utf-8'), next=item))
    return item


def make_controller(is_live=True):
    media_player = MagicMock()
    media_player.audio_output_device_enum.return_value = make_device_list([
        ('', 'Default'), (SPEAKERS_ID, 'Lautsprecher (Realtek(R) Audio)'), (DANTE_ID, 'Dante Via (Dante Via)')])
    return SimpleNamespace(is_live=is_live, vlc_media_player=media_player)


@pytest.fixture
def mocked_vlc():
    with patch('openlp.core.ui.media.vlcplayer.get_vlc') as mocked_get_vlc:
        yield mocked_get_vlc.return_value


def test_enumerate_audio_output_devices(mocked_vlc):
    """
    Test that the devices are listed without the system default and that the list is released
    """
    media_player = make_controller().vlc_media_player

    devices = enumerate_audio_output_devices(media_player)

    assert devices == [(SPEAKERS_ID, 'Lautsprecher (Realtek(R) Audio)'), (DANTE_ID, 'Dante Via (Dante Via)')]
    mocked_vlc.libvlc_audio_output_device_list_release.assert_called_once()


def test_live_sound_goes_to_the_chosen_device(mocked_vlc, mock_settings):
    """
    Test that the live sound goes to the device chosen for live
    """
    mock_settings.value.side_effect = lambda key: {
        'media/live audio device': {'id': DANTE_ID, 'name': 'Dante Via (Dante Via)'},
        'media/preview audio device': {'id': SPEAKERS_ID, 'name': 'Lautsprecher (Realtek(R) Audio)'}}[key]
    live_controller, preview_controller = make_controller(True), make_controller(False)

    set_audio_output_device(live_controller)
    set_audio_output_device(preview_controller)

    live_controller.vlc_media_player.audio_output_device_set.assert_called_once_with(None, DANTE_ID)
    preview_controller.vlc_media_player.audio_output_device_set.assert_called_once_with(None, SPEAKERS_ID)


def test_device_is_found_by_name(mocked_vlc, mock_settings):
    """
    Test that a device whose id has changed, e.g. after reinstalling the driver, is found by its name
    """
    mock_settings.value.return_value = {'id': '{0.0.0.00000000}.{old-id}', 'name': 'Dante Via (Dante Via)'}
    controller = make_controller()

    set_audio_output_device(controller)

    controller.vlc_media_player.audio_output_device_set.assert_called_once_with(None, DANTE_ID)


def test_missing_device_uses_the_system_default(mocked_vlc, mock_settings):
    """
    Test that the sound goes to the system default when the chosen device is not available
    """
    mock_settings.value.return_value = {'id': '{0.0.0.00000000}.{gone}', 'name': 'Dante Virtual Soundcard'}
    controller = make_controller()

    set_audio_output_device(controller)

    controller.vlc_media_player.audio_output_device_set.assert_called_once_with(None, '')


def test_system_default(mocked_vlc, mock_settings):
    """
    Test that the system default is selected without asking VLC for the devices
    """
    mock_settings.value.return_value = {'id': '', 'name': ''}
    controller = make_controller()

    set_audio_output_device(controller)

    controller.vlc_media_player.audio_output_device_enum.assert_not_called()
    controller.vlc_media_player.audio_output_device_set.assert_called_once_with(None, '')


def test_fill_audio_output_combo_box(settings):
    """
    Test the choice of audio outputs in the media settings, including a chosen device that is not connected
    """
    combo_box = MagicMock()
    items = []
    combo_box.addItem.side_effect = lambda text, data: items.append((text, data))
    combo_box.count.side_effect = lambda: len(items)
    combo_box.itemData.side_effect = lambda index: items[index][1]
    devices = [(SPEAKERS_ID, 'Lautsprecher (Realtek(R) Audio)')]

    MediaTab.fill_audio_output_combo_box(combo_box, devices, {'id': DANTE_ID, 'name': 'Dante Via (Dante Via)'})

    assert [text for text, _ in items] == ['System default', 'Lautsprecher (Realtek(R) Audio)',
                                           'Dante Via (Dante Via) (not connected)']
    combo_box.setCurrentIndex.assert_called_once_with(2)


def test_audio_outputs_are_saved_after_the_tab_was_shown(settings):
    """
    Test that the audio outputs are listed when the tab is shown, and saved with the other media settings
    """
    with patch('openlp.core.ui.media.mediatab.get_audio_output_devices',
               return_value=[(DANTE_ID, 'Dante Via (Dante Via)')]):
        tab = MediaTab(None)
        tab.tab_visible()
    tab.live_audio_combo_box.setCurrentIndex(1)

    tab.save()

    assert settings.value('media/live audio device') == {'id': DANTE_ID, 'name': 'Dante Via (Dante Via)'}
    assert settings.value('media/preview audio device') == {'id': '', 'name': ''}
