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

import gtk, gtk.gdk
from newton import PIXMAPS_DIR

STOCK_APPLICATION               = "newton-application"
STOCK_EXPORT                    = "newton-export"
STOCK_DATE                      = "newton-date"
STOCK_TIME                      = "newton-time"
STOCK_WEB                       = "newton-web"
STOCK_WEB_LINK                  = 'newton-web-link'
STOCK_EMAIL_LINK                = 'newton-email-link'
STOCK_MEDIA_LINK                = 'newton-media-link'
STOCK_IMAGE_LINK                = 'newton-image-link'
STOCK_FLOAT_LEFT                = 'newton-float-left'
STOCK_FLOAT_RIGHT               = 'newton-float-right'
STOCK_IMAGE_CENTER              = 'newton-image-center'
STOCK_CATEGORY                  = 'newton-category'
STOCK_PAGE                      = 'newton-page'

class IconFactory(gtk.IconFactory):

    def __init__(self, widget):
        """Create an IconFactory that houses the custom Newton
        icons."""
        gtk.IconFactory.__init__(self)
        self.add_default()

        icons = {
            STOCK_APPLICATION       : "newton.svg",
            STOCK_EXPORT            : "export.svg",
            STOCK_DATE              : "calendar.svg",
            STOCK_TIME              : "clock.svg",
            STOCK_WEB               : "web.svg",
            STOCK_WEB_LINK          : "web_link.svg",
            STOCK_EMAIL_LINK        : "email_link.svg",
            STOCK_MEDIA_LINK        : "media_link.svg",
            STOCK_IMAGE_LINK        : "image_link.svg",
            STOCK_FLOAT_LEFT        : 'float-left.svg',
            STOCK_FLOAT_RIGHT       : "float-right.svg",
            STOCK_IMAGE_CENTER      : "image-center.svg",
            STOCK_CATEGORY          : "category.svg",
            STOCK_PAGE              : "page.svg"
        }

        for id, filename in icons.items():
            iconset = gtk.IconSet(gtk.gdk.pixbuf_new_from_file(PIXMAPS_DIR + '/' + filename))
            self.add(id, iconset)

