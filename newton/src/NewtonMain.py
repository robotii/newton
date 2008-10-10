# Copyright (c) 2004 Dennis Craven
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#

import pygtk
pygtk.require('2.0')

import gtk
import gnome
import gnome.ui
import gobject

import gettext
import locale
#import os.path
import os
import sys

from gettext import gettext as _

from NewtonConfig import Configuration
from NewtonGui import Newton
from newton import NAME, VERSION, UI_DIR, LOCALE_DIR, PIXMAPS_DIR

gettext.bindtextdomain(NAME.lower(), LOCALE_DIR)
gettext.textdomain(NAME.lower())

locale.bindtextdomain(NAME.lower(), LOCALE_DIR)
locale.textdomain(NAME.lower())

def main():
    gnome.program_init(NAME, VERSION)
    config = Configuration()
    newt = Newton(config, 'window')
    newt.toggle_window_visible()
    gtk.main()

