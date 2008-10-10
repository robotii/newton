# Copyright (c) 2005 Dennis Craven
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

import os, sys
import re
import gtk
import gtk.glade
import gtkmozembed
import gtksourceview
import gtkspell
import gnome
import gobject
import pango
import locale
import xml.dom.minidom

from datetime import date, datetime
from shutil import copy, move
from gettext import gettext as _

from newton import NAME, VERSION, GLADE_DIR, PIXMAPS_DIR, LOCALE_DIR, WIKI_DIR, WIKI_DATA, WIKI_MEDIA, WIKI_STYLES
from NewtonWikiEng import WikiEngine
from NewtonConfig import KEY_WINDOW_POS_X, KEY_WINDOW_POS_Y, KEY_WINDOW_SIZE_X, KEY_WINDOW_SIZE_Y, KEY_HPANED_POS, KEY_IGNORE_CAMELCASE \
        ,KEY_STYLESHEET, KEY_ENABLE_SPELL_CHECK, KEY_WINDOW_MAXIMIZED
import NewtonUtils
import NewtonStock 
import Alerts, Dialogs

gtk.glade.bindtextdomain(NAME.lower(), LOCALE_DIR)

class NewtonGui:
    def __init__(self):
        self.gladeXml = gtk.glade.XML(os.path.join(GLADE_DIR, "newton.glade"), "main_window")
        self.prefsXml = gtk.glade.XML(os.path.join(GLADE_DIR, "preferences.glade"))
        self.icon = gtk.gdk.pixbuf_new_from_file(os.path.join(PIXMAPS_DIR, "newton.svg"))

class Newton(NewtonGui):
    def __init__(self, config, method):
        NewtonGui.__init__(self)
        self.config = config
        self.method = method
        self.spellcheck_bug = False

        self.topWindow = self.create_top_window()
        self.preferences = self.create_prefs_dialog()
        self.restore_window_state()
        self.state = "browser"

        self.display = gtk.gdk.display_manager_get().get_default_display()
        self.clipboard = gtk.Clipboard(self.display, 'CLIPBOARD')

    def create_top_window(self):
        topWindow = self.gladeXml.get_widget("main_window")
        topWindow.set_icon(self.icon)
        topWindow.connect("delete-event", self.on_main_window_delete)
        topWindow.connect("key-press-event", self.on_key_press_event)
        topWindow.connect('window-state-event', self.on_top_window_state_event)


        self.icons = NewtonStock.IconFactory(self)

        # UI Actions
        window_actions = [
            ('FileMenu', None, _('_File')),
            ('NewPage', gtk.STOCK_NEW, _('New Page'), '<control>N', _('Create a new wiki page'), 'on_new_page_action'),
            ('NewCategory', gtk.STOCK_NEW, _('New Category'), '<control><alt>N', _('Create a new category'), 'on_new_category_action'),
            ('Backup', gtk.STOCK_HARDDISK, _('Backup All Data'), None, _('Backup all of your wiki data'), 'on_backup_data_action'),
            ('Edit', gtk.STOCK_EDIT, _('Edit Page'), '<control>E', _('Edit the current wiki page'), 'on_edit_action'),
            ('CancelEdit', gtk.STOCK_CANCEL, _('Cancel Edit'), '<control>Z', _('Cancel edit of current wiki page'), 'on_cancel_edit_action'),
            ('Find', gtk.STOCK_FIND, _('Find pattern'), '<control>F', _('Find text in wiki'), 'on_search_button_clicked'),
            ('Delete', gtk.STOCK_DELETE, _('Delete'), '<control>D', _('Delete the current wiki page or category'), 'on_delete_action'),
            ('Rename', None, _('Rename'), None, _('Rename the current wiki page or category'), 'on_rename_action'),
            ('ExportMenu', NewtonStock.STOCK_EXPORT, _('Export to...')),
            ('ExportHTML', NewtonStock.STOCK_WEB, 'HTML', None, _('Export to HTML file'), 'on_export_html_activate'),
            ('EditMenu', None, _('_Edit')),
            ('Copy', gtk.STOCK_COPY, _('Copy'), '<control>C', _('Copy to clipboard'), 'on_copy_action'), 
            ('Cut', gtk.STOCK_CUT, _('Cut'), '<control>X', _('Cut to clipboard'), 'on_cut_action'), 
            ('Paste', gtk.STOCK_PASTE, _('Paste'), '<control>V', _('Paste from clipboard'), 'on_paste_action'), 
            ('Save', gtk.STOCK_SAVE, _('Save Page'), '<control>S', _('Save the current wiki page'), 'on_save_action'),
            ('Preferences', gtk.STOCK_PREFERENCES, _('Preferences'), '<control>P', _('Edit preferences'), 'on_preferences_action'),
            ('GoMenu', None, _('_Go')),
            ('Back', gtk.STOCK_GO_BACK, _('Back'), None, _('Go back in history'), 'on_back_action'),
            ('Forward', gtk.STOCK_GO_FORWARD, _('Forward'), None, _('Go forward in history'), 'on_forward_action'),
            ('Home', gtk.STOCK_HOME, _("Home"), '<control>H', _('Go to NewtonHome'), 'on_home_action'),
            ('Refresh', gtk.STOCK_REFRESH, _('Refresh'), '<control>R', _('Refresh current page'), 'on_reload_action'),
            ('HelpMenu', None, _('_Help')),
            ('About', gtk.STOCK_ABOUT, _('About Newton'), None, _('About Newton'), 'on_about_action'),
            ('Bold', gtk.STOCK_BOLD, _('Bold'), None, _('Insert bolded text'), 'on_bold_action'),
            ('Italic', gtk.STOCK_ITALIC, _('Italic'), '<control>I', _('Insert italic text'), 'on_italic_action'),
            ('Underline', gtk.STOCK_UNDERLINE, _('Underline'), '<control>U', _('Insert underlined text'), 'on_underline_action'),
            ('Strikethrough', gtk.STOCK_STRIKETHROUGH, _('Strikethrough'), '<control>T', _('Insert strikethrough text'), 'on_strikethrough_action'),
            ('WebLink', NewtonStock.STOCK_WEB_LINK, _('Insert Web Link'), None, _('Insert link to a web page'), 'on_web_link_action'),
            ('EmailLink', NewtonStock.STOCK_EMAIL_LINK, _('Insert Email Link'), None, _('Insert link to an email address'), 'on_email_link_action'),
            ('MediaLink', NewtonStock.STOCK_MEDIA_LINK, _('Insert Media Link'), None, _('Insert link to media file'), 'on_media_link_action'),
            ('ImageLink', NewtonStock.STOCK_IMAGE_LINK, _('Insert Image Link'), None, _('Embed local or remote image'), 'on_image_link_action'),
            ('Date', NewtonStock.STOCK_DATE, _('Insert Date'), None, _('Insert the current date'), 'on_date_action'),
            ('Time', NewtonStock.STOCK_TIME, _('Insert Time'), None, _('Insert the current time'), 'on_time_action'),
            ('Website', NewtonStock.STOCK_WEB, _('Newton Homepage'), None, _('Go to the Newton Homepage'), 'on_website_activate')
        ]

        self.ag = gtk.ActionGroup('NewtonActions')
        actions = self.fix_actions(window_actions, self)
        self.ag.add_actions(actions)
        self.ui = gtk.UIManager()
        self.ui.insert_action_group(self.ag, 0)
        self.ui.add_ui_from_file(os.path.join(GLADE_DIR, 'newtonui.xml'))
        topWindow.add_accel_group(self.ui.get_accel_group())

        self.menudock = self.gladeXml.get_widget("bonobodockitem1")
        self.tooldock = self.gladeXml.get_widget("bonobodockitem2")
        self.menubar = self.ui.get_widget('/Menubar')
        self.toolbar = self.ui.get_widget('/Toolbar')
        self.toolbar.set_style(gtk.TOOLBAR_ICONS)
        self.menudock.add(self.menubar)
        self.tooldock.add(self.toolbar)

        tree_popup = self.ui.get_widget('/TreePopup')
        self.treeview = WikiTreeView(tree_popup)
        self.treeview.connect("cursor-changed", self.on_tree_cursor_changed)

        # Create and add the search button and entry.
        self.search_widget = gtk.ToolItem()
        hbox = gtk.HBox(False, 3)
        self.search_button = gtk.Button(stock=gtk.STOCK_FIND)
        self.search_button.unset_flags(gtk.CAN_FOCUS)
        self.search_button.set_relief(gtk.RELIEF_NONE)
        self.search_entry = gtk.Entry()
        self.search_entry.set_width_chars(10)
        hbox.pack_start(self.search_button)
        hbox.pack_start(self.search_entry)
        self.search_widget.add(hbox)
        self.toolbar.insert(gtk.SeparatorToolItem(), -1)
        self.toolbar.show_all()
        self.toolbar.insert(self.search_widget, -1)
        self.search_button.connect("clicked", self.on_search_button_clicked)
        self.search_entry.connect("activate", self.on_search_widget_activate)
        self.search_widget.show_all()
        self.search_entry.hide()

        self.editor = EditWidget(self.ui, self.config, self.method)
        self.editor.connect("wiki-save-clicked", self.on_wiki_save_clicked)
        self.editor.connect("wiki-cancel-clicked", self.on_wiki_cancel_clicked)
        self.editor.connect("spellcheck-bug", self.on_spell_enable_fail)

        self.browser = BrowserWidget(self.treeview, self.ui, self.config, self.method)
        self.browser.connect("wiki-location-changed", self.on_wiki_location_changed)
        self.browser.connect("wiki-edit-clicked", self.on_wiki_edit_clicked)
        self.browser.connect("wiki-new-clicked", self.on_wiki_new_clicked)
        self.browser.connect("wiki-new-from-link", self.on_wiki_new_from_link)
        self.browser.connect("wiki-delete-clicked", self.on_wiki_delete_clicked)
        self.browser.connect("wiki-link-clicked", self.on_wiki_link_clicked)
        self.browser.connect("show", self.browser.on_browser_widget_show)
        self.browser.connect("wiki-link-message", self.on_wiki_link_message)

        # try to load tree via XML file, if fail, do old fashioned way
        if not self.treeview.load_tree_structure():
            self.treeview.populate_wiki_tree(WIKI_DATA)
        self.browser.rebuild_completion_list()

        self.statusbar = self.gladeXml.get_widget("appbar1")
        self.style_combobox = None
        
        treeview_scroller = self.gladeXml.get_widget("treeview_scroller")
        self.hpaned = self.gladeXml.get_widget("hpaned1")
        treeview_scroller.add(self.treeview)
        browser_vbox = self.gladeXml.get_widget("browser_vbox")
        browser_vbox.pack_start(self.browser)
        browser_vbox.pack_start(self.editor)

        self.ag.get_action("Paste").set_sensitive(False)

        return topWindow

    def create_prefs_dialog(self):
        prefs = self.prefsXml.get_widget("preferences_dialog")
        prefs.set_resizable(False)

        camelcase_checkbutton = self.prefsXml.get_widget("camelcase_checkbutton")
        camelcase_checkbutton.set_active(self.config.get_bool(KEY_IGNORE_CAMELCASE, False))

        if not self.spellcheck_bug:
            check_vbox = self.prefsXml.get_widget('vbox128')
            spell_checkbutton = gtk.CheckButton('Enable spell checking')
            spell_checkbutton.set_active(self.config.get_bool(KEY_ENABLE_SPELL_CHECK, True))
            check_vbox.pack_start(spell_checkbutton)
            spell_checkbutton.connect("toggled", self.on_spell_checkbutton_toggled)
            check_vbox.show_all()
        # spell_checkbutton = self.prefsXml.get_widget("spell_checkbutton")
        # spell_checkbutton.set_active(self.config.get_bool(KEY_ENABLE_SPELL_CHECK, True))

        if self.style_combobox:
            self.style_combobox.destroy()

        combo_hbox = self.prefsXml.get_widget("combo_hbox")
        self.style_combobox = gtk.combo_box_new_text()
        combo_hbox.pack_start(self.style_combobox)
        styles = os.listdir(WIKI_STYLES)
        css = []
        for style in styles:
            if style.endswith(".css"):
                css.append(style)
                self.style_combobox.append_text(style[:style.rfind(".")])
        try:
            self.style_combobox.set_active(styles.index(self.config.get_string(KEY_STYLESHEET, 'Blue') + ".css"))
        except ValueError:
            self.config.set_string(KEY_STYLESHEET, 'Blue')
            self.style_combobox.set_active(css.index('Blue.css'))
        self.style_combobox.show_all()

        camelcase_checkbutton.connect("toggled", self.on_camelcase_checkbutton_toggled)
        self.style_combobox.connect("changed", self.on_style_combobox_changed)

        return prefs

    def on_website_activate(self, action):
        gnome.url_show('http://newton.sourceforge.net')

    def on_backup_data_action(self, action):
        self.treeview.backup_data()

    def on_top_window_state_event(self, window, event):
        if event.type == gtk.gdk.WINDOW_STATE:
            if not bool(event.new_window_state & gtk.gdk.WINDOW_STATE_WITHDRAWN):
                self.config.set_bool(KEY_WINDOW_MAXIMIZED, bool(event.new_window_state & gtk.gdk.WINDOW_STATE_MAXIMIZED))
                if self.config.get_bool(KEY_WINDOW_MAXIMIZED, False) == False:
                    self.topWindow.resize(self.config.get_int(KEY_WINDOW_SIZE_X, 750), self.config.get_int(KEY_WINDOW_SIZE_Y, 500))
                    self.topWindow.move(self.config.get_int(KEY_WINDOW_POS_X, 200), self.config.get_int(KEY_WINDOW_POS_Y, 120))

    def on_spell_enable_fail(self, str1, str2):
        self.spellcheck_bug = True

    def fix_actions(self, actions, instance):
        "Helper function to map methods to an instance"
        retval = []
        for i in range(len(actions)):
            curr = actions[i]
            if len(curr) > 5:
                curr = list(curr)
                curr[5] = getattr(instance, curr[5])
                curr = tuple(curr)
            retval.append(curr)
        return retval

    def on_search_button_clicked(self, button):
        """Toggles the search entry field's visibility."""
        if self.search_entry.get_property('visible'):
            self.search_entry.hide()
        else:
            self.search_entry.show()
            self.search_entry.grab_focus()

    def on_search_widget_activate(self, obj):
        """Initiate a search for the pattern in the search entry."""
        pattern = self.search_entry.get_text()
        self.search_entry.hide()
        self.browser.display_search_results(pattern)

    def on_copy_action(self, widget):
        copied = self.editor.copy_text_to_clipboard(self.clipboard)
        if copied:
            self.ag.get_action("Paste").set_sensitive(True)

    def on_cut_action(self, widget):
        cut = self.editor.cut_text_to_clipboard(self.clipboard)
        if cut:
            self.ag.get_action("Paste").set_sensitive(True)

    def on_paste_action(self, widget):
        self.editor.paste_text_from_clipboard(self.clipboard)

    def on_web_link_action(self, obj):
        """User wants to insert a web link in editor."""
        self.editor.web_link_insert_clicked()

    def on_email_link_action(self, obj):
        """User wants to insert a email link in editor."""
        self.editor.email_link_insert_clicked()

    def on_media_link_action(self, obj):
        """User wants to insert a media link in editor."""
        self.editor.media_link_insert_clicked()

    def on_image_link_action(self, obj):
        """User wants to insert an image link in editor."""
        self.editor.image_link_insert_clicked()

    def on_bold_action(self, action):
        """User wants to insert bolded text."""
        self.editor.bold_insert_clicked()

    def on_bold_accel_action(self, action):
        """User bolds text via the key accelerator"""
        self.editor.bold_accel_action()

    def on_italic_action(self, obj):
        """User wants to insert italicized text."""
        self.editor.italic_insert_clicked()

    def on_underline_action(self, obj):
        """User wants to insert underlined text."""
        self.editor.underline_insert_clicked()

    def on_strikethrough_action(self, obj):
        """User wants to insert strikethrough text."""
        self.editor.strikethrough_insert_clicked()

    def on_date_action(self, obj):
        """User wants to insert date in editor."""
        self.editor.insert_current_date()

    def on_time_action(self, obj):
        """User wants to insert time in editor."""
        self.editor.insert_current_time()

    def on_new_page_action(self, obj):
        """New page creation action activated."""
        (model, current_iter) = self.treeview.get_selection().get_selected()
        if model.get_value(current_iter, 2) == 'page':
            parentiter = model.iter_parent(current_iter)
        elif model.get_value(current_iter, 2) == 'category':
            parentiter = current_iter

        if parentiter:
            self.on_wiki_new_clicked(None, self.treeview.get_full_node_name(parentiter))
        else:
            self.on_wiki_new_clicked(None, None)

    def on_new_category_action(self, obj):
        (model, current_iter) = self.treeview.get_selection().get_selected()
        if model.get_value(current_iter, 2) == 'page':
            dialog = Dialogs.NewCategoryDialog(None)
        elif model.get_value(current_iter, 2) == 'category':
            dialog = Dialogs.NewCategoryDialog(model.get_value(current_iter, 1))
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            newcat = dialog.get_entry()
            if len(newcat):
                if dialog.get_checked():
                    new_nodename = '%s::%s' % (self.treeview.get_full_node_name(current_iter), newcat)
                    if not new_nodename in self.treeview.treeview_nodes():
                        self.treeview.add_wiki_node(newcat, 'category', current_iter)
                        # create the actual dir on filesystem
                        NewtonUtils.make_path(os.path.join(NewtonUtils.path_from_nodename(self.treeview.get_full_node_name(current_iter)), newcat))
                    else:
                        dlg = Alerts.Error(None, _("The category %s already exists") % new_nodename,
                                _("Please choose another name for the new category or edit the existing instance."))
                        dlg.run()
                        dlg.hide()
                else:
                    selected_node = self.treeview.get_full_node_name(current_iter)
                    if selected_node.count('::'):
                        new_nodename = '%s::%s' % (selected_node[:selected_node.rfind('::')], newcat)
                    else:
                        new_nodename = newcat
                    if not new_nodename in self.treeview.treeview_nodes():
                        self.treeview.add_wiki_node(newcat, 'category', None)
                        # create the actual dir on filesystem
                        NewtonUtils.make_path(NewtonUtils.path_from_nodename(newcat))
                    else:
                        dlg = Alerts.Error(None, _("The category %s already exists") % new_nodename,
                                _("Please choose another name for the new category or edit the existing instance."))
                        dlg.run()
                        dlg.hide()
        dialog.destroy()
        self.browser.rebuild_completion_list()
                
    def on_edit_action(self, obj):
        """Edit page action activated."""
        self.browser.on_edit_button_clicked(None)

    def on_cancel_edit_action(self, obj):
        """User cancels while editing a wiki page"""
        self.editor.on_cancel_button_clicked(None)

    def on_save_action(self, obj):
        """Save page action activated."""
        self.editor.on_save_button_clicked(None)

    def on_delete_action(self, obj):
        """Delete page action activated."""
        self.browser.on_delete_button_clicked(None)

    def on_rename_action(self, obj):
        """Rename page action activated."""
        #FIXME: make sure new name is unique!
        (model, iter) = self.treeview.get_selection().get_selected()
        dialog = Alerts.Input(None, _("Enter the new page name."), 
                _("The pages that link to this page can be updated automatically."))
        fix_links = gtk.CheckButton('_Fix links from other pages.')
        fix_links.set_active(True)
        hbox = gtk.HBox(False)
        hbox.pack_start(gtk.Label())
        hbox.pack_start(fix_links, False, False, 3)
        dialog.contents.pack_start(hbox)
        dialog.set_input(model[iter][1])
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            input = dialog.get_input()
            current_title = self.treeview.selected_wiki_page()
            if not len(input) or current_title == input:
                dialog.hide()
                return

            # see if the parent of the current node already has a child with this name
            conflict = False
            sibling = model.iter_children(model.iter_parent(iter))
            while sibling:
                if model[sibling][1] == input:
                    conflict = True
                    break
                sibling = model.iter_next(sibling)
            if conflict:
                dialog.hide()
                error = Alerts.Error(None, _("Page or Category Name Conflict"),
                        _('A page or category with the name "%s" already exists. Please choose a new name.' % input)).run()
                return

            old_nodename = self.treeview.get_full_node_name(iter)
            new_nodename = self.treeview.rename_current_page(input)
            try:
                move(NewtonUtils.path_from_nodename(current_title), NewtonUtils.path_from_nodename(new_nodename))
            except:
                # FIXME: Should a dialog appear here reporting failure?
                dialog.hide()
                return
            self.treeview.select_wiki_page(new_nodename)

            if fix_links.get_active():
                (model, iter) = self.treeview.get_selection().get_selected()
                self.treeview.rename_all_links(old_nodename, new_nodename)
                self.browser.on_refresh_button_clicked(None)
        dialog.hide()
        self.browser.rebuild_completion_list()


    def on_back_action(self, obj):
        self.browser.on_back_button_clicked(None)

    def on_forward_action(self, obj):
        self.browser.on_forward_button_clicked(None)

    def on_home_action(self, obj):
        self.browser.on_home_button_clicked(None)

    def on_reload_action(self, obj):
        self.browser.on_refresh_button_clicked(None)

    def on_preferences_action(self, obj):
        self.on_wiki_preferences_clicked(None)

    def on_export_html_activate(self, obj):
        self.browser.on_export_html_activate()

    def on_about_action(self, obj):
        """Displays the about box."""
        pixbuf = gtk.gdk.pixbuf_new_from_file(os.path.join(PIXMAPS_DIR, "newton.svg"))
        pixbuf = pixbuf.scale_simple(120, 120, gtk.gdk.INTERP_BILINEAR)

        gnome.ui.About(NAME,
                        VERSION,
                        ('Copyright 2005 Dennis Craven'),
                        ('A Personal Wiki applet for the GNOME2 Desktop Environment.'),
                        ['Dennis Craven <dcraven@gmail.com>'],
                        [''],
                        '',
                        pixbuf).show()

    def on_key_press_event(self, obj, event):
        if event.keyval == gtk.keysyms.Escape and not self.method == 'window':
            self.toggle_window_visible()
            return True
        elif event.keyval == gtk.keysyms.l and self.browser.get_property('visible'):
            if (event.state & gtk.gdk.CONTROL_MASK):
                self.browser.activate_address_bar()
                return True
        elif event.keyval == gtk.keysyms.slash and self.browser.get_property('visible'):
            self.browser.activate_address_bar()
            return True
        return False

    def on_tree_cursor_changed(self, treeview):
        (model, iter) = self.treeview.get_selection().get_selected()
        if model.get_value(iter, 2) == 'page':
            self.browser.navigate_to_wiki_page(self.treeview.get_full_node_name(iter))
            self.ag.get_action('Edit').set_sensitive(True)
            self.ag.get_action('ExportMenu').set_sensitive(True)
            self.browser.edit_button.set_sensitive(True)
        elif model.get_value(iter, 2) == 'category':
            self.browser.display_category_listing(self.treeview.get_full_node_name(iter))
            self.ag.get_action('Edit').set_sensitive(False)
            self.ag.get_action('ExportMenu').set_sensitive(False)
            self.browser.edit_button.set_sensitive(False)


    def disable_toolbuttons(self):
        self.ag.get_action("Back").set_sensitive(False)
        self.ag.get_action("Forward").set_sensitive(False)
        self.ag.get_action("Home").set_sensitive(False)
        self.ag.get_action("Refresh").set_sensitive(False)
        self.ag.get_action("Find").set_sensitive(False)
        self.search_button.set_sensitive(False)
        if self.search_entry.get_property("visible"):
            self.search_entry.hide()
        self.treeview.set_sensitive(False)

    def enable_toolbuttons(self):
        self.ag.get_action("Back").set_sensitive(self.browser.engine.can_go_back())
        self.ag.get_action("Forward").set_sensitive(self.browser.engine.can_go_forward())
        self.ag.get_action("Home").set_sensitive(True)
        self.ag.get_action("Refresh").set_sensitive(True)
        self.ag.get_action("Find").set_sensitive(True)
        self.search_button.set_sensitive(True)
        self.treeview.set_sensitive(True)

    def on_wiki_new_clicked(self, widget, pagename):
        (model, current_iter) = self.treeview.get_selection().get_selected()
        parentiter = None
        if model.get_value(current_iter, 2) == 'page':
            parentiter = model.iter_parent(current_iter)
            if parentiter:
                parentname = pagename
            else:
                parentname = None
        elif model.get_value(current_iter, 2) == 'category':
            parentiter = current_iter
            parentname = self.treeview.get_full_node_name(parentiter)
        dialog = Dialogs.NewPageDialog(parentname)
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            dialog.hide()
            newpage = dialog.get_entry()
            if parentname:
                fullnewpage = parentname + '::' + newpage
            else:
                fullnewpage = newpage
            if len(newpage) and fullnewpage not in self.treeview.treeview_nodes():
                if dialog.get_checked():
                    self.treeview.pending_page_parent_iter = parentiter
                    self.topWindow.set_title(fullnewpage)
                else:
                    self.treeview.pending_page_parent_iter = None
                    self.topWindow.set_title(newpage)
                self.browser.hide()
                self.editor.show_all()
                self.state = "editor"
                self.disable_toolbuttons()
                self.toggle_edit_actions_sensitive()
                self.editor.set_edit_wiki_text(self.topWindow.get_title(), "")
            else:
                dialog = Alerts.Error(None, _("The page %s already exists") % fullnewpage,
                        _("Please choose another name for the new page or edit the existing instance."))
                dialog.run()
                dialog.hide()
                return
        dialog.destroy()

    def on_wiki_new_from_link(self, widget, link):
        model = self.treeview.get_model()
        nodename = NewtonUtils.nodename_from_path(link)
        if '::' in nodename:
            parent_cat = nodename[:nodename.rfind('::')]
        else:
            parent_cat = None
        if parent_cat and not parent_cat in self.treeview.treeview_nodes():
            error = Alerts.Error(None, _("Category Not Found"),
                    _('The category "%s" was not found. The parent categories must be created before this page is created.' % parent_cat)).run()
            return

        parent_iter = self.treeview.get_iter_from_nodename(parent_cat)

        self.treeview.pending_page_parent_iter = parent_iter
        self.topWindow.set_title(nodename)
        self.browser.hide()
        self.editor.show_all()
        self.state = "editor"
        self.disable_toolbuttons()
        self.toggle_edit_actions_sensitive()
        self.editor.set_edit_wiki_text(self.topWindow.get_title(), "")

    def toggle_edit_actions_sensitive(self):
        if not self.ag.get_action("Save").get_sensitive():
            self.ag.get_action("Save").set_sensitive(True)
            self.ag.get_action("CancelEdit").set_sensitive(True)
            self.ag.get_action("NewPage").set_sensitive(False)
            self.ag.get_action("NewCategory").set_sensitive(False)
            self.ag.get_action("Delete").set_sensitive(False)
            self.ag.get_action("Edit").set_sensitive(False)
            self.ag.get_action("Bold").set_sensitive(True)
            self.ag.get_action("Italic").set_sensitive(True)
            self.ag.get_action("Underline").set_sensitive(True)
            self.ag.get_action("Strikethrough").set_sensitive(True)
        else:
            self.ag.get_action("Save").set_sensitive(False)
            self.ag.get_action("CancelEdit").set_sensitive(False)
            self.ag.get_action("NewPage").set_sensitive(True)
            self.ag.get_action("NewCategory").set_sensitive(True)
            self.ag.get_action("Delete").set_sensitive(True)
            self.ag.get_action("Edit").set_sensitive(True)
            self.ag.get_action("Bold").set_sensitive(False)
            self.ag.get_action("Italic").set_sensitive(False)
            self.ag.get_action("Underline").set_sensitive(False)
            self.ag.get_action("Strikethrough").set_sensitive(False)

    def on_wiki_link_clicked(self, widget, pagename):
        self.ag.get_action("Save").set_sensitive(False)
        self.ag.get_action("CancelEdit").set_sensitive(False)
        self.treeview.select_wiki_page(pagename)

    def on_wiki_link_message(self, widget, link):
        self.statusbar.pop()
        if link:
            self.statusbar.push(link)

    def on_wiki_edit_clicked(self, blah, str):
        self.ag.get_action("NewPage").set_sensitive(False)
        self.ag.get_action("NewCategory").set_sensitive(False)
        self.ag.get_action("Edit").set_sensitive(False)
        self.ag.get_action("Save").set_sensitive(True)
        self.ag.get_action("CancelEdit").set_sensitive(True)
        self.ag.get_action("Delete").set_sensitive(False)
        self.ag.get_action("Find").set_sensitive(False)
        self.search_button.set_sensitive(False)
        if self.search_entry.get_property("visible"):
            self.search_entry.hide()
        self.browser.hide()
        self.editor.show_all()
        self.state = "editor"
        self.editor.set_edit_wiki_text(self.topWindow.get_title(), str)
        self.disable_toolbuttons()

    def on_wiki_save_clicked(self, blah, content):
        self.ag.get_action("NewPage").set_sensitive(True)
        self.ag.get_action("NewCategory").set_sensitive(True)
        self.ag.get_action("Edit").set_sensitive(True)
        self.ag.get_action("Save").set_sensitive(False)
        self.ag.get_action("CancelEdit").set_sensitive(False)
        self.ag.get_action("Delete").set_sensitive(True)
        self.ag.get_action("Find").set_sensitive(True)
        self.search_button.set_sensitive(True)
        current_page = self.topWindow.get_title()
        path = NewtonUtils.path_from_nodename(current_page)
        NewtonUtils.write_wiki_file(path, content)
        self.enable_toolbuttons()
        # if page doesn't exist, make it
        if current_page not in self.treeview.treeview_nodes():
            if current_page.count('::'):
                self.treeview.add_new_wiki_page(current_page[current_page.rfind('::') + 2:])
            else:
                self.treeview.add_new_wiki_page(current_page)
            self.browser.rebuild_completion_list()
        self.editor.hide()
        self.browser.show_all()
        self.state = "browser"
        self.treeview.select_wiki_page(current_page)
        self.browser.display_content(current_page)

    def on_wiki_cancel_clicked(self, blah, str):
        self.ag.get_action("NewPage").set_sensitive(True)
        self.ag.get_action("NewCategory").set_sensitive(True)
        self.ag.get_action("Edit").set_sensitive(True)
        self.ag.get_action("Save").set_sensitive(False)
        self.ag.get_action("CancelEdit").set_sensitive(False)
        self.ag.get_action("Delete").set_sensitive(True)
        self.ag.get_action("Find").set_sensitive(True)
        self.editor.hide()
        self.browser.show_all()
        self.state = "browser"
        self.enable_toolbuttons()

    def on_wiki_preferences_clicked(self, button):
        self.preferences.run()
        self.preferences.hide()

    def on_style_combobox_changed(self, combo):
        self.config.set_string(KEY_STYLESHEET, combo.get_active_text())
        self.ag.get_action("Refresh").activate()

    def on_camelcase_checkbutton_toggled(self, button):
        self.config.set_bool(KEY_IGNORE_CAMELCASE, button.get_active())
        self.ag.get_action("Refresh").activate()

    def on_spell_checkbutton_toggled(self, button):
        self.config.set_bool(KEY_ENABLE_SPELL_CHECK, button.get_active())
        if not self.editor.enable_spell_check_toggle(button.get_active()):
            self.preferences.emit('spellcheck-fail', None)

    def on_wiki_location_changed(self, blah, location):
        pagename = location[location.rfind("/") + 1:]
        self.topWindow.set_title(pagename)
        self.browser.current_location = pagename
        if pagename == 'WikiRoot':
            self.ag.get_action("Delete").set_sensitive(False)
            self.ag.get_action("Edit").set_sensitive(False)
            self.ag.get_action("Rename").set_sensitive(False)
            self.ag.get_action("ExportMenu").set_sensitive(False)
            self.browser.delete_button.set_sensitive(False)
            self.browser.edit_button.set_sensitive(False)
        elif pagename == 'NewtonHome':
            self.ag.get_action("Delete").set_sensitive(False)
            self.ag.get_action("Rename").set_sensitive(False)
            self.browser.delete_button.set_sensitive(False)
        else:
            self.ag.get_action("Delete").set_sensitive(True)
            self.ag.get_action("Rename").set_sensitive(True)
            self.browser.delete_button.set_sensitive(True)
        self.ag.get_action("Back").set_sensitive(self.browser.engine.can_go_back())
        self.ag.get_action("Forward").set_sensitive(self.browser.engine.can_go_forward())

    def on_main_window_delete(self, widget, event):
        self.treeview.save_tree_structure()
        self.save_window_state()
        if self.method == "window":
            gtk.main_quit()
        else:
            self.topWindow.hide()
        return True

    def on_wiki_delete_clicked(self, widget, nodename):
        if self.treeview.get_selected_type() == 'page':
            dialog = Alerts.Confirm(None, _('Are you sure you want to delete page "%s"?') % nodename,
                    _("Deleting this page is permanent and can not be undone."))
        else:
            dialog = Alerts.Confirm(None, _('Are you sure you want to delete category "%s"?') % nodename,
                    _("Deleting this category is permanent and can not be undone."))
        if dialog.run() == gtk.RESPONSE_OK:
            # FIXME: probably should save (relocate) subtrees
            if NewtonUtils.is_category(nodename):
                for root, dirs, files in os.walk(NewtonUtils.path_from_nodename(nodename), topdown=False):
#                    print 'Walk:', root, dirs, files
                    for name in files:
                        try:
                            os.remove(os.path.join(root, name))
                        except:
                            pass
                    for name in dirs:
                        try:
                            os.rmdir(os.path.join(root, name))
                        except:
                            pass
                    try:
                        os.rmdir(root)
                    except:
                        pass
            else:
                os.remove(NewtonUtils.path_from_nodename(nodename))
            self.treeview.remove_selected_node()
        else:
            dialog.hide()
        self.browser.rebuild_completion_list()

    def on_click_event(self, widget, event):
        print "Clicked"

    def on_button_toggled(self, button):
        if button.get_active():
            self.topWindow.show_all()
            self.restore_window_state()
            if self.state == "browser":
                self.editor.hide()
                self.search_entry.hide()
            else:
                self.browser.hide()
                self.search_entry.hide()
        else:
            self.save_window_state()
            self.topWindow.hide()
        return True

    def toggle_window_visible(self):
        if not self.topWindow.get_property('visible'):
            self.topWindow.show_all()
            self.browser.address_toolbar.hide()
            self.restore_window_state()
            if self.state == "browser":
                self.editor.hide()
                self.search_entry.hide()
            else:
                self.browser.hide()
                self.search_entry.hide()
        else:
            if not self.topWindow.is_active():
                self.topWindow.present()
                self.browser.address_toolbar.hide()
            else:
                self.treeview.save_tree_structure()
                self.save_window_state()
                self.topWindow.hide()
        return True

    def restore_window_state(self):
        if self.config.get_bool(KEY_WINDOW_MAXIMIZED, False) == True:
            self.topWindow.maximize()
        else:
            self.topWindow.resize(self.config.get_int(KEY_WINDOW_SIZE_X, 750), self.config.get_int(KEY_WINDOW_SIZE_Y, 500))
            self.topWindow.move(self.config.get_int(KEY_WINDOW_POS_X, 200), self.config.get_int(KEY_WINDOW_POS_Y, 120))
        self.hpaned.set_position(self.config.get_int(KEY_HPANED_POS, 150))

    def save_window_state(self):
        if self.config.get_bool(KEY_WINDOW_MAXIMIZED, False) == False:
            (x, y) = self.topWindow.get_size()
            self.config.set_int(KEY_WINDOW_SIZE_X, x)
            self.config.set_int(KEY_WINDOW_SIZE_Y, y)
            (x, y) = self.topWindow.get_position()
            self.config.set_int(KEY_WINDOW_POS_X, x)
            self.config.set_int(KEY_WINDOW_POS_Y, y)
        pos = self.hpaned.get_position()
        self.config.set_int(KEY_HPANED_POS, pos)

    def on_button_press(self, widget, event):
        if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
            widget.stop_emission("button-press-event")

class BrowserWidget(gtk.VBox):
    def __init__(self, treeview, ui, config, method):
        self.treeview = treeview
        self.ui = ui
        self.config = config
        gtk.VBox.__init__(self, False, 3)
        self.mozframe = gtk.Frame()
        self.pack_start(self.mozframe, True, True, 3)

        hbox = gtk.HBox(False, 3)

        self.edit_button = gtk.Button(_("Edit"), gtk.STOCK_EDIT)
        hbox.pack_start(self.edit_button, False, False, 3)
        self.edit_button.connect("clicked", self.on_edit_button_clicked)
        self.edit_button.set_use_underline(False)

        self.delete_button = gtk.Button(_("Delete"), gtk.STOCK_DELETE)
        hbox.pack_start(self.delete_button, False, False, 3)
        self.delete_button.connect("clicked", self.on_delete_button_clicked)
        self.delete_button.set_use_underline(False)

        self.new_button = gtk.Button(_("New"), gtk.STOCK_NEW)
        hbox.pack_start(self.new_button, False, False, 3)
        self.new_button.connect("clicked", self.on_new_button_clicked)
        self.new_button.set_use_underline(False)

        if not method == 'window':
            label = gtk.Label("%s<span weight='bold'> %s </span>%s" \
                    % (_("Press"), _("escape to hide"), _("this window.")))
            label.set_use_markup(True)
            label.set_justify(gtk.JUSTIFY_RIGHT)
            label.set_alignment(1.0, 0.5)
            hbox.pack_start(label, True, True, 3)

        self.current_location = "NewtonHome"
        self.engine = WikiEngine(config)

        self.address_toolbar = gtk.Toolbar()
        # the address bar
        self.goto_widget = gtk.ToolItem()
        self.goto_widget.set_expand(True)
        self.goto_widget.set_homogeneous(False)
        goto_hbox = gtk.HBox(False, 3)
        self.goto_widget.add(goto_hbox)
        goto_label = gtk.Label(_("Address:"))
        self.goto_entry = gtk.Entry()
        goto_hbox.pack_start(goto_label, False, False)
        goto_hbox.pack_start(self.goto_entry, True, True)
        self.address_toolbar.insert(self.goto_widget, -1)
        self.address_toolbar.show_all()
        self.goto_entry.connect('activate', self.on_goto_entry_activate)

        self.completion = gtk.EntryCompletion()
        self.goto_entry.set_completion(self.completion)
        liststore = gtk.ListStore(str)
        self.completion.set_model(liststore)
        self.completion.set_text_column(0)
        for node in self.treeview.treeview_nodes():
            liststore.append([node])
        self.completion.connect('action-activated', self.on_goto_completion_action_activated)
        if gtk.gtk_version >= (2, 8, 0) and gtk.pygtk_version >= (2, 8, 0):
            self.completion.set_inline_completion(True)

        self.pack_start(self.address_toolbar, False, False, 3)

        self.moz = gtkmozembed.MozEmbed()
        self.moz.connect("open-uri", self.on_link_clicked)
        self.moz.connect("realize", self.on_moz_realize)
        self.moz.connect("link-message", self.on_moz_link_message)
        self.mozframe.add(self.moz)
        self.pack_start(hbox, False, False, 3)

        self.moz.show()

    def activate_address_bar(self):
        self.address_toolbar.show_all()
        self.goto_entry.grab_focus()
        self.goto_entry.set_text(self.current_location)
        self.goto_entry.select_region(0, -1)

    def on_goto_completion_action_activated(self, completion, index):
        self.on_goto_entry_activate(self.goto_entry)

    def on_goto_entry_activate(self, entry):
        dest = entry.get_text()
        if not len(dest) or dest == 'WikiRoot':
            self.display_category_listing('')
        elif dest in self.treeview.treeview_nodes():
            self.treeview.select_wiki_page(entry.get_text())
        else:
            Alerts.Error(None, "Page Unavailable", 
                    'The page you have chosen does not yet exist. To create a new page, press the "New" button.').run()
            self.goto_entry.select_region(0, -1)
        self.address_toolbar.hide()

    def rebuild_completion_list(self):
        completion = self.goto_entry.get_completion()
        model = completion.get_model()
        model.clear()
        for node in self.treeview.treeview_nodes():
            model.append([node])

    # this is really bad, but it seems that for now, once the mozembed
    # widget is hidden, it cannot be shown again... As a workaround for
    # now, I'm creating a new one each time.. I hope the old gets caught
    # in the garbage collector... damn.
    # now I can't use go_back() etc and need to maintain my own history
    def on_browser_widget_show(self, widget):
        self.address_toolbar.hide()
        self.mozframe.remove(self.moz)
        self.moz = gtkmozembed.MozEmbed()
        self.moz.connect("open-uri", self.on_link_clicked)
        self.moz.connect("realize", self.on_moz_realize)
        self.moz.connect("link-message", self.on_moz_link_message)
        self.mozframe.add(self.moz)
        self.moz.show()

    def on_export_html_activate(self):
        loc_data = self.engine.get_wiki_content(self.current_location)
        css = NewtonUtils.get_file_contents(os.path.join(WIKI_STYLES, self.config.get_string(KEY_STYLESHEET, "style-blue") + ".css"))
        html = loc_data[1].replace("@STYLE@", css)
        dialog = gtk.FileChooserDialog("Export to HTML...", 
                None, 
                gtk.FILE_CHOOSER_ACTION_SAVE,
                (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                 gtk.STOCK_SAVE, gtk.RESPONSE_OK))
        title = self.moz.get_title()
        dialog.set_current_name(title.replace('::', '_-_'))
        result = dialog.run()
        if result == gtk.RESPONSE_OK:
            dialog.hide()
            filename = dialog.get_filename()

            if not filename.endswith(".html"):
                filename = filename + ".html"

            if not NewtonUtils.check_write_permissions(filename):
                Alerts.Error(None, "Permission Denied", "You don't have permission to write to the specified location.").run()
                dialog.destroy()
                return

            # Does the file already exist?
            if NewtonUtils.check_path_exists(filename):
                if not Alerts.FileOverwrite(None, filename).run():
                    dialog.destroy()
                    return
        
            try:
                NewtonUtils.write_wiki_file(filename, html)
            except:
                Alerts.Error(None, "Export Failed", 'The attempt to export this page has failed. Please make sure you choose a valid filename.').run()
        dialog.destroy()

    def display_search_results(self, pattern):
        data = self.engine.get_search_results(pattern)
        self.render_wiki_content((_("Search Results: %s") % pattern, data))

    def display_category_listing(self, catname):
        data = self.engine.get_category_listing(catname)
        if catname == '' or catname == 'WikiRoot':
            self.render_wiki_content(('WikiRoot', data))
        else:
            self.render_wiki_content((catname, data))

    def on_delete_button_clicked(self, button):
        self.emit("wiki-delete-clicked", self.current_location)

    def on_new_button_clicked(self, button):
        self.emit("wiki-new-clicked", None)

    def on_moz_realize(self, widget):
        self.emit("wiki-link-clicked", self.current_location)

    def display_content(self, pagename):
        loc_data = self.engine.get_wiki_content(pagename)
        self.render_wiki_content(loc_data)

    def navigate_to_wiki_page(self, pagename):
        loc_data = self.engine.new_location(pagename)
        self.render_wiki_content(loc_data)

    def render_wiki_content(self, loc_data):
        content = loc_data[1]
        self.moz.open_stream('file://' + WIKI_DIR, 'text/html')
        self.moz.append_data(content, long(len(content)))
        self.moz.close_stream()
        self.emit("wiki-location-changed", loc_data[0])

    def on_link_clicked(self, mozembed, gpointer):
        link = self.moz.get_link_message()
        pagename = link[link.rfind("/")+1:]
        path = NewtonUtils.path_from_nodename(pagename)
        if self.current_location.startswith("Search Results:"):
            wiki_text = NewtonUtils.get_file_contents(path)
            target = self.current_location[self.current_location.rfind(":") + 1:].strip()
            self.emit("wiki-link-clicked", pagename)
            if len(target):
                regex = NewtonUtils.build_case_insensitive_regex(target)
                match = re.search(r"%s" % regex, wiki_text)
                while match:
                    wiki_text = wiki_text.replace(match.group(1), '<span class="search">%s</span>' % match.group(1))
                    match = re.search(r"%s" % regex, wiki_text)
                loc_data = self.engine.transform_arbitrary_string(wiki_text, pagename)
                self.render_wiki_content(loc_data)
            return True

        if NewtonUtils.is_external_link(link):
            gnome.url_show(link)
            return True
        path = NewtonUtils.path_from_nodename(pagename)
        if link.find("@") > 0:
            return False
        if NewtonUtils.is_media_link(link):
            local_path = link.replace('file://', '', 1)
            if NewtonUtils.check_path_exists(local_path):
                success = os.system('gnome-open "%s"' % local_path)
                return True
            else:
                dialog = Alerts.Error(None, _('The media file "%s" does not exist' % pagename),
                        _("It may be either typed incorrectly or it has been deleted since this link was created."))
                dialog.run()
                dialog.hide()
                return True
        if NewtonUtils.check_path_exists(path):
            self.emit("wiki-link-clicked", pagename)
        else:
            dialog = Alerts.Confirm(None, _('The link "%s" points to a page that does not yet exist.' % pagename),
                    _("Would you like to create this page now?"))
            if dialog.run() == gtk.RESPONSE_OK:
                self.emit("wiki-new-from-link", link)
            else:
                dialog.hide()
        return True


    def on_moz_link_message(self, mozembed):
        link = mozembed.get_link_message()
        pagename = link[link.rfind('/') + 1:]
        if not link:
            self.emit("wiki-link-message", "")
            return
        if NewtonUtils.is_external_link(link):
            self.emit("wiki-link-message", "External link: %s" % link)
        elif "@" in link:
            self.emit("wiki-link-message", "Email %s" % link.replace("mailto:", ''))
        elif NewtonUtils.is_media_link(link):
            self.emit("wiki-link-message", "Open: %s" % link[link.rfind("/")+1:])
        else:
            if NewtonUtils.check_path_exists(NewtonUtils.path_from_nodename(pagename)):
                self.emit("wiki-link-message", "Go to %s" % link[link.rfind("/")+1:])
            else:
                self.emit("wiki-link-message", "Create page %s" % link[link.rfind("/")+1:])

    def on_back_button_clicked(self, widget):
        loc_data = self.engine.go_back()
        self.render_wiki_content(loc_data)

    def on_forward_button_clicked(self, widget):
        loc_data = self.engine.go_forward()
        self.render_wiki_content(loc_data)

    def on_home_button_clicked(self, widget):
        if self.current_location == "NewtonHome":
            return
        loc_data = self.engine.new_location("NewtonHome")
        self.render_wiki_content(loc_data)

    def on_refresh_button_clicked(self, widget):
        if os.path.isdir(NewtonUtils.path_from_nodename(self.current_location)):
            self.display_category_listing(self.current_location)
        else:
            loc_data = self.engine.get_wiki_content(self.current_location)
            self.render_wiki_content(loc_data)

    def on_edit_button_clicked(self, widget):
        raw_text = self.engine.get_raw_wiki_text(self.current_location)
        self.emit('wiki-edit-clicked', raw_text)

class EditWidget(gtk.VBox, NewtonGui):
    def __init__(self, ui, config, method):

        self.ui = ui
        self.config = config
        gtk.VBox.__init__(self, False, 3)

        labelbox = gtk.EventBox()
        labelbox.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("slate grey"))
        labelbox.set_border_width(3)
        self.editing_label = gtk.Label()
        self.editing_label.set_alignment(0.1, 0.5)
        self.editing_label.modify_fg(gtk.STATE_NORMAL, gtk.gdk.color_parse("white"))
        pagetitle_font = pango.FontDescription("normal 20")
        self.editing_label.modify_font(pagetitle_font)
        labelbox.add(self.editing_label)


        self.pack_start(labelbox, False, False, 3)

        self.edit_tools = self.ui.get_widget('/EditTools')
        self.edit_tools.set_style(gtk.TOOLBAR_ICONS)
        self.pack_start(self.edit_tools, False, False, 3)
        
        frame = gtk.Frame()
        self.pack_start(frame, True, True, 3)

        hbox = gtk.HBox(False, 3)

        self.cancel_button = gtk.Button(_("_Cancel"), gtk.STOCK_CANCEL)
        hbox.pack_start(self.cancel_button, False, False, 3)
        self.cancel_button.connect("clicked", self.on_cancel_button_clicked)
        self.cancel_button.set_use_underline(False)

        self.save_button = gtk.Button(_("_Save"), gtk.STOCK_SAVE)
        hbox.pack_start(self.save_button, False, False, 3)
        self.save_button.connect("clicked", self.on_save_button_clicked)
        self.save_button.set_use_underline(False)

        if not method == 'window':
            label = gtk.Label("%s<span weight='bold'> %s </span>%s" \
                    % (_("Press"), _("escape to hide"), _("this window.")))
            label.set_use_markup(True)
            label.set_justify(gtk.JUSTIFY_RIGHT)
            label.set_alignment(1.0, 0.5)
            hbox.pack_start(label, True, True, 3)

        lm = gtksourceview.SourceLanguagesManager()
        buffer = gtksourceview.SourceBuffer()
        buffer.set_data('languages-manager', lm)
        language = lm.get_language_from_mime_type('application/x-newton')
        buffer.set_highlight(True)
        buffer.set_language(language)
        self.editor = gtksourceview.SourceView(buffer)

        self.editor.connect('key-press-event', self.on_key_press_event)

        if self.config.get_bool(KEY_ENABLE_SPELL_CHECK, True):
            try:
                self.spell = gtkspell.Spell(self.editor)
            except: # avoid gtkspell issues discovered in 0.0.8
                self.config.set_bool(KEY_ENABLE_SPELL_CHECK, False)
                self.emit('spellcheck-bug', None)
        else:             
            try:
                self.spell = gtkspell.Spell(self.editor)
                self.spell.detach()
            except: # avoid gtkspell issues discovered in 0.0.8
                self.emit('spellcheck-bug', None)
                pass

        gconf_mono_font = self.config.get_string("/desktop/gnome/interface/monospace_font_name")
        font = pango.FontDescription(gconf_mono_font)
        self.editor.modify_font(font)
        self.editor.set_wrap_mode(gtk.WRAP_WORD)
        scroller = gtk.ScrolledWindow()
        scroller.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroller.add(self.editor)
        frame.add(scroller)
        self.pack_start(hbox, False, False, 3)
        self.show_all()

    def get_selected_text(self, buffer):
        insert = buffer.get_iter_at_mark(buffer.get_insert())
        selection_bound = buffer.get_iter_at_mark(buffer.get_selection_bound())
        if insert and selection_bound:
            return (buffer.get_text(insert, selection_bound), insert, selection_bound)
        else:
            return (None, None, None)

    def copy_text_to_clipboard(self, clipboard):
        buffer = self.editor.get_buffer()
        (text, insert, select_bound) = self.get_selected_text(buffer)
        if text and len(text):
            buffer.copy_clipboard(clipboard)
            self.ui.get_action_groups()[0].get_action('Paste').set_sensitive(True)

    def cut_text_to_clipboard(self, clipboard):
        buffer = self.editor.get_buffer()
        (text, insert, select_bound) = self.get_selected_text(buffer)
        if text and len(text):
            buffer.cut_clipboard(clipboard, self.editor.get_editable())
            self.ui.get_action_groups()[0].get_action('Paste').set_sensitive(True)

    def paste_text_from_clipboard(self, clipboard):
        buffer = self.editor.get_buffer()
        cursor_mark = buffer.get_insert()
        insert_iter = buffer.get_iter_at_mark(cursor_mark)
        buffer.paste_clipboard(clipboard, insert_iter, self.editor.get_editable())

    def on_key_press_event(self, obj, event):
        if event.keyval == gtk.keysyms.b:
            if (event.state & gtk.gdk.CONTROL_MASK):
                self.format_accel_action('bold')
        elif event.keyval == gtk.keysyms.i:
            if (event.state & gtk.gdk.CONTROL_MASK):
                self.format_accel_action('italic')
        elif event.keyval == gtk.keysyms.u:
            if (event.state & gtk.gdk.CONTROL_MASK):
                self.format_accel_action('underline')
        return False

    def enable_spell_check_toggle(self, enable):
        if enable:
            try:
                self.spell = gtkspell.Spell(self.editor)
#                self.spell.set_language(locale.getlocale()[0])
                return True
            except:
                self.config.set_bool(KEY_ENABLE_SPELL_CHECK, False)
                return False
        else:
            try:
                self.spell = gtkspell.get_from_text_view(self.editor)
                self.spell.detach()
                return True
            except:
                self.config.set_bool(KEY_ENABLE_SPELL_CHECK, False)
                return True

    def web_link_insert_clicked(self):
        visible_text = ''
        url = ''
        dialog = Alerts.Input(None, _("Enter the visible text (optional)."),
                _("If left blank, the URL itself will be shown."))
                
        result = dialog.run()
        if not result == gtk.RESPONSE_OK:
            dialog.hide()
            return
        else:
            visible_text = dialog.get_input()
            dialog.hide()
            dialog = Alerts.Input(None, _("Enter the URL of your link."),
                    _("This is the target web document."), "http://")
        result = dialog.run()
        if not result == gtk.RESPONSE_OK:
            dialog.hide()
            return
        else:
            url = dialog.get_input()

        if len(visible_text):
            self.insert_text_at_cursor("[[%s|%s]] " % (url, visible_text))
        else:
            self.insert_text_at_cursor("[[%s]] " % url)

    def email_link_insert_clicked(self):
        visible_text = ''
        address = ''
        dialog = Alerts.Input(None, _("Enter the visible text (optional)."),
                _("If left blank, the email address itself will be shown."))
                
        result = dialog.run()
        if not result == gtk.RESPONSE_OK:
            dialog.hide()
            return
        else:
            visible_text = dialog.get_input()
            dialog.hide()
            dialog = Alerts.Input(None, _("Enter the email address."),
                    _("This is the target email address."))
        result = dialog.run()
        if not result == gtk.RESPONSE_OK:
            dialog.hide()
            return
        else:
            address = dialog.get_input()

        if len(visible_text):
            self.insert_text_at_cursor("[[%s|%s]] " % (address, visible_text))
        else:
            self.insert_text_at_cursor("[[%s]] " % address)

    def media_link_insert_clicked(self):
        dialog = Alerts.Input(None, _("Enter the visible text (optional)."),
                _("If left blank, the file path itself will be shown."))
        result = dialog.run()
        if not result == gtk.RESPONSE_OK:
            dialog.hide()
            return
        else:
            visible_text = dialog.get_input()
            dialog.hide()
            dialog = gtk.FileChooserDialog("Inserting media...", 
                    None, 
                    gtk.FILE_CHOOSER_ACTION_OPEN,
                    (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                     gtk.STOCK_SAVE, gtk.RESPONSE_OK))
            result = dialog.run()
            if not result == gtk.RESPONSE_OK:
                dialog.hide()
                return
            filename = dialog.get_filename()
        dialog.hide()
        if len(visible_text):
            self.insert_text_at_cursor("{{%s|%s}} " % (filename, visible_text))
        else:
            self.insert_text_at_cursor("{{%s}} " % filename)

    def image_link_insert_clicked(self):
        dialog = Dialogs.ImageInsert()
        while True:
            response = dialog.run()
            if not response == gtk.RESPONSE_OK:
                dialog.hide()
                return
            if dialog.validate_size():
                break
            error = Alerts.Error(dialog, _("The size entered is not valid"),
                    _("Width and height entries must be numbers only, and cannot be empty."))
            error.run()
            error.hide()
        size = dialog.get_size()
        location = dialog.get_location()
        position = dialog.get_position()
        dialog.hide()
        caption = NewtonUtils.escape_text_for_html(dialog.get_caption())
        if len(location):
            if position == 'center':
                if len(caption):
                    self.insert_text_at_cursor("{{ %s%s|%s }} " % (location, size, caption))
                else:
                    self.insert_text_at_cursor("{{ %s%s }} " % (location, size))
            elif position == 'float-left':
                if len(caption):
                    self.insert_text_at_cursor("{{%s%s|%s }} " % (location, size, caption))
                else:
                    self.insert_text_at_cursor("{{%s%s }} " % (location, size))
            elif position == 'float-right':
                if len(caption):
                    self.insert_text_at_cursor("{{ %s%s|%s}} " % (location, size, caption))
                else:
                    self.insert_text_at_cursor("{{ %s%s}} " % (location, size))
            else:
                if len(caption):
                    self.insert_text_at_cursor("{{%s%s|%s}} " % (location, size, caption))
                else:
                    self.insert_text_at_cursor("{{%s%s}} " % (location, size))

    def peek_forward(self, num_chars):
        text = ''
        buffer = self.editor.get_buffer()
        current_iter = buffer.get_iter_at_mark(buffer.get_insert())
        for i in range(num_chars):
            text += current_iter.get_char()
            if not current_iter.forward_char():
                break
        if len(text) == num_chars:
            return text
        else: 
            return None
            
    def format_accel_action(self, type):

        formats = { 'bold'             : '**',
                    'italic'           : '//',
                    'underline'        : '__' }
        
        # Make me do the fast insert of formatted text.
        buffer = self.editor.get_buffer()
        bounds = buffer.get_selection_bounds()
        if len(bounds): # there is selected text
            text = buffer.get_text(bounds[0], bounds[1])
            buffer.delete_selection(True, True)
            self.insert_text_at_cursor('%s%s%s' % (formats[type], text, formats[type]))
        else: # there is no selected text
            current_mark = buffer.get_insert()
            forward_text = self.peek_forward(2)
            if forward_text == self.formats[type]: # we are at the end of formatted text
                current_iter = buffer.get_iter_at_mark(current_mark)
                if current_iter.forward_chars(2):
                    buffer.place_cursor(current_iter)
                else:
                    buffer.place_cursor(buffer.get_end_iter())
            else:
                self.insert_text_at_cursor('%s' % formats[type] * 2)
                current_iter = buffer.get_iter_at_mark(buffer.get_insert())
                if current_iter.backward_chars(2):
                    buffer.place_cursor(current_iter)

    def bold_insert_clicked(self):
        buffer = self.editor.get_buffer()
        bounds = buffer.get_selection_bounds()
        if len(bounds):
            text = buffer.get_text(bounds[0], bounds[1])
            buffer.delete_selection(True, True)
        else:
            dialog = Alerts.Input(None, _("Enter text to be bolded."),
                    _("Newton will insert the correct syntax to bold your text."))
            result = dialog.run()
            if not result == gtk.RESPONSE_OK:
                dialog.hide()
                return
            text = dialog.get_input()
        self.insert_text_at_cursor("**%s** " % text)

    def italic_insert_clicked(self):
        buffer = self.editor.get_buffer()
        bounds = buffer.get_selection_bounds()
        if len(bounds):
            text = buffer.get_text(bounds[0], bounds[1])
            buffer.delete_selection(True, True)
        else:
            dialog = Alerts.Input(None, _("Enter text to be italicized."),
                    _("Newton will insert the correct syntax to italicize your text."))
            result = dialog.run()
            if not result == gtk.RESPONSE_OK:
                dialog.hide()
                return
            text = dialog.get_input()
        self.insert_text_at_cursor("//%s// " % text)

    def underline_insert_clicked(self):
        buffer = self.editor.get_buffer()
        bounds = buffer.get_selection_bounds()
        if len(bounds):
            text = buffer.get_text(bounds[0], bounds[1])
            buffer.delete_selection(True, True)
        else:
            dialog = Alerts.Input(None, _("Enter text to be underlined."),
                    _("Newton will insert the correct syntax to underline your text."))
            result = dialog.run()
            if not result == gtk.RESPONSE_OK:
                dialog.hide()
                return
            text = dialog.get_input()
        self.insert_text_at_cursor("__%s__ " % text)

    def strikethrough_insert_clicked(self):
        buffer = self.editor.get_buffer()
        bounds = buffer.get_selection_bounds()
        if len(bounds):
            text = buffer.get_text(bounds[0], bounds[1])
            buffer.delete_selection(True, True)
        else:
            dialog = Alerts.Input(None, _("Enter text to be strikethrough formatted."),
                    _("Newton will insert the correct syntax to strikethrough format your text."))
            result = dialog.run()
            if not result == gtk.RESPONSE_OK:
                dialog.hide()
                return
            text = dialog.get_input()
        self.insert_text_at_cursor("<del>%s</del> " % text)

    def insert_current_date(self):
        buffer = self.editor.get_buffer()
        t = date.today()
        buffer.insert_at_cursor(t.strftime('%x') + ' ')

    def insert_current_time(self):
        buffer = self.editor.get_buffer()
        t = datetime.now()
        buffer.insert_at_cursor(t.strftime('%X') + ' ')

    def insert_text_at_cursor(self, text):
        buffer = self.editor.get_buffer()
        buffer.insert_at_cursor(text)

    def set_page_name(self, pagename):
        self.editing_label.set_text("Editing: %s" % pagename)

    def set_edit_wiki_text(self, pagename, text):
        self.set_page_name(pagename)
        text = text[text.find("\n") + 1:] # lose the moddate
        self.editor.get_buffer().set_text(text)
        self.editor.grab_focus()
        self.editor.place_cursor_onscreen()
        self.editor.get_buffer().set_modified(False)

    def on_cancel_button_clicked(self, widget):
        if self.editor.get_buffer().get_modified():
            dialog = Alerts.CustomConfirm(None, _('Cancel without saving changes?'), 
                    _("There have been changes to this document since last save."), 
                    [ [_('Save Changes'), gtk.RESPONSE_ACCEPT], [_('Continue Editing'), gtk.RESPONSE_REJECT], 
                    [gtk.STOCK_OK, gtk.RESPONSE_OK] ], gtk.RESPONSE_OK)
            response = dialog.run()
            if response == gtk.RESPONSE_OK:
                pass
            elif response == gtk.RESPONSE_ACCEPT:
                self.on_save_button_clicked(widget)
            else:
                return
        self.emit("wiki-cancel-clicked", None)

    def on_save_button_clicked(self, widget):
        buffer = self.editor.get_buffer()
        wiki_text = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter())
        wiki_text = "@@@ %s\n%s" % (NewtonUtils.get_datetime(), wiki_text)
        self.emit("wiki-save-clicked", wiki_text)

class WikiTreeView(gtk.TreeView):
    def __init__(self, menu):
        gtk.TreeView.__init__(self)
        self.popup = menu
        self.init_model()
        self.init_view_columns()
        self.set_rules_hint(True)
        self.set_reorderable(True)
        self.set_headers_visible(False)

        self.connect("button-press-event", self.on_button_press_event)

        self.enable_model_drag_source(gtk.gdk.BUTTON1_MASK, [("newton", 0, 0)], gtk.gdk.ACTION_COPY)
        self.enable_model_drag_dest([("newton", 0, 0)], gtk.gdk.ACTION_COPY)
        self.connect('drag-data-received', self.drag_data_recieved_data)

        # When a new page is created, the page name is given by the user, then the user
        # is placed in the edit screen to create the new page's content. The new page
        # should _not_ be added to the tree until the save button is pressed in this
        # state, since the "Cancel" button is always present. Canceling here should exit
        # the edit screen and _not_ add the newly created note. This variable stores the
        # iter (if any) where the new note should be appended.
        self.pending_page_parent_iter = None

    def drag_data_recieved_data(self, treeview, drag_context, x, y, selection, info, eventtime):
        model, iter_to_copy = self.get_selection().get_selected()
        temp = self.get_dest_row_at_pos(x, y)
        if temp != None:
            path, pos = temp
        else:
            path, pos = (len(model)-1,), gtk.TREE_VIEW_DROP_AFTER
        target_iter = model.get_iter(path)
        if self.check_row_path(model, iter_to_copy, target_iter):
            self.iter_copy(model, iter_to_copy, target_iter, pos)
            drag_context.finish(True, True, eventtime)
            treepath = model.get_path(target_iter)
            self.expand_to_path(treepath)
        else:
            drag_context.finish(False, False, eventtime)

        # select the newly moved row
        if model.get_value(target_iter, 2) == 'category':
            if pos == gtk.TREE_VIEW_DROP_INTO_OR_AFTER:
                self.set_cursor(model.get_path(model.iter_children(target_iter)))
            else:
                test = model.iter_next(target_iter)
                if test:
                    self.set_cursor(model.get_path(test))
                else: # give up for now and just select the row that we dropped on
                    self.set_cursor(model.get_path(target_iter))
        else:
            if not target_iter:
                iter = model.iter_root()
                while model.iter_next():
                    iter = model.iter_next()
                self.set_cursor(model.get_path(iter))
            else:
                next_iter = model.iter_next(target_iter)
                if next_iter:
                    self.set_cursor(model.get_path(next_iter))
                else: # target_iter is the last in the tree
                    self.set_cursor(model.get_path(target_iter))


    def check_row_path(self, model, iter_to_copy, target_iter):
        path_of_iter_to_copy = model.get_path(iter_to_copy)
        path_of_target_iter = model.get_path(target_iter)
        if path_of_target_iter[0:len(path_of_iter_to_copy)] == path_of_iter_to_copy:
            return False
        else:
            return True

    def iter_copy(self, model, iter_to_copy, target_iter, pos):
        # retrieve data of the selected row
        copy_icon = model.get_value(iter_to_copy, 0)            
        copy_name = model.get_value(iter_to_copy, 1)            
        copy_type = model.get_value(iter_to_copy, 2)            

        copy_path = NewtonUtils.path_from_nodename(self.get_full_node_name(iter_to_copy))
        target_path = None

        if (pos == gtk.TREE_VIEW_DROP_INTO_OR_BEFORE) or (pos ==
 	    gtk.TREE_VIEW_DROP_INTO_OR_AFTER):
            if model.get_value(target_iter, 2) == 'category':
                target_path = NewtonUtils.path_from_nodename(self.get_full_node_name(target_iter))
                new_iter = model.prepend(target_iter, None)
            else:
                target_path = NewtonUtils.path_from_nodename(self.get_full_node_name(model.iter_parent(target_iter)))
                new_iter = model.insert_after(None, target_iter)
        elif pos == gtk.TREE_VIEW_DROP_BEFORE:
            target_path = NewtonUtils.path_from_nodename(self.get_full_node_name(model.iter_parent(target_iter)))
            new_iter = model.insert_after(None, target_iter)
        elif pos == gtk.TREE_VIEW_DROP_AFTER:
            target_path = NewtonUtils.path_from_nodename(self.get_full_node_name(model.iter_parent(target_iter)))
            new_iter = model.insert_after(None, target_iter)

        # copy over the values of the old row into the new one ...
        model.set_value(new_iter, 0, copy_icon)
        model.set_value(new_iter, 1, copy_name)
        model.set_value(new_iter, 2, copy_type)

        # move the data files to the appropriate new location
        if os.path.exists(copy_path) and copy_path != target_path:
#            print copy_path, 'to', target_path
            try:
                move(copy_path, os.path.join(target_path, copy_name))
            except:
                return

        # fix links that point to the moved node
        copy_nodename = self.get_full_node_name(iter_to_copy)
        new_nodename = self.get_full_node_name(new_iter)
        self.rename_all_links(copy_nodename, new_nodename)

        # copy the rows in the tree that need copy
        for n in range(model.iter_n_children(iter_to_copy)): 
            next_iter_to_copy = model.iter_nth_child(iter_to_copy, 0)
            self.iter_copy(model, next_iter_to_copy, new_iter, gtk.TREE_VIEW_DROP_INTO_OR_BEFORE)

            # fix links that point to the children of the moved node
            copy_nodename = self.get_full_node_name(iter_to_copy)
            new_nodename = self.get_full_node_name(new_iter)
            self.rename_all_links(copy_nodename, new_nodename)

        # remove old row..
        model.remove(iter_to_copy)

    def get_iter_from_nodename(self, nodename):
        if not nodename in self.treeview_nodes():
            return None
        nodes_list = nodename.split('::')
        model = self.get_model()
        found_iter = None
        iter = model.get_iter_root()
        for i in range(len(nodes_list)):
            if not iter:
                return None
            while iter:
                if model[iter][1] == nodes_list[i]:
                    found_iter = iter
                    iter = model.iter_children(iter)
                    break
                iter = model.iter_next(iter)
        return found_iter


    def rename_all_links(self, src, dest):
        '''src and dest are FULL nodenames'''
        if src == dest:
            return
        camelcase = re.compile(r'\s+(([A-Z*]+[a-z0-9*]+[A-Z0-9*]+\w*(::)*)+)')
        bracketed = re.compile(r"\[{2}(\S.*?\S)\]{2}")
        for root, dirs, files in os.walk(WIKI_DATA):
            for file in files:
                path = os.path.join(root, file)
                contents = NewtonUtils.get_file_contents(path)
                # CamelCased links first
                match = camelcase.search(contents)
                while match:
                    # the src is a prefix of this link (ie. in this category)
                    if match.group(1).startswith(src + '::'):
                        contents = contents[:match.start()] + match.group().replace(src, dest, 1) + contents[match.end():]
                        match = camelcase.search(contents, match.end())
                        continue
                    # exact match
                    if match.group(1) == src:
                        if camelcase.match(dest):
                            contents = contents[:match.start()] + dest + contents[match.end(): ]
                        else:
                            contents = contents[:match.start()] + '[[%s]]' % dest + contents[match.end(): ]
                        match = camelcase.search(contents, match.end())
                        continue
                    match = camelcase.search(contents, match.end())
                # Bracketed links next
                match = bracketed.search(contents)
                while match:
                    components = match.group(1).split('|')
                    if len(components) == 2:
                        string = components[0].strip()
                        # the src is a prefix of this link (ie. in this category)
                        if string.startswith(src + '::'):
                            contents = contents[:match.start(1)] + match.group(1).replace(src, dest, 1) + contents[match.end(1):]
                            match = bracketed.search(contents, match.start(1))
                            continue
                        # exact match
                        if string == src:
                            contents = contents[:match.start(1)] + '%s|%s' % (dest, components[1]) + contents[match.end(1): ]
                            match = bracketed.search(contents, match.start(1))
                            continue
                    elif len(components) > 2:
                        # This is an invalid link, skip it.
                        match = bracketed.search(contents, match.end())
                        continue
                    else:
                        # the src is a prefix of this link (ie. in this category)
                        if match.group(1).startswith(src + '::'):
                            contents = contents[:match.start(1)] + match.group(1).replace(src, dest) + contents[match.end(1):]
                            match = bracketed.search(contents, match.start(1))
                            continue
                        # exact match
                        if match.group(1) == src:
                            contents = contents[:match.start(1)] + dest + contents[match.end(1): ]
                            match = bracketed.search(contents, match.start(1))
                            continue
                    match = bracketed.search(contents, match.end())
                NewtonUtils.write_wiki_file(path, contents)

    def on_button_press_event(self, object, event):
        """Handle a mouse button key press."""
        if event.button == 3: # right mouse button - show popup menu
            path = self.get_path_at_pos(int(event.x), int(event.y))
            if path:
                self.set_cursor(path[0])
                self.popup.popup(None, None, None, event.button, event.time)
                return True

    def get_selected_type(self):
        (model, iter) = self.get_selection().get_selected()
        return model.get_value(iter, 2)

    def populate_wiki_tree(self, top, topiter=None):
        if not os.path.exists(top):
            return
        for child in os.listdir(top):
            childpath = os.path.join(top, child)
            if os.path.isfile(childpath):
                iter = self.add_wiki_node(os.path.basename(childpath), 'page', topiter)
            elif os.path.isdir(childpath):
                iter = self.add_wiki_node(os.path.basename(childpath), 'category', topiter)
                self.populate_wiki_tree(childpath, iter)

    def get_full_node_name(self, iter):
        if iter:
            nodename = self.store.get_value(iter, 1)
            while self.store.iter_parent(iter):
                parent_iter = self.store.iter_parent(iter)
                nodename = '%s::%s' % (self.store.get_value(parent_iter, 1), nodename)
                iter = parent_iter
        else:
            nodename = ''
        return nodename

    def load_tree_structure(self):
        try:
            self.document = xml.dom.minidom.parse(os.path.join(WIKI_DIR, 'structure.xml'))
        except:
            return False
        nodes = self.document.getElementsByTagName('node')
        node_list = []
        for node in nodes:
            treepath = node.getAttribute('treepath')
            filepath = node.getAttribute('filepath')
            expanded = node.getAttribute('expanded')
            name = node.getAttribute('name')
            type = node.getAttribute('type')
            node_list.append((treepath, filepath, expanded, name, type))
        if self.verify_data(node_list):
            # structure is good, stick the nodes in the tree
            for node in node_list:
                if ':' in node[0]:
                    parent = self.store.get_iter_from_string(node[0][:node[0].rfind(':')])
                else:
                    parent = None
                if node[4] == 'page':
                    self.store.append(parent, [self.render_icon(NewtonStock.STOCK_PAGE, gtk.ICON_SIZE_MENU, None), node[3], node[4]])
                else:
                    self.store.append(parent, [self.render_icon(NewtonStock.STOCK_CATEGORY, gtk.ICON_SIZE_MENU, None), node[3], node[4]])
        else:
            return False
        structure = self.document.getElementsByTagName('structure')
        expanded_paths = structure[0].getAttribute('expands').split(',')
        if not expanded_paths[0] == '': # there are no expanded paths
            for path in expanded_paths:
                self.expand_row(self.store.get_path(self.store.get_iter_from_string(path)), False)
        return True

    def verify_data(self, nodes):
        files = []
        self.get_data_files_and_directories(WIKI_DATA, files)
        if not len(nodes) == len(files):
            # number of treenodes isn't the same as number of data files
            return False
        for node in nodes:
            if not node[1] in files:
                return False
        return True

    def get_data_files_and_directories(self, top, list):
        for child in os.listdir(top):
            childpath = os.path.join(top, child)
            if os.path.isfile(childpath):
                list.append(childpath)
            elif os.path.isdir(childpath):
                list.append(childpath)
                self.get_data_files_and_directories(childpath, list)

    def backup_data(self):
        dialog = gtk.FileChooserDialog("Backup all data...", 
                None, 
                gtk.FILE_CHOOSER_ACTION_SAVE,
                (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                 gtk.STOCK_SAVE, gtk.RESPONSE_OK))
        dialog.set_current_name('newton-data.tar.gz')
        result = dialog.run()
        if result == gtk.RESPONSE_OK:
            dialog.hide()
            filename = dialog.get_filename()

            if not filename.endswith(".tar.gz"):
                filename = filename + ".tar.gz"

            if not NewtonUtils.check_write_permissions(filename):
                Alerts.Error(None, "Permission Denied", "You don't have permission to write to the specified location.").run()
                dialog.destroy()
                return

            # Does the file already exist?
            if NewtonUtils.check_path_exists(filename):
                if not Alerts.FileOverwrite(None, filename).run():
                    dialog.destroy()
                    return

            list = []
            self.get_data_files_and_directories(WIKI_DATA, list)
            if not NewtonUtils.backup_all_data(filename, list):
                Alerts.Error(None, "Backup Failed", "Newton failed to create a backup copy of your data.").run()
                return
        else:
            dialog.destroy()


    def save_tree_structure(self):
        expands = []
        self.document = xml.dom.minidom.Document()
        structure = self.document.createElement('structure')
        structure.setAttribute('version', VERSION)
        self.document.appendChild(structure)

        self.store.foreach(self.add_node_to_xml_document, (structure, expands))

        structure.setAttribute('expands', ','.join(expands))
        xml_str = self.document.toprettyxml()
        NewtonUtils.write_wiki_file(os.path.join(WIKI_DIR, 'structure.xml'), xml_str)

    def add_node_to_xml_document(self, model, path, iter, user_data):
        node_elem = self.document.createElement('node')
        node_elem.setAttribute('treepath', model.get_string_from_iter(iter))
        node_elem.setAttribute('filepath', NewtonUtils.path_from_nodename(self.get_full_node_name(iter)))
        if self.row_expanded(path):
            node_elem.setAttribute('expanded', 'True')
        else:
            node_elem.setAttribute('expanded', 'False')
        node_elem.setAttribute('name', model.get_value(iter, 1))
        node_elem.setAttribute('type', model.get_value(iter, 2))
        user_data[0].appendChild(node_elem)
        if self.row_expanded(path):
            user_data[1].append(model.get_string_from_iter(iter))

    def treeview_nodes(self):
        list = []
        self.store.foreach(self.add_node_to_pylist, list)
        return list

    def rename_current_page(self, new_name):
        (model, iter) = self.get_selection().get_selected()
        model.set_value(iter, 1, new_name)
        return self.get_full_node_name(iter)

    def add_node_to_pylist(self, model, path, iter, list):
        nodename = model.get_value(iter, 1)
        while model.iter_parent(iter):
            parent_iter = model.iter_parent(iter)
            nodename = '%s::%s' % (model.get_value(parent_iter, 1), nodename)
            iter = parent_iter
        list.append(nodename)

    def selected_wiki_page(self):
        (model, iter) = self.get_selection().get_selected()
        return self.get_full_node_name(iter)

    def select_wiki_page(self, pagename):
        self.store.foreach(self.select_page, pagename)

    def select_page(self, model, path, iter, pagename):
        full_name = self.get_full_node_name(iter)
        if pagename == full_name:
            # category to page before selecting it in tree
            if not self.row_expanded(path):
                self.expand_to_path(path)
            self.set_cursor(path)

    def remove_selected_node(self):
        (model, iter) = self.get_selection().get_selected()
        if iter:
            parent = model.iter_parent(iter)
            if parent:
                self.select_wiki_page(model.get_value(parent, 1))
            else:
                self.select_wiki_page("NewtonHome")
            self.store.remove(iter)

    def init_model(self):
        self.store = gtk.TreeStore(gtk.gdk.Pixbuf, str, str)
        self.set_model(self.store)

    def init_view_columns(self):
        self.col = gtk.TreeViewColumn()
        self.col.set_title(_('WikiPage'))
        render_pixbuf = gtk.CellRendererPixbuf()
        self.col.pack_start(render_pixbuf, expand=False)
        self.col.add_attribute(render_pixbuf, 'pixbuf', 0)
        render_text = gtk.CellRendererText()
        self.col.pack_start(render_text, expand=True)
        self.col.add_attribute(render_text, 'text', 1)
        self.append_column(self.col)

    def add_new_wiki_page(self, pagename):
        self.add_wiki_node(pagename, 'page', self.pending_page_parent_iter)

    def add_wiki_node(self, nodename, type, parent=None):
        if type == 'page':
            return self.store.append(parent, [self.render_icon(NewtonStock.STOCK_PAGE, gtk.ICON_SIZE_MENU, None), nodename, type])
        elif type == 'category':
            return self.store.append(parent, [self.render_icon(NewtonStock.STOCK_CATEGORY, gtk.ICON_SIZE_MENU, None), nodename, type])



gobject.signal_new("spellcheck-bug", EditWidget, gobject.SIGNAL_ACTION, gobject.TYPE_STRING, (gobject.TYPE_STRING, ))
gobject.signal_new("wiki-location-changed", BrowserWidget, gobject.SIGNAL_ACTION, gobject.TYPE_STRING, (gobject.TYPE_STRING, ))
gobject.signal_new("wiki-link-clicked", BrowserWidget, gobject.SIGNAL_ACTION, gobject.TYPE_STRING, (gobject.TYPE_STRING, ))
gobject.signal_new("wiki-edit-clicked", BrowserWidget, gobject.SIGNAL_ACTION, gobject.TYPE_STRING, (gobject.TYPE_STRING, ))
gobject.signal_new("wiki-link-message", BrowserWidget, gobject.SIGNAL_ACTION, gobject.TYPE_STRING, (gobject.TYPE_STRING, ))
gobject.signal_new("wiki-save-clicked", EditWidget, gobject.SIGNAL_ACTION, gobject.TYPE_STRING, (gobject.TYPE_STRING, ))
gobject.signal_new("wiki-new-clicked", BrowserWidget, gobject.SIGNAL_ACTION, gobject.TYPE_STRING, (gobject.TYPE_STRING, ))
gobject.signal_new("wiki-new-from-link", BrowserWidget, gobject.SIGNAL_ACTION, gobject.TYPE_STRING, (gobject.TYPE_STRING, ))
gobject.signal_new("wiki-delete-clicked", BrowserWidget, gobject.SIGNAL_ACTION, gobject.TYPE_STRING, (gobject.TYPE_STRING, ))
gobject.signal_new("wiki-cancel-clicked", EditWidget, gobject.SIGNAL_ACTION, gobject.TYPE_STRING, (gobject.TYPE_STRING, ))
