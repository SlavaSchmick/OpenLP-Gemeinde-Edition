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
Package to test the openlp.core.version package.
"""
from datetime import date
from unittest.mock import MagicMock, patch

import pytest
from requests.exceptions import ConnectionError

from openlp.core.version import VersionWorker, check_for_update, get_version, update_check_date


def test_worker_init():
    """
    Test the VersionWorker constructor
    """
    # GIVEN: A last check date and a current version
    last_check_date = '1970-01-01'
    current_version = '2.0'

    # WHEN: A worker is created
    worker = VersionWorker(last_check_date, current_version)

    # THEN: The correct attributes should have been set
    assert worker.last_check_date == last_check_date
    assert worker.current_version == current_version


RELEASE_JSON = '''{"tag_name": "v3.1.7+gemeinde.2", "html_url": "https://github.com/gemeinde/openlp/releases/tag/v3",
 "draft": false, "prerelease": false,
 "assets": [{"name": "OpenLP-Gemeinde-Edition-3.1.7-gemeinde.2-Setup-x64.exe",
             "browser_download_url": "https://github.com/gemeinde/openlp/releases/download/v3/setup.exe",
             "digest": "sha256:abc123"}]}'''
EXPECTED_URL = 'https://api.github.com/repos/gemeinde/openlp/releases/latest'
EXPECTED_HEADERS = {'User-Agent': 'OpenLP/3.1.7+gemeinde.1 Linux/4.12.0-1-amd64; ',
                    'Accept': 'application/vnd.github+json'}
CURRENT_VERSION = {'full': '3.1.7+gemeinde.1', 'version': '3.1.7', 'build': 'gemeinde.1'}


@pytest.fixture
def worker_env():
    """The platform and the GitHub repository of the edition, for the version worker"""
    with patch('openlp.core.version.platform') as mock_platform, \
            patch('openlp.core.edition.EDITION_REPOSITORY', 'gemeinde/openlp'):
        mock_platform.system.return_value = 'Linux'
        mock_platform.release.return_value = '4.12.0-1-amd64'
        yield


@patch('openlp.core.version.get_web_page')
def test_worker_start(mock_get_web_page, worker_env):
    """
    Test that the worker finds a newer release of the edition on GitHub
    """
    # GIVEN: A newer release on GitHub
    mock_get_web_page.return_value = RELEASE_JSON
    worker = VersionWorker('1970-01-01', CURRENT_VERSION)

    # WHEN: The worker is run
    with patch.object(worker, 'new_version') as mock_new_version, \
            patch.object(worker, 'quit') as mock_quit:
        worker.start()

    # THEN: The release with its setup is announced
    mock_get_web_page.assert_called_once_with(EXPECTED_URL, headers=EXPECTED_HEADERS)
    release = mock_new_version.emit.call_args[0][0]
    assert release.version == '3.1.7+gemeinde.2'
    assert release.setup_url == 'https://github.com/gemeinde/openlp/releases/download/v3/setup.exe'
    assert release.setup_sha256 == 'abc123'
    mock_quit.emit.assert_called_once_with()


@patch('openlp.core.version.get_web_page')
def test_worker_start_same_version(mock_get_web_page, worker_env):
    """
    Test that the running release is not announced again
    """
    # GIVEN: The running release is the latest one
    mock_get_web_page.return_value = RELEASE_JSON.replace('gemeinde.2', 'gemeinde.1')
    worker = VersionWorker('1970-01-01', CURRENT_VERSION)

    # WHEN: The worker is run
    with patch.object(worker, 'new_version') as mock_new_version, \
            patch.object(worker, 'quit'):
        worker.start()

    # THEN: Nothing is announced
    mock_new_version.emit.assert_not_called()


@patch('openlp.core.version.get_web_page')
def test_worker_start_fail(mock_get_web_page, worker_env):
    """
    Test that nothing is announced without an answer
    """
    # GIVEN: No answer from GitHub
    mock_get_web_page.return_value = None
    worker = VersionWorker('1970-01-01', CURRENT_VERSION)

    # WHEN: The worker is run
    with patch.object(worker, 'new_version') as mock_new_version, \
            patch.object(worker, 'quit') as mock_quit:
        worker.start()

    # THEN: Nothing is announced
    mock_get_web_page.assert_called_once_with(EXPECTED_URL, headers=EXPECTED_HEADERS)
    mock_new_version.emit.assert_not_called()
    mock_quit.emit.assert_called_once_with()


@patch('openlp.core.version.get_web_page')
def test_worker_invalid_answer(mock_get_web_page, worker_env):
    """
    Test that an answer which isn't JSON is ignored
    """
    # GIVEN: An answer which isn't JSON
    mock_get_web_page.return_value = '<html>Not found</html>'
    worker = VersionWorker('1970-01-01', CURRENT_VERSION)

    # WHEN: The worker is run
    with patch.object(worker, 'new_version') as mock_new_version, \
            patch.object(worker, 'quit') as mock_quit:
        worker.start()

    # THEN: Nothing is announced and the worker finishes
    mock_new_version.emit.assert_not_called()
    mock_quit.emit.assert_called_once_with()


@patch('openlp.core.version.get_web_page')
def test_worker_without_repository(mock_get_web_page):
    """
    Test that there is no update check without a GitHub repository, and never one on openlp.org
    """
    # GIVEN: No repository for the edition
    worker = VersionWorker('1970-01-01', CURRENT_VERSION)

    # WHEN: The worker is run
    with patch('openlp.core.edition.EDITION_REPOSITORY', ''), \
            patch.object(worker, 'new_version') as mock_new_version, \
            patch.object(worker, 'quit') as mock_quit:
        worker.start()

    # THEN: Nothing is downloaded or announced
    mock_get_web_page.assert_not_called()
    mock_new_version.emit.assert_not_called()
    mock_quit.emit.assert_called_once_with()


@patch('openlp.core.version.get_web_page')
def test_worker_start_connection_error(mock_get_web_page, worker_env):
    """
    Test the VersionWorkder.start() method when a ConnectionError happens
    """
    # GIVEN: GitHub can't be reached
    mock_get_web_page.side_effect = ConnectionError('Could not connect')
    worker = VersionWorker('1970-01-01', CURRENT_VERSION)

    # WHEN: The worker is run
    with patch.object(worker, 'no_internet') as mocked_no_internet, \
            patch.object(worker, 'quit') as mocked_quit:
        worker.start()

    # THEN: It is tried three times, and the check completes
    mock_get_web_page.assert_called_with(EXPECTED_URL, headers=EXPECTED_HEADERS)
    assert mock_get_web_page.call_count == 3
    mocked_no_internet.emit.assert_called_once_with()
    mocked_quit.emit.assert_called_once_with()


def test_update_check_date(mock_settings):
    """
    Test that the update_check_date() function writes the correct date
    """
    # GIVEN: A mocked Settings object
    # WHEN: update_check_date() is called
    update_check_date()

    # THEN: The correct date should have been saved
    mock_settings.setValue.assert_called_once_with('core/last version test', date.today().strftime('%Y-%m-%d'))


@patch('openlp.core.version.run_thread')
def test_check_for_update(mocked_run_thread, mock_settings):
    """
    Test the check_for_update() function
    """
    # GIVEN: A mocked settings object
    mock_settings.value.return_value = '1970-01-01'

    # WHEN: check_for_update() is called
    check_for_update(MagicMock())

    # THEN: The right things should have been called and a thread set in motion
    assert mocked_run_thread.call_count == 1


@patch('openlp.core.version.run_thread')
def test_check_for_update_at_every_start(mocked_run_thread, mock_settings):
    """
    Test that the check_for_update() function also runs when it already ran today, so that a new release is offered
    as soon as it is published
    """
    # GIVEN: A mocked settings object, with a check today
    mock_settings.value.return_value = date.today().strftime('%Y-%m-%d')

    # WHEN: check_for_update() is called
    check_for_update(MagicMock())

    # THEN: The version is checked again
    assert mocked_run_thread.call_count == 1


@pytest.mark.parametrize('in_version, out_version', [
    ('3.1.1', {'full': '3.1.1', 'version': '3.1.1', 'build': None}),
    ('3.0.2+git.cb1db9f43', {'full': '3.0.2+git.cb1db9f43', 'version': '3.0.2', 'build': 'git.cb1db9f43'}),
    ('3.1.2.dev15+gff6b05ed3', {'full': '3.1.2.dev15+gff6b05ed3', 'version': '3.1.2', 'build': 'gff6b05ed3'})
])
@patch('openlp.core.version.AppLocation.get_directory')
def test_get_version(mocked_get_directory: MagicMock, in_version: str, out_version: dict):
    """
    Test the get_version() function
    """
    # GIVEN: Some mocks and predefined versions
    mocked_path = MagicMock()
    mocked_path.__truediv__.return_value = mocked_path
    mocked_path.read_text.return_value = in_version
    mocked_get_directory.return_value = mocked_path

    # WHEN: get_version() is run
    with patch('openlp.core.version.APPLICATION_VERSION', None):
        version = get_version()

    # THEN: version is something
    assert version == out_version
