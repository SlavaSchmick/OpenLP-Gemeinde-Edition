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
The :mod:`~openlp.plugins.livevideo.forms.sourceform` module contains the dialog to add and edit live video sources.

The video inputs and the preview come from a small web page (openlp://livevideo/picker.html) rather than from Qt, so
that the dialog sees the devices exactly the way the display does.
"""
import json
import logging
import re

from PyQt5 import QtCore, QtWebChannel, QtWidgets

from openlp.core.common.i18n import translate
from openlp.core.common.mixins import RegistryProperties
from openlp.core.common.registry import Registry
from openlp.core.lib.ui import critical_error_message_box
from openlp.plugins.livevideo.forms.sourcedialog import Ui_SourceDialog
from openlp.plugins.livevideo.lib import string_to_resolution, resolution_to_string, spec_to_display_source, \
    validate_scale_mode
from openlp.plugins.livevideo.lib.db import LiveVideoSource
from openlp.plugins.livevideo.lib.ui import fill_frame_rate_combo_box, fill_resolution_combo_box, \
    fill_scale_mode_combo_box, select_combo_box_data


log = logging.getLogger(__name__)

PICKER_URL = 'openlp://livevideo/picker.html'
# Chromium appends the USB vendor and product id to the label of USB devices, which doesn't belong in a name
USB_ID_SUFFIX = re.compile(r'\s*\([0-9a-f]{4}:[0-9a-f]{4}\)\s*$', re.IGNORECASE)


class PickerBridge(QtCore.QObject):
    """
    Lets the preview page tell the dialog about the video inputs and the state of the preview
    """
    page_ready = QtCore.pyqtSignal()
    devices_changed = QtCore.pyqtSignal(list)
    preview_started = QtCore.pyqtSignal(int, int, float)
    preview_failed = QtCore.pyqtSignal(str)

    @QtCore.pyqtSlot()
    def pageReady(self):
        self.page_ready.emit()

    @QtCore.pyqtSlot('QVariantList')
    def setDevices(self, labels):
        self.devices_changed.emit([str(label) for label in labels])

    @QtCore.pyqtSlot(float, float, float)
    def previewStarted(self, width, height, frame_rate):
        self.preview_started.emit(int(width), int(height), frame_rate)

    @QtCore.pyqtSlot(str)
    def previewFailed(self, reason):
        self.preview_failed.emit(reason)


class SourceForm(QtWidgets.QDialog, Ui_SourceDialog, RegistryProperties):
    """
    The dialog to add and edit a live video source
    """
    log.info('Live Video Source Form loaded')

    def __init__(self, media_item, parent, manager):
        """
        :param media_item: The library panel of the plugin
        :param parent: The parent widget
        :param manager: The database manager of the plugin
        """
        super(SourceForm, self).__init__(parent, QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint |
                                         QtCore.Qt.WindowCloseButtonHint)
        self.media_item = media_item
        self.manager = manager
        self.source = None
        self.devices = []
        self.selected_device_label = ''
        self.automatic_title = ''
        self.is_page_ready = False
        self.has_searched_devices = False
        self.setup_ui(self)
        fill_resolution_combo_box(self.resolution_combo_box)
        fill_frame_rate_combo_box(self.frame_rate_combo_box)
        fill_scale_mode_combo_box(self.scale_mode_combo_box)
        self.bridge = PickerBridge(self)
        self.webview = self.create_preview()
        # Connecting signals and slots
        self.bridge.page_ready.connect(self.on_page_ready)
        self.bridge.devices_changed.connect(self.on_devices_changed)
        self.bridge.preview_started.connect(self.on_preview_started)
        self.bridge.preview_failed.connect(self.on_preview_failed)
        self.device_combo_box.currentIndexChanged.connect(self.on_device_changed)
        self.resolution_combo_box.currentIndexChanged.connect(self.update_preview)
        self.frame_rate_combo_box.currentIndexChanged.connect(self.update_preview)
        self.scale_mode_combo_box.currentIndexChanged.connect(self.update_preview)
        self.mirror_check_box.toggled.connect(self.update_preview)
        self.refresh_button.clicked.connect(self.refresh_devices)

    def create_preview(self):
        """
        Create the web view which shows the preview and finds the video inputs
        """
        # Need to import this inline to get around a QtWebEngine issue
        from openlp.core.display.webengine import WebEngineView, WebViewSchemes, OpenLPScheme
        webview = WebEngineView(self.preview_frame)
        profile = webview.page().profile()
        if not profile.urlSchemeHandler(OpenLPScheme.scheme_name):
            WebViewSchemes().get_scheme(OpenLPScheme.scheme_name).init_handler(profile)
        webview.page().setBackgroundColor(QtCore.Qt.black)
        self.channel = QtWebChannel.QWebChannel(self)
        self.channel.registerObject('pickerBridge', self.bridge)
        webview.page().setWebChannel(self.channel)
        self.preview_frame_layout.addWidget(webview)
        webview.setUrl(QtCore.QUrl(PICKER_URL))
        return webview

    def run_in_preview(self, action, *parameters, callback=None):
        """
        Call a function of the preview page

        :param str action: The name of the function of ``LiveVideoPicker``
        :param parameters: The parameters, which are converted to JSON
        :param callback: Receives the return value of the function
        """
        script = 'LiveVideoPicker.{action}({parameters})'.format(
            action=action, parameters=', '.join(json.dumps(parameter) for parameter in parameters))
        if callback:
            self.webview.page().runJavaScript(script, callback)
        else:
            self.webview.page().runJavaScript(script)

    def load_source(self, source_id):
        """
        Called when adding or editing a source.

        :param int source_id: The id of the source to edit, 0 to add a new source
        """
        if source_id:
            self.source = self.manager.get_object(LiveVideoSource, source_id)
            self.automatic_title = None
            resolution = resolution_to_string(self.source.width, self.source.height)
            frame_rate = self.source.frame_rate or 0
            scale_mode = validate_scale_mode(self.source.scale_mode)
        else:
            self.source = LiveVideoSource(title='', device_label='', mirror=False)
            # The name of a new source follows the selected video input until it is changed by the user
            self.automatic_title = ''
            resolution = self.settings.value('livevideo/default resolution')
            frame_rate = self.settings.value('livevideo/default frame rate')
            scale_mode = validate_scale_mode(self.settings.value('livevideo/default scale mode'))
        self.title_edit.setText(self.source.title)
        self.selected_device_label = self.source.device_label
        for widget in (self.resolution_combo_box, self.frame_rate_combo_box, self.scale_mode_combo_box,
                       self.mirror_check_box):
            widget.blockSignals(True)
        select_combo_box_data(self.resolution_combo_box, resolution)
        select_combo_box_data(self.frame_rate_combo_box, frame_rate)
        select_combo_box_data(self.scale_mode_combo_box, scale_mode)
        self.mirror_check_box.setChecked(bool(self.source.mirror))
        for widget in (self.resolution_combo_box, self.frame_rate_combo_box, self.scale_mode_combo_box,
                       self.mirror_check_box):
            widget.blockSignals(False)
        self.preview_info_label.setText('')
        self.save_button.setEnabled(True)
        self.populate_devices(self.devices)
        self.title_edit.setFocus()
        if self.is_page_ready:
            self.refresh_devices()

    def populate_devices(self, devices):
        """
        Show the video inputs in the combo box. The video input of the source stays selected, even if it is not
        connected at the moment.

        :param list[str] devices: The labels of the connected video inputs
        """
        self.devices = devices
        wanted_label = self.selected_device_label
        self.device_combo_box.blockSignals(True)
        self.device_combo_box.clear()
        for label in devices:
            self.device_combo_box.addItem(label, label)
        if wanted_label and wanted_label not in devices:
            self.device_combo_box.addItem(translate('LiveVideoPlugin.SourceForm', '{device} (not connected)').format(
                device=wanted_label), wanted_label)
        if self.device_combo_box.count() == 0:
            if self.has_searched_devices:
                self.device_combo_box.addItem(translate('LiveVideoPlugin.SourceForm', 'No video input found'), '')
            else:
                self.device_combo_box.addItem(translate('LiveVideoPlugin.SourceForm', 'Searching for video inputs...'),
                                              '')
        select_combo_box_data(self.device_combo_box, wanted_label)
        self.device_combo_box.blockSignals(False)
        self.on_device_changed()

    def refresh_devices(self):
        """
        Ask the preview page for the connected video inputs
        """
        if self.is_page_ready:
            self.run_in_preview('refreshDevices')

    def get_source_spec(self):
        """
        :return: A source spec of the current settings in the dialog
        """
        width, height = string_to_resolution(self.resolution_combo_box.currentData())
        return {
            'source_id': self.source.id if self.source else None,
            'title': self.title_edit.text().strip(),
            'device_label': self.device_combo_box.currentData() or '',
            'width': width,
            'height': height,
            'frame_rate': self.frame_rate_combo_box.currentData() or 0,
            'scale_mode': self.scale_mode_combo_box.currentData(),
            'mirror': self.mirror_check_box.isChecked()
        }

    def update_preview(self):
        """
        Show the current settings in the preview
        """
        if not self.is_page_ready:
            return
        spec = self.get_source_spec()
        if spec['device_label']:
            self.preview_info_label.setText(translate('LiveVideoPlugin', 'Connecting...'))
        self.run_in_preview('preview', spec_to_display_source(spec))

    def on_page_ready(self):
        """
        The preview page has loaded
        """
        self.is_page_ready = True
        self.refresh_devices()

    def on_devices_changed(self, devices):
        """
        The preview page has found the connected video inputs

        :param list[str] devices: The labels of the video inputs
        """
        self.has_searched_devices = True
        self.populate_devices(devices)

    def on_device_changed(self):
        """
        Another video input has been selected
        """
        self.selected_device_label = self.device_combo_box.currentData() or ''
        title = self.title_edit.text().strip()
        if self.automatic_title is not None and title in ('', self.automatic_title):
            self.automatic_title = USB_ID_SUFFIX.sub('', self.selected_device_label)
            self.title_edit.setText(self.automatic_title)
        self.update_preview()

    def on_preview_started(self, width, height, frame_rate):
        """
        The preview shows the picture of the video input

        :param int width: The width the video input delivers
        :param int height: The height the video input delivers
        :param float frame_rate: The frame rate the video input delivers, 0 if unknown
        """
        if frame_rate:
            text = translate('LiveVideoPlugin.SourceForm',
                             'The video input delivers {width} × {height} at {frame_rate} fps.').format(
                width=width, height=height, frame_rate=round(frame_rate))
        else:
            text = translate('LiveVideoPlugin.SourceForm', 'The video input delivers {width} × {height}.').format(
                width=width, height=height)
        self.preview_info_label.setText(text)

    def on_preview_failed(self, reason):
        """
        The preview could not show the picture of the video input

        :param str reason: Why the preview failed: "not-connected", "in-use", "not-allowed" or "error"
        """
        messages = {
            'not-connected': translate('LiveVideoPlugin.SourceForm', 'The video input is not connected.'),
            'in-use': translate('LiveVideoPlugin.SourceForm', 'The video input is in use by another program.'),
            'not-allowed': translate('LiveVideoPlugin.SourceForm', 'Access to the video input was denied. Please check '
                                                                   'the camera privacy settings of your system.')
        }
        self.preview_info_label.setText(messages.get(reason, translate('LiveVideoPlugin.SourceForm',
                                                                       'The video input could not be started.')))

    def accept(self):
        """
        Save the source, together with a still image of its picture as thumbnail
        """
        spec = self.get_source_spec()
        if not spec['title']:
            critical_error_message_box(message=translate('LiveVideoPlugin.SourceForm',
                                                         'You need to type in a name for the source.'))
            self.title_edit.setFocus()
            return
        if not spec['device_label']:
            critical_error_message_box(message=translate('LiveVideoPlugin.SourceForm',
                                                         'You need to choose a video input.'))
            self.device_combo_box.setFocus()
            return
        self.save_button.setEnabled(False)
        if self.is_page_ready:
            self.run_in_preview('takeSnapshot', callback=self.save_and_close)
        else:
            self.save_and_close(None)

    def save_and_close(self, snapshot):
        """
        Save the source and close the dialog

        :param str | None snapshot: A still image of the picture as a data URL, None if there is no picture
        """
        self.save_source(snapshot)
        QtWidgets.QDialog.accept(self)

    def save_source(self, snapshot=None):
        """
        Save the source

        :param str | None snapshot: A still image of the picture as a data URL, None to keep the current thumbnail
        """
        spec = self.get_source_spec()
        self.source.title = spec['title']
        self.source.device_label = spec['device_label']
        self.source.width = spec['width']
        self.source.height = spec['height']
        self.source.frame_rate = spec['frame_rate']
        self.source.scale_mode = spec['scale_mode']
        self.source.mirror = spec['mirror']
        self.manager.save_object(self.source)
        if snapshot:
            self.media_item.save_thumbnail(self.source.id, snapshot)
        self.media_item.auto_select_id = self.source.id
        Registry().execute('livevideo_changed', self.source.id)

    def done(self, result):
        """
        Release the video input when the dialog closes

        :param int result: The result of the dialog
        """
        if self.is_page_ready:
            self.run_in_preview('stop')
        self.preview_info_label.setText('')
        super(SourceForm, self).done(result)
