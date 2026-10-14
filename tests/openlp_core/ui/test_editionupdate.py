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
Test the :mod:`openlp.core.ui.editionupdate` module, which installs a new release of the Gemeinde-Edition.
"""
import hashlib
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import requests
from PyQt5 import QtWidgets

from openlp.core.edition import EditionRelease
from openlp.core.ui import editionupdate

SETUP = b'MZ setup of the new release'
SETUP_SHA256 = hashlib.sha256(SETUP).hexdigest()


def make_release(sha256=SETUP_SHA256, setup_url='https://github.com/g/o/releases/download/v2/setup.exe'):
    return EditionRelease('3.1.7+gemeinde.2', 'https://github.com/g/o/releases/tag/v2', setup_url,
                          'OpenLP-Gemeinde-Edition-3.1.7-gemeinde.2-Setup-x64.exe', sha256)


def make_response(content=SETUP, status=200):
    """A streamed response of requests"""
    response = MagicMock()
    response.__enter__.return_value = response
    response.headers = {'content-length': str(len(content))}
    response.iter_content.return_value = [content[:10], content[10:]]
    if status != 200:
        response.raise_for_status.side_effect = requests.HTTPError(str(status))
    return response


@pytest.fixture
def update_env(settings, tmp_path):
    """The temporary folder and no dialogs"""
    with patch('openlp.core.ui.editionupdate.tempfile.mkdtemp', return_value=str(tmp_path)), \
            patch('openlp.core.ui.editionupdate.QtWidgets.QProgressDialog') as mocked_progress, \
            patch('openlp.core.ui.editionupdate.critical_error_message_box') as mocked_error:
        mocked_progress.return_value.wasCanceled.return_value = False
        yield tmp_path, mocked_progress, mocked_error


def test_download_setup(update_env):
    """
    Test that the setup is downloaded into the temporary folder and checked
    """
    tmp_path, _, mocked_error = update_env
    with patch('openlp.core.ui.editionupdate.requests.get', return_value=make_response()) as mocked_get:
        path = editionupdate.download_setup(None, make_release())

    assert path == tmp_path / 'OpenLP-Gemeinde-Edition-3.1.7-gemeinde.2-Setup-x64.exe'
    assert path.read_bytes() == SETUP
    assert mocked_get.call_args[0][0] == 'https://github.com/g/o/releases/download/v2/setup.exe'
    mocked_error.assert_not_called()


def test_download_setup_wrong_checksum(update_env):
    """
    Test that a damaged download is deleted and not started
    """
    tmp_path, _, mocked_error = update_env
    with patch('openlp.core.ui.editionupdate.requests.get', return_value=make_response(b'damaged')):
        path = editionupdate.download_setup(None, make_release())

    assert path is None
    assert list(tmp_path.iterdir()) == []
    mocked_error.assert_called_once()


def test_download_setup_http_error(update_env):
    """
    Test that an error page of the server is not saved as the setup
    """
    tmp_path, _, mocked_error = update_env
    with patch('openlp.core.ui.editionupdate.requests.get', return_value=make_response(status=404)):
        path = editionupdate.download_setup(None, make_release())

    assert path is None
    assert list(tmp_path.iterdir()) == []
    mocked_error.assert_called_once()


def test_download_setup_cancelled(update_env):
    """
    Test that a cancelled download is deleted
    """
    tmp_path, mocked_progress, mocked_error = update_env
    mocked_progress.return_value.wasCanceled.return_value = True
    with patch('openlp.core.ui.editionupdate.requests.get', return_value=make_response()):
        path = editionupdate.download_setup(None, make_release())

    assert path is None
    assert list(tmp_path.iterdir()) == []
    mocked_error.assert_not_called()


def test_offer_update_installs(settings):
    """
    Test that the setup is downloaded and started when the user wants to update, and OpenLP is closed for it
    """
    parent = MagicMock()
    with patch('openlp.core.ui.editionupdate.QtWidgets.QMessageBox.question',
               return_value=QtWidgets.QMessageBox.Yes), \
            patch('openlp.core.ui.editionupdate.download_setup', return_value=Path('setup.exe')) as mocked_download, \
            patch('openlp.core.ui.editionupdate.start_setup', return_value=True) as mocked_start:
        result = editionupdate.offer_update(parent, make_release())

    assert result is True
    mocked_download.assert_called_once()
    mocked_start.assert_called_once_with(Path('setup.exe'))
    parent.close.assert_called_once_with()


def test_offer_update_later(settings):
    """
    Test that nothing happens when the user doesn't want to update now
    """
    parent = MagicMock()
    with patch('openlp.core.ui.editionupdate.QtWidgets.QMessageBox.question', return_value=QtWidgets.QMessageBox.No), \
            patch('openlp.core.ui.editionupdate.download_setup') as mocked_download:
        result = editionupdate.offer_update(parent, make_release())

    assert result is False
    mocked_download.assert_not_called()
    parent.close.assert_not_called()


def test_offer_update_without_setup_opens_the_page(settings):
    """
    Test that a release without a setup leads to its page
    """
    with patch('openlp.core.ui.editionupdate.QtWidgets.QMessageBox.question',
               return_value=QtWidgets.QMessageBox.Yes), \
            patch('openlp.core.ui.editionupdate.webbrowser.open_new') as mocked_open, \
            patch('openlp.core.ui.editionupdate.download_setup') as mocked_download:
        result = editionupdate.offer_update(MagicMock(), make_release(setup_url=None))

    assert result is False
    mocked_open.assert_called_once_with('https://github.com/g/o/releases/tag/v2')
    mocked_download.assert_not_called()


def test_offer_update_setup_not_started(settings):
    """
    Test that OpenLP stays open when the setup can't be started, and the user is told where it is
    """
    parent = MagicMock()
    with patch('openlp.core.ui.editionupdate.QtWidgets.QMessageBox.question',
               return_value=QtWidgets.QMessageBox.Yes), \
            patch('openlp.core.ui.editionupdate.download_setup', return_value=Path('setup.exe')), \
            patch('openlp.core.ui.editionupdate.start_setup', return_value=False), \
            patch('openlp.core.ui.editionupdate.critical_error_message_box') as mocked_error:
        result = editionupdate.offer_update(parent, make_release())

    assert result is False
    mocked_error.assert_called_once()
    parent.close.assert_not_called()


@pytest.mark.skipif('not __import__("sys").platform.startswith("win")')
def test_start_setup_silently():
    """
    Test that the setup is started silently, so that it starts OpenLP again afterwards
    """
    with patch('ctypes.windll.shell32.ShellExecuteW', return_value=42) as mocked_execute:
        assert editionupdate.start_setup(Path('C:/temp/setup.exe')) is True
    mocked_execute.assert_called_once_with(None, 'open', str(Path('C:/temp/setup.exe')),
                                           '/SILENT /SUPPRESSMSGBOXES /NORESTART', None, 1)
