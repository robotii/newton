@INTLTOOL_SCHEMAS_RULE@

# if GCONF_SCHEMAS_INSTALL
# install-data-local:
#         GCONF_CONFIG_SOURCE=$(GCONF_SCHEMA_CONFIG_SOURCE) \
#         $(GCONFTOOL) --makefile-install-rule $(schema_DATA)
# endif

desktopdir 	= $(datadir)/applications
desktop_in_files = newton.desktop.in
desktop_DATA 	= $(desktop_in_files:.desktop.in=.desktop)
@INTLTOOL_DESKTOP_RULE@

serverdir       = $(libdir)/bonobo/servers
server_in_files = GNOME_NewtonApplet.server.in
server_DATA     = $(server_in_files:.server.in=.server)

$(server_in_files): $(server_in_files:.server.in=.server.in.in)
	sed -e "s|\@LIBEXECDIR\@|$(libexecdir)|"	\
	    -e "s|\@DATADIR\@|$(datadir)|"		\
	    < $< > $@

@INTLTOOL_SERVER_RULE@

gladedir   = $(datadir)/newton
glade_DATA = newton.glade preferences.glade newtonui.xml

wikidatadir = $(datadir)/newton
wikidata_DATA = Blue.css Human.css

langdatadir = $(datadir)/gtksourceview-1.0/language-specs
langdata_DATA = newton.lang

pixmapsdir   = $(datadir)/newton/pixmaps
pixmaps_DATA = newton.svg link_icon.gif mail_icon.gif calendar.svg \
	       clock.svg export.svg web.svg web_link.svg email_link.svg \
	       media_link.svg image_link.svg image-center.svg float-left.svg \
	       float-right.svg category.png page.png category.svg page.svg 

icondir = $(datadir)/pixmaps
icon_DATA = newton.svg

uidir   = $(datadir)/gnome-2.0/ui
ui_DATA = GNOME_NewtonApplet.xml

schemadir       = @GCONF_SCHEMA_FILE_DIR@
schema_in_files = newton.schemas.in
schema_DATA     = $(schema_in_files:.schemas.in=.schemas)

install-data-hook:
if GCONF_SCHEMAS_INSTALL
	GCONF_CONFIG_SOURCE=$(GCONF_SCHEMA_CONFIG_SOURCE) \
	$(GCONFTOOL) --makefile-install-rule $(schema_DATA)
endif

DISTCLEANFILES =		\
	$(schema_DATA)		\
	$(server_in_files)	\
	$(server_DATA)		

EXTRA_DIST =				\
	GNOME_NewtonApplet.server.in.in	\
	GNOME_NewtonApplet.xml		\
	$(glade_DATA)			\
	$(wikidata_DATA)		\
	$(langdata_DATA)		\
	$(pixmaps_DATA)			\
	$(ui_DATA)			\
	$(icon_DATA) 			\
	$(schema_in_files)		\
	$(desktop_in_files)
