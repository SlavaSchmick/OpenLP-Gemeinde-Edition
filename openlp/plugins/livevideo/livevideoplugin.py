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
The :mod:`~openlp.plugins.livevideo.livevideoplugin` module contains the Plugin class for the Live Video plugin.
"""
import logging
import os

from openlp.core.common.applocation import AppLocation
from openlp.core.common.i18n import translate
from openlp.core.common.registry import Registry
from openlp.core.db.manager import DBManager
from openlp.core.lib import build_icon
from openlp.core.lib.plugin import Plugin, StringContent
from openlp.core.state import State
from openlp.core.ui.icons import UiIcons
from openlp.plugins.livevideo.lib.db import init_schema
from openlp.plugins.livevideo.lib.livevideotab import LiveVideoTab
from openlp.plugins.livevideo.lib.mediaitem import LiveVideoMediaItem


log = logging.getLogger(__name__)


class LiveVideoPlugin(Plugin):
    """
    This plugin shows the picture of live video sources on the screen. A source can be anything that the operating
    system offers as a video input: USB and built-in cameras, HDMI or SDI capture cards, and virtual cameras like the
    one of OBS Studio.
    """
    log.info('Live Video Plugin loaded')

    def __init__(self):
        super(LiveVideoPlugin, self).__init__('livevideo', LiveVideoMediaItem, LiveVideoTab)
        self.weight = -4
        self.db_manager = DBManager('livevideo', init_schema)
        self.icon_path = UiIcons().live_video
        self.icon = build_icon(self.icon_path)
        Registry().register('livevideo_manager', self.db_manager)
        self.register_web_resources()
        State().add_service('live_video', self.weight, is_plugin=True)
        State().update_pre_conditions('live_video', self.check_pre_conditions())

    @staticmethod
    def register_web_resources():
        """
        Make the web pages of this plugin available at openlp://livevideo/, which is where the preview of the source
        dialog comes from. Being an openlp:// page allows it to use the video devices.
        """
        # Need to import this inline to get around a QtWebEngine issue
        from openlp.core.display.webengine import OpenLPScheme, WebViewSchemes
        scheme = WebViewSchemes().get_scheme(OpenLPScheme.scheme_name)
        if scheme:
            html_path = AppLocation.get_directory(AppLocation.PluginsDir) / 'livevideo' / 'resources' / 'html'
            scheme.set_root_path('livevideo', os.path.realpath(str(html_path)))

    @staticmethod
    def about():
        about_text = translate('LiveVideoPlugin', '<strong>Live Video Plugin</strong><br />The live video plugin shows '
                               'the picture of live video sources on the screen, such as USB and built-in cameras, '
                               'HDMI capture cards and virtual cameras like the one of OBS Studio. Sources can be '
                               'added to the service like any other item.')
        return about_text

    def check_pre_conditions(self):
        """
        Check the plugin can run.
        """
        return self.db_manager.session is not None

    def set_plugin_text_strings(self):
        """
        Called to define all translatable texts of the plugin
        """
        # Name PluginList
        self.text_strings[StringContent.Name] = {
            'singular': translate('LiveVideoPlugin', 'Live Video', 'name singular'),
            'plural': translate('LiveVideoPlugin', 'Live Videos', 'name plural')
        }
        # Name for MediaDockManager, SettingsManager
        self.text_strings[StringContent.VisibleName] = {
            'title': translate('LiveVideoPlugin', 'Live Video', 'container title')
        }
        # Middle Header Bar
        tooltips = {
            'load': '',
            'import': '',
            'new': translate('LiveVideoPlugin', 'Add a new live video source.'),
            'edit': translate('LiveVideoPlugin', 'Edit the selected live video source.'),
            'delete': translate('LiveVideoPlugin', 'Delete the selected live video source.'),
            'preview': translate('LiveVideoPlugin', 'Preview the selected live video source.'),
            'live': translate('LiveVideoPlugin', 'Send the selected live video source live.'),
            'service': translate('LiveVideoPlugin', 'Add the selected live video source to the service.')
        }
        self.set_plugin_ui_text_strings(tooltips)

    def uses_theme(self, theme):
        """
        Called to find out if the live video plugin is currently using a theme.

        :param theme: Theme to be queried
        :return: 1 if the theme is the background of live video, otherwise 0
        """
        return int(self.settings.value('livevideo/theme') == theme)

    def rename_theme(self, old_theme, new_theme):
        """
        Renames a theme the live video plugin is using making the plugin use the new name.

        :param old_theme: The name of the theme the plugin should stop using.
        :param new_theme: The new name the plugin should now use.
        """
        if self.settings.value('livevideo/theme') == old_theme:
            self.settings.setValue('livevideo/theme', new_theme)

    def finalise(self):
        """
        Time to tidy up on exit
        """
        log.info('Live Video Finalising')
        self.db_manager.finalise()
        super(LiveVideoPlugin, self).finalise()
