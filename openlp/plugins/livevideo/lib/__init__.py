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
The :mod:`~openlp.plugins.livevideo.lib` module contains the definitions shared by the Live Video plugin.

A live video source is stored in the database, and travels inside a service item as a plain dict (the "source spec")
so that a service file still knows which device to show when it is opened on another computer.
"""
from openlp.core.common.i18n import translate
from openlp.core.ui.media import parse_stream_path


# The prefix of the path of live video service items
SERVICE_PATH_PREFIX = 'livevideo'
# Resolutions offered for a source, the device decides what it actually delivers
RESOLUTIONS = [(3840, 2160), (2560, 1440), (1920, 1080), (1280, 720), (960, 540), (640, 480)]
# Used when no resolution is chosen. Every view of a device must ask for the same size, because a device that is
# shared between the screen and the preview panels runs at the size requested first.
AUTOMATIC_RESOLUTION = (1920, 1080)
FRAME_RATES = [60, 50, 30, 25, 24, 15]


class ScaleMode(object):
    """
    How the picture of a live video source is fitted to the screen. The values are CSS ``object-fit`` values.
    """
    Fit = 'contain'
    Fill = 'cover'
    Stretch = 'fill'

    @staticmethod
    def get_choices():
        """
        :return: A list of (value, translated name) tuples to show to the user
        """
        return [(ScaleMode.Fit, translate('LiveVideoPlugin', 'Fit – show the whole picture')),
                (ScaleMode.Fill, translate('LiveVideoPlugin', 'Fill – crop to the screen')),
                (ScaleMode.Stretch, translate('LiveVideoPlugin', 'Stretch to the screen'))]


def validate_scale_mode(scale_mode):
    """
    :param str scale_mode: A scale mode, e.g. from the settings
    :return: The scale mode if it is valid, otherwise "fit"
    """
    return scale_mode if scale_mode in (ScaleMode.Fit, ScaleMode.Fill, ScaleMode.Stretch) else ScaleMode.Fit


def resolution_to_string(width, height):
    """
    Convert a resolution into the string that is stored in the settings, e.g. "1920x1080"

    :param int width: The width, 0 for automatic
    :param int height: The height, 0 for automatic
    :return: The resolution as a string, or an empty string for automatic
    """
    if not width or not height:
        return ''
    return '{width}x{height}'.format(width=width, height=height)


def string_to_resolution(text):
    """
    Convert a resolution string such as "1920x1080" back into a resolution

    :param str text: The resolution as a string
    :return: A (width, height) tuple, (0, 0) for automatic or invalid values
    """
    try:
        width, height = (text or '').lower().split('x')
        return int(width), int(height)
    except ValueError:
        return 0, 0


def source_to_spec(source):
    """
    Create the source spec, which is stored in a service item, from a database source

    :param openlp.plugins.livevideo.lib.db.LiveVideoSource source: The source
    :return: The source spec
    :rtype: dict
    """
    return {
        'source_id': source.id,
        'title': source.title,
        'device_label': source.device_label,
        'width': source.width or 0,
        'height': source.height or 0,
        'frame_rate': source.frame_rate or 0,
        'scale_mode': validate_scale_mode(source.scale_mode),
        'mirror': bool(source.mirror)
    }


def spec_to_service_path(spec):
    """
    Create the path of a live video service item. Live video items are stream items, which OpenLP validates by parsing
    their path in the same format as device streams: "<prefix>:<name>&&<device>&&<options>".

    :param dict spec: The source spec
    :return: The path
    :rtype: str
    """
    def clean(text):
        return str(text or '').replace('&&', '&').strip() or '-'
    return '{prefix}:{title}&&{device}&&{scale_mode}'.format(prefix=SERVICE_PATH_PREFIX, title=clean(spec['title']),
                                                             device=clean(spec['device_label']),
                                                             scale_mode=clean(spec['scale_mode']))


def service_item_to_spec(service_item):
    """
    Get the source spec of a live video service item

    :param openlp.core.lib.serviceitem.ServiceItem service_item: The service item
    :return: The source spec
    :rtype: dict
    """
    if isinstance(service_item.data_string, dict) and service_item.data_string.get('device_label'):
        return dict(service_item.data_string)
    # The spec is missing, e.g. the service file was edited by hand, so recover what the path tells
    title, device_label, scale_mode = parse_stream_path(service_item.slides[0]['path'])
    return {'source_id': None, 'title': title, 'device_label': device_label, 'width': 0, 'height': 0, 'frame_rate': 0,
            'scale_mode': validate_scale_mode(scale_mode), 'mirror': False}


def spec_to_display_source(spec):
    """
    Create the source object which the display needs to show a source spec, see ``Display.setLiveVideo()``

    :param dict spec: The source spec
    :return: The source for the display
    :rtype: dict
    """
    width, height = spec.get('width') or 0, spec.get('height') or 0
    if not width or not height:
        width, height = AUTOMATIC_RESOLUTION
    return {
        'deviceLabel': spec.get('device_label', ''),
        'width': width,
        'height': height,
        'frameRate': spec.get('frame_rate') or 0,
        'scaleMode': validate_scale_mode(spec.get('scale_mode')),
        'mirror': bool(spec.get('mirror')),
        'strings': {
            'connecting': translate('LiveVideoPlugin', 'Connecting...'),
            'noSignal': translate('LiveVideoPlugin', 'No signal')
        }
    }
