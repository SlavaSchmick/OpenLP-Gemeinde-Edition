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
The :mod:`~openlp.plugins.livevideo.lib.ui` module contains user interface helpers shared by the settings tab and the
source dialog of the Live Video plugin.
"""
from openlp.core.common.i18n import translate
from openlp.plugins.livevideo.lib import FRAME_RATES, RESOLUTIONS, ScaleMode, resolution_to_string


def fill_resolution_combo_box(combo_box):
    """
    Fill a combo box with the resolutions. The item data is the resolution as a string, "" for automatic.

    :param QtWidgets.QComboBox combo_box: The combo box to fill
    """
    combo_box.clear()
    combo_box.addItem(translate('LiveVideoPlugin', 'Automatic (Full HD if available)'), '')
    for width, height in RESOLUTIONS:
        combo_box.addItem('{width} × {height}'.format(width=width, height=height), resolution_to_string(width, height))


def fill_frame_rate_combo_box(combo_box):
    """
    Fill a combo box with the frame rates. The item data is the frame rate, 0 for automatic.

    :param QtWidgets.QComboBox combo_box: The combo box to fill
    """
    combo_box.clear()
    combo_box.addItem(translate('LiveVideoPlugin', 'Automatic'), 0)
    for frame_rate in FRAME_RATES:
        combo_box.addItem(translate('LiveVideoPlugin', '{frame_rate} fps').format(frame_rate=frame_rate), frame_rate)


def fill_scale_mode_combo_box(combo_box):
    """
    Fill a combo box with the scale modes. The item data is the scale mode.

    :param QtWidgets.QComboBox combo_box: The combo box to fill
    """
    combo_box.clear()
    for scale_mode, name in ScaleMode.get_choices():
        combo_box.addItem(name, scale_mode)


def select_combo_box_data(combo_box, data):
    """
    Select the item of a combo box which has the given data, or the first item if there is none

    :param QtWidgets.QComboBox combo_box: The combo box
    :param data: The data of the item to select
    """
    index = combo_box.findData(data)
    combo_box.setCurrentIndex(index if index > -1 else 0)
