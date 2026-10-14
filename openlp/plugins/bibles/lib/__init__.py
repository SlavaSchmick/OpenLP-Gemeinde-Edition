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
The :mod:`lib` module contains all the library functionality for the bibles
plugin.
"""
import logging
import re

from openlp.core.common import Singleton
from openlp.core.common.i18n import translate
from openlp.core.common.registry import Registry

log = logging.getLogger(__name__)


REFERENCE_MATCHES = {}
REFERENCE_SEPARATORS = {}


class BibleStrings(metaclass=Singleton):
    """
    Provide standard strings for objects to use.
    """
    def __init__(self):
        """
        These strings should need a good reason to be retranslated elsewhere.
        """
        self.BookNames = {
            'Gen': translate('BiblesPlugin', 'Genesis'),
            'Exod': translate('BiblesPlugin', 'Exodus'),
            'Lev': translate('BiblesPlugin', 'Leviticus'),
            'Num': translate('BiblesPlugin', 'Numbers'),
            'Deut': translate('BiblesPlugin', 'Deuteronomy'),
            'Josh': translate('BiblesPlugin', 'Joshua'),
            'Judg': translate('BiblesPlugin', 'Judges'),
            'Ruth': translate('BiblesPlugin', 'Ruth'),
            '1Sam': translate('BiblesPlugin', '1 Samuel'),
            '2Sam': translate('BiblesPlugin', '2 Samuel'),
            '1Kgs': translate('BiblesPlugin', '1 Kings'),
            '2Kgs': translate('BiblesPlugin', '2 Kings'),
            '1Chr': translate('BiblesPlugin', '1 Chronicles'),
            '2Chr': translate('BiblesPlugin', '2 Chronicles'),
            'Esra': translate('BiblesPlugin', 'Ezra'),
            'Neh': translate('BiblesPlugin', 'Nehemiah'),
            'Esth': translate('BiblesPlugin', 'Esther'),
            'Job': translate('BiblesPlugin', 'Job'),
            'Ps': translate('BiblesPlugin', 'Psalms'),
            'Prov': translate('BiblesPlugin', 'Proverbs'),
            'Eccl': translate('BiblesPlugin', 'Ecclesiastes'),
            'Song': translate('BiblesPlugin', 'Song of Solomon'),
            'Isa': translate('BiblesPlugin', 'Isaiah'),
            'Jer': translate('BiblesPlugin', 'Jeremiah'),
            'Lam': translate('BiblesPlugin', 'Lamentations'),
            'Ezek': translate('BiblesPlugin', 'Ezekiel'),
            'Dan': translate('BiblesPlugin', 'Daniel'),
            'Hos': translate('BiblesPlugin', 'Hosea'),
            'Joel': translate('BiblesPlugin', 'Joel'),
            'Amos': translate('BiblesPlugin', 'Amos'),
            'Obad': translate('BiblesPlugin', 'Obadiah'),
            'Jonah': translate('BiblesPlugin', 'Jonah'),
            'Mic': translate('BiblesPlugin', 'Micah'),
            'Nah': translate('BiblesPlugin', 'Nahum'),
            'Hab': translate('BiblesPlugin', 'Habakkuk'),
            'Zeph': translate('BiblesPlugin', 'Zephaniah'),
            'Hag': translate('BiblesPlugin', 'Haggai'),
            'Zech': translate('BiblesPlugin', 'Zechariah'),
            'Mal': translate('BiblesPlugin', 'Malachi'),
            'Matt': translate('BiblesPlugin', 'Matthew'),
            'Mark': translate('BiblesPlugin', 'Mark'),
            'Luke': translate('BiblesPlugin', 'Luke'),
            'John': translate('BiblesPlugin', 'John'),
            'Acts': translate('BiblesPlugin', 'Acts'),
            'Rom': translate('BiblesPlugin', 'Romans'),
            '1Cor': translate('BiblesPlugin', '1 Corinthians'),
            '2Cor': translate('BiblesPlugin', '2 Corinthians'),
            'Gal': translate('BiblesPlugin', 'Galatians'),
            'Eph': translate('BiblesPlugin', 'Ephesians'),
            'Phil': translate('BiblesPlugin', 'Philippians'),
            'Col': translate('BiblesPlugin', 'Colossians'),
            '1Thess': translate('BiblesPlugin', '1 Thessalonians'),
            '2Thess': translate('BiblesPlugin', '2 Thessalonians'),
            '1Tim': translate('BiblesPlugin', '1 Timothy'),
            '2Tim': translate('BiblesPlugin', '2 Timothy'),
            'Titus': translate('BiblesPlugin', 'Titus'),
            'Phlm': translate('BiblesPlugin', 'Philemon'),
            'Heb': translate('BiblesPlugin', 'Hebrews'),
            'Jas': translate('BiblesPlugin', 'James'),
            '1Pet': translate('BiblesPlugin', '1 Peter'),
            '2Pet': translate('BiblesPlugin', '2 Peter'),
            '1John': translate('BiblesPlugin', '1 John'),
            '2John': translate('BiblesPlugin', '2 John'),
            '3John': translate('BiblesPlugin', '3 John'),
            'Jude': translate('BiblesPlugin', 'Jude'),
            'Rev': translate('BiblesPlugin', 'Revelation'),
            'Jdt': translate('BiblesPlugin', 'Judith'),
            'Wis': translate('BiblesPlugin', 'Wisdom'),
            'Tob': translate('BiblesPlugin', 'Tobit'),
            'Sir': translate('BiblesPlugin', 'Sirach'),
            'Bar': translate('BiblesPlugin', 'Baruch'),
            '1Macc': translate('BiblesPlugin', '1 Maccabees'),
            '2Macc': translate('BiblesPlugin', '2 Maccabees'),
            '3Macc': translate('BiblesPlugin', '3 Maccabees'),
            '4Macc': translate('BiblesPlugin', '4 Maccabees'),
            'AddDan': translate('BiblesPlugin', 'Rest of Daniel'),
            'AddEsth': translate('BiblesPlugin', 'Rest of Esther'),
            'PrMan': translate('BiblesPlugin', 'Prayer of Manasses'),
            'LetJer': translate('BiblesPlugin', 'Letter of Jeremiah'),
            'PrAza': translate('BiblesPlugin', 'Prayer of Azariah'),
            'Sus': translate('BiblesPlugin', 'Susanna'),
            'Bel': translate('BiblesPlugin', 'Bel'),
            '1Esdr': translate('BiblesPlugin', '1 Esdras'),
            '2Esdr': translate('BiblesPlugin', '2 Esdras')
        }


# Common German names and abbreviations of the books (Loccumer Richtlinien and everyday use), by book reference id. They
# are used when a typed book can't be found by the names in the Bible, e.g. "1mos" for a Bible which calls it "Genesis".
GERMAN_BOOK_ALIASES = {
    1: ['1. Mose', '1Mo', '1Mos', 'Genesis'], 2: ['2. Mose', '2Mo', '2Mos', 'Exodus', 'Ex'],
    3: ['3. Mose', '3Mo', '3Mos', 'Levitikus', 'Lev'], 4: ['4. Mose', '4Mo', '4Mos', 'Numeri', 'Num'],
    5: ['5. Mose', '5Mo', '5Mos', 'Deuteronomium', 'Dtn'], 6: ['Josua', 'Jos'], 7: ['Richter', 'Ri'],
    8: ['Rut', 'Ruth'], 9: ['1. Samuel', '1Sam'], 10: ['2. Samuel', '2Sam'], 11: ['1. Könige', '1Kön', '1Kö'],
    12: ['2. Könige', '2Kön', '2Kö'], 13: ['1. Chronik', '1Chr'], 14: ['2. Chronik', '2Chr'], 15: ['Esra', 'Esr'],
    16: ['Nehemia', 'Neh'], 17: ['Ester', 'Esther', 'Est'], 18: ['Hiob', 'Ijob', 'Hi'], 19: ['Psalm', 'Psalmen', 'Ps'],
    20: ['Sprüche', 'Sprichwörter', 'Spr'], 21: ['Prediger', 'Kohelet', 'Pred', 'Koh'],
    22: ['Hoheslied', 'Hohelied', 'Hld'], 23: ['Jesaja', 'Jes'], 24: ['Jeremia', 'Jer'], 25: ['Klagelieder', 'Klgl'],
    26: ['Hesekiel', 'Ezechiel', 'Hes', 'Ez'], 27: ['Daniel', 'Dan'], 28: ['Hosea', 'Hos'], 29: ['Joel'],
    30: ['Amos', 'Am'], 31: ['Obadja', 'Obd'], 32: ['Jona'], 33: ['Micha', 'Mi'], 34: ['Nahum', 'Nah'],
    35: ['Habakuk', 'Hab'], 36: ['Zefanja', 'Zephanja', 'Zef'], 37: ['Haggai', 'Hag'], 38: ['Sacharja', 'Sach'],
    39: ['Maleachi', 'Mal'], 40: ['Matthäus', 'Mt'], 41: ['Markus', 'Mk'], 42: ['Lukas', 'Lk'],
    43: ['Johannes', 'Joh'], 44: ['Apostelgeschichte', 'Apg'], 45: ['Römer', 'Röm'], 46: ['1. Korinther', '1Kor'],
    47: ['2. Korinther', '2Kor'], 48: ['Galater', 'Gal'], 49: ['Epheser', 'Eph'], 50: ['Philipper', 'Phil'],
    51: ['Kolosser', 'Kol'], 52: ['1. Thessalonicher', '1Thess'], 53: ['2. Thessalonicher', '2Thess'],
    54: ['1. Timotheus', '1Tim'], 55: ['2. Timotheus', '2Tim'], 56: ['Titus', 'Tit'], 57: ['Philemon', 'Phlm'],
    58: ['Hebräer', 'Hebr'], 59: ['Jakobus', 'Jak'], 60: ['1. Petrus', '1Petr'], 61: ['2. Petrus', '2Petr'],
    62: ['1. Johannes', '1Joh'], 63: ['2. Johannes', '2Joh'], 64: ['3. Johannes', '3Joh'], 65: ['Judas', 'Jud'],
    66: ['Offenbarung', 'Offb', 'Apk']
}

# Common Russian names and abbreviations of the books (Synodal translation), by book reference id
RUSSIAN_BOOK_ALIASES = {
    1: ['Бытие', 'Быт'], 2: ['Исход', 'Исх'], 3: ['Левит', 'Лев'], 4: ['Числа', 'Чис'], 5: ['Второзаконие', 'Втор'],
    6: ['Иисус Навин', 'Иисуса Навина', 'Нав'], 7: ['Судьи', 'Суд'], 8: ['Руфь', 'Руф'], 9: ['1 Царств', '1Цар'],
    10: ['2 Царств', '2Цар'], 11: ['3 Царств', '3Цар'], 12: ['4 Царств', '4Цар'], 13: ['1 Паралипоменон', '1Пар'],
    14: ['2 Паралипоменон', '2Пар'], 15: ['Ездра', 'Ездр', 'Езд'], 16: ['Неемия', 'Неем'], 17: ['Есфирь', 'Есф'],
    18: ['Иов'], 19: ['Псалтирь', 'Псалом', 'Псалмы', 'Пс'], 20: ['Притчи', 'Притч', 'Прит'],
    21: ['Екклесиаст', 'Еккл'], 22: ['Песнь Песней', 'Песн'], 23: ['Исаия', 'Ис'], 24: ['Иеремия', 'Иер'],
    25: ['Плач Иеремии', 'Плач'], 26: ['Иезекииль', 'Иез'], 27: ['Даниил', 'Дан'], 28: ['Осия', 'Ос'],
    29: ['Иоиль', 'Иоил'], 30: ['Амос', 'Ам'], 31: ['Авдий', 'Авд'], 32: ['Иона', 'Ион'], 33: ['Михей', 'Мих'],
    34: ['Наум'], 35: ['Аввакум', 'Авв'], 36: ['Софония', 'Соф'], 37: ['Аггей', 'Агг'], 38: ['Захария', 'Зах'],
    39: ['Малахия', 'Мал'], 40: ['Матфея', 'Матфей', 'Мф', 'Мат'], 41: ['Марка', 'Марк', 'Мк', 'Мар'],
    42: ['Луки', 'Лука', 'Лк', 'Лук'], 43: ['Иоанна', 'Иоанн', 'Ин', 'Иоан'], 44: ['Деяния', 'Деян'],
    45: ['Римлянам', 'Рим'], 46: ['1 Коринфянам', '1Кор'], 47: ['2 Коринфянам', '2Кор'], 48: ['Галатам', 'Гал'],
    49: ['Ефесянам', 'Еф'], 50: ['Филиппийцам', 'Флп', 'Фил'], 51: ['Колоссянам', 'Кол'],
    52: ['1 Фессалоникийцам', '1Фес'], 53: ['2 Фессалоникийцам', '2Фес'], 54: ['1 Тимофею', '1Тим'],
    55: ['2 Тимофею', '2Тим'], 56: ['Титу', 'Тит'], 57: ['Филимону', 'Флм'], 58: ['Евреям', 'Евр'],
    59: ['Иакова', 'Иак'], 60: ['1 Петра', '1Пет'], 61: ['2 Петра', '2Пет'], 62: ['1 Иоанна', '1Ин'],
    63: ['2 Иоанна', '2Ин'], 64: ['3 Иоанна', '3Ин'], 65: ['Иуды', 'Иуд'], 66: ['Откровение', 'Откр']
}

# Common Ukrainian names and abbreviations of the books (Ohienko translation), by book reference id
UKRAINIAN_BOOK_ALIASES = {
    1: ['Буття', 'Бут'], 2: ['Вихід', 'Вих'], 3: ['Левит', 'Лев'], 4: ['Числа', 'Чис'],
    5: ['Повторення Закону', 'Повт'], 6: ['Ісус Навин', 'Ісуса Навина', 'ІсН', 'Нав'], 7: ['Суддів', 'Суд'],
    8: ['Рут'], 9: ['1 Самуїлова', '1Сам'], 10: ['2 Самуїлова', '2Сам'], 11: ['1 Царів', '1Цар'],
    12: ['2 Царів', '2Цар'], 13: ['1 Хроніки', '1Хр'], 14: ['2 Хроніки', '2Хр'], 15: ['Ездра', 'Езд'],
    16: ['Неемія', 'Неем'], 17: ['Естер', 'Ест'], 18: ['Йов'], 19: ['Псалми', 'Псалом', 'Пс'],
    20: ['Приповісті', 'Прип'], 21: ['Екклезіяст', 'Проповідник', 'Екл'], 22: ['Пісня над піснями', 'Пісн'],
    23: ['Ісая', 'Іс'], 24: ['Єремія', 'Єр'], 25: ['Плач Єремії', 'Плач'], 26: ['Єзекіїль', 'Єз'],
    27: ['Даниїл', 'Дан'], 28: ['Осія', 'Ос'], 29: ['Йоіл'], 30: ['Амос', 'Ам'], 31: ['Овдій', 'Ов'], 32: ['Йона'],
    33: ['Михей', 'Мих'], 34: ['Наум'], 35: ['Авакум', 'Ав'], 36: ['Софонія', 'Соф'], 37: ['Огій', 'Ог'],
    38: ['Захарія', 'Зах'], 39: ['Малахії', 'Малахія', 'Мал'], 40: ['Матвія', 'Матвій', 'Мт'],
    41: ['Марка', 'Марк', 'Мр', 'Мк'], 42: ['Луки', 'Лука', 'Лк'], 43: ['Івана', 'Іван', 'Ів'], 44: ['Дії'],
    45: ['Римлян', 'Рим'], 46: ['1 Коринтян', '1Кор'], 47: ['2 Коринтян', '2Кор'], 48: ['Галатів', 'Гал'],
    49: ['Ефесян', 'Еф'], 50: ["Филип'ян", 'Флп'], 51: ['Колоссян', 'Кол'], 52: ['1 Солунян', '1Сол'],
    53: ['2 Солунян', '2Сол'], 54: ['1 Тимофія', '1Тим'], 55: ['2 Тимофія', '2Тим'], 56: ['Тита', 'Тит'],
    57: ['Филимона', 'Флм'], 58: ['Євреїв', 'Євр'], 59: ['Якова', 'Як'], 60: ['1 Петра', '1Пет'],
    61: ['2 Петра', '2Пет'], 62: ['1 Івана', '1Ів'], 63: ['2 Івана', '2Ів'], 64: ['3 Івана', '3Ів'],
    65: ['Юди', 'Юд'], 66: ["Об'явлення", 'Одкровення', 'Об']
}

# The book aliases by language code. Some abbreviations mean different books in different languages, e.g. "1Цар" is
# 1 Samuel in Russian and 1 Kings in Ukrainian, so the aliases of the user interface language are preferred.
BOOK_ALIASES = {'de': GERMAN_BOOK_ALIASES, 'ru': RUSSIAN_BOOK_ALIASES, 'uk': UKRAINIAN_BOOK_ALIASES}


def get_interface_language():
    """
    Get the two letter code of the language of the user interface, e.g. "de", or an empty string if it is unknown.
    """
    try:
        settings = Registry().get('settings') if Registry().has('settings') else None
    except AttributeError:
        # The registry has not been created yet
        settings = None
    if settings is None:
        return ''
    language = str(settings.value('core/language'))
    if re.match(r'\[(.*)\]', language):
        from PyQt5 import QtCore
        language = QtCore.QLocale.system().name()
    return language[:2].lower()


def normalise_book_name(name):
    """
    Normalise a book name for a tolerant comparison: lower case, umlauts written out, without spaces, full stops and
    apostrophes. E.g. "1. Mose" becomes "1mose", "Röm" becomes "roem" and "Об'явлення" becomes "обявлення".
    """
    name = name.lower()
    for letter, replacement in (('ä', 'ae'), ('ö', 'oe'), ('ü', 'ue'), ('ß', 'ss'), ('ё', 'е'), ('ʼ', '')):
        name = name.replace(letter, replacement)
    return re.sub(r'[\W_]+', '', name)


def find_book_ref_ids(book, bible, language=None):
    """
    Find a book tolerantly, by its German, Russian, Ukrainian, English or Bible specific name or abbreviation, or the
    start of one of them. This is used when the book can't be found by the usual way.

    :param str book: The typed book, e.g. "1mos", "1 Mo", "gen", "Röm", "Ин" or "Ів"
    :param bible: The Bible database
    :param str language: The preferred language of the aliases, the user interface language if None
    :return: A list with the book reference id of the best matching book in the Bible, or an empty list
    """
    wanted = normalise_book_name(book)
    if not wanted:
        return []
    if language is None:
        language = get_interface_language()
    from openlp.plugins.bibles.lib.db import BiblesResourcesDB
    # The Bible specific and English names and the aliases of the interface language are preferred over other aliases
    preferred_names = {book_id: list(aliases) for book_id, aliases in BOOK_ALIASES.get(language, {}).items()}
    for resource_book in BiblesResourcesDB.get_books():
        preferred_names.setdefault(resource_book['id'], []).extend([resource_book['name'],
                                                                    resource_book['abbreviation']])
    for bible_book in bible.get_books() or []:
        preferred_names.setdefault(bible_book.book_reference_id, []).append(bible_book.name)
    other_names = {}
    for aliases_language, aliases in BOOK_ALIASES.items():
        if aliases_language != language:
            for book_id, book_aliases in aliases.items():
                other_names.setdefault(book_id, []).extend(book_aliases)
    name_groups = [{book_id: [normalise_book_name(name) for name in book_names if name]
                    for book_id, book_names in names.items()} for names in (preferred_names, other_names)]
    book_ids = sorted(set(preferred_names) | set(other_names))
    in_bible = [book_id for book_id in book_ids if bible.get_book_by_book_ref_id(book_id)]
    # An exact name or abbreviation wins over the start of a name, a preferred name over another alias, and the first
    # book of the Bible over later ones
    for is_match in (lambda name: name == wanted, lambda name: name.startswith(wanted)):
        for names in name_groups:
            for book_id in in_bible:
                if any(is_match(name) for name in names.get(book_id, [])):
                    return [book_id]
    return []


def normalise_reference(reference):
    """
    Make a typed reference more tolerant: chapter and verse can be separated by a space, as in "gen 3 4" or
    "joh 3 16-18", which is turned into "gen 3,4" with the verse separator of the current language.

    :param str reference: The typed reference
    :return: The reference, with a verse separator if it was missing
    """
    if get_reference_match('full').match(reference):
        return reference
    match = re.match(r'^(?P<book>\s*\d*\.?\s*[^\d]+?)\s*(?P<chapter>\d+)\s+(?P<verse>\d+)(?P<rest>.*)$', reference)
    if not match:
        return reference
    normalised = '{book} {chapter}{sep}{verse}{rest}'.format(sep=get_reference_separator('sep_v_display'),
                                                             **match.groupdict())
    return normalised if get_reference_match('full').match(normalised) else reference


def update_reference_separators():
    """
    Updates separators and matches for parsing and formatting scripture references.
    """
    default_separators = [
        '|'.join([
            translate('BiblesPlugin', ':', 'Verse identifier e.g. Genesis 1 : 1 = Genesis Chapter 1 Verse 1'),
            translate('BiblesPlugin', 'v', 'Verse identifier e.g. Genesis 1 v 1 = Genesis Chapter 1 Verse 1'),
            translate('BiblesPlugin', 'V', 'Verse identifier e.g. Genesis 1 V 1 = Genesis Chapter 1 Verse 1'),
            translate('BiblesPlugin', 'verse', 'Verse identifier e.g. Genesis 1 verse 1 = Genesis Chapter 1 Verse 1'),
            translate('BiblesPlugin', 'verses',
                      'Verse identifier e.g. Genesis 1 verses 1 - 2 = Genesis Chapter 1 Verses 1 to 2')]),
        '|'.join([
            translate('BiblesPlugin', '-',
                      'range identifier e.g. Genesis 1 verse 1 - 2 = Genesis Chapter 1 Verses 1 To 2'),
            translate('BiblesPlugin', 'to',
                      'range identifier e.g. Genesis 1 verse 1 - 2 = Genesis Chapter 1 Verses 1 To 2')]),
        '|'.join([
            translate('BiblesPlugin', ',', 'connecting identifier e.g. Genesis 1 verse 1 - 2, 4 - 5 = '
                                           'Genesis Chapter 1 Verses 1 To 2 And Verses 4 To 5'),
            translate('BiblesPlugin', 'and', 'connecting identifier e.g. Genesis 1 verse 1 - 2 and 4 - 5 = '
                                             'Genesis Chapter 1 Verses 1 To 2 And Verses 4 To 5')]),
        '|'.join([translate('BiblesPlugin', 'end', 'ending identifier e.g. Genesis 1 verse 1 - end = '
                                                   'Genesis Chapter 1 Verses 1 To The Last Verse')])]
    settings = Registry().get('settings')
    custom_separators = [
        settings.value('bibles/verse separator'),
        settings.value('bibles/range separator'),
        settings.value('bibles/list separator'),
        settings.value('bibles/end separator')]
    for index, role in enumerate(['v', 'r', 'l', 'e']):
        if custom_separators[index].strip('|') == '':
            source_string = default_separators[index].strip('|')
        else:
            source_string = custom_separators[index].strip('|')
        while '||' in source_string:
            source_string = source_string.replace('||', '|')
        if role != 'e':
            REFERENCE_SEPARATORS['sep_{role}_display'.format(role=role)] = source_string.split('|')[0]
        # escape reserved characters
        for character in '\\.^$*+?{}[]()':
            source_string = source_string.replace(character, '\\' + character)
        # add various Unicode alternatives
        source_string = source_string.replace('-', '(?:[-\u00AD\u2010\u2011\u2012\u2014\u2014\u2212\uFE63\uFF0D])')
        source_string = source_string.replace(',', '(?:[,\u201A])')
        REFERENCE_SEPARATORS['sep_{role}'.format(role=role)] = r'\s*(?:{source})\s*'.format(source=source_string)
        REFERENCE_SEPARATORS['sep_{role}_default'.format(role=role)] = default_separators[index]
    # verse range match: (<chapter>:)?<verse>(-((<chapter>:)?<verse>|end)?)?
    range_regex = '(?:(?P<from_chapter>[0-9]+){sep_v})?' \
        '(?P<from_verse>[0-9]+)(?P<range_to>{sep_r}(?:(?:(?P<to_chapter>' \
        '[0-9]+){sep_v})?(?P<to_verse>[0-9]+)|{sep_e})?)?'.format_map(REFERENCE_SEPARATORS)
    REFERENCE_MATCHES['range'] = re.compile(r'^\s*{range}\s*$'.format(range=range_regex))
    REFERENCE_MATCHES['range_separator'] = re.compile(REFERENCE_SEPARATORS['sep_l'])
    # full reference match: <book>(<range>(,(?!$)|(?=$)))+
    REFERENCE_MATCHES['full'] = \
        re.compile(r'^\s*(?!\s)(?P<book>[\d]*[.]?[^\d\.]+)\.*(?<!\s)\s*'
                   r'(?P<ranges>(?:{range_regex}(?:{sep_l}(?!\s*$)|(?=\s*$)))+)\s*$'.format(
                       range_regex=range_regex, sep_l=REFERENCE_SEPARATORS['sep_l']))


def get_reference_separator(separator_type):
    """
    Provides separators for parsing and formatting scripture references.

    :param separator_type: The role and format of the separator.
    """
    if not REFERENCE_SEPARATORS:
        update_reference_separators()
    return REFERENCE_SEPARATORS[separator_type]


def get_reference_match(match_type):
    """
    Provides matches for parsing scripture references strings.

    :param match_type:  The type of match is ``range_separator``, ``range`` or ``full``.
    """
    if not REFERENCE_MATCHES:
        update_reference_separators()
    return REFERENCE_MATCHES[match_type]


def parse_reference(reference, bible, language_selection, book_ref_id=False):
    r"""
    This is the next generation über-awesome function that takes a person's typed in string and converts it to a list
    of references to be queried from the Bible database files.

    :param reference: A string. The Bible reference to parse.
    :param bible:  A object. The Bible database object.
    :param language_selection:  An int. The language selection the user has chosen in settings section.
    :param book_ref_id: A string. The book reference id.

    The reference list is a list of tuples, with each tuple structured like this::

        (book, chapter, from_verse, to_verse)

    For example::

        [('John', 3, 16, 18), ('John', 4, 1, 1)]

    **Reference string details:**

    Each reference starts with the book name and a chapter number. These are both mandatory.

    * ``John 3`` refers to Gospel of John chapter 3

    A reference range can be given after a range separator.

    * ``John 3-5`` refers to John chapters 3 to 5

    Single verses can be addressed after a verse separator.

    * ``John 3:16`` refers to John chapter 3 verse 16
    * ``John 3:16-4:3`` refers to John chapter 3 verse 16 to chapter 4 verse 3

    After a verse reference all further single values are treat as verse in the last selected chapter.

    * ``John 3:16-18`` refers to John chapter 3 verses 16 to 18

    After a list separator it is possible to refer to additional verses. They are build analog to the first ones. This
    way it is possible to define each number of verse references. It is not possible to refer to verses in additional
    books.

    * ``John 3:16,18`` refers to John chapter 3 verses 16 and 18
    * ``John 3:16-18,20`` refers to John chapter 3 verses 16 to 18 and 20
    * ``John 3:16-18,4:1`` refers to John chapter 3 verses 16 to 18 and chapter 4 verse 1

    If there is a range separator without further verse declaration the last refered chapter is addressed until the end.

    ``range_regex`` is a regular expression which matches for verse range declarations:

    ``(?:(?P<from_chapter>[0-9]+)%(sep_v)s)?``
        It starts with a optional chapter reference ``from_chapter`` followed by a verse separator.

    ``(?P<from_verse>[0-9]+)``
        The verse reference ``from_verse`` is manditory

    ``(?P<range_to>%(sep_r)s(?:`` ... ``|%(sep_e)s)?)?``
        A ``range_to`` declaration is optional. It starts with a range separator and contains optional a chapter and
        verse declaration or a end separator.

    ``(?:(?P<to_chapter>[0-9]+)%(sep_v)s)?``
        The ``to_chapter`` reference with separator is equivalent to group 1.

    ``(?P<to_verse>[0-9]+)``
        The ``to_verse`` reference is equivalent to group 2.

    The full reference is matched against get_reference_match('full'). This regular expression looks like this:

    ``^\s*(?!\s)(?P<book>[\d]*[^\d]+)(?<!\s)\s*``
        The ``book`` group starts with the first non-whitespace character. There are optional leading digits followed by
        non-digits. The group ends before the whitespace, or a full stop in front of the next digit.

    ``(?P<ranges>(?:%(range_regex)s(?:%(sep_l)s(?!\s*$)|(?=\s*$)))+)\s*$``
        The second group contains all ``ranges``. This can be multiple declarations of range_regex separated by a list
        separator.

    """
    log.debug('parse_reference("{text}")'.format(text=reference))
    match = get_reference_match('full').match(reference)
    if match:
        log.debug('Matched reference {text}'.format(text=reference))
        book = match.group('book')
        if not book_ref_id:
            book_ref_ids = bible.get_book_ref_id_by_localised_name(book, language_selection) or \
                find_book_ref_ids(book, bible)
        elif not bible.get_book_by_book_ref_id(book_ref_id):
            return []
        else:
            book_ref_ids = [book_ref_id]
        # We have not found the book so do not continue
        if not book_ref_ids:
            return []
        ranges = match.group('ranges')
        range_list = get_reference_match('range_separator').split(ranges)
        ref_list = []
        chapter = None
        for this_range in range_list:
            range_match = get_reference_match('range').match(this_range)
            from_chapter = range_match.group('from_chapter')
            from_verse = range_match.group('from_verse')
            has_range = range_match.group('range_to')
            to_chapter = range_match.group('to_chapter')
            to_verse = range_match.group('to_verse')
            if from_chapter:
                from_chapter = int(from_chapter)
            if from_verse:
                from_verse = int(from_verse)
            if to_chapter:
                to_chapter = int(to_chapter)
            if to_verse:
                to_verse = int(to_verse)
            # Fill chapter fields with reasonable values.
            if from_chapter:
                chapter = from_chapter
            elif chapter:
                from_chapter = chapter
            else:
                from_chapter = from_verse
                from_verse = None
            if to_chapter:
                if from_chapter and to_chapter < from_chapter:
                    continue
                else:
                    chapter = to_chapter
            elif to_verse:
                if chapter:
                    to_chapter = chapter
                else:
                    to_chapter = to_verse
                    to_verse = None
            # Append references to the list
            for book_ref_id in book_ref_ids:
                if has_range:
                    if not from_verse:
                        from_verse = 1
                    if not to_verse:
                        to_verse = -1
                    if to_chapter and to_chapter > from_chapter:
                        ref_list.append((book_ref_id, from_chapter, from_verse, -1))
                        for i in range(from_chapter + 1, to_chapter):
                            ref_list.append((book_ref_id, i, 1, -1))
                        ref_list.append((book_ref_id, to_chapter, 1, to_verse))
                    elif to_verse >= from_verse or to_verse == -1:
                        ref_list.append((book_ref_id, from_chapter, from_verse, to_verse))
                elif from_verse:
                    ref_list.append((book_ref_id, from_chapter, from_verse, from_verse))
                else:
                    ref_list.append((book_ref_id, from_chapter, 1, -1))
        return ref_list
    else:
        log.debug('Invalid reference: {text}'.format(text=reference))
        return []


class SearchResults(object):
    """
    Encapsulate a set of search results. This is Bible-type independent.
    """
    def __init__(self, book, chapter, verse_list):
        """
        Create the search result object.

        :param book: The book of the Bible.
        :param chapter: The chapter of the book.
        :param verse_list: The list of verses for this reading.
        """
        self.book = book
        self.chapter = chapter
        self.verse_list = verse_list

    def has_verse_list(self):
        """
        Returns whether or not the verse list contains verses.
        """
        return len(self.verse_list) > 0
