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
The :mod:`statistics` module computes the song statistics: the songs which were sung in a period, the most sung first.
"""
import calendar
import re
from collections import Counter
from datetime import timedelta

# The song number at the start of a title, e.g. "D0203 Title" or "R047_Title" -> book "D", number 203
SONG_NUMBER = re.compile(r'^\s*(?P<book>[^\W\d_]{1,3})\s*0*(?P<number>\d+)(?![^\W_])[\s_.:-]*')
# A search for a song number, e.g. "d203", "R 47" or "203"
NUMBER_SEARCH = re.compile(r'^(?P<book>[^\W\d_]{0,3})0*(?P<number>\d+)$')


class Period:
    """
    The periods of the statistics
    """
    FourWeeks = 0
    ThreeMonths = 1
    TwelveMonths = 2
    ThisYear = 3
    All = 4
    Custom = 5


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
    Prepare the song usage for the statistics. A song that is shown several times on a day (e.g. when it is sent to
    live again, or printed) counts once on that day.

    :param items: The song usage items, sorted by date and time
    :return: A dictionary with the songs ("songs") and the days they were sung ("events": (date, song index))
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
        event = (item.usagedate, indexes[title])
        if event not in seen:
            seen.add(event)
            events.append(event)
    return {'songs': songs, 'events': events}


def song_label(song):
    """
    The song number of a song, e.g. "D203", or an empty string if it has none
    """
    return song['book'] + song['number'] if song['book'] else ''


def song_books(data):
    """
    The song books of the songs, e.g. ["D", "R"]
    """
    return sorted({song['book'] for song in data['songs'] if song['book']})


def song_matches(song, book='', search=''):
    """
    Whether a song is shown with a song book and a search

    :param dict song: The song
    :param str book: Only songs of this song book, or all songs if it is empty
    :param str search: A song number (e.g. "d203" or "203") or a part of the title or the authors
    """
    if book and song['book'] != book:
        return False
    search = (search or '').strip().lower()
    if not search:
        return True
    match = NUMBER_SEARCH.match(re.sub(r'\s+', '', search))
    if match and song['book']:
        return match.group('book') in ('', song['book'].lower()) and match.group('number') == song['number']
    return search in song['title'].lower() or search in song['authors'].lower()


def _add_months(day, months):
    month = day.month - 1 + months
    year = day.year + month // 12
    month = month % 12 + 1
    return day.replace(year=year, month=month, day=min(day.day, calendar.monthrange(year, month)[1]))


def period_range(period, today, data=None, first_day=None, last_day=None):
    """
    The first and the last day of a period

    :param int period: The period, see :class:`Period`
    :param datetime.date today: The current day, the end of the periods
    :param dict data: The statistics data, for the first day of all song usage
    :param datetime.date first_day: The first day of a custom period
    :param datetime.date last_day: The last day of a custom period
    :return: The first and the last day
    """
    if period == Period.FourWeeks:
        return today - timedelta(days=27), today
    if period == Period.ThreeMonths:
        return _add_months(today, -3) + timedelta(days=1), today
    if period == Period.TwelveMonths:
        return _add_months(today, -12) + timedelta(days=1), today
    if period == Period.ThisYear:
        return today.replace(month=1, day=1), today
    if period == Period.All:
        first = min((event[0] for event in data['events']), default=today) if data else today
        return min(first, today), today
    first_day, last_day = first_day or today, last_day or today
    return min(first_day, last_day), max(first_day, last_day)


def rank_songs(data, first_day, last_day, book='', search=''):
    """
    The songs which were sung in a period, the most sung first. Songs which were sung equally often have the same rank.

    :param dict data: The statistics data of :func:`build_statistics_data`
    :param datetime.date first_day: The first day of the period
    :param datetime.date last_day: The last day of the period
    :param str book: Only songs of this song book, or all songs if it is empty
    :param str search: Only songs which match this search, see :func:`song_matches`
    :return: The songs, as dictionaries with "rank", "song" and "count"
    """
    counts = Counter(index for day, index in data['events'] if first_day <= day <= last_day)
    entries = [{'song': data['songs'][index], 'count': count} for index, count in counts.items()
               if song_matches(data['songs'][index], book, search)]
    entries.sort(key=lambda entry: (-entry['count'], entry['song']['book'], int(entry['song']['number'] or 0),
                                    entry['song']['title'].lower()))
    previous = None
    for position, entry in enumerate(entries, 1):
        if entry['count'] != previous:
            rank, previous = position, entry['count']
        entry['rank'] = rank
    return entries
