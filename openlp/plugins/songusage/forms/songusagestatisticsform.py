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
The song usage statistics: a window with the most sung songs, the songs per week or month, the songs per day and the
songs which weren't sung for a while. It can be saved as a PDF or as a web page.
"""
import logging
from datetime import date
from pathlib import Path

from PyQt5 import QtCore, QtWebEngineWidgets, QtWidgets

from openlp.core.common.applocation import AppLocation
from openlp.core.common.i18n import LanguageManager, translate
from openlp.core.common.mixins import RegistryProperties
from openlp.core.lib.ui import critical_error_message_box
from openlp.core.ui.icons import UiIcons
from openlp.core.widgets.dialogs import FileDialog
from openlp.plugins.songusage.lib.db import SongUsageItem
from openlp.plugins.songusage.lib.statistics import build_statistics_data, render_statistics_page

log = logging.getLogger(__name__)

# QWebEngineView.setHtml() can't show pages larger than 2 MB, larger pages are shown from a file
MAX_HTML_SIZE = 1800000


def statistics_texts():
    """
    The translated texts of the statistics page
    """
    def text(source):
        return translate('SongUsagePlugin.SongUsageStatisticsForm', source)

    sources = [
        'Song statistics', '4 weeks', '3 months', '12 months', 'This year', 'All', 'Period', 'All songbooks',
        'Search song or number, e.g. d203', 'Days with songs', 'Songs sung', 'Different songs', 'Songs per day',
        'Songbooks', 'Other', 'W{week}', 'Week of {date}', '{songs} songs on {days} days', 'Songs per week',
        'Songs per month', 'Show less', 'Show all ({count})', 'Most sung songs', 'No songs in this period.', 'Song',
        'Times sung', 'Last sung', 'Not sung in this period', '{days} days ago', 'No song usage recorded yet',
        'Turn on song usage tracking: Tools → Song Usage Tracking → Toggle Tracking. From then on, every song which '
        'is shown live is recorded.',
        '{from} to {to}', 'Songbook {book}', 'Search: {query}',
        'A song which is shown several times on a day counts once on that day. Click on a song to see the days it '
        'was sung.'
    ]
    return {source: text(source) for source in sources}


class SongUsageStatisticsForm(QtWidgets.QDialog, RegistryProperties):
    """
    The window with the song usage statistics
    """
    def __init__(self, plugin, parent):
        super().__init__(parent, QtCore.Qt.Window | QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint |
                         QtCore.Qt.WindowMinMaxButtonsHint | QtCore.Qt.WindowCloseButtonHint)
        self.plugin = plugin
        self.page_html = ''
        self.page_arguments = None
        self.setup_ui()

    def setup_ui(self):
        self.setObjectName('song_usage_statistics_form')
        self.setWindowIcon(UiIcons().main_icon)
        self.resize(1180, 820)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 8)
        self.layout.setSpacing(8)
        self.web_view = QtWebEngineWidgets.QWebEngineView(self)
        self.web_view.setObjectName('web_view')
        self.web_view.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.layout.addWidget(self.web_view, 1)
        self.button_box = QtWidgets.QDialogButtonBox(self)
        self.button_box.setObjectName('button_box')
        self.pdf_button = self.button_box.addButton('', QtWidgets.QDialogButtonBox.ActionRole)
        self.pdf_button.setObjectName('pdf_button')
        self.html_button = self.button_box.addButton('', QtWidgets.QDialogButtonBox.ActionRole)
        self.html_button.setObjectName('html_button')
        self.close_button = self.button_box.addButton(QtWidgets.QDialogButtonBox.Close)
        self.button_box.setContentsMargins(8, 0, 8, 0)
        self.layout.addWidget(self.button_box)
        self.pdf_button.clicked.connect(self.on_save_pdf)
        self.html_button.clicked.connect(self.on_save_html)
        self.button_box.rejected.connect(self.close)
        self.retranslate_ui()

    def retranslate_ui(self):
        self.setWindowTitle(translate('SongUsagePlugin.SongUsageStatisticsForm', 'Song Statistics'))
        self.pdf_button.setText(translate('SongUsagePlugin.SongUsageStatisticsForm', 'Save as &PDF...'))
        self.html_button.setText(translate('SongUsagePlugin.SongUsageStatisticsForm', 'Save as &Web Page...'))

    def load_statistics(self):
        """
        Read the song usage from the database and show the statistics
        """
        items = self.plugin.manager.get_all_objects(SongUsageItem,
                                                    order_by_ref=[SongUsageItem.usagedate, SongUsageItem.usagetime])
        template_path = AppLocation.get_directory(AppLocation.PluginsDir) / 'songusage' / 'html' / 'statistics.html'
        template = template_path.read_text(encoding='utf-8')
        window_colour = self.palette().color(self.palette().Window)
        self.page_arguments = dict(template=template, data=build_statistics_data(items), texts=statistics_texts(),
                                   language=LanguageManager.get_language().replace('_', '-'), today=date.today())
        self.page_html = render_statistics_page(dark=window_colour.lightness() < 128, **self.page_arguments)
        if len(self.page_html.encode('utf-8')) < MAX_HTML_SIZE:
            self.web_view.setHtml(self.page_html, QtCore.QUrl('about:blank'))
        else:
            page_path = AppLocation.get_section_data_path('songusage') / 'statistics.html'
            page_path.write_text(self.page_html, encoding='utf-8')
            self.web_view.setUrl(QtCore.QUrl.fromLocalFile(str(page_path)))

    def show_statistics(self):
        """
        Show the window with the current statistics
        """
        self.load_statistics()
        self.show()
        self.raise_()
        self.activateWindow()

    def _file_name(self, suffix):
        return '{name}_{date}{suffix}'.format(
            name=translate('SongUsagePlugin.SongUsageStatisticsForm', 'song_statistics'),
            date=date.today().isoformat(), suffix=suffix)

    def _ask_path(self, title, suffix, file_filter):
        directory = self.settings.value('songusage/last directory export') or Path.home()
        path, _ = FileDialog.getSaveFileName(self, title, Path(directory) / self._file_name(suffix), file_filter)
        if not path:
            return None
        if path.suffix.lower() != suffix:
            path = path.with_name(path.name + suffix)
        self.settings.setValue('songusage/last directory export', path.parent)
        return path

    def on_save_pdf(self):
        """
        Save the statistics, as they are shown, as a PDF
        """
        path = self._ask_path(translate('SongUsagePlugin.SongUsageStatisticsForm', 'Save as PDF'), '.pdf',
                              translate('SongUsagePlugin.SongUsageStatisticsForm', 'PDF files') + ' (*.pdf)')
        if path:
            self.web_view.page().pdfPrintingFinished.connect(self._on_pdf_finished)
            self.web_view.page().printToPdf(str(path))

    def _on_pdf_finished(self, file_path, success):
        self.web_view.page().pdfPrintingFinished.disconnect(self._on_pdf_finished)
        if not success:
            critical_error_message_box(translate('SongUsagePlugin.SongUsageStatisticsForm', 'Saving Failed'),
                                       translate('SongUsagePlugin.SongUsageStatisticsForm',
                                                 'The statistics could not be saved as {file}.').format(file=file_path))

    def on_save_html(self):
        """
        Save the statistics as a web page, which can be opened in any browser
        """
        path = self._ask_path(translate('SongUsagePlugin.SongUsageStatisticsForm', 'Save as Web Page'), '.html',
                              translate('SongUsagePlugin.SongUsageStatisticsForm', 'Web pages') + ' (*.html)')
        if not path or not self.page_arguments:
            return
        try:
            # A saved page uses light colours, and the date of saving as the end of its periods
            path.write_text(render_statistics_page(dark=False, **self.page_arguments), encoding='utf-8')
        except OSError as error:
            log.exception('Failed to save the song statistics')
            critical_error_message_box(translate('SongUsagePlugin.SongUsageStatisticsForm', 'Saving Failed'),
                                       translate('SongUsagePlugin.SongUsageStatisticsForm',
                                                 'The statistics could not be saved as {file}.').format(file=path) +
                                       '\n' + str(error.strerror))
