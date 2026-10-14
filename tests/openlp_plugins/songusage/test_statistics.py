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
Test the song statistics in openlp.plugins.songusage.lib.statistics
"""
from datetime import date, time
from types import SimpleNamespace

import pytest

from openlp.plugins.songusage.lib.statistics import Period, build_statistics_data, period_range, rank_songs, \
    song_books, song_label, song_matches, song_number


def usage(day, title, authors='Autor unbekannt', hour=10):
    return SimpleNamespace(usagedate=day, usagetime=time(hour), title=title, authors=authors)


def song(title, book='', number='', authors=''):
    return {'title': title, 'name': title, 'book': book, 'number': number, 'authors': authors}


@pytest.mark.parametrize('title,expected', [
    ('D0203 Großer Gott, wir loben Dich!', ('D', '203', 'Großer Gott, wir loben Dich!')),
    ('R001_Слушайте повесть любви', ('R', '1', 'Слушайте повесть любви')),
    ('d47 Title', ('D', '47', 'Title')),
    ('EG 362 Ein feste Burg', ('EG', '362', 'Ein feste Burg')),
    ('R12', ('R', '12', '')),
    ('Amazing Grace', None),
    ('10000 Reasons', None),
    ('D12a Title', None),
    ('', None),
    (None, None),
])
def test_song_number(title, expected):
    """
    Test that the song number at the start of a title is found
    """
    # GIVEN: A title
    # WHEN: Its song number is found
    # THEN: The book, the number and the rest of the title are returned, or None without a song number
    assert song_number(title) == expected


def test_build_statistics_data():
    """
    Test that the song usage is prepared for the statistics, with each song once per day
    """
    # GIVEN: Song usage with a song shown twice on a day, and an empty title
    items = [usage(date(2026, 10, 4), 'D0203 Großer Gott'),
             usage(date(2026, 10, 4), 'R047_Тебе поём'),
             usage(date(2026, 10, 4), 'D0203 Großer Gott', hour=11),
             usage(date(2026, 10, 4), '   '),
             usage(date(2026, 10, 11), 'Amazing Grace', authors=' John Newton '),
             usage(date(2026, 10, 11), 'D0203 Großer Gott')]

    # WHEN: The data is built
    data = build_statistics_data(items)

    # THEN: The songs are listed once, and a song counts once per day
    assert data['songs'] == [
        {'title': 'D0203 Großer Gott', 'name': 'Großer Gott', 'book': 'D', 'number': '203',
         'authors': 'Autor unbekannt'},
        {'title': 'R047_Тебе поём', 'name': 'Тебе поём', 'book': 'R', 'number': '47', 'authors': 'Autor unbekannt'},
        {'title': 'Amazing Grace', 'name': 'Amazing Grace', 'book': '', 'number': '', 'authors': 'John Newton'}]
    assert data['events'] == [(date(2026, 10, 4), 0), (date(2026, 10, 4), 1), (date(2026, 10, 11), 2),
                              (date(2026, 10, 11), 0)]
    assert song_books(data) == ['D', 'R']
    assert [song_label(item) for item in data['songs']] == ['D203', 'R47', '']


@pytest.mark.parametrize('book,search,expected', [
    ('', '', True),
    ('D', '', True),
    ('R', '', False),
    ('', 'd203', True),
    ('', 'D 0203', True),
    ('', '203', True),
    ('', 'r203', False),
    ('', 'd20', False),
    ('', 'großer', True),
    ('', 'newton', True),
    ('', 'amazing', False),
])
def test_song_matches(book, search, expected):
    """
    Test that a song is found by its song book, its number, its title and its authors
    """
    # GIVEN: A song
    item = song('D0203 Großer Gott', 'D', '203', 'John Newton')

    # WHEN: It is filtered
    # THEN: It is shown when it matches
    assert song_matches(item, book, search) is expected


@pytest.mark.parametrize('period,expected', [
    (Period.FourWeeks, (date(2026, 9, 17), date(2026, 10, 14))),
    (Period.ThreeMonths, (date(2026, 7, 15), date(2026, 10, 14))),
    (Period.TwelveMonths, (date(2025, 10, 15), date(2026, 10, 14))),
    (Period.ThisYear, (date(2026, 1, 1), date(2026, 10, 14))),
    (Period.All, (date(2024, 3, 3), date(2026, 10, 14))),
])
def test_period_range(period, expected):
    """
    Test the first and the last day of the periods
    """
    # GIVEN: Song usage since 3 March 2024
    data = {'songs': [], 'events': [(date(2024, 3, 3), 0), (date(2026, 10, 4), 0)]}

    # WHEN: The range of a period is computed on 14 October 2026
    # THEN: The days are correct
    assert period_range(period, date(2026, 10, 14), data) == expected


def test_period_range_end_of_month_and_custom():
    """
    Test months of different lengths and a custom period given the wrong way round
    """
    # GIVEN: The last day of a month
    # WHEN: The ranges are computed
    # THEN: Days which don't exist in the other month are moved to its end, and a custom period is put in order
    assert period_range(Period.ThreeMonths, date(2026, 5, 31)) == (date(2026, 3, 1), date(2026, 5, 31))
    assert period_range(Period.All, date(2026, 5, 31), {'songs': [], 'events': []}) == \
        (date(2026, 5, 31), date(2026, 5, 31))
    assert period_range(Period.Custom, date(2026, 5, 31), first_day=date(2026, 5, 1),
                        last_day=date(2026, 4, 1)) == (date(2026, 4, 1), date(2026, 5, 1))


def test_rank_songs():
    """
    Test that the songs of a period are ranked, the most sung first, with the same rank for the same count
    """
    # GIVEN: Song usage of three songs
    data = {'songs': [song('D0010 A', 'D', '10'), song('R0002 B', 'R', '2'), song('D0003 C', 'D', '3')],
            'events': [(date(2026, 9, 1), 0), (date(2026, 9, 6), 1), (date(2026, 9, 6), 0), (date(2026, 9, 13), 2),
                       (date(2026, 9, 13), 1), (date(2026, 9, 20), 0), (date(2026, 10, 4), 2)]}

    # WHEN: The songs of September are ranked
    entries = rank_songs(data, date(2026, 9, 1), date(2026, 9, 30))

    # THEN: The most sung song is first, songs sung equally often share the rank and are sorted by their number
    assert [(entry['rank'], song_label(entry['song']), entry['count']) for entry in entries] == \
        [(1, 'D10', 3), (2, 'R2', 2), (3, 'D3', 1)]
    assert [song_label(entry['song']) for entry in rank_songs(data, date(2026, 9, 1), date(2026, 10, 31))] == \
        ['D10', 'D3', 'R2']
    assert [entry['rank'] for entry in rank_songs(data, date(2026, 9, 1), date(2026, 10, 31))] == [1, 2, 2]
    assert [song_label(entry['song']) for entry in rank_songs(data, date(2026, 9, 1), date(2026, 9, 30), 'R')] == \
        ['R2']
    searched = rank_songs(data, date(2026, 9, 1), date(2026, 9, 30), search='d3')
    assert [song_label(entry['song']) for entry in searched] == ['D3']
    assert rank_songs(data, date(2025, 1, 1), date(2025, 12, 31)) == []
