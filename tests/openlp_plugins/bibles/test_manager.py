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
This module contains tests for the manager submodule of the Bibles plugin.
"""
from pathlib import Path
from unittest.mock import MagicMock, patch

from openlp.plugins.bibles.lib.manager import BibleManager


def test_delete_bible(settings):
    """
    Test the BibleManager delete_bible method
    """
    # GIVEN: An instance of BibleManager and a mocked bible
    with patch.object(BibleManager, 'reload_bibles'), \
            patch('openlp.plugins.bibles.lib.manager.delete_file', return_value=True) as mocked_delete_file:
        instance = BibleManager(MagicMock())
        # We need to keep a reference to the mock for close_all as it gets set to None later on!
        mocked_close = MagicMock()
        mocked_bible = MagicMock(file_path='KJV.sqlite', path=Path('bibles'),
                                 **{'session.close': mocked_close})
        instance.db_cache = {'KJV': mocked_bible}

        # WHEN: Calling delete_bible with 'KJV'
        result = instance.delete_bible('KJV')

        # THEN: The session should have been closed and set to None, the bible should be deleted, and the result of
        #       the deletion returned.
        assert result is True
        mocked_close.assert_called_once_with()
        assert mocked_bible.session is None
        mocked_delete_file.assert_called_once_with(Path('bibles') / 'KJV.sqlite')


def test_delete_bible_releases_the_file(settings):
    """
    Test that deleting a Bible also closes the connections of its database engine, which would otherwise keep the file
    open and prevent deleting it on Windows
    """
    # GIVEN: A Bible with a session bound to an engine
    with patch.object(BibleManager, 'reload_bibles'), \
            patch('openlp.plugins.bibles.lib.manager.delete_file', return_value=True):
        instance = BibleManager(MagicMock())
        mocked_engine = MagicMock()
        mocked_bible = MagicMock(path=Path('bibles'), **{'session.get_bind.return_value': mocked_engine})
        instance.db_cache = {'KJV': mocked_bible}

        # WHEN: Deleting the Bible
        instance.delete_bible('KJV')

    # THEN: The connections of the engine are closed
    mocked_engine.dispose.assert_called_once_with()


def test_reload_bibles_removes_an_empty_bible(settings, tmp_path):
    """
    Test that an empty Bible without a name, as a failed import leaves it behind, is removed when the Bibles are loaded,
    also on Windows where an open file can't be deleted
    """
    import sqlite3
    # GIVEN: An empty Bible database next to the Bibles
    bibles = tmp_path / 'bibles'
    bibles.mkdir()
    connection = sqlite3.connect(bibles / '..sqlite')
    connection.executescript('create table metadata (key varchar(255) primary key, value varchar(255));'
                             'insert into metadata values ("version", "2");')
    connection.close()
    settings.setValue('advanced/data path', tmp_path)

    # WHEN: The Bibles are loaded
    BibleManager(MagicMock())

    # THEN: The empty Bible is gone
    assert not (bibles / '..sqlite').exists()
