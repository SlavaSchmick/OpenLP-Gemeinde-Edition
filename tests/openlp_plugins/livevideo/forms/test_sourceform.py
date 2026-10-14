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
This module contains tests for the source dialog of the Live Video plugin.
"""
from unittest.mock import MagicMock, patch

import pytest

from openlp.core.common.registry import Registry
from openlp.plugins.livevideo.forms.sourceform import SourceForm
from openlp.plugins.livevideo.lib import ScaleMode


@pytest.fixture
def form(settings):
    Registry().register('main_window', MagicMock())
    with patch.object(SourceForm, 'create_preview'):
        source_form = SourceForm(MagicMock(), None, MagicMock())
    yield source_form
    del source_form


def test_new_source_uses_the_default_settings(form, settings):
    """
    Test that a new source starts with the defaults from the settings tab
    """
    # GIVEN: Defaults for new sources
    settings.setValue('livevideo/default resolution', '1280x720')
    settings.setValue('livevideo/default frame rate', 50)
    settings.setValue('livevideo/default scale mode', ScaleMode.Stretch)

    # WHEN: Adding a new source
    form.load_source(0)

    # THEN: The defaults should be selected
    assert form.resolution_combo_box.currentData() == '1280x720'
    assert form.frame_rate_combo_box.currentData() == 50
    assert form.scale_mode_combo_box.currentData() == ScaleMode.Stretch
    assert form.mirror_check_box.isChecked() is False


def test_new_source_is_named_after_the_video_input(form):
    """
    Test that a new source takes the name of the selected video input, without the USB ids
    """
    # GIVEN: A new source
    form.load_source(0)

    # WHEN: The video inputs are found
    form.on_devices_changed(['HD Pro Webcam C920 (046d:082d)', 'OBS Virtual Camera'])

    # THEN: The first video input should be selected and give the source its name
    assert form.device_combo_box.currentData() == 'HD Pro Webcam C920 (046d:082d)'
    assert form.title_edit.text() == 'HD Pro Webcam C920'

    # WHEN: Another video input is selected
    form.device_combo_box.setCurrentIndex(1)

    # THEN: The name should follow
    assert form.title_edit.text() == 'OBS Virtual Camera'


def test_typed_name_is_kept(form):
    """
    Test that a name typed by the user doesn't change when another video input is selected
    """
    # GIVEN: A new source with a name typed by the user
    form.load_source(0)
    form.on_devices_changed(['HD Pro Webcam C920', 'OBS Virtual Camera'])
    form.title_edit.setText('Stage')

    # WHEN: Another video input is selected
    form.device_combo_box.setCurrentIndex(1)

    # THEN: The name should be kept
    assert form.title_edit.text() == 'Stage'


def test_disconnected_video_input_stays_selected(form):
    """
    Test that the video input of an existing source stays selected when it is not connected
    """
    # GIVEN: An existing source with a video input that is not connected
    form.manager.get_object.return_value = MagicMock(id=4, title='Stage', device_label='Magewell USB Capture HDMI',
                                                     width=1280, height=720, frame_rate=25,
                                                     scale_mode=ScaleMode.Fill, mirror=True)
    form.load_source(4)

    # WHEN: The video inputs are found
    form.on_devices_changed(['Integrated Camera'])

    # THEN: The video input of the source should still be selected, and the settings loaded
    assert form.device_combo_box.count() == 2
    assert form.device_combo_box.currentData() == 'Magewell USB Capture HDMI'
    assert form.title_edit.text() == 'Stage'
    assert form.resolution_combo_box.currentData() == '1280x720'
    assert form.frame_rate_combo_box.currentData() == 25
    assert form.scale_mode_combo_box.currentData() == ScaleMode.Fill
    assert form.mirror_check_box.isChecked() is True


def test_accept_requires_a_name(form):
    """
    Test that a source without a name is not saved
    """
    # GIVEN: A new source without a name
    form.load_source(0)
    form.on_devices_changed(['Integrated Camera'])
    form.title_edit.setText('')

    # WHEN: Saving
    with patch('openlp.plugins.livevideo.forms.sourceform.critical_error_message_box') as mocked_error:
        form.accept()

    # THEN: An error should be shown and nothing saved
    mocked_error.assert_called_once()
    form.manager.save_object.assert_not_called()


def test_accept_requires_a_video_input(form):
    """
    Test that a source without a video input is not saved
    """
    # GIVEN: A new source with a name but no video inputs
    form.load_source(0)
    form.on_devices_changed([])
    form.title_edit.setText('Stage')

    # WHEN: Saving
    with patch('openlp.plugins.livevideo.forms.sourceform.critical_error_message_box') as mocked_error:
        form.accept()

    # THEN: An error should be shown and nothing saved
    mocked_error.assert_called_once()
    form.manager.save_object.assert_not_called()


def test_save_source(form):
    """
    Test that the settings of the dialog and the thumbnail are saved
    """
    # GIVEN: A new source with its settings
    form.load_source(0)
    form.on_devices_changed(['Integrated Camera'])
    form.title_edit.setText('Pulpit')
    form.resolution_combo_box.setCurrentIndex(form.resolution_combo_box.findData('1280x720'))
    form.mirror_check_box.setChecked(True)

    # WHEN: Saving with a snapshot
    form.save_source('data:image/jpeg;base64,aGVsbG8=')

    # THEN: The source and the thumbnail should be saved
    form.manager.save_object.assert_called_once_with(form.source)
    assert form.source.title == 'Pulpit'
    assert form.source.device_label == 'Integrated Camera'
    assert (form.source.width, form.source.height) == (1280, 720)
    assert form.source.mirror is True
    form.media_item.save_thumbnail.assert_called_once_with(form.source.id, 'data:image/jpeg;base64,aGVsbG8=')


def test_save_source_without_snapshot_keeps_thumbnail(form):
    """
    Test that the thumbnail is kept when there is no picture, e.g. because the camera is not connected
    """
    # GIVEN: A source
    form.load_source(0)
    form.on_devices_changed(['Integrated Camera'])

    # WHEN: Saving without a snapshot
    form.save_source(None)

    # THEN: The thumbnail should not be touched
    form.media_item.save_thumbnail.assert_not_called()


def test_preview_failure_messages(form):
    """
    Test that the reason of a failed preview is explained to the user
    """
    form.on_preview_failed('in-use')
    assert 'another program' in form.preview_info_label.text()

    form.on_preview_failed('something unexpected')
    assert 'could not be started' in form.preview_info_label.text()
