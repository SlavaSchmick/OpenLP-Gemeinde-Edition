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
This module contains tests for the message listener of the Live Video plugin.
"""
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from openlp.core.common.enum import ServiceItemType
from openlp.core.common.registry import Registry
from openlp.core.ui import HideMode
from openlp.plugins.livevideo.lib import ScaleMode, spec_to_display_source
from openlp.plugins.livevideo.lib.messagelistener import LiveVideoMessageListener


SPEC = {'source_id': 1, 'title': 'Stage', 'device_label': 'Integrated Camera', 'width': 0, 'height': 0,
        'frame_rate': 0, 'scale_mode': ScaleMode.Fit, 'mirror': False}


@pytest.fixture
def listener(registry, mock_settings):
    return LiveVideoMessageListener('livevideo')


def make_service_item(name='livevideo'):
    service_item = MagicMock()
    service_item.name = name
    service_item.title = 'Stage'
    service_item.data_string = SPEC
    service_item.get_theme_data.return_value = 'theme data'
    service_item.get_rendered_frame.return_value = Path('thumbnail.jpg')
    return service_item


def make_controller(is_live, displays=None):
    controller = MagicMock()
    controller.is_live = is_live
    controller.displays = displays or []
    return controller


def test_events_are_registered(listener):
    """
    Test that the listener answers the events of the slide controllers
    """
    for event in ['start', 'stop', 'blank', 'unblank', 'next', 'previous', 'slide']:
        assert Registry().has_function('livevideo_{event}'.format(event=event)), event


def test_start_live(listener):
    """
    Test that a live video item which goes live is shown in the live panel and on all screens
    """
    # GIVEN: A live controller with a screen
    display = MagicMock()
    live_controller = make_controller(True, [display])
    Registry().register('live_controller', live_controller)
    service_item = make_service_item()

    # WHEN: The item goes live
    listener.on_start([service_item, True, None, 0])

    # THEN: The live panel and the screen should show the source with the theme of an image
    source = spec_to_display_source(SPEC)
    for target in (live_controller.preview_display, display):
        target.set_theme.assert_called_once_with('theme data', service_item_type=ServiceItemType.Image)
        target.load_live_video.assert_called_once_with(source)


def test_start_preview_with_live_picture(listener, mock_settings):
    """
    Test that the Preview panel shows the live picture when that is enabled
    """
    # GIVEN: A preview controller and the live picture setting enabled
    mock_settings.value.return_value = True
    preview_controller = make_controller(False)
    Registry().register('preview_controller', preview_controller)

    # WHEN: The item is previewed
    listener.on_start([make_service_item(), False, None, 0])

    # THEN: The live picture should be shown
    preview_controller.preview_display.load_live_video.assert_called_once()
    preview_controller.preview_display.set_single_image.assert_not_called()


def test_start_preview_with_still_image(listener, mock_settings):
    """
    Test that the Preview panel shows the thumbnail when the live picture is disabled
    """
    # GIVEN: A preview controller and the live picture setting disabled
    mock_settings.value.return_value = False
    preview_controller = make_controller(False)
    Registry().register('preview_controller', preview_controller)

    # WHEN: The item is previewed
    listener.on_start([make_service_item(), False, None, 0])

    # THEN: The thumbnail should be shown instead of the live picture
    preview_controller.preview_display.set_single_image.assert_called_once_with('#000', Path('thumbnail.jpg'))
    preview_controller.preview_display.load_live_video.assert_not_called()


def test_stop_shows_current_live_video_item(listener):
    """
    Test that the current item is shown when the slide controller replaced a live video item with one that looks the
    same, since the slide controller doesn't send a start event then.
    """
    # GIVEN: A live controller which shows a live video item
    display = MagicMock()
    live_controller = make_controller(True, [display])
    live_controller.service_item = make_service_item()
    Registry().register('live_controller', live_controller)

    # WHEN: The old item is stopped
    listener.on_stop([make_service_item(), True])

    # THEN: The current item should be shown
    display.load_live_video.assert_called_once_with(spec_to_display_source(SPEC))


def test_stop_does_nothing_for_other_items(listener):
    """
    Test that nothing is shown when a live video item is replaced by another kind of item
    """
    # GIVEN: A live controller which shows a song
    display = MagicMock()
    live_controller = make_controller(True, [display])
    live_controller.service_item = make_service_item(name='songs')
    Registry().register('live_controller', live_controller)

    # WHEN: The live video item is stopped
    listener.on_stop([make_service_item(), True])

    # THEN: The displays should be left alone, they release the device by themselves
    display.load_live_video.assert_not_called()


def test_blank_and_unblank_live(listener):
    """
    Test that blanking and unblanking a live video item hides and shows the screens
    """
    # GIVEN: Listeners for the screens
    mocked_hide = MagicMock(return_value=None)
    mocked_show = MagicMock(return_value=None)
    Registry().register_function('live_display_hide', mocked_hide)
    Registry().register_function('live_display_show', mocked_show)

    # WHEN: Blanking and unblanking the live item
    listener.on_blank([make_service_item(), True, HideMode.Theme])
    listener.on_unblank([make_service_item(), True])

    # THEN: The screens should be hidden to the theme and shown again
    mocked_hide.assert_called_once_with(HideMode.Theme)
    mocked_show.assert_called_once_with()


def test_blank_preview_does_nothing(listener):
    """
    Test that blanking only affects the live screens
    """
    # GIVEN: A listener for hiding the screens
    mocked_hide = MagicMock(return_value=None)
    Registry().register_function('live_display_hide', mocked_hide)

    # WHEN: Blanking in the preview
    listener.on_blank([make_service_item(), False, HideMode.Blank])

    # THEN: The screens should not be hidden
    mocked_hide.assert_not_called()


def test_next_and_previous_leave_the_item(listener):
    """
    Test that a live video item tells the slide controller that it has no other slides, so that the next and previous
    keys move on to the next and previous service item
    """
    assert listener.on_next([make_service_item(), True]) is True
    assert listener.on_previous([make_service_item(), True]) is True
