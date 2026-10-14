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
The :mod:`~openlp.plugins.livevideo.lib.messagelistener` module shows live video service items in the displays.

The slide controllers treat live video items as command items, so instead of loading slides themselves they send
``livevideo_*`` events, the same way they do for presentations. This listener answers those events.
"""
import logging
from pathlib import Path

from openlp.core.common.enum import ServiceItemType
from openlp.core.common.mixins import LogMixin, RegistryProperties
from openlp.core.common.registry import Registry
from openlp.plugins.livevideo.lib import service_item_to_spec, spec_to_display_source


log = logging.getLogger(__name__)


class LiveVideoMessageListener(RegistryProperties, LogMixin):
    """
    Answers the events which the slide controllers send for live video items
    """
    def __init__(self, plugin_name):
        """
        :param str plugin_name: The name of the plugin, which is the prefix of the events
        """
        self.plugin_name = plugin_name
        Registry().register_function('{name}_start'.format(name=plugin_name), self.on_start)
        Registry().register_function('{name}_stop'.format(name=plugin_name), self.on_stop)
        Registry().register_function('{name}_blank'.format(name=plugin_name), self.on_blank)
        Registry().register_function('{name}_unblank'.format(name=plugin_name), self.on_unblank)
        Registry().register_function('{name}_next'.format(name=plugin_name), self.on_next)
        Registry().register_function('{name}_previous'.format(name=plugin_name), self.on_previous)
        Registry().register_function('{name}_slide'.format(name=plugin_name), self.on_slide)

    def get_controller(self, is_live):
        """
        :param bool is_live: True for the live controller, False for the preview controller
        :return: The slide controller
        """
        return self.live_controller if is_live else self.preview_controller

    def show_item(self, controller, service_item):
        """
        Show a live video item in the preview panel of a slide controller and, for the live controller, on the screens

        :param controller: The slide controller
        :param openlp.core.lib.serviceitem.ServiceItem service_item: The live video item
        """
        spec = service_item_to_spec(service_item)
        source = spec_to_display_source(spec)
        # Live video is a full screen picture, so treat it like an image when it comes to themes. The theme is
        # visible around the picture and when the screen is blanked to the theme.
        theme = service_item.get_theme_data()
        thumbnail = service_item.get_rendered_frame(0)
        if controller.is_live or self.settings.value('{name}/live picture in preview'.format(name=self.plugin_name)) \
                or not isinstance(thumbnail, Path):
            controller.preview_display.set_theme(theme, service_item_type=ServiceItemType.Image)
            controller.preview_display.load_live_video(source)
        else:
            # Showing a still image saves the computing power needed for decoding the video
            controller.preview_display.set_single_image('#000', thumbnail)
        for display in controller.displays:
            display.set_theme(theme, service_item_type=ServiceItemType.Image)
            display.load_live_video(source)

    def is_live_video_item(self, service_item):
        """
        :param service_item: A service item or None
        :return: True if the service item belongs to this plugin
        """
        return bool(service_item) and service_item.name == self.plugin_name

    def on_start(self, message):
        """
        A live video item was sent to a slide controller

        :param list message: [service_item, is_live, hide_mode, slide_number]
        """
        service_item, is_live = message[0], message[1]
        log.debug('Showing live video "{title}", live: {live}'.format(title=service_item.title, live=is_live))
        self.show_item(self.get_controller(is_live), service_item)

    def on_stop(self, message):
        """
        A slide controller has replaced a live video item.

        The displays release the device by themselves when the item disappears, so there is nothing to stop here.
        However the slide controller doesn't send a start event when the new item looks the same as the old one, for
        example when the same item is sent live again or when the screens have been rebuilt. So make sure the current
        item is showing.

        :param list message: [old_service_item, is_live]
        """
        controller = self.get_controller(message[1])
        if self.is_live_video_item(controller.service_item):
            self.show_item(controller, controller.service_item)

    def on_blank(self, message):
        """
        The live screen is blanked while showing a live video item

        :param list message: [service_item, is_live, hide_mode]
        """
        if message[1]:
            Registry().execute('live_display_hide', message[2])

    def on_unblank(self, message):
        """
        The live screen is shown again while showing a live video item

        :param list message: [service_item, is_live]
        """
        if message[1]:
            Registry().execute('live_display_show')

    def on_next(self, message):
        """
        A live video item has a single slide, so going to the next slide means leaving the item

        :param list message: [service_item, is_live]
        :return: True, as there is no next slide
        """
        return True

    def on_previous(self, message):
        """
        A live video item has a single slide, so going to the previous slide means leaving the item

        :param list message: [service_item, is_live]
        :return: True, as there is no previous slide
        """
        return True

    def on_slide(self, message):
        """
        A live video item has a single slide, so there is nothing to change

        :param list message: [service_item, is_live, slide_number]
        """
        pass
