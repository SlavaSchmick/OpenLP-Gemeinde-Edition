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
This module contains tests for the shared definitions of the Live Video plugin.
"""
from unittest.mock import MagicMock

from openlp.core.ui.media import parse_stream_path
from openlp.plugins.livevideo.lib import AUTOMATIC_RESOLUTION, ScaleMode, resolution_to_string, \
    service_item_to_spec, source_to_spec, spec_to_display_source, spec_to_service_path, string_to_resolution, \
    validate_scale_mode


SPEC = {
    'source_id': 3,
    'title': 'Stage camera',
    'device_label': 'HD Pro Webcam C920 (046d:082d)',
    'width': 1280,
    'height': 720,
    'frame_rate': 25,
    'scale_mode': ScaleMode.Fill,
    'mirror': True
}


def test_resolution_to_string():
    """
    Test that resolutions are converted to strings, and that automatic is an empty string
    """
    assert resolution_to_string(1920, 1080) == '1920x1080'
    assert resolution_to_string(0, 0) == ''
    assert resolution_to_string(None, None) == ''


def test_string_to_resolution():
    """
    Test that strings are converted to resolutions, and that invalid values become automatic
    """
    assert string_to_resolution('1920x1080') == (1920, 1080)
    assert string_to_resolution('') == (0, 0)
    assert string_to_resolution(None) == (0, 0)
    assert string_to_resolution('full hd') == (0, 0)


def test_validate_scale_mode():
    """
    Test that unknown scale modes fall back to fit
    """
    assert validate_scale_mode(ScaleMode.Fill) == ScaleMode.Fill
    assert validate_scale_mode(ScaleMode.Stretch) == ScaleMode.Stretch
    assert validate_scale_mode('zoom') == ScaleMode.Fit
    assert validate_scale_mode(None) == ScaleMode.Fit


def test_source_to_spec_with_defaults():
    """
    Test that a source without optional values becomes a complete spec
    """
    # GIVEN: A source with only the required values
    source = MagicMock(id=5, title='Camera', device_label='Integrated Camera', width=None, height=None,
                       frame_rate=None, scale_mode=None, mirror=None)

    # WHEN: Converting it to a spec
    spec = source_to_spec(source)

    # THEN: The spec should contain the defaults
    assert spec == {'source_id': 5, 'title': 'Camera', 'device_label': 'Integrated Camera', 'width': 0, 'height': 0,
                    'frame_rate': 0, 'scale_mode': ScaleMode.Fit, 'mirror': False}


def test_spec_to_service_path_can_be_parsed():
    """
    Test that the path of a service item passes the stream validation of service items
    """
    # GIVEN: A spec with the separator of stream paths in its title
    spec = dict(SPEC, title='Stage && Pulpit')

    # WHEN: Creating the path and parsing it like a stream path
    path = spec_to_service_path(spec)
    name, device, options = parse_stream_path(path)

    # THEN: The path should have all parts, without the separator in the title
    assert path.startswith('livevideo:')
    assert name == 'Stage & Pulpit'
    assert device == 'HD Pro Webcam C920 (046d:082d)'
    assert options == ScaleMode.Fill


def test_service_item_to_spec_from_data():
    """
    Test that the spec of a service item is taken from its data
    """
    # GIVEN: A service item with a spec
    service_item = MagicMock(data_string=SPEC)

    # WHEN: Getting the spec
    spec = service_item_to_spec(service_item)

    # THEN: A copy of the spec should be returned
    assert spec == SPEC
    assert spec is not SPEC


def test_service_item_to_spec_from_path():
    """
    Test that the spec of a service item without data is recovered from its path
    """
    # GIVEN: A service item without a spec
    service_item = MagicMock(data_string='', slides=[{'path': 'livevideo:Stage&&Integrated Camera&&cover'}])

    # WHEN: Getting the spec
    spec = service_item_to_spec(service_item)

    # THEN: The spec should contain what the path tells
    assert spec['source_id'] is None
    assert spec['title'] == 'Stage'
    assert spec['device_label'] == 'Integrated Camera'
    assert spec['scale_mode'] == ScaleMode.Fill
    assert spec['width'] == 0


def test_spec_to_display_source():
    """
    Test that a spec is converted to the source for the display
    """
    # WHEN: Converting a spec
    source = spec_to_display_source(SPEC)

    # THEN: The source should use the names of display.js
    assert source['deviceLabel'] == 'HD Pro Webcam C920 (046d:082d)'
    assert source['width'] == 1280
    assert source['height'] == 720
    assert source['frameRate'] == 25
    assert source['scaleMode'] == ScaleMode.Fill
    assert source['mirror'] is True
    assert set(source['strings'].keys()) == {'connecting', 'noSignal'}


def test_spec_to_display_source_automatic_resolution():
    """
    Test that the display always asks for the same size when the resolution is automatic, because a device that is
    shared between the screen and the preview panels runs at the size requested first.
    """
    # WHEN: Converting a spec with an automatic resolution
    source = spec_to_display_source(dict(SPEC, width=0, height=0, frame_rate=0))

    # THEN: The automatic resolution should be requested
    assert (source['width'], source['height']) == AUTOMATIC_RESOLUTION
    assert source['frameRate'] == 0
