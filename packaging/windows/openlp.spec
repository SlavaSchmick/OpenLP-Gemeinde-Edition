# -*- mode: python ; coding: utf-8 -*-
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
PyInstaller spec for the Windows build of OpenLP, used by build.ps1.

OpenLP finds its plugins, display pages, fonts and translations next to OpenLP.exe, so the application is built as a
folder with everything at the top level (contents_directory='.'). build.ps1 adds the data files, the translations and
VLC afterwards.
"""
from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs, collect_submodules

repo = Path(SPECPATH).parent.parent

# Plugins and other extensions are imported at run time by file name, so include every OpenLP module
hidden_imports = collect_submodules('openlp', filter=lambda name: '.tests' not in name)
hidden_imports += collect_submodules('sqlalchemy.dialects.sqlite')
hidden_imports += collect_submodules('alembic')
hidden_imports += collect_submodules('websockets')
hidden_imports += ['vlc', 'pymediainfo', 'pyodbc', 'waitress', 'flask_cors', 'qrcode', 'qrcode.image.svg', 'win32com.client',
                   'pythoncom', 'pywintypes', 'PyQt5.QtWebChannel', 'PyQt5.QtMultimedia', 'PyQt5.QtPrintSupport']

datas = collect_data_files('qtawesome')
datas += collect_data_files('alembic')
binaries = collect_dynamic_libs('pymediainfo')

a = Analysis(
    [str(repo / 'run_openlp.py')],
    pathex=[str(repo)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hidden_imports,
    excludes=['tkinter', 'pytest', 'pytest_qt', 'flake8', 'tests', 'PySide6', 'PyQt6'],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='OpenLP',
    icon=str(repo / 'resources' / 'images' / 'OpenLP.ico'),
    console=False,
    upx=False,
    contents_directory='.',
    version=str(Path(SPECPATH) / 'build-info' / 'version_info.txt'),
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    upx=False,
    name='OpenLP',
)
