import gtk
from gettext import gettext as _

class Dialog(gtk.Dialog):
    def __init__(self, parent, title, buttons, default = None):
        gtk.Dialog.__init__(self, title, parent, gtk.DIALOG_DESTROY_WITH_PARENT | gtk.DIALOG_MODAL | gtk.DIALOG_NO_SEPARATOR)

        self.set_border_width(6)
        self.vbox.set_spacing(12)
        self.set_resizable(False)

        if buttons is not None:
            for stock, response in buttons:
                self.add_button(stock, response)

        if default is not None:
            self.set_default_response(default)
        else:
            self.set_default_response(buttons[-1][1])

    def get_button(self, index):
        buttons = self.action_area.get_children()
        return index < len(buttons) and buttons[index] or None

class Hig(Dialog):
    def __init__(self, parent, pritext, sectext, stockimage, buttons, default = None):
        """GNOME higified version of the Dialog object. Inherit
        from here if possible when you need a new dialog."""
        Dialog.__init__(self, parent, "", buttons, default)

        # hbox separating dialog image and contents
        hbox = gtk.HBox()
        hbox.set_spacing(12)
        hbox.set_border_width(6)
        self.vbox.pack_start(hbox)

        # set up image
        if stockimage is not None:
            image = gtk.Image()
            image.set_from_stock(stockimage, gtk.ICON_SIZE_DIALOG)
            image.set_alignment(0.5, 0)
            hbox.pack_start(image, False, False)

        # set up main content area
        self.contents = gtk.VBox()
        self.contents.set_spacing(10)
        hbox.pack_start(self.contents)

        label = gtk.Label()
        label.set_markup("<span size=\"larger\" weight=\"bold\">" + pritext + "</span>\n\n" + sectext)
        label.set_line_wrap(True)
        label.set_alignment(0, 0)
        label.set_selectable(True)
        self.contents.pack_start(label)

    def run(self):
        self.show_all()
        response = gtk.Dialog.run(self)
        self.destroy()
        return response

class Input(Hig):
    def __init__(self, parent, pritext, sectext, prefix=None):
        """HIG compliant input dialog with text entry."""
        Hig.__init__(
                self, parent, pritext, sectext, gtk.STOCK_DIALOG_QUESTION,
                [ [ gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL ],
                [gtk.STOCK_OK, gtk.RESPONSE_OK] ], gtk.RESPONSE_OK
        )

        self.entry = gtk.Entry()
        self.entry.set_activates_default(True)
        self.contents.pack_start(self.entry, False, False, 3)

        if prefix:
            self.entry.set_text(prefix)

    def get_input(self):
        return self.entry.get_text()

    def set_input(self, text):
        self.entry.set_text(text)
        self.entry.select_region(0, -1)

class FileOverwrite(Hig):
    def __init__(self, parent, file):
        """Overwrite a file dialog."""
        Hig.__init__(
            self, parent, "Overwrite existing file?",
            "The file '" + file + "' already exists. If you choose to overwrite the file, its contents will be lost.", gtk.STOCK_DIALOG_WARNING,
            [ [ gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL ], [ gtk.STOCK_OK, gtk.RESPONSE_OK ] ],
            gtk.RESPONSE_CANCEL
        )

    def run(self):
        return Hig.run(self) == gtk.RESPONSE_OK

class CustomConfirm(Hig):
    def __init__(self, parent, pritext, sectext, buttons, default=None):
        """HIG compliant confirmation dialog."""
        Hig.__init__(
            self, parent, pritext, sectext, gtk.STOCK_DIALOG_QUESTION, buttons, default 
        )

class YesNo(Hig):
    def __init__(self, parent, pritext, sectext, prefix=None):
        """HIG compliant Yes/No dialog"""
        Hig.__init__(
                self, parent, pritext, sectext, gtk.STOCK_DIALOG_QUESTION,
                [ [ gtk.STOCK_NO, gtk.RESPONSE_NO ],
                [gtk.STOCK_YES, gtk.RESPONSE_YES] ], gtk.RESPONSE_YES
        )

class Error(Hig):
    def __init__(self, parent, pritext, sectext):
        """HIG compliant error dialog."""
        Hig.__init__(
            self, parent, pritext, sectext, gtk.STOCK_DIALOG_ERROR,
            [ [ gtk.STOCK_OK, gtk.RESPONSE_OK ] ]
        )

class Info(Hig):
    def __init__(self, parent, pritext, sectext):
        """HIG compliant information dialog."""
        Hig.__init__(
            self, parent, pritext, sectext, gtk.STOCK_DIALOG_INFO,
            [ [ gtk.STOCK_OK, gtk.RESPONSE_OK ] ]
        )

class Confirm(Hig):
    def __init__(self, parent, pritext, sectext):
        """HIG compliant confirmation dialog."""
        Hig.__init__(
            self, parent, pritext, sectext, gtk.STOCK_DIALOG_QUESTION,
            [ [gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL], [ gtk.STOCK_OK, gtk.RESPONSE_OK ] ]
        )

