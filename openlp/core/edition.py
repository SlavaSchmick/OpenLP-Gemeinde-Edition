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
The :mod:`openlp.core.edition` module describes this modified version of OpenLP, the "Gemeinde-Edition", and finds
its updates, which are published as releases of its GitHub repository (and not on openlp.org).

A release is published with a tag of the version (e.g. "v3.1.7+gemeinde.2") and the Windows setup as an asset.
"""
import json
import logging
import re
from dataclasses import dataclass
from typing import Optional

from packaging.version import InvalidVersion, Version

log = logging.getLogger(__name__)

# The name of this modified version of OpenLP
EDITION_NAME = 'Gemeinde-Edition'
# The GitHub repository ("owner/name") whose releases are the updates of this edition. Without it, there is no update
# check.
EDITION_REPOSITORY = 'SlavaSchmick/OpenLP-Gemeinde-Edition'


# The version of the defaults of this edition which differ from OpenLP. Increase it when a default is added to
# apply_edition_defaults(), so that it is applied once to existing settings.
EDITION_DEFAULTS_VERSION = 1


def apply_edition_defaults(settings):
    """
    Apply the defaults of this edition once to existing settings, e.g. after an update from OpenLP or an older edition.
    New settings get them from the defaults of the settings.

    :param openlp.core.common.settings.Settings settings: The settings
    """
    from openlp.core.common.enum import PluginStatus
    try:
        applied = int(settings.value('core/edition defaults') or 0)
    except (TypeError, ValueError):
        applied = 0
    if applied >= EDITION_DEFAULTS_VERSION:
        return
    if applied < 1:
        # The song usage is always recorded, for the song statistics
        settings.setValue('songusage/status', PluginStatus.Active)
        settings.setValue('songusage/active', True)
    settings.setValue('core/edition defaults', EDITION_DEFAULTS_VERSION)
    log.info('Applied the defaults of the edition (version {version})'.format(version=EDITION_DEFAULTS_VERSION))


def edition_title():
    """
    The name of the program, e.g. for the title of the main window: "OpenLP Gemeinde-Edition"
    """
    return 'OpenLP {edition}'.format(edition=EDITION_NAME)


def repository_url():
    """
    The web address of the GitHub repository of this edition, or an empty string if it isn't known
    """
    return 'https://github.com/{repository}'.format(repository=EDITION_REPOSITORY) if EDITION_REPOSITORY else ''


def releases_api_url():
    """
    The address of the latest release in the GitHub API, or an empty string if the repository isn't known
    """
    if not EDITION_REPOSITORY:
        return ''
    return 'https://api.github.com/repos/{repository}/releases/latest'.format(repository=EDITION_REPOSITORY)


def parse_edition_version(text):
    """
    Turn the version of a release tag into a comparable version, e.g. "v3.1.7+gemeinde.2" or "3.1.7-gemeinde.2"

    :param str text: The version, as it is written in a tag
    :return: The version, or None if it isn't a version
    :rtype: Version | None
    """
    text = (text or '').strip()
    text = re.sub(r'^[vV]', '', text)
    # A local version after a hyphen, as hyphens are more common in tags than plus signs
    text = re.sub(r'^(\d+(?:\.\d+)*)-(?=[A-Za-z])', r'\1+', text)
    try:
        return Version(text)
    except InvalidVersion:
        return None


@dataclass
class EditionRelease:
    """
    A release of this edition on GitHub
    """
    version: str
    page_url: str
    setup_url: Optional[str]
    setup_name: Optional[str]
    setup_sha256: Optional[str]


def parse_latest_release(data):
    """
    Read the latest release of the GitHub API

    :param data: The answer of the GitHub API, as text or as parsed JSON
    :return: The release, or None if it has no valid version
    :rtype: EditionRelease | None
    """
    if isinstance(data, (str, bytes)):
        data = json.loads(data)
    tag = data.get('tag_name') or ''
    if parse_edition_version(tag) is None or data.get('draft') or data.get('prerelease'):
        return None
    setup = next((asset for asset in data.get('assets') or []
                  if asset.get('name', '').lower().endswith('.exe') and 'setup' in asset.get('name', '').lower()),
                 None)
    sha256 = None
    if setup and (setup.get('digest') or '').startswith('sha256:'):
        sha256 = setup['digest'][len('sha256:'):]
    return EditionRelease(version=re.sub(r'^[vV]', '', tag.strip()), page_url=data.get('html_url') or '',
                          setup_url=setup.get('browser_download_url') if setup else None,
                          setup_name=setup.get('name') if setup else None, setup_sha256=sha256)


def is_newer_release(release, current_version):
    """
    Whether a release is newer than the running version

    :param EditionRelease release: The release
    :param str current_version: The full version of the running OpenLP, e.g. "3.1.7+gemeinde.1"
    """
    release_version = parse_edition_version(release.version) if release else None
    current = parse_edition_version(current_version)
    return bool(release_version and current and release_version > current)
