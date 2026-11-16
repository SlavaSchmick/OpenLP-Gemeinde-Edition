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
Tests for the upload of presentations from the web remote (OpenLP Gemeinde-Edition)
"""
from io import BytesIO
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from openlp.core.common.enum import PluginStatus
from openlp.core.common.registry import Registry
from openlp.core.api.versions.v2.plugins import safe_file_name


@pytest.fixture
def presentations_plugin(registry):
    plugin = MagicMock(status=PluginStatus.Active)
    plugin.media_item.supported_suffixes.return_value = ['pptx', 'pdf', 'odp']
    Registry().register('plugin_manager', MagicMock(**{'get_plugin_by_name.return_value': plugin}))
    return plugin


@pytest.fixture
def upload_folder(temp_folder):
    with patch('openlp.core.api.versions.v2.plugins.AppLocation.get_section_data_path',
               return_value=Path(temp_folder)):
        yield Path(temp_folder) / 'uploads'


def upload(flask_client, name, content=b'presentation'):
    return flask_client.post('/api/v2/plugins/presentations/upload', data={'file': (BytesIO(content), name)},
                             content_type='multipart/form-data')


@pytest.mark.parametrize('name, expected', [
    ('Gemeindefest.pptx', 'Gemeindefest.pptx'),
    ('C:\\Users\\x\\Gemeindefest.pptx', 'Gemeindefest.pptx'),
    ('../../evil/Gemeindefest.pdf', 'Gemeindefest.pdf'),
    ('Праздник урожая.pptx', 'Праздник урожая.pptx'),
    ('Was?: "Fest" <2026>.pptx', 'Was__ _Fest_ _2026_.pptx'),
    ('..', ''),
    ('', ''),
    (None, ''),
])
def test_safe_file_name(name, expected):
    """The file name keeps letters of every language, but no folders and no forbidden characters"""
    assert safe_file_name(name) == expected


def test_upload_saves_and_adds_presentation(flask_client, settings, presentations_plugin, upload_folder):
    """An uploaded presentation is saved in the data folder and added to OpenLP"""
    # WHEN: A presentation is uploaded
    res = upload(flask_client, 'Gemeindefest.pptx', b'slides')

    # THEN: It is saved and handed to the media item, the answer has its id and title
    target = upload_folder / 'Gemeindefest.pptx'
    assert res.status_code == 201
    assert target.read_bytes() == b'slides'
    assert res.get_json() == {'id': str(target), 'title': 'Gemeindefest.pptx'}
    presentations_plugin.media_item.presentations_uploaded.emit.assert_called_once_with([str(target)])


def test_upload_does_not_overwrite(flask_client, settings, presentations_plugin, upload_folder):
    """A second presentation with the same name gets a number, the first one stays"""
    # GIVEN: A presentation which was uploaded before
    upload(flask_client, 'Fest.pdf', b'first')

    # WHEN: Another one with the same name is uploaded
    res = upload(flask_client, 'Fest.pdf', b'second')

    # THEN: Both are there
    assert res.get_json()['title'] == 'Fest (2).pdf'
    assert (upload_folder / 'Fest.pdf').read_bytes() == b'first'
    assert (upload_folder / 'Fest (2).pdf').read_bytes() == b'second'


def test_upload_unsupported_format(flask_client, settings, presentations_plugin, upload_folder):
    """A file which no presentation program can show is refused and not saved"""
    res = upload(flask_client, 'virus.exe')

    assert res.status_code == 415
    assert not (upload_folder / 'virus.exe').exists()
    presentations_plugin.media_item.presentations_uploaded.emit.assert_not_called()


def test_upload_without_file(flask_client, settings, presentations_plugin, upload_folder):
    """A request without a file is refused"""
    res = flask_client.post('/api/v2/plugins/presentations/upload', data={}, content_type='multipart/form-data')

    assert res.status_code == 400


def test_upload_presentations_inactive(flask_client, settings, presentations_plugin, upload_folder):
    """Without the active presentations plugin nothing is uploaded"""
    presentations_plugin.status = PluginStatus.Inactive

    res = upload(flask_client, 'Fest.pdf')

    assert res.status_code == 404
    assert not (upload_folder / 'Fest.pdf').exists()
