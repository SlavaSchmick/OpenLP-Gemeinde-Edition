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
The :mod:`~openlp.plugins.livevideo.lib.mediaitem` module contains the library panel of the Live Video plugin.
"""
import base64
import binascii
import hashlib
import logging
from typing import Any

from PyQt5 import QtCore, QtGui, QtWidgets
from sqlalchemy.sql import func, or_

from openlp.core.common import delete_file
from openlp.core.common.applocation import AppLocation
from openlp.core.common.enum import ImageThemeMode
from openlp.core.common.i18n import UiStrings, translate
from openlp.core.common.path import create_paths
from openlp.core.common.registry import Registry
from openlp.core.lib import build_icon, check_item_selected
from openlp.core.lib.mediamanageritem import MediaManagerItem
from openlp.core.lib.plugin import PluginStatus
from openlp.core.lib.serviceitem import ItemCapabilities
from openlp.core.lib.ui import create_widget_action
from openlp.core.ui.icons import UiIcons
from openlp.plugins.livevideo.lib import service_item_to_spec, source_to_spec, spec_to_service_path
from openlp.plugins.livevideo.lib.db import LiveVideoSource
from openlp.plugins.livevideo.lib.messagelistener import LiveVideoMessageListener


log = logging.getLogger(__name__)

THUMBNAIL_SIZE = QtCore.QSize(320, 180)


class LiveVideoMediaItem(MediaManagerItem):
    """
    This is the library panel of the Live Video plugin, which lists the live video sources.
    """
    livevideo_go_live = QtCore.pyqtSignal(list)
    livevideo_add_to_service = QtCore.pyqtSignal(list)
    log.info('Live Video Media Item loaded')

    def __init__(self, parent, plugin):
        self.icon_path = UiIcons().live_video
        self._source_form = None
        super(LiveVideoMediaItem, self).__init__(parent, plugin)

    def setup_item(self):
        """
        Do some additional setup.
        """
        self.livevideo_go_live.connect(self.go_live_remote)
        self.livevideo_add_to_service.connect(self.add_to_service_remote)
        self.single_service_item = False
        self.quick_preview_allowed = True
        self.has_search = True
        self.message_listener = LiveVideoMessageListener(self.plugin.name)
        Registry().register_function('{name}_load_list'.format(name=self.plugin.name), self.load_list)

    def add_custom_context_actions(self):
        """
        Add custom actions to the context menu.
        """
        create_widget_action(self.list_view, separator=True)
        create_widget_action(self.list_view, text=translate('OpenLP.MediaManagerItem', '&Clone'),
                             icon=UiIcons().clone, triggers=self.on_clone_click)

    @property
    def source_form(self):
        """
        The dialog to add and edit sources. It contains a web view for the preview, so it is only created when needed.
        """
        if self._source_form is None:
            from openlp.plugins.livevideo.forms.sourceform import SourceForm
            self._source_form = SourceForm(self, self.main_window, self.plugin.db_manager)
        return self._source_form

    @property
    def thumbnail_path(self):
        """
        The folder where the thumbnails of the sources are stored
        """
        path = AppLocation.get_section_data_path(self.settings_section) / 'thumbnails'
        create_paths(path)
        return path

    def initialise(self):
        """
        Load the list of sources
        """
        self.list_view.setIconSize(QtCore.QSize(88, 50))
        self.load_list()

    def load_list(self, sources=None, target_group=None):
        """
        Show the sources in the list

        :param list[LiveVideoSource] | None sources: The sources to show, all sources if None
        :param target_group: Unused, only here to match the base class
        """
        self.save_auto_select_id()
        self.list_view.clear()
        if not sources:
            sources = self.plugin.db_manager.get_all_objects(LiveVideoSource)
        sources.sort()
        for source in sources:
            list_item = QtWidgets.QListWidgetItem(source.title)
            list_item.setData(QtCore.Qt.UserRole, source.id)
            list_item.setIcon(build_icon(self.get_thumbnail_path(source.id)))
            list_item.setToolTip(self.get_source_description(source))
            self.list_view.addItem(list_item)
            if source.id == self.auto_select_id:
                self.list_view.setCurrentItem(list_item)
        self.auto_select_id = -1

    @staticmethod
    def get_source_description(source):
        """
        Describe a source for a tool tip, e.g. "HD Pro Webcam C920\n1920 × 1080, 30 fps"

        :param LiveVideoSource source: The source
        :return: The description
        """
        if source.width and source.height:
            resolution = '{width} × {height}'.format(width=source.width, height=source.height)
        else:
            resolution = translate('LiveVideoPlugin.MediaItem', 'Automatic resolution')
        if source.frame_rate:
            resolution = translate('LiveVideoPlugin.MediaItem', '{resolution}, {frame_rate} fps').format(
                resolution=resolution, frame_rate=source.frame_rate)
        return '{device}\n{resolution}'.format(device=source.device_label, resolution=resolution)

    def get_thumbnail_path(self, source_id):
        """
        Get the thumbnail of a source, which is a still image taken from its picture

        :param int | None source_id: The id of the source
        :return: The path to the thumbnail, or to a generic image if the source has no thumbnail
        :rtype: Path
        """
        if source_id:
            thumbnail_path = self.thumbnail_path / 'source-{id}.jpg'.format(id=source_id)
            if thumbnail_path.exists():
                return thumbnail_path
        return self.get_placeholder_thumbnail_path()

    def get_placeholder_thumbnail_path(self):
        """
        Get a generic image for sources without a thumbnail, which is created when it doesn't exist yet

        :rtype: Path
        """
        placeholder_path = self.thumbnail_path / 'placeholder.png'
        if not placeholder_path.exists():
            image = QtGui.QImage(THUMBNAIL_SIZE, QtGui.QImage.Format_RGB32)
            image.fill(QtGui.QColor('#202020'))
            pixmap = UiIcons().get_icon_variant('live_video', color='#9e9e9e').pixmap(96, 96)
            painter = QtGui.QPainter(image)
            painter.drawPixmap((THUMBNAIL_SIZE.width() - pixmap.width()) // 2,
                               (THUMBNAIL_SIZE.height() - pixmap.height()) // 2, pixmap)
            painter.end()
            image.save(str(placeholder_path))
        return placeholder_path

    def save_thumbnail(self, source_id, image_data_url):
        """
        Save the thumbnail of a source

        :param int source_id: The id of the source
        :param str | None image_data_url: The image as a data URL, None to remove the thumbnail
        """
        thumbnail_path = self.thumbnail_path / 'source-{id}.jpg'.format(id=source_id)
        image_data = None
        if image_data_url and image_data_url.startswith('data:image/') and ',' in image_data_url:
            try:
                image_data = base64.b64decode(image_data_url.split(',', 1)[1])
            except (binascii.Error, ValueError):
                log.exception('Invalid thumbnail data for live video source {id}'.format(id=source_id))
        if image_data:
            thumbnail_path.write_bytes(image_data)
        else:
            delete_file(thumbnail_path)

    def on_new_click(self):
        """
        Add a new source
        """
        self.source_form.load_source(0)
        if self.source_form.exec() == QtWidgets.QDialog.Accepted:
            self.load_list()
            self.on_selection_change()

    def on_edit_click(self):
        """
        Edit the selected source
        """
        if check_item_selected(self.list_view, UiStrings().SelectEdit):
            source_id = self.list_view.currentItem().data(QtCore.Qt.UserRole)
            self.source_form.load_source(source_id)
            if self.source_form.exec() == QtWidgets.QDialog.Accepted:
                self.load_list()

    def on_remote_edit(self, source_id, preview=False):
        """
        Edit a source from the service manager or the preview panel

        :param int source_id: The id of the source to edit
        :param bool preview: True when the source is edited from the preview panel
        :return: A new service item for the edited source, or None if it was not edited
        """
        source_id = int(source_id)
        if not self.plugin.db_manager.get_object(LiveVideoSource, source_id):
            return None
        self.source_form.load_source(source_id)
        if self.source_form.exec() != QtWidgets.QDialog.Accepted:
            return None
        self.load_list()
        service_item = self.build_service_item(self.create_item_from_id(source_id), remote=True)
        if service_item and preview:
            # A source can only be edited from the preview panel if it comes from the plugin
            service_item.from_plugin = True
        return service_item

    def on_delete_click(self):
        """
        Remove the selected sources from the list and the database
        """
        if not check_item_selected(self.list_view, UiStrings().SelectDelete):
            return
        items = self.list_view.selectedIndexes()
        if QtWidgets.QMessageBox.question(
                self, UiStrings().ConfirmDelete,
                translate('LiveVideoPlugin.MediaItem',
                          'Are you sure you want to delete the {items:d} selected live video source(s)?'
                          ).format(items=len(items)),
                defaultButton=QtWidgets.QMessageBox.Yes) == QtWidgets.QMessageBox.No:
            return
        for source_id in [item.data(QtCore.Qt.UserRole) for item in items]:
            self.plugin.db_manager.delete_object(LiveVideoSource, source_id)
            self.save_thumbnail(source_id, None)
            Registry().execute('{name}_deleted'.format(name=self.plugin.name), source_id)
        self.load_list()

    def on_clone_click(self):
        """
        Clone the selected source, e.g. to show the same camera with other settings
        """
        if not check_item_selected(self.list_view, UiStrings().SelectEdit):
            return
        source_id = self.list_view.currentItem().data(QtCore.Qt.UserRole)
        source = self.plugin.db_manager.get_object(LiveVideoSource, source_id)
        title = '{title} <{text}>'.format(title=source.title,
                                          text=translate('LiveVideoPlugin.MediaItem', 'copy', 'For item cloning'))
        clone = LiveVideoSource(title=title, device_label=source.device_label, width=source.width,
                                height=source.height, frame_rate=source.frame_rate, scale_mode=source.scale_mode,
                                mirror=source.mirror)
        self.plugin.db_manager.save_object(clone)
        thumbnail_path = self.get_thumbnail_path(source.id)
        if thumbnail_path != self.get_placeholder_thumbnail_path():
            (self.thumbnail_path / 'source-{id}.jpg'.format(id=clone.id)).write_bytes(thumbnail_path.read_bytes())
        self.auto_select_id = clone.id
        self.load_list()

    def generate_slide_data(self, service_item, *, item=None, **kwargs):
        """
        Generate the service item for a source

        :param service_item: The service item to fill
        :param item: The list item of the source, the selected source if None
        :param kwargs: Consume other unused args specified by the base implementation, but not used by this one.
        """
        source_id = self._get_id_of_item_to_generate(item, None)
        if not source_id:
            return False
        source = self.plugin.db_manager.get_object(LiveVideoSource, int(source_id))
        if not source:
            return False
        self.fill_service_item(service_item, source_to_spec(source))
        return True

    def fill_service_item(self, service_item, spec):
        """
        Fill a service item with a source spec

        :param openlp.core.lib.serviceitem.ServiceItem service_item: The service item to fill
        :param dict spec: The source spec
        """
        service_item.title = spec['title']
        service_item.edit_id = spec.get('source_id')
        service_item.data_string = spec
        # Live video is a stream, i.e. a command item without a file
        service_item.add_capability(ItemCapabilities.CanStream)
        service_item.add_capability(ItemCapabilities.CanPreview)
        service_item.add_capability(ItemCapabilities.CanEdit)
        service_item.add_capability(ItemCapabilities.CanEditTitle)
        service_item.add_capability(ItemCapabilities.ProvidesOwnTheme)
        service_item.add_capability(ItemCapabilities.OnLoadUpdate)
        if self.settings.value('{name}/background mode'.format(name=self.settings_section)) == \
                ImageThemeMode.CustomTheme:
            service_item.theme = self.settings.value('{name}/theme'.format(name=self.settings_section))
        else:
            # force a nonexistent theme, which is a black background
            service_item.theme = -1
        self.set_service_item_source(service_item, spec)

    def set_service_item_source(self, service_item, spec):
        """
        Put a source spec into the slide of a service item

        :param openlp.core.lib.serviceitem.ServiceItem service_item: The service item
        :param dict spec: The source spec
        """
        path = spec_to_service_path(spec)
        thumbnail_path = self.get_thumbnail_path(spec.get('source_id'))
        service_item.data_string = spec
        if service_item.slides:
            service_item.slides[0].update({'path': path, 'title': spec['title'], 'image': thumbnail_path,
                                           'thumbnail': thumbnail_path})
        else:
            service_item.add_from_command(path, spec['title'], thumbnail_path)
        # The slide controllers only start command items whose hash differs from the item shown before
        service_item.sha256_file_hash = hashlib.sha256(path.encode('utf-8')).hexdigest()
        service_item.validate_item()

    def service_load(self, item):
        """
        A live video item has been loaded from a service file. Sources are referred to by their title, so if the
        library has a source with that title, it is used. This way a service prepared on another computer shows the
        camera of this computer. Otherwise the item shows the device it was saved with.

        :param item: The service item from the service file
        :return: The updated service item
        """
        if self.plugin.status != PluginStatus.Active:
            return item
        spec = service_item_to_spec(item)
        source = self.plugin.db_manager.get_object_filtered(
            LiveVideoSource, func.lower(LiveVideoSource.title) == spec['title'].lower())
        if source:
            spec = source_to_spec(source)
        else:
            spec['source_id'] = None
        item.edit_id = spec['source_id']
        self.set_service_item_source(item, spec)
        return item

    def on_focus(self):
        """
        Set the focus on the list
        """
        self.list_view.setFocus()

    def search_options(self, option=None):
        """
        Live video sources have no search options

        :param option: Unused, only here to match the base class
        """
        return []

    @QtCore.pyqtSlot(str, bool, result=list)
    def search(self, string: str, show_error: bool = True) -> list[list[Any]]:
        """
        Search the sources by title and device, used by the web remote

        :param string: The search string
        :param show_error: Unused, only here to match the base class
        :return: A list of [id, title] lists
        """
        search = '%{search}%'.format(search=string.lower())
        sources = self.plugin.db_manager.get_all_objects(
            LiveVideoSource, or_(func.lower(LiveVideoSource.title).like(search),
                                 func.lower(LiveVideoSource.device_label).like(search)))
        sources.sort()
        return [[source.id, source.title] for source in sources]
