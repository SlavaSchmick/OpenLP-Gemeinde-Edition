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
The :mod:`statistics` module prepares the song usage data for the statistics page (html/statistics.html), which
computes and shows the statistics of a period in the browser engine.
"""
import json
import re

# The song number at the start of a title, e.g. "D0203 Title" or "R047_Title" -> book "D", number 203
SONG_NUMBER = re.compile(r'^\s*(?P<book>[^\W\d_]{1,3})\s*0*(?P<number>\d+)(?![^\W_])[\s_.:-]*')


def song_number(title):
    """
    The song number at the start of a title, e.g. "D203" for "D0203 Großer Gott"

    :param str title: The title of the song
    :return: The book, the number and the rest of the title, e.g. ("D", "203", "Großer Gott"), or None if the title
        doesn't start with a song number
    """
    match = SONG_NUMBER.match(title or '')
    if not match:
        return None
    return match.group('book').upper(), match.group('number'), title[match.end():].strip()


def build_statistics_data(items):
    """
    Prepare the song usage for the statistics page. A song that is shown several times on a day (e.g. when it is
    sent to live again, or printed) counts once on that day.

    :param items: The song usage items, sorted by date and time
    :return: A dictionary with the songs ("songs") and the days they were sung ("events": [date, song index])
    """
    songs = []
    indexes = {}
    events = []
    seen = set()
    for item in items:
        title = (item.title or '').strip()
        if not title or item.usagedate is None:
            continue
        if title not in indexes:
            number = song_number(title)
            indexes[title] = len(songs)
            songs.append({'title': title, 'name': number[2] or title if number else title,
                          'book': number[0] if number else '', 'number': number[1] if number else '',
                          'authors': (item.authors or '').strip()})
        date = item.usagedate.isoformat()
        if (date, indexes[title]) not in seen:
            seen.add((date, indexes[title]))
            events.append([date, indexes[title]])
    return {'songs': songs, 'events': events}


def _to_script(value):
    """
    The value as JSON, safe to be put into a script element
    """
    return json.dumps(value, ensure_ascii=False).replace('</', '<\\/')


def render_statistics_page(template, data, texts, language='en', dark=False, today=None):
    """
    Put the data and the texts into the statistics page

    :param str template: The page (html/statistics.html)
    :param dict data: The data of :func:`build_statistics_data`
    :param dict texts: The translated texts of the page
    :param str language: The language for dates and numbers, e.g. "de"
    :param bool dark: Whether to use dark colours
    :param datetime.date today: The current day (the end of the periods)
    :rtype: str
    """
    settings = {'language': language, 'dark': bool(dark), 'today': today.isoformat() if today else None}
    return template.replace('/*DATA*/null', _to_script(data)) \
        .replace('/*TEXTS*/null', _to_script(texts)) \
        .replace('/*SETTINGS*/null', _to_script(settings))
