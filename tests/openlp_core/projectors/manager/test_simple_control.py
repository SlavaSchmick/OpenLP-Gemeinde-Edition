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
Test the simpler projector control: the state in plain words, buttons which also work when a state isn't known, and
connecting again to projectors which closed the connection (e.g. in standby)
"""
from unittest.mock import DEFAULT, MagicMock, patch

import pytest
from PyQt5 import QtWidgets

from openlp.core.projectors.constants import QSOCKET_STATE, S_CONNECTED, S_CONNECTING, S_COOLDOWN, \
    S_NOT_CONNECTED, S_ON, S_STANDBY, S_WARMUP
from openlp.core.projectors.manager import ProjectorItem, projector_state_text

SOCKET_STATE = {status: state for state, status in QSOCKET_STATE.items()}


def make_item(connection=S_CONNECTED, power=None, shutter=None, keep_connected=False):
    link = MagicMock()
    link.name = 'Beamer'
    link.state.return_value = SOCKET_STATE[connection]
    link.power = power
    link.shutter = shutter
    item = ProjectorItem(item=link)
    item.keep_connected = keep_connected
    return item


@pytest.mark.parametrize('connection, power, shutter, keep, expected', [
    (S_NOT_CONNECTED, None, None, False, 'Not connected'),
    (S_NOT_CONNECTED, None, None, True, 'Not connected - connecting again...'),
    (S_CONNECTING, None, None, True, 'Connecting...'),
    (S_CONNECTED, None, None, True, 'Connected'),
    (S_CONNECTED, S_STANDBY, None, True, 'Standby'),
    (S_CONNECTED, S_WARMUP, None, True, 'Warming up...'),
    (S_CONNECTED, S_COOLDOWN, None, True, 'Cooling down...'),
    (S_CONNECTED, S_ON, False, True, 'On'),
    (S_CONNECTED, S_ON, True, True, 'On - picture blanked')])
def test_projector_state_text(connection, power, shutter, keep, expected):
    """
    Test the state of a projector in plain words
    """
    # GIVEN: A projector in a state
    item = make_item(connection, power, shutter, keep)

    # WHEN: Its state is described
    # THEN: The words match the state
    assert projector_state_text(item) == expected


@pytest.fixture
def manager(projector_manager):
    with patch.multiple(projector_manager, udp_listen_add=DEFAULT, udp_listen_delete=DEFAULT):
        projector_manager.bootstrap_initialise()
        projector_manager.bootstrap_post_set_up()
    yield projector_manager
    projector_manager.reconnect_timer.stop()


def toolbar_state(manager, name):
    """Whether a toolbar button is shown, and whether it can be used"""
    action = manager.one_toolbar.findChild(QtWidgets.QAction, name)
    return action.isVisible(), action.isEnabled()


SHOWN, HIDDEN, DISABLED = (True, True), (False, False), (True, False)


@pytest.mark.parametrize('connection, power, shutter, expected', [
    # Not connected: only "Power On", which can't be used
    (S_NOT_CONNECTED, None, None, {'poweron_projector': DISABLED, 'poweroff_projector': HIDDEN,
                                   'blank_projector': HIDDEN, 'show_projector': HIDDEN}),
    # Power state not known (yet): both power buttons
    (S_CONNECTED, None, None, {'poweron_projector': SHOWN, 'poweroff_projector': SHOWN,
                               'blank_projector': HIDDEN, 'show_projector': HIDDEN}),
    (S_CONNECTED, S_STANDBY, None, {'poweron_projector': SHOWN, 'poweroff_projector': HIDDEN,
                                    'blank_projector': HIDDEN, 'show_projector': HIDDEN}),
    (S_CONNECTED, S_WARMUP, None, {'poweron_projector': HIDDEN, 'poweroff_projector': SHOWN,
                                   'blank_projector': HIDDEN, 'show_projector': HIDDEN}),
    (S_CONNECTED, S_ON, False, {'poweron_projector': HIDDEN, 'poweroff_projector': SHOWN,
                                'blank_projector': SHOWN, 'show_projector': HIDDEN}),
    # Shutter state not known: "Blank"
    (S_CONNECTED, S_ON, None, {'poweron_projector': HIDDEN, 'poweroff_projector': SHOWN,
                               'blank_projector': SHOWN, 'show_projector': HIDDEN}),
    (S_CONNECTED, S_ON, True, {'poweron_projector': HIDDEN, 'poweroff_projector': SHOWN,
                               'blank_projector': HIDDEN, 'show_projector': SHOWN})])
def test_buttons_for_states(manager, connection, power, shutter, expected):
    """
    Test that only the buttons which fit the state of the projector are shown (at most two), and that they can be
    used, also when a state isn't known
    """
    # GIVEN: One selected projector in a state
    item = make_item(connection, power, shutter)
    with patch.object(manager.projector_list_widget, 'selectedItems') as mocked_selected:
        mocked_selected.return_value = [MagicMock(data=MagicMock(return_value=item))]

        # WHEN: The buttons are updated
        manager.update_icons()

    # THEN: The fitting buttons are shown
    assert {name: toolbar_state(manager, name) for name in expected} == expected


def test_main_buttons_have_labels(manager):
    """
    Test that the main buttons show a short label next to their icon
    """
    # GIVEN: The projector manager
    # WHEN: Its toolbar is set up
    labels = {name: manager.one_toolbar.findChild(QtWidgets.QAction, name).iconText()
              for name in ('connect_projector', 'poweron_projector', 'poweroff_projector', 'blank_projector',
                           'show_projector')}

    # THEN: The labels are short
    assert labels == {'connect_projector': 'Connect', 'poweron_projector': 'Power On',
                      'poweroff_projector': 'Standby', 'blank_projector': 'Blank', 'show_projector': 'Show'}


def test_reconnect_projectors(manager):
    """
    Test that only the projectors which should be connected, and aren't, are connected again
    """
    # GIVEN: A projector which lost its connection, one which the user disconnected, and a connected one
    lost = make_item(S_NOT_CONNECTED, keep_connected=True)
    disconnected = make_item(S_NOT_CONNECTED, keep_connected=False)
    connected = make_item(S_CONNECTED, keep_connected=True)
    manager.projector_list = [lost, disconnected, connected]

    # WHEN: The projectors are checked
    manager.reconnect_projectors()

    # THEN: Only the lost one is connected again
    lost.link.connect_to_host.assert_called_once_with()
    disconnected.link.connect_to_host.assert_not_called()
    connected.link.connect_to_host.assert_not_called()


def test_connect_and_disconnect_remember_the_choice(manager):
    """
    Test that connecting keeps a projector connected, and disconnecting stops that
    """
    # GIVEN: A projector
    item = make_item(S_NOT_CONNECTED)

    # WHEN: It is connected and then disconnected
    manager.on_connect_projector(item=item)
    after_connect = item.keep_connected
    manager.on_disconnect_projector(item=item)

    # THEN: It should stay connected after connecting, but not after disconnecting
    assert after_connect is True
    assert item.keep_connected is False
