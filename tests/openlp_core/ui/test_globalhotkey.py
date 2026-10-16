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
Test the global shortcut which brings OpenLP to the front, in openlp.core.ui.globalhotkey
"""
import ctypes
from unittest.mock import MagicMock, patch

import pytest
from PyQt5 import QtCore, QtGui, QtWidgets

from openlp.core.ui import globalhotkey
from openlp.core.ui.globalhotkey import HOTKEY_ID, MOD_ALT, MOD_CONTROL, MOD_NOREPEAT, MOD_SHIFT, MOD_WIN, \
    WM_HOTKEY, GlobalHotkey, hotkey_from_sequence


@pytest.mark.parametrize('sequence,expected', [
    ('Ctrl+Alt+O', (MOD_CONTROL | MOD_ALT | MOD_NOREPEAT, 0x4F)),
    ('Ctrl+Shift+5', (MOD_CONTROL | MOD_SHIFT | MOD_NOREPEAT, 0x35)),
    ('Meta+F12', (MOD_WIN | MOD_NOREPEAT, 0x7B)),
    ('F1', (MOD_NOREPEAT, 0x70)),
    ('Ctrl+Alt+Space', (MOD_CONTROL | MOD_ALT | MOD_NOREPEAT, 0x20)),
    ('Ctrl+Alt+Ö', None),
    ('', None),
])
def test_hotkey_from_sequence(sequence, expected):
    """
    Test that a key sequence becomes the modifiers and the virtual key code of Windows
    """
    # GIVEN: A key sequence
    # WHEN: It is converted
    # THEN: The modifiers and the key code are returned, or None if the key isn't supported
    assert hotkey_from_sequence(QtGui.QKeySequence(sequence)) == expected


def test_hotkey_from_no_sequence():
    """
    Test that no sequence gives no hotkey
    """
    assert hotkey_from_sequence(None) is None


@pytest.fixture
def window_and_action(qapp):
    window = QtWidgets.QMainWindow()
    action = QtWidgets.QAction(window)
    action.setShortcut(QtGui.QKeySequence('Ctrl+Alt+O'))
    yield window, action
    window.close()


@patch.object(globalhotkey, 'is_win', return_value=True)
def test_register_and_change(mocked_is_win, window_and_action):
    """
    Test that the shortcut of the action is registered with Windows, and registered again when it changes
    """
    # GIVEN: A main window and an action with a shortcut, and Windows
    window, action = window_and_action
    user32 = MagicMock()
    user32.RegisterHotKey.return_value = 1
    with patch.object(ctypes, 'windll', MagicMock(user32=user32), create=True), \
            patch.object(QtCore.QCoreApplication.instance(), 'installNativeEventFilter'):
        # WHEN: The global shortcut is set up, and then the shortcut is changed and removed
        hotkey = GlobalHotkey(window, action)
        first = user32.RegisterHotKey.call_args[0][1:]
        action.setShortcut(QtGui.QKeySequence('Ctrl+Alt+F5'))
        second = user32.RegisterHotKey.call_args[0][1:]
        action.setShortcut(QtGui.QKeySequence())

    # THEN: The shortcuts were registered one after the other, and the old one was removed each time
    assert first == (HOTKEY_ID, MOD_CONTROL | MOD_ALT | MOD_NOREPEAT, 0x4F)
    assert second == (HOTKEY_ID, MOD_CONTROL | MOD_ALT | MOD_NOREPEAT, 0x74)
    assert user32.UnregisterHotKey.call_count == 2
    assert hotkey.registered is None


@patch.object(globalhotkey, 'is_win', return_value=True)
def test_register_failed(mocked_is_win, window_and_action):
    """
    Test that a shortcut which another program uses is not registered, without an error
    """
    # GIVEN: A shortcut which can't be registered
    window, action = window_and_action
    user32 = MagicMock()
    user32.RegisterHotKey.return_value = 0
    with patch.object(ctypes, 'windll', MagicMock(user32=user32), create=True), \
            patch.object(QtCore.QCoreApplication.instance(), 'installNativeEventFilter'):
        # WHEN: The global shortcut is set up
        hotkey = GlobalHotkey(window, action)

    # THEN: It isn't registered
    assert hotkey.registered is None


@patch.object(globalhotkey, 'is_win', return_value=False)
def test_not_on_other_platforms(mocked_is_win, window_and_action):
    """
    Test that nothing is registered on other platforms
    """
    # GIVEN: Another platform than Windows
    window, action = window_and_action
    with patch.object(QtCore.QCoreApplication.instance(), 'installNativeEventFilter') as mocked_install:
        # WHEN: The global shortcut is set up
        hotkey = GlobalHotkey(window, action)

    # THEN: Nothing is registered
    mocked_install.assert_not_called()
    assert hotkey.registered is None


@pytest.mark.skipif(not hasattr(ctypes, 'windll'), reason='Windows messages only exist on Windows')
@patch.object(globalhotkey, 'is_win', return_value=False)
def test_hotkey_message_activates(mocked_is_win, window_and_action):
    """
    Test that the message of Windows for the shortcut brings the window to the front, and other messages are ignored
    """
    from ctypes import wintypes
    # GIVEN: The global shortcut and two Windows messages
    window, action = window_and_action
    hotkey = GlobalHotkey(window, action)
    hotkey_message = wintypes.MSG(message=WM_HOTKEY, wParam=HOTKEY_ID)
    other_message = wintypes.MSG(message=WM_HOTKEY + 1, wParam=HOTKEY_ID)

    # WHEN: Windows sends the messages
    with patch.object(hotkey, 'activate') as mocked_activate:
        handled = hotkey.nativeEventFilter(QtCore.QByteArray(b'windows_generic_MSG'),
                                           ctypes.addressof(hotkey_message))
        ignored = hotkey.nativeEventFilter(QtCore.QByteArray(b'windows_generic_MSG'),
                                           ctypes.addressof(other_message))

    # THEN: Only the shortcut message brings OpenLP to the front
    assert handled == (True, 0)
    assert ignored == (False, 0)
    mocked_activate.assert_called_once_with()


@patch.object(globalhotkey, 'is_win', return_value=False)
def test_activate_restores_minimized_window(mocked_is_win, window_and_action):
    """
    Test that a minimized window is restored, and a maximized one stays maximized
    """
    # GIVEN: A maximized window which is minimized
    window, action = window_and_action
    hotkey = GlobalHotkey(window, action)
    window.setWindowState(QtCore.Qt.WindowMaximized | QtCore.Qt.WindowMinimized)

    # WHEN: OpenLP is brought to the front
    with patch.object(window, 'raise_') as mocked_raise, patch.object(window, 'activateWindow') as mocked_activate:
        hotkey.activate()

    # THEN: It is restored to its maximized state and brought to the front
    assert not window.windowState() & QtCore.Qt.WindowMinimized
    assert window.windowState() & QtCore.Qt.WindowMaximized
    mocked_raise.assert_called_once_with()
    mocked_activate.assert_called_once_with()
