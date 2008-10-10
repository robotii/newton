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

import os.path
import gconf

DIR_NEWTON = "/apps/newton"

KEY_WINDOW_MAXIMIZED = "%s/general/window_maximized" % DIR_NEWTON
KEY_WINDOW_POS_X = "%s/general/window_position_x" % DIR_NEWTON
KEY_WINDOW_POS_Y = "%s/general/window_position_y" % DIR_NEWTON
KEY_WINDOW_SIZE_X = "%s/general/window_size_x" % DIR_NEWTON
KEY_WINDOW_SIZE_Y = "%s/general/window_size_y" % DIR_NEWTON
KEY_HPANED_POS = "%s/general/hpaned_position" % DIR_NEWTON
KEY_SHOW_TREE_VIEW = "%s/general/show_treeview" % DIR_NEWTON
KEY_IGNORE_CAMELCASE = "%s/behaviour/ignore_camelcase" % DIR_NEWTON
KEY_ENABLE_SPELL_CHECK = "%s/behaviour/enable_spell_check" % DIR_NEWTON
KEY_STYLESHEET = "%s/appearance/stylesheet" % DIR_NEWTON

class Configuration(object):
    def __init__(self):
        self.client = gconf.client_get_default()
        if not self.client.dir_exists(DIR_NEWTON):
            self.client.add_dir(DIR_NEWTON, gconf.CLIENT_PRELOAD_RECURSIVE)
            self.set_bool(KEY_WINDOW_MAXIMIZED, False)
            self.set_int(KEY_WINDOW_POS_X, 200)
            self.set_int(KEY_WINDOW_POS_Y, 120)
            self.set_int(KEY_WINDOW_SIZE_X, 750)
            self.set_int(KEY_WINDOW_SIZE_Y, 500)
            self.set_int(KEY_HPANED_POS, 150)
            self.set_bool(KEY_SHOW_TREE_VIEW, 1)
            self.set_bool(KEY_IGNORE_CAMELCASE, 0)
            self.set_bool(KEY_ENABLE_SPELL_CHECK, 1)
            self.set_string(KEY_STYLESHEET, "Blue")
        self.client.add_dir(DIR_NEWTON, gconf.CLIENT_PRELOAD_RECURSIVE)
        self.load_config()

    def load_config(self):
        self.window_maximized = self.get_bool(KEY_WINDOW_MAXIMIZED, False)
        self.window_position_x = self.get_int(KEY_WINDOW_POS_X, 200)
        self.window_position_y = self.get_int(KEY_WINDOW_POS_Y, 120)
        self.window_size_x = self.get_int(KEY_WINDOW_SIZE_X, 750)
        self.window_size_y = self.get_int(KEY_WINDOW_SIZE_Y, 500)
        self.hpaned_position = self.get_int(KEY_HPANED_POS, 150)
        self.show_treeview = self.get_bool(KEY_SHOW_TREE_VIEW, 1)
        self.ignore_camelcase = self.get_bool(KEY_IGNORE_CAMELCASE, 0)
        self.enable_spell_check = self.get_bool(KEY_ENABLE_SPELL_CHECK, 1)
        self.stylesheet = self.get_string(KEY_STYLESHEET, "Blue")
        
    def get_string(self, value, defval=''):
        """Get a string value from gconf."""
        v = self.client.get_string(value)
        if self.client.get(value):
            return v
        else:
            return defval

    def get_bool(self, key, defval=0):
        """Get a boolean value from gconf."""
        v = self.client.get_bool(key)
        if self.client.get(key):
            return v
        else:
            return defval

    def get_int(self, key, defval=0):
        """Get an integer value from gconf."""
        v = self.client.get_int(key)
        if self.client.get(key):
            return v
        else:
            return defval

    def set_int(self, key, value):
        """Set an integer value in gconf."""
        self.client.set_int(key, value)

    def set_bool(self, key, value):
        """Set a boolean value in gconf."""
        self.client.set_bool(key, value)

    def set_string(self, key, value):
        """Set a string value in gconf."""
        self.client.set_string(key, value)

            

