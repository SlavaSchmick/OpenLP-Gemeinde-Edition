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
The :mod:`~openlp.plugins.livevideo.lib.livevideotab` module contains the settings tab of the Live Video plugin.
"""
from PyQt5 import QtWidgets

from openlp.core.common.enum import ImageThemeMode
from openlp.core.common.i18n import translate
from openlp.core.common.registry import Registry
from openlp.core.lib.settingstab import SettingsTab
from openlp.core.lib.ui import find_and_set_in_combo_box
from openlp.plugins.livevideo.lib import validate_scale_mode
from openlp.plugins.livevideo.lib.ui import fill_frame_rate_combo_box, fill_resolution_combo_box, \
    fill_scale_mode_combo_box, select_combo_box_data


class LiveVideoTab(SettingsTab):
    """
    LiveVideoTab is the Live Video settings tab in the settings dialog.
    """
    def setup_ui(self):
        self.setObjectName('LiveVideoTab')
        super(LiveVideoTab, self).setup_ui()
        # Background, the same choice as for images
        self.background_group_box = QtWidgets.QGroupBox(self.left_column)
        self.background_group_box.setObjectName('background_group_box')
        self.background_layout = QtWidgets.QFormLayout(self.background_group_box)
        self.background_layout.setObjectName('background_layout')
        self.radio_group = QtWidgets.QButtonGroup(self)
        self.use_black_radio = QtWidgets.QRadioButton('', self.background_group_box)
        self.use_black_radio.setObjectName('use_black_radio')
        self.radio_group.addButton(self.use_black_radio, ImageThemeMode.Black)
        self.background_layout.addRow(self.use_black_radio)
        self.custom_theme_radio = QtWidgets.QRadioButton('', self.background_group_box)
        self.custom_theme_radio.setObjectName('custom_theme_radio')
        self.radio_group.addButton(self.custom_theme_radio, ImageThemeMode.CustomTheme)
        self.background_layout.addRow(self.custom_theme_radio)
        self.theme_label = QtWidgets.QLabel(self.background_group_box)
        self.theme_label.setObjectName('theme_label')
        self.theme_combo_box = QtWidgets.QComboBox(self.background_group_box)
        self.theme_combo_box.setSizeAdjustPolicy(QtWidgets.QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLength)
        self.theme_combo_box.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        self.theme_combo_box.setObjectName('theme_combo_box')
        self.theme_label.setBuddy(self.theme_combo_box)
        self.background_layout.addRow(self.theme_label, self.theme_combo_box)
        self.background_info_label = QtWidgets.QLabel(self.background_group_box)
        self.background_info_label.setObjectName('background_info_label')
        self.background_info_label.setWordWrap(True)
        self.background_layout.addRow(self.background_info_label)
        self.left_layout.addWidget(self.background_group_box)
        # Preview panel
        self.preview_group_box = QtWidgets.QGroupBox(self.left_column)
        self.preview_group_box.setObjectName('preview_group_box')
        self.preview_layout = QtWidgets.QVBoxLayout(self.preview_group_box)
        self.preview_layout.setObjectName('preview_layout')
        self.live_picture_check_box = QtWidgets.QCheckBox(self.preview_group_box)
        self.live_picture_check_box.setObjectName('live_picture_check_box')
        self.preview_layout.addWidget(self.live_picture_check_box)
        self.live_picture_info_label = QtWidgets.QLabel(self.preview_group_box)
        self.live_picture_info_label.setObjectName('live_picture_info_label')
        self.live_picture_info_label.setWordWrap(True)
        self.preview_layout.addWidget(self.live_picture_info_label)
        self.left_layout.addWidget(self.preview_group_box)
        self.left_layout.addStretch()
        # Defaults for new sources
        self.defaults_group_box = QtWidgets.QGroupBox(self.right_column)
        self.defaults_group_box.setObjectName('defaults_group_box')
        self.defaults_layout = QtWidgets.QFormLayout(self.defaults_group_box)
        self.defaults_layout.setObjectName('defaults_layout')
        self.resolution_label = QtWidgets.QLabel(self.defaults_group_box)
        self.resolution_label.setObjectName('resolution_label')
        self.resolution_combo_box = QtWidgets.QComboBox(self.defaults_group_box)
        self.resolution_combo_box.setObjectName('resolution_combo_box')
        self.resolution_label.setBuddy(self.resolution_combo_box)
        self.defaults_layout.addRow(self.resolution_label, self.resolution_combo_box)
        self.frame_rate_label = QtWidgets.QLabel(self.defaults_group_box)
        self.frame_rate_label.setObjectName('frame_rate_label')
        self.frame_rate_combo_box = QtWidgets.QComboBox(self.defaults_group_box)
        self.frame_rate_combo_box.setObjectName('frame_rate_combo_box')
        self.frame_rate_label.setBuddy(self.frame_rate_combo_box)
        self.defaults_layout.addRow(self.frame_rate_label, self.frame_rate_combo_box)
        self.scale_mode_label = QtWidgets.QLabel(self.defaults_group_box)
        self.scale_mode_label.setObjectName('scale_mode_label')
        self.scale_mode_combo_box = QtWidgets.QComboBox(self.defaults_group_box)
        self.scale_mode_combo_box.setObjectName('scale_mode_combo_box')
        self.scale_mode_label.setBuddy(self.scale_mode_combo_box)
        self.defaults_layout.addRow(self.scale_mode_label, self.scale_mode_combo_box)
        self.right_layout.addWidget(self.defaults_group_box)
        self.right_layout.addStretch()
        # Signals and slots
        self.radio_group.buttonToggled.connect(self.on_radio_group_button_toggled)
        self.theme_combo_box.activated.connect(self.on_theme_changed)
        Registry().register_function('theme_update_list', self.update_theme_list)

    def retranslate_ui(self):
        self.background_group_box.setTitle(translate('LiveVideoPlugin.LiveVideoTab', 'Background'))
        self.use_black_radio.setText(translate('LiveVideoPlugin.LiveVideoTab', 'Use blank theme'))
        self.custom_theme_radio.setText(translate('LiveVideoPlugin.LiveVideoTab', 'Custom theme'))
        self.theme_label.setText(translate('LiveVideoPlugin.LiveVideoTab', 'Theme:'))
        self.background_info_label.setText(
            translate('LiveVideoPlugin.LiveVideoTab', 'The background is visible around a picture that doesn\'t fill '
                                                      'the screen, and when the screen is blanked to the theme.'))
        self.preview_group_box.setTitle(translate('LiveVideoPlugin.LiveVideoTab', 'Preview Panel'))
        self.live_picture_check_box.setText(translate('LiveVideoPlugin.LiveVideoTab',
                                                      'Show the live picture in the Preview panel'))
        self.live_picture_info_label.setText(
            translate('LiveVideoPlugin.LiveVideoTab', 'When this is disabled, the Preview panel shows a still image of '
                                                      'the source, which saves computing power.'))
        self.defaults_group_box.setTitle(translate('LiveVideoPlugin.LiveVideoTab', 'New Sources'))
        self.resolution_label.setText(translate('LiveVideoPlugin.LiveVideoTab', 'Resolution:'))
        self.frame_rate_label.setText(translate('LiveVideoPlugin.LiveVideoTab', 'Frame rate:'))
        self.scale_mode_label.setText(translate('LiveVideoPlugin.LiveVideoTab', 'Scaling:'))
        fill_resolution_combo_box(self.resolution_combo_box)
        fill_frame_rate_combo_box(self.frame_rate_combo_box)
        fill_scale_mode_combo_box(self.scale_mode_combo_box)

    def on_radio_group_button_toggled(self, button, checked):
        """
        Handles the toggled signal on the radio buttons. The signal is emitted twice if a radio butting being toggled on
        causes another radio button in the group to be toggled off.

        :param QtWidgets.QRadioButton button: The button that has toggled
        :param bool checked: The buttons new state
        """
        group_id = self.radio_group.id(button)
        if checked:
            self.background_mode = group_id
        self.theme_combo_box.setEnabled(group_id == ImageThemeMode.CustomTheme and checked)

    def on_theme_changed(self):
        self.theme = self.theme_combo_box.currentText()

    def update_theme_list(self, theme_list):
        """
        Called from ThemeManager when the Themes have changed.

        :param theme_list: The list of available themes::

                ['Bible Theme', 'Song Theme']
        """
        self.theme = self.settings.value('livevideo/theme')
        self.theme_combo_box.clear()
        self.theme_combo_box.addItems(theme_list)
        find_and_set_in_combo_box(self.theme_combo_box, self.theme)

    def load(self):
        self.background_mode = self.settings.value('livevideo/background mode')
        self.initial_background_mode = self.background_mode
        self.radio_group.button(self.background_mode).setChecked(True)
        self.theme = self.settings.value('livevideo/theme')
        self.initial_theme = self.theme
        find_and_set_in_combo_box(self.theme_combo_box, self.theme)
        self.live_picture_check_box.setChecked(self.settings.value('livevideo/live picture in preview'))
        select_combo_box_data(self.resolution_combo_box, self.settings.value('livevideo/default resolution'))
        select_combo_box_data(self.frame_rate_combo_box, self.settings.value('livevideo/default frame rate'))
        select_combo_box_data(self.scale_mode_combo_box,
                              validate_scale_mode(self.settings.value('livevideo/default scale mode')))

    def save(self):
        self.settings.setValue('livevideo/background mode', self.radio_group.checkedId())
        self.settings.setValue('livevideo/theme', self.theme)
        self.settings.setValue('livevideo/live picture in preview', self.live_picture_check_box.isChecked())
        self.settings.setValue('livevideo/default resolution', self.resolution_combo_box.currentData())
        self.settings.setValue('livevideo/default frame rate', self.frame_rate_combo_box.currentData())
        self.settings.setValue('livevideo/default scale mode', self.scale_mode_combo_box.currentData())
        if self.initial_theme != self.theme or self.initial_background_mode != self.background_mode:
            self.settings_form.register_post_process('livevideo_config_updated')
