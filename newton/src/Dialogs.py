import os
import gtk
import gtk.glade

from newton import GLADE_DIR
import Alerts
import NewtonStock

from gettext import gettext as _

class ImageInsert(object):
    def __init__(self):
        xml = gtk.glade.XML(os.path.join(GLADE_DIR, "newton.glade"), "insert_image_dialog")
        self.dlg = xml.get_widget('insert_image_dialog')

        # get a whole whack of widgets..
        self.location_entry = xml.get_widget('location_entry')
        browse_button = xml.get_widget('browse_button')
        float_left_image = xml.get_widget('float_left_image')
        self.float_left_radiobutton = xml.get_widget('float_left_radiobutton')
        center_image = xml.get_widget('center_image')
        self.center_radiobutton = xml.get_widget('center_radiobutton')
        float_right_image = xml.get_widget('float_right_image')
        self.float_right_radiobutton = xml.get_widget('float_right_radiobutton')
        self.actual_size_radiobutton = xml.get_widget('actual_size_radiobutton')
        self.scaled_size_radiobutton = xml.get_widget('scaled_size_radiobutton')
        self.custom_size_radiobutton = xml.get_widget('custom_size_radiobutton')
        scaled_size_vbox = xml.get_widget('scaled_size_vbox')
        custom_size_vbox = xml.get_widget('custom_size_vbox')
        self.scaled_width_entry = xml.get_widget('scaled_width_entry')
        self.custom_width_entry = xml.get_widget('custom_width_entry')
        self.custom_height_entry = xml.get_widget('custom_height_entry')
        self.caption_entry = xml.get_widget('caption_entry')

        self.location_entry.set_activates_default(True)
        self.location_entry.set_text("http://")
        self.location_entry.select_region(0, -1)

        scaled_size_vbox.set_sensitive(False)
        custom_size_vbox.set_sensitive(False)

        browse_button.connect('clicked', self.on_browse_button_clicked)

        float_left_image.set_from_stock(NewtonStock.STOCK_FLOAT_LEFT, gtk.ICON_SIZE_DIALOG)
        float_right_image.set_from_stock(NewtonStock.STOCK_FLOAT_RIGHT, gtk.ICON_SIZE_DIALOG)
        center_image.set_from_stock(NewtonStock.STOCK_IMAGE_CENTER, gtk.ICON_SIZE_DIALOG)

        self.scaled_size_radiobutton.connect("toggled", self.on_scale_radio_toggled, scaled_size_vbox)
        self.custom_size_radiobutton.connect("toggled", self.on_custom_radio_toggled, custom_size_vbox)

    def hide(self):
        self.dlg.hide()

    def run(self):
        return self.dlg.run()

    def on_browse_button_clicked(self, button):
        filter = gtk.FileFilter()
        patterns = ['*.png', '*.jpg', '*.gif', '*.jpeg']
        for pattern in patterns:
            filter.add_pattern(pattern)
        filter.set_name("Image files")

        file_dialog = gtk.FileChooserDialog("Choose an image file...", 
                self.dlg, 
                gtk.FILE_CHOOSER_ACTION_OPEN,
                (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                 gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        file_dialog.add_filter(filter)

        response = file_dialog.run()
        if response == gtk.RESPONSE_OK:
            self.location_entry.set_text(file_dialog.get_filename())
        file_dialog.hide()

    def on_scale_radio_toggled(self, radio, vbox):
        vbox.set_sensitive(radio.get_active())
        if radio.get_active():
            self.scaled_width_entry.grab_focus()

    def on_custom_radio_toggled(self, radio, vbox):
        vbox.set_sensitive(radio.get_active())
        if radio.get_active():
            self.custom_width_entry.grab_focus()

    def get_location(self):
        return self.location_entry.get_text()

    def get_position(self):
        if self.float_left_radiobutton.get_active():
            return "float-left"
        elif self.float_right_radiobutton.get_active():
            return "float-right"
        else:
            return "center"

    def get_caption(self):
        return self.caption_entry.get_text()

    def validate_size(self):
        if self.scaled_size_radiobutton.get_active():
            width = self.scaled_width_entry.get_text()
            if not len(width):
                return False
            for char in width:
                if not char.isdigit():
                    return False
        elif self.custom_size_radiobutton.get_active():
            width = self.custom_width_entry.get_text()
            if not len(width):
                return False
            for char in width:
                if not char.isdigit():
                    return False
            height = self.custom_height_entry.get_text()
            if not len(height):
                return False
            for char in height:
                if not char.isdigit():
                    return False
        return True

    def get_size(self):
        if self.actual_size_radiobutton.get_active():
            return ''
        elif self.scaled_size_radiobutton.get_active():
            return "?%s" % self.scaled_width_entry.get_text()
        else:
            return "?%sx%s" % (self.custom_width_entry.get_text(), self.custom_height_entry.get_text())

class NewPageDialog(gtk.Dialog):
    def __init__(self, parentname):
        """Dialog shown when the user is going to add a new page to the
        wiki."""
        gtk.Dialog.__init__(self, _('New Wiki Page'))
        self.parentname = parentname
        self.hbox = gtk.HBox(False, 8)
        self.table = gtk.Table(3, 2, False)
        self.label1 = gtk.Label(_('New page title'))
        self.entry = gtk.Entry()
        self.image = gtk.Image()
        self.image.set_from_stock(gtk.STOCK_DIALOG_QUESTION, gtk.ICON_SIZE_DIALOG)
        self.set_has_separator(False)

        self.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
        self.add_button(gtk.STOCK_OK, gtk.RESPONSE_OK)
        self.set_default_response(gtk.RESPONSE_OK)
        self.entry.set_activates_default(True)

        self.hbox.set_border_width(8)
        self.vbox.pack_start(self.hbox, False, False, 0)
        self.hbox.pack_start(self.image, gtk.SHRINK)
        
        self.table.set_row_spacings(4)
        self.table.set_col_spacings(4)
        self.hbox.pack_start(self.table)

        self.table.attach(self.label1, 0, 1, 0, 1)
        self.table.attach(self.entry, 1, 2, 0 ,1)
        self.label1.set_mnemonic_widget(self.entry)

        # if current node is category, ask to append or not
        if self.parentname:
            check_hbox = gtk.HBox(False)
            check_hbox.pack_start(gtk.Label(), True, True)
            self.checkbutton = gtk.CheckButton(_('Add to category %s') % parentname)
            self.checkbutton.set_active(True)
            self.checkbutton.set_alignment(0.5, 0.1)
            check_hbox.pack_start(self.checkbutton, False)
            self.vbox.pack_start(check_hbox)

        self.set_resizable(False)
        self.show_all()

    def get_entry(self):
        """Get the path in the dialog."""
        return self.entry.get_text()

    def set_entry(self, text):
        """Set the path in the dialog."""
        self.entry.set_text(text)
        self.entry.select_region(-1, -1)

    def get_checked(self):
        """Get whether the new page is child of parentnode."""
        if self.parentname:
            return self.checkbutton.get_active()
        else:
            return None


class NewCategoryDialog(gtk.Dialog):
    def __init__(self, parentname):
        """Dialog shown when the user is going to add a new category to the
        wiki."""
        gtk.Dialog.__init__(self, _('New Wiki Category'))
        self.parentname = parentname
        self.hbox = gtk.HBox(False, 8)
        self.table = gtk.Table(3, 2, False)
        self.label1 = gtk.Label(_('New category title'))
        self.entry = gtk.Entry()
        self.image = gtk.Image()
        self.image.set_from_stock(gtk.STOCK_DIALOG_QUESTION, gtk.ICON_SIZE_DIALOG)
        self.set_has_separator(False)

        self.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
        self.add_button(gtk.STOCK_OK, gtk.RESPONSE_OK)
        self.set_default_response(gtk.RESPONSE_OK)
        self.entry.set_activates_default(True)

        self.hbox.set_border_width(8)
        self.vbox.pack_start(self.hbox, False, False, 0)
        self.hbox.pack_start(self.image, gtk.SHRINK)
        
        self.table.set_row_spacings(4)
        self.table.set_col_spacings(4)
        self.hbox.pack_start(self.table)

        self.table.attach(self.label1, 0, 1, 0, 1)
        self.table.attach(self.entry, 1, 2, 0 ,1)
        self.label1.set_mnemonic_widget(self.entry)

        # if current node is category, ask to append or not
        if parentname:
            check_hbox = gtk.HBox(False)
            check_hbox.pack_start(gtk.Label(), True, True)
            self.checkbutton = gtk.CheckButton(_('Add to category %s') % parentname)
            self.checkbutton.set_active(True)
            self.checkbutton.set_alignment(0.5, 0.1)
            check_hbox.pack_start(self.checkbutton, False)
            self.vbox.pack_start(check_hbox)

        self.set_resizable(False)
        self.show_all()

    def get_entry(self):
        """Get the path in the dialog."""
        return self.entry.get_text()

    def set_entry(self, text):
        """Set the path in the dialog."""
        self.entry.set_text(text)
        self.entry.select_region(-1, -1)

    def get_checked(self):
        """Get whether the new category is child of parentnode."""
        if self.parentname:
            return self.checkbutton.get_active()
        else:
            return None
