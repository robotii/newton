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
import gnomeapplet
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

class NewtonApplet(gnomeapplet.Applet):
    def __init__(self, applet, iid):
        self.__gobject_init__()
        self.applet = applet

        self.icon = gtk.gdk.pixbuf_new_from_file(os.path.join(PIXMAPS_DIR, "newton.svg"))
        self.config = Configuration()
        self.newt = Newton(self.config, 'applet')
        self.applet.connect("change-size", self.on_resize_panel)
        self.applet.connect("button-press-event", self.on_button_press)

        self.image = gtk.Image()
        self.scaled_icon = self.icon.scale_simple(16, 16,
                gtk.gdk.INTERP_BILINEAR)
        self.image.set_from_pixbuf(self.scaled_icon)
        self.applet.add(self.image)

        self.applet.show_all()
        
        applet.setup_menu_from_file(None, os.path.join(UI_DIR, "GNOME_NewtonApplet.xml"),
                None, [(_("Preferences"), self.on_preferences_activated),
                (_("About"), self.on_about_activated)])

    def on_resize_panel(self, widget, size):
        self.scaled_icon = self.icon.scale_simple(size - 8, size - 8,
                gtk.gdk.INTERP_BILINEAR)
        self.image.set_from_pixbuf(self.scaled_icon)

    def on_button_press(self, widget, event):
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            return False
        elif event.type == gtk.gdk.BUTTON_PRESS and event.button == 1:
            self.newt.toggle_window_visible()

    def on_preferences_activated(self, uicomponent=None, verb=None):
        self.newt.on_wiki_preferences_clicked(None)

    def on_about_activated(self, uicomponent=None, verb=None):
        self.newt.on_about_action(None)

def main():
    gobject.type_register(NewtonApplet)
    if len(sys.argv) == 2 and sys.argv[1] == "test":
        applet_window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        applet_window.set_title(NAME)
        applet_window.connect("destroy", gtk.main_quit)
        gnome.init(NAME, VERSION)
        applet = gnomeapplet.Applet()
        applet_factory(applet, None)
        applet.reparent(applet_window)
        applet_window.show_all()
        gtk.main()
    else:
        activate_factory()

def applet_factory(applet, iid):
    newtonapplet = NewtonApplet(applet, iid)
    newtonapplet.show_all()

def activate_factory():
    gnomeapplet.bonobo_factory("OAFIID:GNOME_NewtonApplet_Factory",
            gnomeapplet.Applet.__gtype__,
            NAME, VERSION, applet_factory)

