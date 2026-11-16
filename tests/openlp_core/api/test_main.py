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

from openlp.core.api.main import get_mime_type


def test_get_mime_type():
    assert get_mime_type('index.html') == 'text/html'
    assert get_mime_type('stage.js') == 'application/javascript'
    assert get_mime_type('stage.css') == 'text/css'


def test_index_serves_web_remote(temp_folder):
    """The web remote of the Gemeinde-Edition is shipped with OpenLP and served at the root"""
    # GIVEN: The Flask app, no old web remote
    from pathlib import Path
    from unittest.mock import patch
    from openlp.core.api import app as flask_app
    client = flask_app.test_client()

    # WHEN: The root, a file of the remote and an unknown path are requested
    with patch('openlp.core.api.main.AppLocation.get_section_data_path', return_value=Path(temp_folder)):
        index = client.get('/')
        script = client.get('/remote.js')
        unknown = client.get('/unknown-page')

    # THEN: The remote is answered, an unknown path gets the remote too
    assert index.status_code == 200
    assert b'remote.js' in index.data
    assert script.status_code == 200
    assert script.mimetype == 'application/javascript'
    assert b'/api/v2' in script.data
    assert unknown.status_code == 200
    assert b'remote.js' in unknown.data


def test_old_remote_views_still_served(temp_folder):
    """The stage, chords and live views of a downloaded web remote of openlp.org keep working"""
    # GIVEN: A downloaded old web remote
    from pathlib import Path
    from unittest.mock import patch
    from openlp.core.api import app as flask_app
    old_remote = Path(temp_folder)
    (old_remote / 'index.html').write_text('<html>old remote</html>')
    (old_remote / 'main-ABC.js').write_text('// old script')
    client = flask_app.test_client()

    with patch('openlp.core.api.main.AppLocation.get_section_data_path', return_value=old_remote):
        # WHEN: Its views, its script and the root are requested
        stage = client.get('/stage')
        script = client.get('/main-ABC.js')
        root = client.get('/')

    # THEN: The views come from the old remote, the root is the new remote
    assert b'old remote' in stage.data
    assert b'old script' in script.data
    assert b'remote.js' in root.data


def test_old_remote_views_without_old_remote(temp_folder):
    """Without a downloaded old web remote the new remote is shown"""
    from pathlib import Path
    from unittest.mock import patch
    from openlp.core.api import app as flask_app
    client = flask_app.test_client()

    with patch('openlp.core.api.main.AppLocation.get_section_data_path', return_value=Path(temp_folder)):
        stage = client.get('/stage')

    assert b'remote.js' in stage.data
