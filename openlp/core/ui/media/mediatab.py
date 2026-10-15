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
The :mod:`~openlp.core.ui.media.mediatab` module holds the configuration tab for the media stuff.
"""
import logging

from PyQt5 import QtWidgets

from openlp.core.common.i18n import translate
from openlp.core.lib.settingstab import SettingsTab
from openlp.core.lib.ui import critical_error_message_box
from openlp.core.ui.icons import UiIcons
from openlp.core.ui.media.vlcplayer import get_audio_output_devices

VLC_ARGUMENT_BLACKLIST = [' -h ', ' --help ', ' -H ', '--full-help ', ' --longhelp ', ' --help-verbose ', ' -l ',
                          ' --list ', ' --list-verbose ']

log = logging.getLogger(__name__)


class MediaTab(SettingsTab):
    """
    MediaTab is the Media settings tab in the settings dialog.
    """
    def __init__(self, parent):
        """
        Constructor
        """
        self.icon_path = UiIcons().video
        player_translated = translate('OpenLP.MediaTab', 'Media')
        super(MediaTab, self).__init__(parent, 'Media', player_translated)

    def setup_ui(self):
        """
        Set up the UI
        """
        self.setObjectName('MediaTab')
        super(MediaTab, self).setup_ui()
        self.live_media_group_box = QtWidgets.QGroupBox(self.left_column)
        self.live_media_group_box.setObjectName('live_media_group_box')
        self.media_layout = QtWidgets.QVBoxLayout(self.live_media_group_box)
        self.media_layout.setObjectName('live_media_layout')
        self.auto_start_check_box = QtWidgets.QCheckBox(self.live_media_group_box)
        self.auto_start_check_box.setObjectName('auto_start_check_box')
        self.media_layout.addWidget(self.auto_start_check_box)
        self.left_layout.addWidget(self.live_media_group_box)
        self.vlc_arguments_group_box = QtWidgets.QGroupBox(self.left_column)
        self.vlc_arguments_group_box.setObjectName('vlc_arguments_group_box')
        self.vlc_arguments_layout = QtWidgets.QFormLayout(self.vlc_arguments_group_box)
        self.vlc_arguments_layout.setObjectName('vlc_arguments_layout')
        self.vlc_arguments_label = QtWidgets.QLabel(self.vlc_arguments_group_box)
        self.vlc_arguments_label.setObjectName('vlc_arguments_label')
        self.vlc_arguments_edit = QtWidgets.QLineEdit(self)
        self.vlc_arguments_layout.addRow(self.vlc_arguments_label, self.vlc_arguments_edit)
        self.left_layout.addWidget(self.vlc_arguments_group_box)
        self.left_layout.addStretch()
        # Audio outputs, e.g. live to Dante and preview to the headphones
        self.audio_output_group_box = QtWidgets.QGroupBox(self.right_column)
        self.audio_output_group_box.setObjectName('audio_output_group_box')
        self.audio_output_layout = QtWidgets.QFormLayout(self.audio_output_group_box)
        self.audio_output_layout.setObjectName('audio_output_layout')
        self.live_audio_label = QtWidgets.QLabel(self.audio_output_group_box)
        self.live_audio_label.setObjectName('live_audio_label')
        self.live_audio_combo_box = QtWidgets.QComboBox(self.audio_output_group_box)
        self.live_audio_combo_box.setObjectName('live_audio_combo_box')
        self.live_audio_combo_box.setSizeAdjustPolicy(
            QtWidgets.QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.live_audio_label.setBuddy(self.live_audio_combo_box)
        self.audio_output_layout.addRow(self.live_audio_label, self.live_audio_combo_box)
        self.preview_audio_label = QtWidgets.QLabel(self.audio_output_group_box)
        self.preview_audio_label.setObjectName('preview_audio_label')
        self.preview_audio_combo_box = QtWidgets.QComboBox(self.audio_output_group_box)
        self.preview_audio_combo_box.setObjectName('preview_audio_combo_box')
        self.preview_audio_combo_box.setSizeAdjustPolicy(
            QtWidgets.QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.preview_audio_label.setBuddy(self.preview_audio_combo_box)
        self.audio_output_layout.addRow(self.preview_audio_label, self.preview_audio_combo_box)
        self.audio_output_info_label = QtWidgets.QLabel(self.audio_output_group_box)
        self.audio_output_info_label.setObjectName('audio_output_info_label')
        self.audio_output_info_label.setWordWrap(True)
        self.audio_output_layout.addRow(self.audio_output_info_label)
        self.right_layout.addWidget(self.audio_output_group_box)
        self.right_layout.addStretch()
        # Connect vlc_arguments_edit content validator
        self.vlc_arguments_edit.editingFinished.connect(self.on_vlc_arguments_edit_finished)

    def retranslate_ui(self):
        """
        Translate the UI on the fly
        """
        self.live_media_group_box.setTitle(translate('MediaPlugin.MediaTab', 'Live Media'))
        self.vlc_arguments_group_box.setTitle(translate('MediaPlugin.MediaTab', 'VLC (requires restart)'))
        self.vlc_arguments_label.setText(translate('MediaPlugin.MediaTab', 'Extra arguments:'))
        self.auto_start_check_box.setText(translate('MediaPlugin.MediaTab', 'Start Live items automatically'))
        self.audio_output_group_box.setTitle(translate('MediaPlugin.MediaTab', 'Audio Output'))
        self.live_audio_label.setText(translate('MediaPlugin.MediaTab', 'Live:'))
        self.preview_audio_label.setText(translate('MediaPlugin.MediaTab', 'Preview:'))
        self.audio_output_info_label.setText(
            translate('MediaPlugin.MediaTab', 'Choose where the sound of videos and background audio goes, e.g. the '
                                              'live sound to Dante Via or Dante Virtual Soundcard and the preview '
                                              'sound to your headphones.'))

    def load(self):
        """
        Load the settings
        """
        self.auto_start_check_box.setChecked(self.settings.value('media/media auto start'))
        self.vlc_arguments_edit.setText(self.settings.value('media/vlc arguments'))
        # The audio outputs are listed when the tab is shown, as asking VLC for them takes a moment
        self.has_audio_outputs = False
        if self.isVisible():
            self.tab_visible()

    def tab_visible(self):
        """
        List the audio outputs when the tab is shown for the first time
        """
        if self.has_audio_outputs:
            return
        devices = get_audio_output_devices()
        for combo_box, key in ((self.live_audio_combo_box, 'media/live audio device'),
                               (self.preview_audio_combo_box, 'media/preview audio device')):
            self.fill_audio_output_combo_box(combo_box, devices, self.settings.value(key) or {})
        self.has_audio_outputs = True

    @staticmethod
    def fill_audio_output_combo_box(combo_box, devices, selected):
        """
        Fill a combo box with the audio outputs. The chosen output stays in the list when it is not connected.

        :param QtWidgets.QComboBox combo_box: The combo box to fill
        :param list[(str, str)] devices: The audio outputs as (id, name) tuples
        :param dict selected: The chosen output, {'id': '', 'name': ''} for the system default
        """
        combo_box.clear()
        combo_box.addItem(translate('MediaPlugin.MediaTab', 'System default'), {'id': '', 'name': ''})
        for device_id, name in devices:
            combo_box.addItem(name, {'id': device_id, 'name': name})
        selected_id = selected.get('id', '')
        index = next((i for i in range(combo_box.count()) if combo_box.itemData(i)['id'] == selected_id), -1)
        if index == -1:
            # Fall back to the name, since the id can change when a driver is reinstalled
            index = next((i for i in range(1, combo_box.count())
                          if combo_box.itemData(i)['name'] == selected.get('name')), -1)
        if index == -1:
            combo_box.addItem(translate('MediaPlugin.MediaTab', '{device} (not connected)').format(
                device=selected.get('name') or selected_id), dict(selected))
            index = combo_box.count() - 1
        combo_box.setCurrentIndex(index)

    def save(self):
        """
        Save the settings
        """
        setting_key = 'media/media auto start'
        if self.settings.value(setting_key) != self.auto_start_check_box.checkState():
            self.settings.setValue(setting_key, self.auto_start_check_box.checkState())
        self.settings.setValue('media/vlc arguments', self.vlc_arguments_edit.text())
        if self.has_audio_outputs:
            self.settings.setValue('media/live audio device', self.live_audio_combo_box.currentData())
            self.settings.setValue('media/preview audio device', self.preview_audio_combo_box.currentData())

    def post_set_up(self, post_update=False):
        """
        Late setup for players as the MediaController has to be initialised first.

        :param post_update: Indicates if called before or after updates.
        """
        pass

    def on_revert(self):
        pass

    def on_vlc_arguments_edit_finished(self):
        """
        Verify that there is no blacklisted arguments in entered that could cause issues, like shutting down OpenLP.
        """
        # This weird modified checking and setting is needed to prevent an infinite loop due to setting the focus
        # back to vlc_arguments_edit triggers the editingFinished signal.
        if not self.vlc_arguments_edit.isModified():
            self.vlc_arguments_edit.setModified(True)
            return
        self.vlc_arguments_edit.setModified(False)
        # Check for blacklisted arguments
        arguments = ' ' + self.vlc_arguments_edit.text() + ' '
        self.vlc_arguments_edit.setModified(False)
        for blacklisted in VLC_ARGUMENT_BLACKLIST:
            if blacklisted in arguments:
                critical_error_message_box(message=translate('MediaPlugin.MediaTab',
                                                             'The argument {arg} must not be used for VLC!').format(
                                                                 arg=blacklisted.strip()), parent=self)
                self.vlc_arguments_edit.setFocus()
                return
