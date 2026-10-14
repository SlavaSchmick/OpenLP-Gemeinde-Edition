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
This module contains tests for the library panel of the Live Video plugin.
"""
import hashlib
from pathlib import Path
from unittest.mock import MagicMock, PropertyMock, patch

import pytest

from openlp.core.common.registry import Registry
from openlp.core.lib.plugin import PluginStatus
from openlp.core.lib.serviceitem import ItemCapabilities, ServiceItem
from openlp.plugins.livevideo.lib import ScaleMode, source_to_spec, spec_to_service_path
from openlp.plugins.livevideo.lib.mediaitem import LiveVideoMediaItem


def make_source(source_id=3, title='Stage camera', device_label='HD Pro Webcam C920 (046d:082d)'):
    return MagicMock(id=source_id, title=title, device_label=device_label, width=1920, height=1080, frame_rate=30,
                     scale_mode=ScaleMode.Fill, mirror=False)


@pytest.fixture()
def media_item(mock_settings, temp_folder):
    Registry().register('main_window', MagicMock())
    with patch('openlp.core.lib.mediamanageritem.MediaManagerItem._setup'), \
            patch('openlp.plugins.livevideo.lib.mediaitem.LiveVideoMediaItem.setup_item'):
        m_item = LiveVideoMediaItem(None, MagicMock())
    m_item.plugin = MagicMock()
    m_item.plugin.name = 'livevideo'
    m_item.plugin.status = PluginStatus.Active
    m_item.settings_section = 'livevideo'
    with patch.object(LiveVideoMediaItem, 'thumbnail_path', new_callable=PropertyMock) as mocked_thumbnail_path:
        mocked_thumbnail_path.return_value = Path(temp_folder)
        yield m_item


def build_service_item(media_item, source):
    media_item.plugin.db_manager.get_object.return_value = source
    list_item = MagicMock()
    list_item.data.return_value = source.id
    service_item = ServiceItem(media_item.plugin)
    result = media_item.generate_slide_data(service_item, item=list_item)
    return result, service_item


def test_generate_slide_data(media_item):
    """
    Test that a source becomes a stream command item, which the slide controllers start through the message listener
    """
    # GIVEN: A source in the database
    source = make_source()

    # WHEN: Generating the service item
    result, service_item = build_service_item(media_item, source)

    # THEN: The service item should be a valid stream item which carries the source spec
    spec = source_to_spec(source)
    path = spec_to_service_path(spec)
    assert result is True
    assert service_item.is_command() is True
    assert service_item.is_capable(ItemCapabilities.CanStream) is True
    assert service_item.is_capable(ItemCapabilities.ProvidesOwnTheme) is True
    assert service_item.is_capable(ItemCapabilities.OnLoadUpdate) is True
    assert service_item.uses_file() is False
    assert service_item.is_media() is False
    assert service_item.is_valid is True
    assert service_item.title == 'Stage camera'
    assert service_item.edit_id == 3
    assert service_item.data_string == spec
    assert service_item.slides[0]['path'] == path
    assert service_item.sha256_file_hash == hashlib.sha256(path.encode('utf-8')).hexdigest()
    assert service_item.theme == -1


def test_generate_slide_data_missing_source(media_item):
    """
    Test that no service item is generated for a source that doesn't exist
    """
    # GIVEN: A source that is not in the database
    media_item.plugin.db_manager.get_object.return_value = None
    list_item = MagicMock()
    list_item.data.return_value = 42

    # WHEN: Generating the service item
    result = media_item.generate_slide_data(ServiceItem(media_item.plugin), item=list_item)

    # THEN: Nothing should be generated
    assert result is False


def test_service_load_uses_library_source(media_item):
    """
    Test that a service item from a service file shows the source with the same title from the library
    """
    # GIVEN: A service item from another computer and a library source with the same title but another device
    _, service_item = build_service_item(media_item, make_source(source_id=3, device_label='Laptop Camera'))
    library_source = make_source(source_id=7, title='STAGE CAMERA', device_label='Magewell USB Capture HDMI')
    media_item.plugin.db_manager.get_object_filtered.return_value = library_source

    # WHEN: Loading the service item
    item = media_item.service_load(service_item)

    # THEN: The library source should be used
    assert item is service_item
    assert item.edit_id == 7
    assert item.data_string['device_label'] == 'Magewell USB Capture HDMI'
    assert item.slides[0]['path'] == spec_to_service_path(source_to_spec(library_source))
    assert item.is_valid is True


def test_service_load_keeps_saved_source(media_item):
    """
    Test that a service item from a service file keeps its device when the library has no source with that title
    """
    # GIVEN: A service item and no library source with the same title
    _, service_item = build_service_item(media_item, make_source(device_label='Laptop Camera'))
    media_item.plugin.db_manager.get_object_filtered.return_value = None

    # WHEN: Loading the service item
    item = media_item.service_load(service_item)

    # THEN: The saved device should be kept, but the item can't be edited
    assert item.edit_id is None
    assert item.data_string['device_label'] == 'Laptop Camera'
    assert item.data_string['source_id'] is None


def test_service_load_inactive_plugin(media_item):
    """
    Test that service items are left alone when the plugin is inactive
    """
    # GIVEN: An inactive plugin
    _, service_item = build_service_item(media_item, make_source())
    media_item.plugin.status = PluginStatus.Inactive

    # WHEN: Loading the service item
    item = media_item.service_load(service_item)

    # THEN: The item should be unchanged
    assert item is service_item
    media_item.plugin.db_manager.get_object_filtered.assert_not_called()


def test_save_and_remove_thumbnail(media_item, temp_folder):
    """
    Test that thumbnails are saved from a data URL and removed again
    """
    # GIVEN: An image as a data URL
    data_url = 'data:image/jpeg;base64,' + 'aGVsbG8='

    # WHEN: Saving the thumbnail
    media_item.save_thumbnail(3, data_url)

    # THEN: The thumbnail should be used for the source
    thumbnail_path = Path(temp_folder) / 'source-3.jpg'
    assert thumbnail_path.read_bytes() == b'hello'
    assert media_item.get_thumbnail_path(3) == thumbnail_path

    # WHEN: Removing the thumbnail
    media_item.save_thumbnail(3, None)

    # THEN: The file should be gone
    assert thumbnail_path.exists() is False


def test_get_thumbnail_path_without_thumbnail(media_item):
    """
    Test that sources without a thumbnail use the placeholder
    """
    # GIVEN: A placeholder
    with patch.object(media_item, 'get_placeholder_thumbnail_path', return_value=Path('placeholder.png')):
        # WHEN: Getting the thumbnail of a source without one, and of a spec without a source
        # THEN: The placeholder should be used
        assert media_item.get_thumbnail_path(9) == Path('placeholder.png')
        assert media_item.get_thumbnail_path(None) == Path('placeholder.png')


def test_search(media_item):
    """
    Test that the search returns the id and the title of the sources, sorted by title
    """
    # GIVEN: Two sources
    first_source, second_source = MagicMock(id=1, title='Stage'), MagicMock(id=2, title='Pulpit')
    first_source.__lt__ = lambda self, other: False
    second_source.__lt__ = lambda self, other: True
    media_item.plugin.db_manager.get_all_objects.return_value = [first_source, second_source]

    # WHEN: Searching
    results = media_item.search('a', False)

    # THEN: The sources should be returned sorted
    assert results == [[2, 'Pulpit'], [1, 'Stage']]


def test_get_source_description():
    """
    Test the tool tip of a source
    """
    assert LiveVideoMediaItem.get_source_description(make_source()) == 'HD Pro Webcam C920 (046d:082d)\n' \
        '1920 × 1080, 30 fps'
    automatic_source = MagicMock(device_label='Integrated Camera', width=0, height=0, frame_rate=0)
    assert LiveVideoMediaItem.get_source_description(automatic_source) == 'Integrated Camera\nAutomatic resolution'
