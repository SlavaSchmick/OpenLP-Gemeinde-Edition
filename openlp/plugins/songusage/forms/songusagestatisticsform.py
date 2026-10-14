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
The song usage statistics: a window with the songs which were sung in a period, the most sung first. The list can be
saved as a PDF or as a CSV file.
"""
import csv
import logging
from datetime import date
from html import escape
from pathlib import Path

from PyQt5 import QtCore, QtGui, QtPrintSupport, QtWidgets

from openlp.core.common.i18n import translate
from openlp.core.common.mixins import RegistryProperties
from openlp.core.lib.ui import critical_error_message_box
from openlp.core.ui.icons import UiIcons
from openlp.core.widgets.dialogs import FileDialog
from openlp.plugins.songusage.lib.db import SongUsageItem
from openlp.plugins.songusage.lib.statistics import Period, build_statistics_data, period_range, rank_songs, \
    song_books, song_label

log = logging.getLogger(__name__)


class SongUsageStatisticsForm(QtWidgets.QDialog, RegistryProperties):
    """
    The window with the song usage statistics
    """
    def __init__(self, plugin, parent):
        super().__init__(parent, QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint |
                         QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        self.plugin = plugin
        self.data = {'songs': [], 'events': []}
        self.entries = []
        self.setup_ui()

    def setup_ui(self):
        self.setObjectName('song_usage_statistics_form')
        self.setWindowIcon(UiIcons().main_icon)
        self.resize(760, 680)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setSpacing(8)
        self.layout.setContentsMargins(8, 8, 8, 8)
        # The filters: period, song book and search
        self.filter_layout = QtWidgets.QGridLayout()
        self.filter_layout.setHorizontalSpacing(8)
        self.period_label = QtWidgets.QLabel(self)
        self.period_combo_box = QtWidgets.QComboBox(self)
        self.period_combo_box.setObjectName('period_combo_box')
        self.period_combo_box.addItems([''] * 6)
        self.period_label.setBuddy(self.period_combo_box)
        self.from_date_edit = QtWidgets.QDateEdit(self)
        self.from_date_edit.setObjectName('from_date_edit')
        self.from_date_edit.setCalendarPopup(True)
        self.to_label = QtWidgets.QLabel(self)
        self.to_date_edit = QtWidgets.QDateEdit(self)
        self.to_date_edit.setObjectName('to_date_edit')
        self.to_date_edit.setCalendarPopup(True)
        self.period_layout = QtWidgets.QHBoxLayout()
        self.period_layout.addWidget(self.period_combo_box)
        self.period_layout.addWidget(self.from_date_edit)
        self.period_layout.addWidget(self.to_label)
        self.period_layout.addWidget(self.to_date_edit)
        self.period_layout.addStretch()
        self.filter_layout.addWidget(self.period_label, 0, 0)
        self.filter_layout.addLayout(self.period_layout, 0, 1)
        self.book_label = QtWidgets.QLabel(self)
        self.book_combo_box = QtWidgets.QComboBox(self)
        self.book_combo_box.setObjectName('book_combo_box')
        self.book_label.setBuddy(self.book_combo_box)
        self.search_edit = QtWidgets.QLineEdit(self)
        self.search_edit.setObjectName('search_edit')
        self.search_edit.setClearButtonEnabled(True)
        self.book_layout = QtWidgets.QHBoxLayout()
        self.book_layout.addWidget(self.book_combo_box)
        self.book_layout.addWidget(self.search_edit, 1)
        self.filter_layout.addWidget(self.book_label, 1, 0)
        self.filter_layout.addLayout(self.book_layout, 1, 1)
        self.layout.addLayout(self.filter_layout)
        # The songs
        self.song_table = QtWidgets.QTableWidget(0, 4, self)
        self.song_table.setObjectName('song_table')
        self.song_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.song_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.song_table.setAlternatingRowColors(True)
        self.song_table.setWordWrap(False)
        self.song_table.verticalHeader().setVisible(False)
        header = self.song_table.horizontalHeader()
        for column in (0, 1, 3):
            header.setSectionResizeMode(column, QtWidgets.QHeaderView.Fixed)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        header.setHighlightSections(False)
        self.layout.addWidget(self.song_table, 1)
        self.empty_label = QtWidgets.QLabel(self)
        self.empty_label.setObjectName('empty_label')
        self.empty_label.setAlignment(QtCore.Qt.AlignCenter)
        self.empty_label.setWordWrap(True)
        self.empty_label.hide()
        self.layout.addWidget(self.empty_label, 1)
        # The buttons
        self.button_box = QtWidgets.QDialogButtonBox(self)
        self.button_box.setObjectName('button_box')
        self.pdf_button = self.button_box.addButton('', QtWidgets.QDialogButtonBox.ActionRole)
        self.pdf_button.setObjectName('pdf_button')
        self.csv_button = self.button_box.addButton('', QtWidgets.QDialogButtonBox.ActionRole)
        self.csv_button.setObjectName('csv_button')
        self.close_button = self.button_box.addButton(QtWidgets.QDialogButtonBox.Close)
        self.layout.addWidget(self.button_box)
        self.retranslate_ui()
        self.period_combo_box.setCurrentIndex(Period.TwelveMonths)
        # Signals
        self.period_combo_box.currentIndexChanged.connect(self.on_period_changed)
        self.from_date_edit.dateChanged.connect(self.on_date_changed)
        self.to_date_edit.dateChanged.connect(self.on_date_changed)
        self.book_combo_box.currentIndexChanged.connect(self.update_songs)
        self.search_edit.textChanged.connect(self.update_songs)
        self.pdf_button.clicked.connect(self.on_save_pdf)
        self.csv_button.clicked.connect(self.on_save_csv)
        self.button_box.rejected.connect(self.close)

    def retranslate_ui(self):
        def text(source):
            return translate('SongUsagePlugin.SongUsageStatisticsForm', source)

        self.setWindowTitle(text('Most Sung Songs'))
        self.period_label.setText(text('&Period:'))
        for period, name in ((Period.FourWeeks, text('Last 4 weeks')), (Period.ThreeMonths, text('Last 3 months')),
                             (Period.TwelveMonths, text('Last 12 months')), (Period.ThisYear, text('This year')),
                             (Period.All, text('All')), (Period.Custom, text('Custom'))):
            self.period_combo_box.setItemText(period, name)
        self.to_label.setText(text('to'))
        self.book_label.setText(text('Song&book:'))
        self.search_edit.setPlaceholderText(text('Search song or number, e.g. d203'))
        self.song_table.setHorizontalHeaderLabels([text('Rank'), text('No.'), text('Song'), text('Times Sung')])
        self.pdf_button.setText(text('Save as &PDF...'))
        self.csv_button.setText(text('Save as &CSV...'))

    def load_statistics(self):
        """
        Read the song usage from the database and show the statistics
        """
        items = self.plugin.manager.get_all_objects(SongUsageItem,
                                                    order_by_ref=[SongUsageItem.usagedate, SongUsageItem.usagetime])
        self.data = build_statistics_data(items)
        book = self.book_combo_box.currentData() or ''
        self.book_combo_box.blockSignals(True)
        self.book_combo_box.clear()
        self.book_combo_box.addItem(translate('SongUsagePlugin.SongUsageStatisticsForm', 'All songbooks'), '')
        for name in song_books(self.data):
            self.book_combo_box.addItem(name, name)
        self.book_combo_box.setCurrentIndex(max(0, self.book_combo_box.findData(book)))
        self.book_combo_box.blockSignals(False)
        self.on_period_changed()

    def show_statistics(self):
        """
        Show the window with the current statistics
        """
        self.load_statistics()
        self.show()
        self.raise_()
        self.activateWindow()
        self.search_edit.setFocus()

    def on_period_changed(self):
        """
        Show the days of the selected period; they can be changed for a custom period
        """
        period = self.period_combo_box.currentIndex()
        if period != Period.Custom:
            first_day, last_day = period_range(period, date.today(), self.data)
            for date_edit, day in ((self.from_date_edit, first_day), (self.to_date_edit, last_day)):
                date_edit.blockSignals(True)
                date_edit.setDate(QtCore.QDate(day))
                date_edit.blockSignals(False)
        self.update_songs()

    def on_date_changed(self):
        """
        A changed day makes the period a custom period
        """
        if self.period_combo_box.currentIndex() != Period.Custom:
            self.period_combo_box.blockSignals(True)
            self.period_combo_box.setCurrentIndex(Period.Custom)
            self.period_combo_box.blockSignals(False)
        self.update_songs()

    def selected_range(self):
        """
        The first and the last day of the selected period
        """
        return period_range(Period.Custom, date.today(), first_day=self.from_date_edit.date().toPyDate(),
                            last_day=self.to_date_edit.date().toPyDate())

    def update_songs(self):
        """
        Show the songs of the selected period, song book and search, the most sung first
        """
        first_day, last_day = self.selected_range()
        self.entries = rank_songs(self.data, first_day, last_day, self.book_combo_box.currentData() or '',
                                  self.search_edit.text())
        self.song_table.setRowCount(len(self.entries))
        for row, entry in enumerate(self.entries):
            values = ('{rank}.'.format(rank=entry['rank']), song_label(entry['song']), entry['song']['name'],
                      str(entry['count']))
            for column, value in enumerate(values):
                item = QtWidgets.QTableWidgetItem(value)
                if column in (0, 3):
                    item.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
                if column == 2:
                    item.setToolTip(entry['song']['title'])
                self.song_table.setItem(row, column, item)
        if not self.data['events']:
            self.empty_label.setText(translate('SongUsagePlugin.SongUsageStatisticsForm',
                                               'No songs have been sung yet. Every song which is shown live is '
                                               'counted.'))
        else:
            self.empty_label.setText(translate('SongUsagePlugin.SongUsageStatisticsForm', 'No songs in this period.'))
        self.resize_columns()
        self.song_table.setVisible(bool(self.entries))
        self.empty_label.setVisible(not self.entries)
        self.pdf_button.setEnabled(bool(self.entries))
        self.csv_button.setEnabled(bool(self.entries))

    def resize_columns(self):
        """
        Make the narrow columns wide enough for their heading and their values (the heading may have a larger font)
        """
        header = self.song_table.horizontalHeader()
        for column in (0, 1, 3):
            width = header.fontMetrics().horizontalAdvance(self.song_table.horizontalHeaderItem(column).text()) + 24
            for row in range(self.song_table.rowCount()):
                item = self.song_table.item(row, column)
                width = max(width, self.song_table.fontMetrics().horizontalAdvance(item.text()) + 16)
            header.resizeSection(column, width)

    def description(self):
        """
        The selected period, song book and search, e.g. "15.10.25 – 14.10.26, Songbook D"
        """
        first_day, last_day = self.selected_range()
        parts = ['{first} – {last}'.format(first=QtCore.QDate(first_day).toString(QtCore.Qt.DefaultLocaleShortDate),
                                           last=QtCore.QDate(last_day).toString(QtCore.Qt.DefaultLocaleShortDate))]
        if self.book_combo_box.currentData():
            parts.append(translate('SongUsagePlugin.SongUsageStatisticsForm',
                                   'Songbook {book}').format(book=self.book_combo_box.currentData()))
        if self.search_edit.text().strip():
            parts.append(translate('SongUsagePlugin.SongUsageStatisticsForm',
                                   'Search: {search}').format(search=self.search_edit.text().strip()))
        return ', '.join(parts)

    def _ask_path(self, title, suffix, file_filter):
        directory = self.settings.value('songusage/last directory export') or Path.home()
        file_name = '{name}_{day}{suffix}'.format(
            name=translate('SongUsagePlugin.SongUsageStatisticsForm', 'most_sung_songs'), day=date.today().isoformat(),
            suffix=suffix)
        path, _ = FileDialog.getSaveFileName(self, title, Path(directory) / file_name, file_filter)
        if not path:
            return None
        if path.suffix.lower() != suffix:
            path = path.with_name(path.name + suffix)
        self.settings.setValue('songusage/last directory export', path.parent)
        return path

    def _saving_failed(self, path, error):
        log.error('Failed to save the song statistics as {path}: {error}'.format(path=path, error=error))
        critical_error_message_box(translate('SongUsagePlugin.SongUsageStatisticsForm', 'Saving Failed'),
                                   translate('SongUsagePlugin.SongUsageStatisticsForm',
                                             'The list could not be saved as {file}.').format(file=path) +
                                   ('\n' + str(error) if error else ''))

    def statistics_html(self):
        """
        The list as a simple document, for the PDF
        """
        headers = [escape(self.song_table.horizontalHeaderItem(column).text()) for column in range(4)]
        row = '<tr><td align="right">{rank}.</td><td>{number}</td><td>{name}</td><td align="right">{count}</td></tr>'
        rows = ''.join(row.format(rank=entry['rank'], number=escape(song_label(entry['song'])),
                                  name=escape(entry['song']['name']), count=entry['count']) for entry in self.entries)
        return ('<h2>{title}</h2><p>{description}</p>'
                '<table width="100%" cellspacing="0" cellpadding="4" border="0">'
                '<tr><th align="right">{h0}</th><th align="left">{h1}</th><th align="left">{h2}</th>'
                '<th align="right">{h3}</th></tr>{rows}</table>').format(
            title=escape(self.windowTitle()), description=escape(self.description()), h0=headers[0], h1=headers[1],
            h2=headers[2], h3=headers[3], rows=rows)

    def on_save_pdf(self):
        """
        Save the list as a PDF
        """
        path = self._ask_path(translate('SongUsagePlugin.SongUsageStatisticsForm', 'Save as PDF'), '.pdf',
                              translate('SongUsagePlugin.SongUsageStatisticsForm', 'PDF files') + ' (*.pdf)')
        if not path:
            return
        printer = QtPrintSupport.QPrinter(QtPrintSupport.QPrinter.HighResolution)
        printer.setOutputFormat(QtPrintSupport.QPrinter.PdfFormat)
        printer.setPageSize(QtGui.QPageSize(QtGui.QPageSize.A4))
        printer.setPageMargins(15, 15, 15, 15, QtPrintSupport.QPrinter.Millimeter)
        printer.setOutputFileName(str(path))
        document = QtGui.QTextDocument()
        document.setHtml(self.statistics_html())
        document.print_(printer)
        if not path.exists():
            self._saving_failed(path, None)

    def on_save_csv(self):
        """
        Save the list as a CSV file, e.g. for a spreadsheet
        """
        path = self._ask_path(translate('SongUsagePlugin.SongUsageStatisticsForm', 'Save as CSV'), '.csv',
                              translate('SongUsagePlugin.SongUsageStatisticsForm', 'CSV files') + ' (*.csv)')
        if not path:
            return
        headers = [self.song_table.horizontalHeaderItem(column).text() for column in range(4)]
        try:
            # With a byte order mark and semicolons, as spreadsheets expect it
            with path.open('w', encoding='utf-8-sig', newline='') as csv_file:
                writer = csv.writer(csv_file, delimiter=';')
                writer.writerow(headers)
                for entry in self.entries:
                    writer.writerow([entry['rank'], song_label(entry['song']), entry['song']['name'], entry['count']])
        except OSError as error:
            self._saving_failed(path, error.strerror)
