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
from PyQt5 import QtCore, QtWidgets

from openlp.core.common.i18n import translate
from openlp.core.lib.ui import create_button_box
from openlp.core.ui.icons import UiIcons
from openlp.core.widgets.layouts import AspectRatioLayout


class Ui_SourceDialog(object):
    def setup_ui(self, source_dialog):
        """
        Build the source dialog: the settings of the source on the left, a live preview on the right

        :param source_dialog: The dialog
        """
        source_dialog.setObjectName('source_dialog')
        source_dialog.setWindowIcon(UiIcons().main_icon)
        source_dialog.resize(780, 340)
        self.dialog_layout = QtWidgets.QVBoxLayout(source_dialog)
        self.dialog_layout.setObjectName('dialog_layout')
        self.central_layout = QtWidgets.QHBoxLayout()
        self.central_layout.setObjectName('central_layout')
        # Settings of the source
        self.settings_layout = QtWidgets.QFormLayout()
        self.settings_layout.setObjectName('settings_layout')
        self.title_label = QtWidgets.QLabel(source_dialog)
        self.title_label.setObjectName('title_label')
        self.title_edit = QtWidgets.QLineEdit(source_dialog)
        self.title_edit.setObjectName('title_edit')
        self.title_label.setBuddy(self.title_edit)
        self.settings_layout.addRow(self.title_label, self.title_edit)
        self.device_label = QtWidgets.QLabel(source_dialog)
        self.device_label.setObjectName('device_label')
        self.device_layout = QtWidgets.QHBoxLayout()
        self.device_layout.setObjectName('device_layout')
        self.device_combo_box = QtWidgets.QComboBox(source_dialog)
        self.device_combo_box.setObjectName('device_combo_box')
        self.device_combo_box.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,
                                            QtWidgets.QSizePolicy.Policy.Fixed)
        self.device_combo_box.setSizeAdjustPolicy(
            QtWidgets.QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.device_label.setBuddy(self.device_combo_box)
        self.device_layout.addWidget(self.device_combo_box)
        self.refresh_button = QtWidgets.QToolButton(source_dialog)
        self.refresh_button.setObjectName('refresh_button')
        self.refresh_button.setIcon(UiIcons().refresh)
        self.device_layout.addWidget(self.refresh_button)
        self.settings_layout.addRow(self.device_label, self.device_layout)
        self.resolution_label = QtWidgets.QLabel(source_dialog)
        self.resolution_label.setObjectName('resolution_label')
        self.resolution_combo_box = QtWidgets.QComboBox(source_dialog)
        self.resolution_combo_box.setObjectName('resolution_combo_box')
        self.resolution_label.setBuddy(self.resolution_combo_box)
        self.settings_layout.addRow(self.resolution_label, self.resolution_combo_box)
        self.frame_rate_label = QtWidgets.QLabel(source_dialog)
        self.frame_rate_label.setObjectName('frame_rate_label')
        self.frame_rate_combo_box = QtWidgets.QComboBox(source_dialog)
        self.frame_rate_combo_box.setObjectName('frame_rate_combo_box')
        self.frame_rate_label.setBuddy(self.frame_rate_combo_box)
        self.settings_layout.addRow(self.frame_rate_label, self.frame_rate_combo_box)
        self.scale_mode_label = QtWidgets.QLabel(source_dialog)
        self.scale_mode_label.setObjectName('scale_mode_label')
        self.scale_mode_combo_box = QtWidgets.QComboBox(source_dialog)
        self.scale_mode_combo_box.setObjectName('scale_mode_combo_box')
        self.scale_mode_label.setBuddy(self.scale_mode_combo_box)
        self.settings_layout.addRow(self.scale_mode_label, self.scale_mode_combo_box)
        self.mirror_check_box = QtWidgets.QCheckBox(source_dialog)
        self.mirror_check_box.setObjectName('mirror_check_box')
        self.settings_layout.addRow('', self.mirror_check_box)
        self.central_layout.addLayout(self.settings_layout, 1)
        # Live preview, with a 16:9 frame like the screen
        self.preview_layout = QtWidgets.QVBoxLayout()
        self.preview_layout.setObjectName('preview_layout')
        self.preview_frame = QtWidgets.QFrame(source_dialog)
        self.preview_frame.setObjectName('preview_frame')
        self.preview_frame.setMinimumSize(QtCore.QSize(352, 198))
        self.preview_frame.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,
                                         QtWidgets.QSizePolicy.Policy.Expanding)
        self.preview_frame.setFrameShape(QtWidgets.QFrame.Shape.Box)
        self.preview_frame.setStyleSheet('#preview_frame { background: black; }')
        self.preview_frame_layout = AspectRatioLayout(self.preview_frame, 16.0 / 9.0)
        self.preview_frame_layout.setContentsMargins(0, 0, 0, 0)
        self.preview_frame_layout.setObjectName('preview_frame_layout')
        self.preview_layout.addWidget(self.preview_frame, 1)
        self.preview_info_label = QtWidgets.QLabel(source_dialog)
        self.preview_info_label.setObjectName('preview_info_label')
        self.preview_info_label.setAlignment(QtCore.Qt.AlignCenter)
        self.preview_layout.addWidget(self.preview_info_label)
        self.central_layout.addLayout(self.preview_layout, 1)
        self.dialog_layout.addLayout(self.central_layout)
        self.button_box = create_button_box(source_dialog, 'button_box', ['cancel', 'save'])
        self.save_button = self.button_box.button(QtWidgets.QDialogButtonBox.StandardButton.Save)
        self.dialog_layout.addWidget(self.button_box)
        self.retranslate_ui(source_dialog)

    def retranslate_ui(self, source_dialog):
        source_dialog.setWindowTitle(translate('LiveVideoPlugin.SourceForm', 'Live Video Source'))
        self.title_label.setText(translate('LiveVideoPlugin.SourceForm', '&Name:'))
        self.device_label.setText(translate('LiveVideoPlugin.SourceForm', '&Video input:'))
        self.refresh_button.setToolTip(translate('LiveVideoPlugin.SourceForm', 'Search for video inputs again'))
        self.resolution_label.setText(translate('LiveVideoPlugin.SourceForm', '&Resolution:'))
        self.frame_rate_label.setText(translate('LiveVideoPlugin.SourceForm', '&Frame rate:'))
        self.scale_mode_label.setText(translate('LiveVideoPlugin.SourceForm', '&Scaling:'))
        self.mirror_check_box.setText(translate('LiveVideoPlugin.SourceForm', '&Mirror the picture'))
