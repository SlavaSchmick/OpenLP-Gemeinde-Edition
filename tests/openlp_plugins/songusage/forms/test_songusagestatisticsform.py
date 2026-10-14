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
Test the song statistics window in openlp.plugins.songusage.forms.songusagestatisticsform
"""
from datetime import date, time, timedelta
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from PyQt5 import QtCore

from openlp.plugins.songusage.forms import songusagestatisticsform
from openlp.plugins.songusage.forms.songusagestatisticsform import SongUsageStatisticsForm
from openlp.plugins.songusage.lib.statistics import Period

TODAY = date.today()


def usage(days_ago, title):
    return SimpleNamespace(usagedate=TODAY - timedelta(days=days_ago), usagetime=time(10), title=title, authors='')


@pytest.fixture
def form(settings):
    plugin = MagicMock()
    plugin.manager.get_all_objects.return_value = [
        usage(400, 'D0001 Großer Gott'), usage(14, 'D0001 Großer Gott'), usage(14, 'R047_Тебе поём'),
        usage(7, 'D0001 Großer Gott'), usage(7, 'D0005 Nun danket'), usage(0, 'R047_Тебе поём')]
    statistics_form = SongUsageStatisticsForm(plugin, None)
    statistics_form.load_statistics()
    yield statistics_form
    statistics_form.close()


def table(form):
    return [[form.song_table.item(row, column).text() for column in range(4)]
            for row in range(form.song_table.rowCount())]


def test_most_sung_songs(form):
    """
    Test that the songs of the last 12 months are shown, the most sung first
    """
    # GIVEN: The statistics window with song usage
    # WHEN: It is shown
    # THEN: The songs of the last 12 months are listed by how often they were sung
    assert form.period_combo_box.currentIndex() == Period.TwelveMonths
    assert table(form) == [['1.', 'D1', 'Großer Gott', '2'], ['1.', 'R47', 'Тебе поём', '2'],
                           ['3.', 'D5', 'Nun danket', '1']]
    assert [form.book_combo_box.itemData(index) for index in range(form.book_combo_box.count())] == ['', 'D', 'R']
    assert form.pdf_button.isEnabled() and form.csv_button.isEnabled()


def test_filters(form):
    """
    Test that the period, the song book and the search filter the songs
    """
    # GIVEN: The statistics window with song usage
    # WHEN: All song usage is selected
    form.period_combo_box.setCurrentIndex(Period.All)

    # THEN: The older song usage is counted too
    assert table(form)[0] == ['1.', 'D1', 'Großer Gott', '3']
    assert form.from_date_edit.date().toPyDate() == TODAY - timedelta(days=400)

    # WHEN: Only song book R is selected, and then a song is searched in all song books
    form.book_combo_box.setCurrentIndex(form.book_combo_box.findData('R'))
    assert [row[1] for row in table(form)] == ['R47']
    form.book_combo_box.setCurrentIndex(0)
    form.search_edit.setText('d5')

    # THEN: Only the matching songs are listed
    assert [row[1] for row in table(form)] == ['D5']


def test_changed_day_makes_a_custom_period(form):
    """
    Test that changing a day selects a custom period
    """
    # GIVEN: The statistics window with song usage
    # WHEN: The first day is changed to the last week
    form.from_date_edit.setDate(QtCore.QDate(TODAY - timedelta(days=7)))

    # THEN: The period is custom, and only its songs are listed
    assert form.period_combo_box.currentIndex() == Period.Custom
    assert [row[1] for row in table(form)] == ['D1', 'D5', 'R47']


def test_no_songs(form):
    """
    Test that a message is shown instead of an empty list
    """
    # GIVEN: The statistics window with song usage
    form.show()

    # WHEN: A song which wasn't sung is searched
    form.search_edit.setText('d999')

    # THEN: The message is shown instead of the list, and nothing can be saved
    assert form.song_table.isHidden()
    assert form.empty_label.isVisible()
    assert not form.pdf_button.isEnabled()


def test_save_csv(form, tmp_path):
    """
    Test that the list is saved as a CSV file for spreadsheets
    """
    # GIVEN: The statistics window with song usage
    # WHEN: The list is saved without a suffix
    with patch.object(songusagestatisticsform.FileDialog, 'getSaveFileName', return_value=(tmp_path / 'liste', '')):
        form.on_save_csv()

    # THEN: The file has the list, and the folder is remembered
    text = (tmp_path / 'liste.csv').read_text(encoding='utf-8-sig')
    assert text.splitlines() == ['Rank;No.;Song;Times Sung', '1;D1;Großer Gott;2', '1;R47;Тебе поём;2',
                                 '3;D5;Nun danket;1']
    assert form.settings.value('songusage/last directory export') == tmp_path


def test_save_cancelled(form, tmp_path):
    """
    Test that nothing is saved when the file dialog is cancelled
    """
    # GIVEN: The statistics window with song usage
    # WHEN: Saving is cancelled
    with patch.object(songusagestatisticsform.FileDialog, 'getSaveFileName', return_value=(None, '')):
        form.on_save_csv()
        form.on_save_pdf()

    # THEN: Nothing is saved
    assert list(tmp_path.iterdir()) == []


def test_save_pdf(form, tmp_path):
    """
    Test that the list is saved as a PDF
    """
    # GIVEN: The statistics window with song usage
    # WHEN: The list is saved as a PDF
    with patch.object(songusagestatisticsform.FileDialog, 'getSaveFileName',
                      return_value=(tmp_path / 'liste.pdf', '')):
        form.on_save_pdf()

    # THEN: The PDF is written, with the songs in the document
    assert (tmp_path / 'liste.pdf').read_bytes()[:4] == b'%PDF'
    assert 'Тебе поём' in form.statistics_html()
    assert '<td>D5</td><td>Nun danket</td>' in form.statistics_html()


@patch.object(songusagestatisticsform, 'critical_error_message_box')
def test_save_csv_failed(mocked_message_box, form, tmp_path):
    """
    Test that a failed saving is reported
    """
    # GIVEN: The statistics window, and a folder which doesn't exist
    # WHEN: The list is saved there
    with patch.object(songusagestatisticsform.FileDialog, 'getSaveFileName',
                      return_value=(tmp_path / 'missing' / 'liste.csv', '')):
        form.on_save_csv()

    # THEN: The error is shown
    mocked_message_box.assert_called_once()
