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
This module contains tests for the plugin class of the Live Video plugin.
"""
from unittest.mock import MagicMock, patch

import pytest

from openlp.core.common.registry import Registry
from openlp.plugins.livevideo.livevideoplugin import LiveVideoPlugin


@pytest.fixture
def plugin(registry, mock_settings, state):
    with patch('openlp.plugins.livevideo.livevideoplugin.DBManager'), \
            patch('openlp.plugins.livevideo.livevideoplugin.UiIcons'), \
            patch('openlp.plugins.livevideo.livevideoplugin.build_icon'), \
            patch.object(LiveVideoPlugin, 'register_web_resources'):
        yield LiveVideoPlugin()


def test_plugin_about():
    """
    Test the about text of the plugin
    """
    assert LiveVideoPlugin.about().startswith('<strong>Live Video Plugin</strong>')


def test_plugin_registration(plugin):
    """
    Test that the plugin uses the names the rest of OpenLP expects
    """
    assert plugin.name == 'livevideo'
    assert Registry().get('live_video_plugin') is plugin
    assert Registry().has('livevideo_manager')


def test_uses_theme(plugin, mock_settings):
    """
    Test that the plugin reports the theme it uses as background
    """
    mock_settings.value.return_value = 'Stage Theme'

    assert plugin.uses_theme('Stage Theme') == 1
    assert plugin.uses_theme('Song Theme') == 0


def test_rename_theme(plugin, mock_settings):
    """
    Test that renaming the background theme updates the setting
    """
    mock_settings.value.return_value = 'Stage Theme'

    plugin.rename_theme('Stage Theme', 'Camera Theme')
    plugin.rename_theme('Song Theme', 'Lyrics Theme')

    mock_settings.setValue.assert_called_once_with('livevideo/theme', 'Camera Theme')


def test_default_settings_exist(settings):
    """
    Test that the settings and the shortcuts of the library panel have defaults, OpenLP refuses unknown keys
    """
    for key in ['livevideo/status', 'livevideo/background mode', 'livevideo/theme', 'livevideo/default resolution',
                'livevideo/default frame rate', 'livevideo/default scale mode', 'livevideo/live picture in preview',
                'livevideo/db type', 'shortcuts/listViewLivevideoPreviewItem', 'shortcuts/listViewLivevideoLiveItem',
                'shortcuts/listViewLivevideoServiceItem', 'shortcuts/listViewLivevideoDeleteItem']:
        settings.get_default_value(key)


def test_register_web_resources(registry):
    """
    Test that the pages of the plugin are served at openlp://livevideo/
    """
    mocked_scheme = MagicMock()
    with patch('openlp.core.display.webengine.WebViewSchemes') as mocked_schemes:
        mocked_schemes.return_value.get_scheme.return_value = mocked_scheme

        LiveVideoPlugin.register_web_resources()

    base, path = mocked_scheme.set_root_path.call_args[0]
    assert base == 'livevideo'
    assert path.replace('\\', '/').endswith('livevideo/resources/html')
