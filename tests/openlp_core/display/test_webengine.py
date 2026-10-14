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
Package to test the openlp.core.display.webengine package.
"""
from unittest.mock import MagicMock

from PyQt5 import QtCore, QtWebEngineWidgets

from openlp.core.display.webengine import WebEnginePage


def test_video_capture_is_granted_to_openlp_pages():
    """
    Test that OpenLP's own pages may use video devices, which is needed to show live video sources
    """
    # GIVEN: A page and an openlp:// origin
    page = MagicMock()
    origin = QtCore.QUrl('openlp://display/')

    # WHEN: The page asks to capture video
    WebEnginePage.on_feature_permission_requested(page, origin, QtWebEngineWidgets.QWebEnginePage.MediaVideoCapture)

    # THEN: It should be allowed
    page.setFeaturePermission.assert_called_once_with(origin, QtWebEngineWidgets.QWebEnginePage.MediaVideoCapture,
                                                      QtWebEngineWidgets.QWebEnginePage.PermissionGrantedByUser)


def test_video_capture_is_denied_to_other_pages():
    """
    Test that other pages, e.g. a custom display URL, may not use video devices
    """
    # GIVEN: A page and a web origin
    page = MagicMock()
    origin = QtCore.QUrl('https://example.com/')

    # WHEN: The page asks to capture video
    WebEnginePage.on_feature_permission_requested(page, origin, QtWebEngineWidgets.QWebEnginePage.MediaVideoCapture)

    # THEN: It should be denied
    page.setFeaturePermission.assert_called_once_with(origin, QtWebEngineWidgets.QWebEnginePage.MediaVideoCapture,
                                                      QtWebEngineWidgets.QWebEnginePage.PermissionDeniedByUser)


def test_other_features_are_denied_to_openlp_pages():
    """
    Test that OpenLP's own pages get nothing but video capture
    """
    # GIVEN: A page and an openlp:// origin
    page = MagicMock()
    origin = QtCore.QUrl('openlp://display/')

    # WHEN: The page asks to capture audio
    WebEnginePage.on_feature_permission_requested(page, origin, QtWebEngineWidgets.QWebEnginePage.MediaAudioCapture)

    # THEN: It should be denied
    page.setFeaturePermission.assert_called_once_with(origin, QtWebEngineWidgets.QWebEnginePage.MediaAudioCapture,
                                                      QtWebEngineWidgets.QWebEnginePage.PermissionDeniedByUser)
