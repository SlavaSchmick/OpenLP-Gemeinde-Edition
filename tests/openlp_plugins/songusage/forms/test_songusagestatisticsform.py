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
Test the song usage statistics window in openlp.plugins.songusage.forms.songusagestatisticsform
"""
import json
import re
from datetime import date, time
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from PyQt5 import QtWidgets

from openlp.plugins.songusage.forms import songusagestatisticsform
from openlp.plugins.songusage.forms.songusagestatisticsform import SongUsageStatisticsForm, statistics_texts

PLUGINS_DIR = Path(songusagestatisticsform.__file__).parents[2]
PAGE_PATH = PLUGINS_DIR / 'songusage' / 'html' / 'statistics.html'


class FakeWebView(QtWidgets.QWidget):
    """
    A web view which records what it shows, as the browser engine isn't needed for these tests
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHtml = MagicMock()
        self.setUrl = MagicMock()
        self.page = MagicMock()


@pytest.fixture
def form(settings):
    plugin = MagicMock()
    plugin.manager.get_all_objects.return_value = [
        SimpleNamespace(usagedate=date(2026, 10, 4), usagetime=time(10), title='D0203 Großer Gott', authors='A'),
        SimpleNamespace(usagedate=date(2026, 10, 11), usagetime=time(10), title='R047_Тебе поём', authors='B')]
    with patch.object(songusagestatisticsform.QtWebEngineWidgets, 'QWebEngineView', FakeWebView), \
            patch.object(songusagestatisticsform.AppLocation, 'get_directory', return_value=PLUGINS_DIR):
        statistics_form = SongUsageStatisticsForm(plugin, None)
        yield statistics_form
    statistics_form.close()


def page_value(page, name):
    return json.loads(re.search(r'var {name} = (.*);'.format(name=name), page).group(1))


def test_page_texts_are_translated():
    """
    Test that every text of the statistics page is in the translated texts
    """
    # GIVEN: The statistics page
    page = PAGE_PATH.read_text(encoding='utf-8')

    # WHEN: The texts of the page are collected, also those which are split over several lines
    calls = re.findall(r"\bt\(((?:'[^']*'\s*\+\s*)*'[^']*')", page)
    texts = {''.join(re.findall(r"'([^']*)'", call)) for call in calls}

    # THEN: All of them are translated, and there are no unused translations
    assert texts == set(statistics_texts())


def test_load_statistics(form):
    """
    Test that the statistics window shows the song usage
    """
    # GIVEN: The statistics window, with song usage in the database
    # WHEN: The statistics are loaded
    with patch.object(songusagestatisticsform.LanguageManager, 'get_language', return_value='en_GB'):
        form.load_statistics()

    # THEN: The page is shown with the data, the texts and the settings
    page = form.web_view.setHtml.call_args[0][0]
    assert page_value(page, 'DATA')['events'] == [['2026-10-04', 0], ['2026-10-11', 1]]
    assert page_value(page, 'TEXTS')['Most sung songs'] == 'Most sung songs'
    settings = page_value(page, 'SETTINGS')
    assert settings['language'] == 'en-GB'
    assert settings['today'] == date.today().isoformat()
    form.web_view.setUrl.assert_not_called()


def test_load_large_statistics(form, tmp_path):
    """
    Test that a large page is shown from a file, as it is too large to be shown directly
    """
    # GIVEN: The statistics window, with a small limit for the page size
    # WHEN: The statistics are loaded
    with patch.object(songusagestatisticsform, 'MAX_HTML_SIZE', 100), \
            patch.object(songusagestatisticsform.AppLocation, 'get_section_data_path', return_value=tmp_path):
        form.load_statistics()

    # THEN: The page is shown from a file
    form.web_view.setHtml.assert_not_called()
    assert (tmp_path / 'statistics.html').read_text(encoding='utf-8') == form.page_html
    form.web_view.setUrl.assert_called_once()


def test_save_html(form, tmp_path):
    """
    Test that the statistics are saved as a web page with light colours
    """
    # GIVEN: The statistics window with its statistics
    form.load_statistics()

    # WHEN: The statistics are saved
    with patch.object(songusagestatisticsform.FileDialog, 'getSaveFileName',
                      return_value=(tmp_path / 'statistik', '')):
        form.on_save_html()

    # THEN: The page is saved, with the html suffix, in light colours
    page = (tmp_path / 'statistik.html').read_text(encoding='utf-8')
    assert page_value(page, 'DATA')['songs'][1]['name'] == 'Тебе поём'
    assert page_value(page, 'SETTINGS')['dark'] is False
    assert form.settings.value('songusage/last directory export') == tmp_path


def test_save_html_cancelled(form, tmp_path):
    """
    Test that nothing is saved when the file dialog is cancelled
    """
    # GIVEN: The statistics window with its statistics
    form.load_statistics()

    # WHEN: Saving is cancelled
    with patch.object(songusagestatisticsform.FileDialog, 'getSaveFileName', return_value=(None, '')):
        form.on_save_html()

    # THEN: Nothing is saved
    assert list(tmp_path.iterdir()) == []


def test_save_pdf(form, tmp_path):
    """
    Test that the statistics are printed to a PDF
    """
    # GIVEN: The statistics window with its statistics
    form.load_statistics()

    # WHEN: The statistics are saved as a PDF
    with patch.object(songusagestatisticsform.FileDialog, 'getSaveFileName',
                      return_value=(tmp_path / 'statistik.pdf', '')):
        form.on_save_pdf()

    # THEN: The page is printed to the file
    form.web_view.page().printToPdf.assert_called_once_with(str(tmp_path / 'statistik.pdf'))


@patch.object(songusagestatisticsform, 'critical_error_message_box')
def test_save_pdf_failed(mocked_message_box, form):
    """
    Test that a failed PDF is reported
    """
    # GIVEN: The statistics window
    # WHEN: Printing the PDF failed
    form._on_pdf_finished('C:/statistik.pdf', False)

    # THEN: The error is shown
    mocked_message_box.assert_called_once()
    assert 'C:/statistik.pdf' in mocked_message_box.call_args[0][1]
