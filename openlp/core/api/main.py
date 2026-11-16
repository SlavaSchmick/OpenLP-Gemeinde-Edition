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

import os

from flask import Blueprint, send_from_directory
from openlp.core.common.applocation import AppLocation
from openlp.core.common.mime import get_mime_type

main_views = Blueprint('main', __name__)


def remote_path():
    """
    The folder of the web remote of the Gemeinde-Edition, which is part of OpenLP (the web remote of openlp.org,
    which was downloaded into the data folder, isn't used any more)
    """
    return AppLocation.get_directory(AppLocation.AppDir) / 'core' / 'api' / 'remote'


def old_remote_path():
    """
    The folder of the web remote of openlp.org, if it was downloaded before. Its views for the stage, the chords and
    the live display (/stage, /chords, /main) are still served from there.
    """
    return AppLocation.get_section_data_path('remotes')


OLD_REMOTE_VIEWS = ['stage', 'chords', 'main']


@main_views.route('/', defaults={'path': ''})
@main_views.route('/<path>')
def index(path):
    if path and os.path.isfile(remote_path() / path):
        return send_from_directory(str(remote_path()), path, mimetype=get_mime_type(path))
    if path in OLD_REMOTE_VIEWS and os.path.isfile(old_remote_path() / 'index.html'):
        return send_from_directory(str(old_remote_path()), 'index.html', mimetype='text/html')
    if path and os.path.isfile(old_remote_path() / path):
        # The scripts and styles of the old views
        return send_from_directory(str(old_remote_path()), path, mimetype=get_mime_type(path))
    return send_from_directory(str(remote_path()), 'index.html', mimetype='text/html')


@main_views.route('/assets/<path:path>')
def assets(path):
    return send_from_directory(str(AppLocation.get_section_data_path('remotes') / 'assets'),
                               path, mimetype=get_mime_type(path))


@main_views.route('/stage/<path>/')
def stages(path):
    return send_from_directory(str(AppLocation.get_section_data_path('stages') / path),
                               'stage.html', mimetype='text/html')


@main_views.route('/stage/<path:path>/<file>')
def stage_assets(path, file):
    return send_from_directory(str(AppLocation.get_section_data_path('stages') / path),
                               file, mimetype=get_mime_type(file))
