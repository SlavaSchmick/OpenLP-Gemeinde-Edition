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
Test the :mod:`openlp.core.edition` module, which describes the Gemeinde-Edition and reads its releases on GitHub.
"""
from pathlib import Path
from unittest.mock import patch

import pytest

from openlp.core import edition
from openlp.core.edition import EditionRelease, edition_title, is_newer_release, parse_edition_version, \
    parse_latest_release


def test_edition_title():
    """
    Test that the title makes clear that this is the Gemeinde-Edition
    """
    assert edition_title() == 'OpenLP Gemeinde-Edition'


def test_version_file_is_an_edition_version():
    """
    Test that the version of this edition is marked as a modified version
    """
    version = (Path(edition.__file__).parent.parent / '.version').read_text().strip()
    assert '+gemeinde.' in version
    assert parse_edition_version(version) is not None


def test_repository_urls():
    """
    Test the addresses of the GitHub repository, and that there are none without a repository
    """
    with patch.object(edition, 'EDITION_REPOSITORY', 'gemeinde/openlp'):
        assert edition.repository_url() == 'https://github.com/gemeinde/openlp'
        assert edition.releases_api_url() == 'https://api.github.com/repos/gemeinde/openlp/releases/latest'
    with patch.object(edition, 'EDITION_REPOSITORY', ''):
        assert edition.repository_url() == ''
        assert edition.releases_api_url() == ''


@pytest.mark.parametrize('text, expected', [
    ('v3.1.7+gemeinde.2', '3.1.7+gemeinde.2'), ('3.1.7+gemeinde.2', '3.1.7+gemeinde.2'),
    ('V3.1.7-gemeinde.2', '3.1.7+gemeinde.2'), ('3.1.8', '3.1.8'), ('latest', None), ('', None), (None, None)])
def test_parse_edition_version(text, expected):
    """
    Test that the versions of release tags are understood, also with a hyphen instead of a plus sign
    """
    result = parse_edition_version(text)
    assert (str(result) if result else None) == expected


@pytest.mark.parametrize('release, current, newer', [
    ('3.1.7+gemeinde.2', '3.1.7+gemeinde.1', True), ('3.1.7+gemeinde.1', '3.1.7+gemeinde.1', False),
    ('3.1.7+gemeinde.1', '3.1.7+gemeinde.2', False), ('3.1.8+gemeinde.1', '3.1.7+gemeinde.9', True),
    ('3.1.7+gemeinde.10', '3.1.7+gemeinde.9', True), ('nonsense', '3.1.7+gemeinde.1', False)])
def test_is_newer_release(release, current, newer):
    """
    Test which releases are newer than the running version, also after the official version changed
    """
    assert is_newer_release(EditionRelease(release, '', None, None, None), current) is newer


def test_is_newer_release_without_release():
    """
    Test that no release is not newer
    """
    assert is_newer_release(None, '3.1.7+gemeinde.1') is False


def test_parse_latest_release():
    """
    Test that the version, the page, the setup and its checksum are read from the latest release
    """
    # GIVEN: The answer of the GitHub API, with a setup and another file
    data = {'tag_name': 'v3.1.7+gemeinde.2', 'html_url': 'https://github.com/g/o/releases/tag/v3.1.7+gemeinde.2',
            'draft': False, 'prerelease': False,
            'assets': [{'name': 'Liederbuecher.zip', 'browser_download_url': 'https://example.com/songs.zip'},
                       {'name': 'OpenLP-Gemeinde-Edition-3.1.7-gemeinde.2-Setup-x64.exe',
                        'browser_download_url': 'https://example.com/setup.exe', 'digest': 'sha256:ABC'}]}

    # WHEN: The release is read
    release = parse_latest_release(data)

    # THEN: All is known
    assert release == EditionRelease('3.1.7+gemeinde.2', 'https://github.com/g/o/releases/tag/v3.1.7+gemeinde.2',
                                     'https://example.com/setup.exe',
                                     'OpenLP-Gemeinde-Edition-3.1.7-gemeinde.2-Setup-x64.exe', 'ABC')


def test_parse_latest_release_without_setup():
    """
    Test that a release without a setup can still be announced, with its page
    """
    release = parse_latest_release('{"tag_name": "v3.1.7+gemeinde.2", "html_url": "https://x", "assets": []}')
    assert release.setup_url is None
    assert release.page_url == 'https://x'


@pytest.mark.parametrize('data', [{'tag_name': 'nightly'}, {'tag_name': 'v3.1.8', 'draft': True},
                                  {'tag_name': 'v3.1.8', 'prerelease': True}])
def test_parse_latest_release_ignores(data):
    """
    Test that releases without a version, drafts and pre-releases are not updates
    """
    assert parse_latest_release(data) is None
