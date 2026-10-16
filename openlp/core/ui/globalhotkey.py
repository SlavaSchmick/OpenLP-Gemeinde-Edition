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
A global shortcut, registered with Windows, which brings OpenLP to the front from any other program (e.g. Ctrl+Alt+O).
Its key is the shortcut of an action, so it can be changed in the shortcut dialog like any other shortcut.
"""
import ctypes
import logging

from PyQt5 import QtCore

from openlp.core.common.platform import is_win

log = logging.getLogger(__name__)

WM_HOTKEY = 0x0312
MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_WIN = 0x0008
MOD_NOREPEAT = 0x4000
# The id of the shortcut for Windows, unique within OpenLP
HOTKEY_ID = 0x4F4C


def hotkey_from_sequence(sequence):
    """
    The modifiers and the virtual key code of Windows for the first key combination of a key sequence

    :param PyQt5.QtGui.QKeySequence sequence: The key sequence, e.g. Ctrl+Alt+O
    :return: The modifiers and the virtual key code, or None if the sequence is empty or its key isn't supported
    """
    if sequence is None or sequence.isEmpty():
        return None
    combination = sequence[0]
    key = combination & ~int(QtCore.Qt.KeyboardModifierMask)
    modifiers = MOD_NOREPEAT
    for qt_modifier, windows_modifier in ((QtCore.Qt.ControlModifier, MOD_CONTROL), (QtCore.Qt.AltModifier, MOD_ALT),
                                          (QtCore.Qt.ShiftModifier, MOD_SHIFT), (QtCore.Qt.MetaModifier, MOD_WIN)):
        if combination & int(qt_modifier):
            modifiers |= windows_modifier
    if QtCore.Qt.Key_A <= key <= QtCore.Qt.Key_Z or QtCore.Qt.Key_0 <= key <= QtCore.Qt.Key_9:
        # Letters and digits have the same codes in Qt and Windows
        virtual_key = key
    elif QtCore.Qt.Key_F1 <= key <= QtCore.Qt.Key_F24:
        virtual_key = 0x70 + key - QtCore.Qt.Key_F1
    else:
        virtual_key = {QtCore.Qt.Key_Space: 0x20, QtCore.Qt.Key_Home: 0x24, QtCore.Qt.Key_End: 0x23,
                       QtCore.Qt.Key_Insert: 0x2D, QtCore.Qt.Key_PageUp: 0x21, QtCore.Qt.Key_PageDown: 0x22,
                       QtCore.Qt.Key_Pause: 0x13}.get(key)
    if virtual_key is None:
        return None
    return modifiers, virtual_key


class GlobalHotkey(QtCore.QAbstractNativeEventFilter):
    """
    Registers the shortcut of an action globally with Windows, and brings the main window to the front when it is
    pressed, also when another program is in the foreground. Does nothing on other platforms.
    """
    def __init__(self, main_window, action):
        super().__init__()
        self.main_window = main_window
        self.action = action
        self.registered = None
        if not is_win():
            return
        QtCore.QCoreApplication.instance().installNativeEventFilter(self)
        action.changed.connect(self.update_registration)
        self.update_registration()

    def update_registration(self):
        """
        Register the current shortcut of the action, e.g. after it was changed in the shortcut dialog
        """
        hotkey = hotkey_from_sequence(self.action.shortcut())
        if hotkey == self.registered:
            return
        self.unregister()
        if not hotkey:
            return
        if ctypes.windll.user32.RegisterHotKey(self._window_handle(), HOTKEY_ID, hotkey[0], hotkey[1]):
            self.registered = hotkey
            log.info('Registered the global shortcut {key}'.format(key=self.action.shortcut().toString()))
        else:
            log.warning('The global shortcut {key} could not be registered, it is probably used by another '
                        'program'.format(key=self.action.shortcut().toString()))

    def unregister(self):
        """
        Remove the global shortcut, e.g. when OpenLP is closed
        """
        if self.registered and is_win():
            ctypes.windll.user32.UnregisterHotKey(self._window_handle(), HOTKEY_ID)
        self.registered = None

    def nativeEventFilter(self, event_type, message):
        """
        Bring OpenLP to the front when Windows reports the global shortcut
        """
        if bytes(event_type) == b'windows_generic_MSG':
            from ctypes import wintypes
            msg = wintypes.MSG.from_address(int(message))
            if msg.message == WM_HOTKEY and msg.wParam == HOTKEY_ID:
                self.activate()
                return True, 0
        return False, 0

    def activate(self):
        """
        Show the main window in front of all other windows, restored if it was minimized (a maximized window stays
        maximized)
        """
        window = self.main_window
        if window.isMinimized():
            window.setWindowState(window.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
        window.raise_()
        window.activateWindow()
        if is_win():
            # Windows allows this, as the program which received the shortcut may take the foreground
            ctypes.windll.user32.SetForegroundWindow(self._window_handle())

    def _window_handle(self):
        from ctypes import wintypes
        return wintypes.HWND(int(self.main_window.winId()))
