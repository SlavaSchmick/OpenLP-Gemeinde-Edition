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
Test the song usage statistics data in openlp.plugins.songusage.lib.statistics
"""
import json
import re
from datetime import date, time
from types import SimpleNamespace

import pytest

from openlp.plugins.songusage.lib.statistics import build_statistics_data, render_statistics_page, song_number


def usage(day, title, authors='Autor unbekannt', hour=10):
    return SimpleNamespace(usagedate=day, usagetime=time(hour), title=title, authors=authors)


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
    Test that the song usage is prepared for the statistics page, with each song once per day
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
    assert data['events'] == [['2026-10-04', 0], ['2026-10-04', 1], ['2026-10-11', 2], ['2026-10-11', 0]]


def test_build_statistics_data_empty():
    """
    Test that no song usage gives empty data
    """
    # GIVEN: No song usage
    # WHEN: The data is built
    # THEN: There are no songs and no events
    assert build_statistics_data([]) == {'songs': [], 'events': []}


def test_render_statistics_page():
    """
    Test that the data, the texts and the settings are put into the page, safely for the script element
    """
    # GIVEN: A page and a song title that would end the script element
    template = 'var DATA = /*DATA*/null;\nvar TEXTS = /*TEXTS*/null;\nvar SETTINGS = /*SETTINGS*/null;'
    data = {'songs': [{'title': 'D1 </script><b>'}], 'events': []}

    # WHEN: The page is rendered
    page = render_statistics_page(template, data, {'All': 'Gesamt'}, language='de', dark=True,
                                  today=date(2026, 10, 14))

    # THEN: The values are in the page, and the title can't end the script element
    assert '</script>' not in page
    values = dict(re.findall(r'var (\w+) = (.*);', page))
    assert json.loads(values['DATA']) == data
    assert json.loads(values['TEXTS']) == {'All': 'Gesamt'}
    assert json.loads(values['SETTINGS']) == {'language': 'de', 'dark': True, 'today': '2026-10-14'}
