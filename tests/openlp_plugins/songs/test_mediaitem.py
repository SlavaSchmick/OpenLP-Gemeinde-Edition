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
This module contains tests for the lib submodule of the Songs plugin.
"""
import pytest
from unittest.mock import MagicMock, patch

from PyQt5 import QtCore

from openlp.core.common.enum import SongFirstSlideMode, SongSearch
from openlp.core.common.registry import Registry
from openlp.core.lib.serviceitem import ServiceItem
from openlp.plugins.songs.lib.db import AuthorType, Song
from openlp.plugins.songs.lib.mediaitem import SongMediaItem
from openlp.plugins.songs.lib.openlyricsxml import OpenLyrics


__default_settings__ = {
    'songs/footer template': """
${title}<br/>

%if authors_none:
  <%
    authors = ", ".join(authors_none)
  %>
  ${authors_none_label}:&nbsp;${authors}<br/>
%endif

%if authors_words_music:
  <%
    authors = ", ".join(authors_words_music)
  %>
  ${authors_words_music_label}:&nbsp;${authors}<br/>
%endif

%if authors_words:
  <%
    authors = ", ".join(authors_words)
  %>
  ${authors_words_label}:&nbsp;${authors}<br/>
%endif

%if authors_music:
  <%
    authors = ", ".join(authors_music)
  %>
  ${authors_music_label}:&nbsp;${authors}<br/>
%endif

%if authors_translation:
  <%
    authors = ", ".join(authors_translation)
  %>
  ${authors_translation_label}:&nbsp;${authors}<br/>
%endif

%if copyright:
  &copy;&nbsp;${copyright}<br/>
%endif

%if songbook_entries:
  <%
    entries = ", ".join(songbook_entries)
  %>
  ${entries}<br/>
%endif

%if ccli_license:
  ${ccli_license_label}&nbsp;${ccli_license}<br/>
%endif
"""
}


SONG_VERSES_TEST_LYRICS = [[{'type': 'v', 'label': '1'}, 'Test text']]
SONG_VERSES_TEST_VERSE_ORDER = 'v1'


@pytest.fixture
def media_item(settings):
    Registry().register('service_list', MagicMock())
    Registry().register('main_window', MagicMock())
    mocked_plugin = MagicMock()
    with patch('openlp.core.lib.mediamanageritem.MediaManagerItem._setup'), \
            patch('openlp.plugins.songs.forms.editsongform.EditSongForm.__init__'), \
            patch.object(SongMediaItem, 'add_song_search_shortcut'):
        media_item = SongMediaItem(None, mocked_plugin)
        media_item.save_auto_select_id = MagicMock()
        media_item.list_view = MagicMock()
        media_item.list_view.save_auto_select_id = MagicMock()
        media_item.list_view.clear = MagicMock()
        media_item.list_view.addItem = MagicMock()
        media_item.list_view.setCurrentItem = MagicMock()
        media_item.auto_select_id = -1
        media_item.display_songbook = False
        media_item.display_copyright_symbol = False
    settings = Registry().get('settings')
    settings.extend_default_settings(__default_settings__)
    QtCore.QLocale.setDefault(QtCore.QLocale('en_GB'))
    yield media_item


def test_display_results_song(media_item):
    """
    Test displaying song search results with basic song
    """
    # GIVEN: Search results, plus a mocked QtListWidgetItem
    with patch('openlp.core.lib.QtWidgets.QListWidgetItem') as MockedQListWidgetItem, \
            patch('openlp.core.lib.QtCore.Qt.UserRole') as MockedUserRole:
        mock_search_results = []
        mock_song = MagicMock()
        mock_song.id = 1
        mock_song.title = 'My Song'
        mock_song.sort_key = 'My Song'
        mock_song.authors = []
        mock_song_temp = MagicMock()
        mock_song_temp.id = 2
        mock_song_temp.title = 'My Temporary'
        mock_song_temp.sort_key = 'My Temporary'
        mock_song_temp.authors = []
        mock_author = MagicMock()
        mock_author.display_name = 'My Author'
        mock_song.authors.append(mock_author)
        mock_song_temp.authors.append(mock_author)
        mock_song.temporary = False
        mock_song_temp.temporary = True
        mock_search_results.append(mock_song)
        mock_search_results.append(mock_song_temp)
        mock_qlist_widget = MagicMock()
        MockedQListWidgetItem.return_value = mock_qlist_widget
        media_item.auto_select_id = 1

        # WHEN: I display song search results
        media_item.display_results_song(mock_search_results)

        # THEN: The current list view is cleared, the widget is created, and the relevant attributes set
        media_item.list_view.clear.assert_called_with()
        media_item.save_auto_select_id.assert_called_with()
        MockedQListWidgetItem.assert_called_once_with('My Song (My Author)')
        mock_qlist_widget.setData.assert_called_once_with(MockedUserRole, mock_song.id)
        media_item.list_view.addItem.assert_called_once_with(mock_qlist_widget)
        media_item.list_view.setCurrentItem.assert_called_with(mock_qlist_widget)


def test_display_results_author(media_item):
    """
    Test displaying song search results grouped by author with basic song
    """
    # GIVEN: Search results grouped by author, plus a mocked QtListWidgetItem
    with patch('openlp.core.lib.QtWidgets.QListWidgetItem') as MockedQListWidgetItem, \
            patch('openlp.core.lib.QtCore.Qt.UserRole') as MockedUserRole:
        mock_search_results = []
        mock_author = MagicMock()
        mock_song = MagicMock()
        mock_song_temp = MagicMock()
        mock_author.display_name = 'My Author'
        mock_author.songs = []
        mock_song.id = 1
        mock_song.title = 'My Song'
        mock_song.sort_key = 'My Song'
        mock_song.temporary = False
        mock_author_song = MagicMock()
        mock_author_song.author = mock_author
        mock_author_song.song = mock_song
        mock_song_temp.id = 2
        mock_song_temp.title = 'My Temporary'
        mock_song_temp.sort_key = 'My Temporary'
        mock_song_temp.temporary = True
        mock_author_song_temp = MagicMock()
        mock_author_song_temp.author = mock_author
        mock_author_song_temp.song = mock_song_temp
        mock_author.authors_songs = [mock_author_song, mock_author_song_temp]
        mock_search_results.append(mock_author)
        mock_qlist_widget = MagicMock()
        MockedQListWidgetItem.return_value = mock_qlist_widget

        # WHEN: I display song search results grouped by author
        media_item.display_results_author(mock_search_results)

        # THEN: The current list view is cleared, the widget is created, and the relevant attributes set
        media_item.list_view.clear.assert_called_with()
        MockedQListWidgetItem.assert_called_once_with('My Author (My Song)')
        mock_qlist_widget.setData.assert_called_once_with(MockedUserRole, mock_song.id)
        media_item.list_view.addItem.assert_called_once_with(mock_qlist_widget)


def test_display_results_book(media_item):
    """
    Test displaying song search results grouped by book and entry with basic song
    """
    # GIVEN: Search results grouped by book and entry, plus a mocked QtListWidgetItem
    with patch('openlp.core.lib.QtWidgets.QListWidgetItem') as MockedQListWidgetItem, \
            patch('openlp.core.lib.QtCore.Qt.UserRole') as MockedUserRole:
        mock_search_results = [('1', 'My Book', 'My Song', 1)]
        mock_qlist_widget = MagicMock()
        MockedQListWidgetItem.return_value = mock_qlist_widget

        # WHEN: I display song search results grouped by book
        media_item.display_results_book(mock_search_results)

        # THEN: The current list view is cleared, the widget is created, and the relevant attributes set
        media_item.list_view.clear.assert_called_with()
        MockedQListWidgetItem.assert_called_once_with('My Book #1: My Song')
        mock_qlist_widget.setData.assert_called_once_with(MockedUserRole, 1)
        media_item.list_view.addItem.assert_called_once_with(mock_qlist_widget)


def test_songbook_natural_sorting(media_item):
    """
    Test that songbooks are sorted naturally
    """
    # GIVEN: Search results grouped by book and entry
    search_results = [('2', 'Thy Book', 'Thy Song', 50),
                      ('2', 'My Book', 'Your Song', 7),
                      ('10', 'My Book', 'Our Song', 12),
                      ('1', 'My Book', 'My Song', 1),
                      ('2', 'Thy Book', 'A Song', 8)]

    # WHEN: I display song search results grouped by book
    media_item.display_results_book(search_results)

    # THEN: The songbooks are sorted inplace in the right (natural) order,
    #       grouped first by book, then by number, then by song title
    assert search_results == [('1', 'My Book', 'My Song', 1),
                              ('2', 'My Book', 'Your Song', 7),
                              ('10', 'My Book', 'Our Song', 12),
                              ('2', 'Thy Book', 'A Song', 8),
                              ('2', 'Thy Book', 'Thy Song', 50)]


def test_display_results_topic(media_item):
    """
    Test displaying song search results grouped by topic with basic song
    """
    # GIVEN: Search results grouped by topic, plus a mocked QtListWidgetItem
    with patch('openlp.core.lib.QtWidgets.QListWidgetItem') as MockedQListWidgetItem, \
            patch('openlp.core.lib.QtCore.Qt.UserRole') as MockedUserRole:
        mock_search_results = []
        mock_topic = MagicMock()
        mock_song = MagicMock()
        mock_song_temp = MagicMock()
        mock_topic.name = 'My Topic'
        mock_topic.songs = []
        mock_song.id = 1
        mock_song.title = 'My Song'
        mock_song.sort_key = 'My Song'
        mock_song.temporary = False
        mock_song_temp.id = 2
        mock_song_temp.title = 'My Temporary'
        mock_song_temp.sort_key = 'My Temporary'
        mock_song_temp.temporary = True
        mock_topic.songs.append(mock_song)
        mock_topic.songs.append(mock_song_temp)
        mock_search_results.append(mock_topic)
        mock_qlist_widget = MagicMock()
        MockedQListWidgetItem.return_value = mock_qlist_widget

        # WHEN: I display song search results grouped by topic
        media_item.display_results_topic(mock_search_results)

        # THEN: The current list view is cleared, the widget is created, and the relevant attributes set
        media_item.list_view.clear.assert_called_with()
        MockedQListWidgetItem.assert_called_once_with('My Topic (My Song)')
        mock_qlist_widget.setData.assert_called_once_with(MockedUserRole, mock_song.id)
        media_item.list_view.addItem.assert_called_once_with(mock_qlist_widget)


def test_display_results_themes(media_item):
    """
    Test displaying song search results sorted by theme with basic song
    """
    # GIVEN: Search results sorted by theme, plus a mocked QtListWidgetItem
    with patch('openlp.core.lib.QtWidgets.QListWidgetItem') as MockedQListWidgetItem, \
            patch('openlp.core.lib.QtCore.Qt.UserRole') as MockedUserRole:
        mock_search_results = []
        mock_song = MagicMock()
        mock_song_temp = MagicMock()
        mock_song.id = 1
        mock_song.title = 'My Song'
        mock_song.sort_key = 'My Song'
        mock_song.theme_name = 'My Theme'
        mock_song.temporary = False
        mock_song_temp.id = 2
        mock_song_temp.title = 'My Temporary'
        mock_song_temp.sort_key = 'My Temporary'
        mock_song_temp.theme_name = 'My Theme'
        mock_song_temp.temporary = True
        mock_search_results.append(mock_song)
        mock_search_results.append(mock_song_temp)
        mock_qlist_widget = MagicMock()
        MockedQListWidgetItem.return_value = mock_qlist_widget

        # WHEN: I display song search results sorted by theme
        media_item.display_results_themes(mock_search_results)

        # THEN: The current list view is cleared, the widget is created, and the relevant attributes set
        media_item.list_view.clear.assert_called_with()
        MockedQListWidgetItem.assert_called_once_with('My Theme (My Song)')
        mock_qlist_widget.setData.assert_called_once_with(MockedUserRole, mock_song.id)
        media_item.list_view.addItem.assert_called_once_with(mock_qlist_widget)


def test_display_results_cclinumber(media_item):
    """
    Test displaying song search results sorted by CCLI number with basic song
    """
    # GIVEN: Search results sorted by CCLI number, plus a mocked QtListWidgetItem
    with patch('openlp.core.lib.QtWidgets.QListWidgetItem') as MockedQListWidgetItem, \
            patch('openlp.core.lib.QtCore.Qt.UserRole') as MockedUserRole:
        mock_search_results = []
        mock_song = MagicMock()
        mock_song_temp = MagicMock()
        mock_song.id = 1
        mock_song.title = 'My Song'
        mock_song.sort_key = 'My Song'
        mock_song.ccli_number = '12345'
        mock_song.temporary = False
        mock_song_temp.id = 2
        mock_song_temp.title = 'My Temporary'
        mock_song_temp.sort_key = 'My Temporary'
        mock_song_temp.ccli_number = '12346'
        mock_song_temp.temporary = True
        mock_search_results.append(mock_song)
        mock_search_results.append(mock_song_temp)
        mock_qlist_widget = MagicMock()
        MockedQListWidgetItem.return_value = mock_qlist_widget

        # WHEN: I display song search results sorted by CCLI number
        media_item.display_results_cclinumber(mock_search_results)

        # THEN: The current list view is cleared, the widget is created, and the relevant attributes set
        media_item.list_view.clear.assert_called_with()
        MockedQListWidgetItem.assert_called_once_with('12345 (My Song)')
        mock_qlist_widget.setData.assert_called_once_with(MockedUserRole, mock_song.id)
        media_item.list_view.addItem.assert_called_once_with(mock_qlist_widget)


def test_build_song_footer_two_authors(media_item):
    """
    Test build songs footer with basic song and two authors
    """
    # GIVEN: A Song and a Service Item
    mock_song = MagicMock()
    mock_song.title = 'My Song'
    mock_song.authors_songs = []
    mock_author = MagicMock()
    mock_author.display_name = 'my author'
    mock_author_song = MagicMock()
    mock_author_song.author = mock_author
    mock_author_song.author_type = AuthorType.Music
    mock_song.authors_songs.append(mock_author_song)
    mock_author = MagicMock()
    mock_author.display_name = 'another author'
    mock_author_song = MagicMock()
    mock_author_song.author = mock_author
    mock_author_song.author_type = AuthorType.Words
    mock_song.authors_songs.append(mock_author_song)
    mock_author = MagicMock()
    mock_author.display_name = 'translator'
    mock_author_song = MagicMock()
    mock_author_song.author = mock_author
    mock_author_song.author_type = AuthorType.Translation
    mock_song.authors_songs.append(mock_author_song)
    mock_song.copyright = 'My copyright'
    mock_song.songbook_entries = []
    service_item = ServiceItem(None)
    songbooks_str = []
    authors = media_item._get_music_authors(mock_song)
    mako_vars = media_item._get_mako_vars(mock_song, authors, songbooks_str)

    # WHEN: I generate the Footer with default settings
    author_list = media_item.generate_footer(service_item, mock_song, authors, songbooks_str, mako_vars)

    # THEN: I get the following Array returned
    assert service_item.raw_footer == ['My Song', 'Words: another author', 'Music: my author',
                                       'Translation: translator', '© My copyright'], \
        'The array should be returned correctly with a song, two authors and copyright'
    assert author_list == ['another author', 'my author', 'translator'], \
        'The author list should be returned correctly with two authors'


def test_build_song_footer_base_ccli(media_item):
    """
    Test build songs footer with basic song and a CCLI number
    """
    # GIVEN: A Song and a Service Item and a configured CCLI license
    mock_song = MagicMock()
    mock_song.title = 'My Song'
    mock_song.copyright = 'My copyright'
    mock_song.songbook_entries = []
    service_item = ServiceItem(None)
    media_item.settings.setValue('core/ccli number', '1234')
    songbooks_str = []
    authors = media_item._get_music_authors(mock_song)
    mako_vars = media_item._get_mako_vars(mock_song, authors, songbooks_str)

    # WHEN: I generate the Footer with default settings
    media_item.generate_footer(service_item, mock_song, authors, songbooks_str, mako_vars)

    # THEN: I get the following Array returned
    assert service_item.raw_footer == ['My Song', '© My copyright', 'CCLI License: 1234'], \
        'The array should be returned correctly with a song, an author, copyright and ccli'

    # WHEN: I amend the CCLI value
    media_item.settings.setValue('core/ccli number', '4321')
    media_item.generate_footer(service_item, mock_song, authors, songbooks_str, mako_vars)

    # THEN: I would get an amended footer string
    assert service_item.raw_footer == ['My Song', '© My copyright', 'CCLI License: 4321'], \
        'The array should be returned correctly with a song, an author, copyright and amended ccli'


def test_build_song_footer_base_songbook(media_item):
    """
    Test build songs footer with basic song and multiple songbooks
    """
    # GIVEN: A Song and a Service Item
    song = Song()
    song.title = 'My Song'
    song.alternate_title = ''
    song.copyright = 'My copyright'
    song.authors_songs = []
    song.songbook_entries = []
    song.alternate_title = ''
    song.topics = []
    song.ccli_number = ''
    book1 = MagicMock()
    book1.name = 'My songbook'
    book2 = MagicMock()
    book2.name = 'Thy songbook'
    song.songbook_entries = []
    song.add_songbook_entry(book1, '12')
    song.add_songbook_entry(book2, '502A')
    service_item = ServiceItem(None)
    songbooks_str = [str(songbook) for songbook in song.songbook_entries]
    authors = media_item._get_music_authors(song)
    mako_vars = media_item._get_mako_vars(song, authors, songbooks_str)

    # WHEN: I generate the Footer with default settings
    media_item.generate_footer(service_item, song, authors, songbooks_str, mako_vars)

    # THEN: The songbook should be in the footer
    assert service_item.raw_footer == ['My Song', '© My copyright', 'My songbook #12, Thy songbook #502A']


def test_build_song_footer_copyright_enabled(media_item):
    """
    Test building song footer with displaying the copyright symbol
    """
    # GIVEN: A Song and a Service Item; displaying the copyright symbol is enabled
    media_item.display_copyright_symbol = True
    mock_song = MagicMock()
    mock_song.title = 'My Song'
    mock_song.copyright = 'My copyright'
    mock_song.songbook_entries = []
    service_item = ServiceItem(None)
    songbooks_str = []
    authors = media_item._get_music_authors(mock_song)
    mako_vars = media_item._get_mako_vars(mock_song, authors, songbooks_str)

    # WHEN: I generate the Footer with default settings
    media_item.generate_footer(service_item, mock_song, authors, songbooks_str, mako_vars)

    # THEN: The copyright symbol should be in the footer
    assert service_item.raw_footer == ['My Song', '© My copyright']


def test_build_song_footer_copyright_disabled(media_item):
    """
    Test building song footer without displaying the copyright symbol
    """
    # GIVEN: A Song and a Service Item; displaying the copyright symbol should be disabled by default
    mock_song = MagicMock()
    mock_song.title = 'My Song'
    mock_song.copyright = 'My copyright'
    mock_song.songbook_entries = []
    service_item = ServiceItem(None)
    songbooks_str = []
    authors = media_item._get_music_authors(mock_song)
    mako_vars = media_item._get_mako_vars(mock_song, authors, songbooks_str)

    # WHEN: I generate the Footer with default settings
    media_item.generate_footer(service_item, mock_song, authors, songbooks_str, mako_vars)

    # THEN: The copyright symbol should not be in the footer
    assert service_item.raw_footer == ['My Song', '© My copyright']


def test_authors_match(media_item):
    """
    Test the author matching when importing a song from a service
    """
    # GIVEN: A song and a string with authors
    song = MagicMock()
    song.authors = []
    author = MagicMock()
    author.display_name = "Hans Wurst"
    song.authors.append(author)
    author2 = MagicMock()
    author2.display_name = "Max Mustermann"
    song.authors.append(author2)
    # There are occasions where an author appears twice in a song (with different types).
    # We need to make sure that this case works (lp#1313538)
    author3 = MagicMock()
    author3.display_name = "Max Mustermann"
    song.authors.append(author3)
    authors_str = "Hans Wurst, Max Mustermann, Max Mustermann"

    # WHEN: Checking for matching
    result = media_item._authors_match(song, authors_str)

    # THEN: They should match
    assert result is True, "Authors should match"


def test_authors_dont_match(media_item):
    # GIVEN: A song and a string with authors
    song = MagicMock()
    song.authors = []
    author = MagicMock()
    author.display_name = "Hans Wurst"
    song.authors.append(author)
    author2 = MagicMock()
    author2.display_name = "Max Mustermann"
    song.authors.append(author2)
    # There are occasions where an author appears twice in a song (with different types).
    # We need to make sure that this case works (lp#1313538)
    author3 = MagicMock()
    author3.display_name = "Max Mustermann"
    song.authors.append(author3)

    # WHEN: An author is missing in the string
    authors_str = "Hans Wurst, Max Mustermann"
    result = media_item._authors_match(song, authors_str)

    # THEN: They should not match
    assert result is False, "Authors should not match"


def test_build_remote_search(media_item):
    """
    Test results for the remote search api
    """
    # GIVEN: A Song and a search a JSON array should be returned.
    mock_song = MagicMock()
    mock_song.id = 123
    mock_song.title = 'My Song'
    mock_song.search_title = 'My Song'
    mock_song.alternate_title = 'My alternative'
    media_item.search_entire = MagicMock()
    media_item.search_entire.return_value = [mock_song]

    # WHEN: I process a search
    search_results = media_item.search('My Song', False)

    # THEN: The correct formatted results are returned
    assert search_results == [[123, 'My Song', 'My alternative']]


@patch('openlp.plugins.songs.lib.mediaitem.SongBook')
@patch('openlp.plugins.songs.lib.mediaitem.SongBookEntry')
@patch('openlp.plugins.songs.lib.mediaitem.Song')
@patch('openlp.plugins.songs.lib.mediaitem.or_')
def test_entire_song_search(mocked_or, MockedSong, MockedSongBookEntry, MockedBook, media_item):
    """
    Test that searching the entire song does the right queries
    """
    # GIVEN: A song media item, a keyword and some mocks
    keyword = 'Jesus'
    mocked_or.side_effect = lambda a, b, c, d, e: ' '.join([a, b, c, d, e])
    MockedSong.search_title.like.side_effect = lambda a: a
    MockedSong.search_lyrics.like.side_effect = lambda a: a
    MockedSong.comments.like.side_effect = lambda a: a
    MockedSongBookEntry.entry.like.side_effect = lambda a: a
    MockedBook.name.like.side_effect = lambda a: a

    # WHEN: search_entire_song() is called with the keyword
    media_item.search_entire(keyword)

    # THEN: The correct calls were made
    MockedSong.search_title.like.assert_called_once_with('%jesus%')
    MockedSong.search_lyrics.like.assert_called_once_with('%jesus%')
    MockedSong.comments.like.assert_called_once_with('%jesus%')
    MockedSongBookEntry.entry.like.assert_called_once_with('%jesus%')
    MockedBook.name.like.assert_called_once_with('%jesus%')
    mocked_or.assert_called_once_with('%jesus%', '%jesus%', '%jesus%', '%jesus%', '%jesus%')
    media_item.plugin.manager.session.query.assert_called_once_with(MockedSong)

    assert media_item.plugin.manager.session.query.mock_calls[4][0] == '().join().join().filter().all'


def test_build_song_footer_one_author_show_written_by(media_item):
    """
    Test build songs footer with basic song and one author
    """
    # GIVEN: A Song and a Service Item, mocked settings
    media_item.settings.setValue('core/ccli number', "0")
    media_item.settings.setValue('songs/footer template', "")
    with patch('mako.template.Template.render_unicode') as MockedRenderer:
        mock_song = MagicMock()
        mock_song.title = 'My Song'
        mock_song.alternate_title = ''
        mock_song.ccli_number = ''
        mock_song.authors_songs = []
        mock_author = MagicMock()
        mock_author.display_name = 'my author'
        mock_author_song = MagicMock()
        mock_author_song.author = mock_author
        mock_song.authors_songs.append(mock_author_song)
        mock_song.copyright = 'My copyright'
        mock_song.songbook_entries = []
        service_item = ServiceItem(None)
        songbooks_str = []
        authors = media_item._get_music_authors(mock_song)
        mako_vars = media_item._get_mako_vars(mock_song, authors, songbooks_str)

        # WHEN: I generate the Footer with default settings
        author_list = media_item.generate_footer(service_item, mock_song, authors, songbooks_str, mako_vars)

        # THEN: The mako function was called with the following arguments
        args = {'authors_translation': [], 'authors_music_label': 'Music',
                'copyright': 'My copyright', 'songbook_entries': [],
                'alternate_title': '', 'topics': [], 'authors_music_all': [],
                'authors_words_label': 'Words', 'authors_music': [],
                'authors_words_music': [], 'ccli_number': '',
                'authors_none_label': 'Written by', 'title': 'My Song',
                'authors_words_music_label': 'Words and Music',
                'authors_none': ['my author'],
                'ccli_license_label': 'CCLI License', 'authors_words': [],
                'ccli_license': '0', 'authors_translation_label': 'Translation',
                'authors_words_all': [], 'first_slide': False}
        MockedRenderer.assert_called_once_with(**args)
        assert author_list == ['my author'], 'The author list should be returned correctly with one author'


@patch('openlp.plugins.songs.lib.mediaitem.SongMediaItem._get_id_of_item_to_generate')
@patch('openlp.plugins.songs.lib.mediaitem.SongXML.get_verses')
@pytest.mark.parametrize('first_slide_mode', SongFirstSlideMode)
def test_song_first_slide_creation_works(mocked_get_verses, mocked__get_id_of_item_to_generate, media_item,
                                         first_slide_mode, settings):
    """
    Test building song with SongFirstSlideMode = Songbook works
    """
    # GIVEN: A Song and a Service Item
    mocked__get_id_of_item_to_generate.return_value = '00000000-0000-0000-0000-000000000000'
    settings.setValue('songs/first slide mode', first_slide_mode)
    mocked_get_verses.return_value = SONG_VERSES_TEST_LYRICS
    media_item.plugin = MagicMock()
    media_item.open_lyrics = OpenLyrics(media_item.plugin.manager)
    song = Song()
    song.title = 'My Song'
    song.alternate_title = ''
    song.copyright = 'My copyright'
    song.authors_songs = []
    song.songbook_entries = []
    song.alternate_title = ''
    song.lyrics = 'Teste'
    song.theme_name = 'Default'
    song.topics = []
    song.ccli_number = ''
    song.lyrics = '<fake xml>'  # Mocked by mocked_get_verses
    song.verse_order = SONG_VERSES_TEST_VERSE_ORDER
    song.search_title = 'my song@'
    song.last_modified = '2023-02-20T00:00:00Z'
    song.media_files = []
    song.comments = ''
    book1 = MagicMock()
    book1.name = 'My songbook'
    book1.publisher = None
    book2 = MagicMock()
    book2.name = 'Thy songbook'
    book2.publisher = 'Publisher'
    song.songbook_entries = []
    song.add_songbook_entry(book1, '12')
    song.add_songbook_entry(book2, '502A')
    service_item = ServiceItem(None)
    media_item.plugin.manager.get_object.return_value = song

    # WHEN: I generate the Footer with default settings
    media_item.generate_slide_data(service_item, item=song)

    # THEN: The copyright symbol should not be in the footer
    if first_slide_mode == SongFirstSlideMode.Default:
        # No metadata is needed on default slide mode (at least for now)
        assert 'metadata' not in service_item.slides[0]
    else:
        assert service_item.slides[0]['metadata']['songs_first_slide_type'] == first_slide_mode
    if first_slide_mode == SongFirstSlideMode.Songbook:
        assert service_item.slides[0]['text'] == '\nMy songbook #12\n\nThy songbook #502A (Publisher)\n\n'
    if first_slide_mode == SongFirstSlideMode.Footer:
        assert service_item.slides[0]['text'] == service_item.footer_html
        # It needs to have empty footer as it's already shown on text
        assert service_item.slides[0]['footer_html'] == ''


@pytest.fixture
def song_id_db(media_item, tmp_path):
    """
    A real songs database with songs like the ones of the song books, found by ids like "R47" (alternate title)
    """
    from openlp.core.db.manager import DBManager
    from openlp.plugins.songs.lib import clean_song
    from openlp.plugins.songs.lib.db import SongBook, init_schema
    manager = DBManager('songs', init_schema, db_file_path=tmp_path / 'songs.sqlite')
    russian = SongBook(name='Russisch', publisher='')
    german = SongBook(name='Deutsch', publisher='')
    for book, prefix, number, name in ((russian, 'R', 47, 'Song 47'), (russian, 'R', 470, 'Song 470'),
                                       (russian, 'R', 147, 'Song 147'), (german, 'D', 47, 'Lied 47'),
                                       (german, 'D', 203, 'Lied 203'), (german, 'D', 2030, 'Lied 2030')):
        song = Song()
        song.title = '{}{:04d} {}'.format(prefix, number, name)
        song.alternate_title = '{}{}'.format(prefix, number)
        song.lyrics = '<song version="1.0"><lyrics><verse type="v" label="1"><![CDATA[{}]]></verse></lyrics></song>' \
            .format(name)
        song.verse_order = ''
        song.search_title = ''
        song.search_lyrics = ''
        song.temporary = False
        song.add_songbook_entry(book, str(number))
        with patch('openlp.plugins.songs.lib.translate', side_effect=lambda context, text, *args: text):
            clean_song(manager, song)
        manager.save_object(song)
    media_item.plugin.manager = manager
    return manager


@pytest.mark.parametrize('typed, expected', [
    ('r47', ['R0047 Song 47']), ('R47', ['R0047 Song 47']), ('R 47', ['R0047 Song 47']),
    ('r047', ['R0047 Song 47']), ('d203', ['D0203 Lied 203']), ('D0203', ['D0203 Lied 203']),
    ('47', ['D0047 Lied 47', 'R0047 Song 47']), ('r4', []), ('Song', None)])
def test_search_song_id(song_id_db, media_item, typed, expected):
    """
    Test that a song id finds exactly the song with that id, not songs whose id only contains it
    """
    # WHEN: A song id is searched
    result = media_item.search_song_id(typed)

    # THEN: Exactly the songs with that id are found
    if expected is None:
        assert result is None
    else:
        assert sorted(song.title for song in result) == expected


def test_search_song_id_by_song_book(song_id_db, media_item):
    """
    Test that a song id also finds a song by the song book and number, when it has no alternate title
    """
    # GIVEN: A song with a song book number but without an alternate title
    song = song_id_db.get_object_filtered(Song, Song.title == 'R0470 Song 470')
    song.alternate_title = ''
    song.search_title = 'r0470 song 470@'
    song_id_db.save_object(song)

    # WHEN: Its id is searched
    result = media_item.search_song_id('r470')

    # THEN: It is found by the song book "Russisch" and the number 470
    assert [song.title for song in result] == ['R0470 Song 470']


def test_song_id_is_shown_first(song_id_db, media_item):
    """
    Test that the song with the typed id comes first, before the other songs which contain the text
    """
    # GIVEN: The whole song search
    media_item.search_text_edit = MagicMock(**{'displayText.return_value': 'r47',
                                               'current_search_type.return_value': SongSearch.Entire})
    with patch('openlp.plugins.songs.lib.mediaitem.QtWidgets.QListWidgetItem') as MockedQListWidgetItem:
        # WHEN: "r47" is searched
        media_item.on_search_text_button_clicked()

    # THEN: R47 is first, then the other songs with "r47" in them
    shown = [call[0][0] for call in MockedQListWidgetItem.call_args_list]
    assert shown[0].startswith('R0047 Song 47')
    assert any(text.startswith('R0470 Song 470') for text in shown[1:])


@pytest.mark.parametrize('text, search_type, searches', [
    ('r47', SongSearch.Entire, True), ('4', SongSearch.Entire, True), ('Gro', SongSearch.Entire, True),
    ('Gr', SongSearch.Entire, False), ('r', SongSearch.Entire, False), ('r47', SongSearch.Titles, True)])
def test_search_as_you_type_finds_ids_right_away(media_item, text, search_type, searches):
    """
    Test that a song id is searched while typing right away, other texts after a few letters
    """
    # GIVEN: Search as you type
    media_item.is_search_as_you_type_enabled = True
    media_item.search_text_edit = MagicMock(**{'current_search_type.return_value': search_type})
    with patch.object(media_item, 'on_search_text_button_clicked') as mocked_search:
        # WHEN: Something is typed
        media_item.on_search_text_edit_changed(text)

    # THEN: It is searched right away or not yet
    assert mocked_search.called is searches


def test_search_text_return_pressed_previews_the_first_song(media_item):
    """
    Test that Enter in the search field sends the first found song to the Preview and keeps the focus for the next
    search
    """
    # GIVEN: A search which finds songs
    media_item.search_text_edit = MagicMock()
    media_item.list_view = MagicMock(**{'count.return_value': 2, 'selectedItems.return_value': []})
    with patch.object(media_item, 'on_search_text_button_clicked') as mocked_search, \
            patch.object(media_item, 'on_preview_click') as mocked_preview, \
            patch.object(media_item, 'on_live_click') as mocked_live, \
            patch('openlp.plugins.songs.lib.mediaitem.QtWidgets.QApplication.keyboardModifiers',
                  return_value=QtCore.Qt.NoModifier):
        # WHEN: Enter is pressed in the search field
        media_item.on_search_text_return_pressed()

    # THEN: The first song goes to the Preview and the search field keeps the focus
    mocked_search.assert_called_once_with()
    media_item.list_view.setCurrentRow.assert_called_once_with(0)
    mocked_preview.assert_called_once_with(keep_focus=True)
    mocked_live.assert_not_called()
    media_item.search_text_edit.setFocus.assert_called_once_with()


def test_search_text_shift_return_pressed_goes_live(media_item):
    """
    Test that Shift+Enter in the search field sends the found song live and gives the focus to the Live panel, so the
    operator can go on with the arrow keys
    """
    # GIVEN: A search which finds a song, which is selected
    media_item.search_text_edit = MagicMock()
    media_item.list_view = MagicMock(**{'count.return_value': 1, 'selectedItems.return_value': [MagicMock()]})
    live_controller = MagicMock()
    Registry().register('live_controller', live_controller)
    with patch.object(media_item, 'on_search_text_button_clicked'), \
            patch.object(media_item, 'on_preview_click') as mocked_preview, \
            patch.object(media_item, 'on_live_click') as mocked_live, \
            patch('openlp.plugins.songs.lib.mediaitem.QtWidgets.QApplication.keyboardModifiers',
                  return_value=QtCore.Qt.ShiftModifier):
        # WHEN: Shift+Enter is pressed in the search field
        media_item.on_search_text_return_pressed()

    # THEN: The selected song goes live and the Live panel gets the focus
    media_item.list_view.setCurrentRow.assert_not_called()
    mocked_live.assert_called_once_with()
    mocked_preview.assert_not_called()
    live_controller.preview_widget.setFocus.assert_called_once_with()


def test_search_text_return_pressed_without_results(media_item):
    """
    Test that Enter does nothing more than searching when nothing is found
    """
    # GIVEN: A search which finds nothing
    media_item.search_text_edit = MagicMock()
    media_item.list_view = MagicMock(**{'count.return_value': 0})
    with patch.object(media_item, 'on_search_text_button_clicked'), \
            patch.object(media_item, 'on_preview_click') as mocked_preview, \
            patch.object(media_item, 'on_live_click') as mocked_live:
        # WHEN: Enter is pressed in the search field
        media_item.on_search_text_return_pressed()

    # THEN: Nothing goes to the Preview or live
    mocked_preview.assert_not_called()
    mocked_live.assert_not_called()


def test_song_search_shortcut(media_item):
    """
    Test that the song search shortcut (Ctrl+L) shows the songs and puts the cursor into the search field
    """
    # GIVEN: The songs in a hidden library
    media_item.search_text_edit = MagicMock()
    main_window = MagicMock(**{'media_manager_dock.isVisible.return_value': False})
    Registry().remove('main_window')
    Registry().register('main_window', main_window)

    # WHEN: The shortcut is used
    media_item.on_song_search_shortcut_triggered()

    # THEN: The library shows the songs and the search field has the focus with its text selected
    main_window.media_manager_dock.setVisible.assert_called_once_with(True)
    main_window.media_tool_box.setCurrentWidget.assert_called_once_with(media_item)
    media_item.search_text_edit.setFocus.assert_called_once_with()
    media_item.search_text_edit.selectAll.assert_called_once_with()


def test_song_search_shortcut_default(settings):
    """
    Test that the song search shortcut is Ctrl+L by default
    """
    from PyQt5 import QtGui
    assert settings.value('shortcuts/songSearchShortcut') == [QtGui.QKeySequence('Ctrl+L')]


def _add_variants(manager):
    """Add the variants A and B of the song D63, like in the Gemeinde-Gesangbuch"""
    from openlp.plugins.songs.lib import clean_song
    from openlp.plugins.songs.lib.db import SongBook
    german = manager.get_object_filtered(SongBook, SongBook.name == 'Deutsch')
    for variant in ('A', 'B'):
        song = Song()
        song.title = 'D063{} Keiner wird zuschanden'.format(variant)
        song.alternate_title = 'D63{}'.format(variant)
        song.lyrics = '<song version="1.0"><lyrics><verse type="v" label="1"><![CDATA[Keiner]]></verse></lyrics></song>'
        song.verse_order = ''
        song.search_title = ''
        song.search_lyrics = ''
        song.temporary = False
        song.add_songbook_entry(german, '63{}'.format(variant))
        with patch('openlp.plugins.songs.lib.translate', side_effect=lambda context, text, *args: text):
            clean_song(manager, song)
        manager.save_object(song)


@pytest.mark.parametrize('typed, expected', [
    ('d63', ['D063A Keiner wird zuschanden', 'D063B Keiner wird zuschanden']),
    ('d63a', ['D063A Keiner wird zuschanden']), ('D063B', ['D063B Keiner wird zuschanden']),
    ('d 63 b', None), ('d63c', []), ('d47', ['D0047 Lied 47'])])
def test_search_song_id_variants(song_id_db, media_item, typed, expected):
    """
    Test that a song id without a variant letter finds all variants of the song, and with one only that variant
    """
    # GIVEN: A song with the variants A and B
    _add_variants(song_id_db)

    # WHEN: A song id is searched
    result = media_item.search_song_id(typed)

    # THEN: The variants are found as expected
    if expected is None:
        assert result is None
    else:
        assert sorted(song.title for song in result) == expected


def test_search_song_id_variant_by_song_book(song_id_db, media_item):
    """
    Test that a variant is also found by its song book number, when it has no alternate title
    """
    # GIVEN: The variants of D63, without alternate titles
    _add_variants(song_id_db)
    for song in song_id_db.get_all_objects(Song, Song.title.like('D063%')):
        song.alternate_title = ''
        song.search_title = song.title.lower() + '@'
        song_id_db.save_object(song)

    # WHEN: A variant and all variants are searched
    one = media_item.search_song_id('d63b')
    both = media_item.search_song_id('d63')

    # THEN: They are found by the song book "Deutsch" and the number with the variant
    assert [song.title for song in one] == ['D063B Keiner wird zuschanden']
    assert sorted(song.title for song in both) == ['D063A Keiner wird zuschanden', 'D063B Keiner wird zuschanden']
