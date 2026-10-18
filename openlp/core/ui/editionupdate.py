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
The :mod:`openlp.core.ui.editionupdate` module offers a new release of this edition (see :mod:`openlp.core.edition`)
to the user, downloads its setup from GitHub and starts it.
"""
import hashlib
import logging
import tempfile
import webbrowser
from pathlib import Path

import requests
from PyQt5 import QtCore, QtWidgets

from openlp.core.common.httputils import get_proxy_settings
from openlp.core.common.i18n import translate
from openlp.core.common.platform import is_win
from openlp.core.edition import edition_title
from openlp.core.lib.ui import critical_error_message_box
from openlp.core.version import get_version

log = logging.getLogger(__name__)

DOWNLOAD_TIMEOUT = 30
CHUNK_SIZE = 64 * 1024
# The setup updates silently and starts OpenLP again afterwards
SETUP_PARAMETERS = '/SILENT /SUPPRESSMSGBOXES /NORESTART'


def offer_update(parent, release):
    """
    Tell the user about a new release, and download and start its setup when they want to update

    :param parent: The main window
    :param openlp.core.edition.EditionRelease release: The new release
    :return: True when the setup was started (and OpenLP is being closed for it)
    """
    title = translate('OpenLP.EditionUpdate', 'Update available')
    if not release.setup_url:
        text = translate('OpenLP.EditionUpdate', 'Version {new} of {edition} is available (you are using version '
                         '{current}).\n\nOpen its download page?').format(new=release.version, edition=edition_title(),
                                                                          current=get_version()['full'])
        if QtWidgets.QMessageBox.question(parent, title, text) == QtWidgets.QMessageBox.Yes and release.page_url:
            webbrowser.open_new(release.page_url)
        return False
    text = translate('OpenLP.EditionUpdate', 'Version {new} of {edition} is available (you are using version '
                     '{current}).\n\nDownload and install it now? OpenLP will be closed for this; your songs, Bibles, '
                     'services and settings are kept.').format(new=release.version, edition=edition_title(),
                                                               current=get_version()['full'])
    if QtWidgets.QMessageBox.question(parent, title, text) != QtWidgets.QMessageBox.Yes:
        return False
    setup_path = download_setup(parent, release)
    if not setup_path:
        return False
    if not ready_to_close(parent):
        return False
    if not start_setup(setup_path):
        critical_error_message_box(title, translate('OpenLP.EditionUpdate', 'The setup could not be started. You can '
                                                    'start it yourself: {path}').format(path=setup_path))
        return False
    # The setup waits until OpenLP is closed; OpenLP closes without asking again, see ready_to_close()
    parent.closing_for_update = True
    parent.close()
    return True


def ready_to_close(parent):
    """
    Ask whether to save a modified service before the setup is started, because OpenLP then closes for the update
    without asking again (the setup ends OpenLP if it is still open after a while)

    :param parent: The main window
    :return: False if the user cancelled, then there is no update now
    """
    service_manager = getattr(parent, 'service_manager_contents', None)
    if service_manager is None or not service_manager.is_modified():
        return True
    answer = service_manager.save_modified_service()
    if answer == QtWidgets.QMessageBox.Save:
        return bool(service_manager.decide_save_method())
    return answer == QtWidgets.QMessageBox.Discard


def download_setup(parent, release):
    """
    Download the setup of a release into a temporary folder, showing the progress, and check it

    :param parent: The main window
    :param openlp.core.edition.EditionRelease release: The release
    :return: The path of the setup, or None if the download failed or was cancelled
    """
    title = translate('OpenLP.EditionUpdate', 'Update available')
    target = Path(tempfile.mkdtemp(prefix='openlp-update-')) / Path(release.setup_name or 'OpenLP-Setup.exe').name
    progress = QtWidgets.QProgressDialog(translate('OpenLP.EditionUpdate', 'Downloading {name}...').format(
        name=target.name), translate('OpenLP.EditionUpdate', 'Cancel'), 0, 100, parent)
    progress.setWindowTitle(title)
    progress.setWindowModality(QtCore.Qt.WindowModal)
    progress.setMinimumDuration(0)
    hasher = hashlib.sha256()
    cancelled = False
    try:
        with requests.get(release.setup_url, stream=True, timeout=DOWNLOAD_TIMEOUT,
                          proxies=get_proxy_settings()) as response:
            response.raise_for_status()
            total = int(response.headers.get('content-length') or 0)
            done = 0
            with target.open('wb') as setup_file:
                for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                    if progress.wasCanceled():
                        cancelled = True
                        break
                    setup_file.write(chunk)
                    hasher.update(chunk)
                    done += len(chunk)
                    if total:
                        progress.setValue(min(99, done * 100 // total))
                    QtWidgets.QApplication.processEvents()
        if cancelled:
            # Only now that the file is closed, as an open file can't be deleted on Windows
            log.info('Download of the update cancelled')
            target.unlink(missing_ok=True)
            return None
    except (OSError, requests.RequestException):
        log.exception('Download of the update failed')
        target.unlink(missing_ok=True)
        critical_error_message_box(title, translate('OpenLP.EditionUpdate', 'The update could not be downloaded. '
                                                    'Please check the internet connection and try again later.'))
        return None
    finally:
        progress.close()
    if release.setup_sha256 and hasher.hexdigest().lower() != release.setup_sha256.lower():
        log.error('The checksum of the update does not match: %s, expected %s', hasher.hexdigest(),
                  release.setup_sha256)
        target.unlink(missing_ok=True)
        critical_error_message_box(title, translate('OpenLP.EditionUpdate', 'The downloaded update is damaged and was '
                                                    'deleted. Please try again later.'))
        return None
    return target


def start_setup(setup_path):
    """
    Start the setup of an update. Windows asks for administrator rights for it.

    :param Path setup_path: The setup
    :return: True if it was started
    """
    if not is_win():
        return False
    import ctypes
    result = ctypes.windll.shell32.ShellExecuteW(None, 'open', str(setup_path), SETUP_PARAMETERS, None, 1)
    log.info('Started the setup of the update: %s (%s)', setup_path, result)
    # ShellExecute returns a value greater than 32 on success
    return result > 32
