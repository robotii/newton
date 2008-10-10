m4_define(pygtk_required_version,               2.5.3)
m4_define(gnome_python_required_version,        2.9.4)
m4_define(gnome_python_extras_required_version, 2.9.2)

AC_INIT(src)

AM_CONFIG_HEADER(config.h)
AM_INIT_AUTOMAKE(newton, 0.1)

AM_MAINTAINER_MODE

AC_PATH_PROG(GCONFTOOL, gconftool-2)
AM_GCONF_SOURCE_2

AC_PROG_INTLTOOL([0.21])

AM_PATH_PYTHON

PKG_CHECK_MODULES(PYGTK, pygtk-2.0 >= pygtk_required_version)
PKG_CHECK_MODULES(GNOME_PYTHON, gnome-python-2.0 >= gnome_python_required_version)
PKG_CHECK_MODULES(GNOME_PYTHON_EXTRAS, gnome-python-extras-2.0 >= gnome_python_extras_required_version)

ALL_LINGUAS=""

GETTEXT_PACKAGE=newton
AC_SUBST(GETTEXT_PACKAGE)
AC_DEFINE_UNQUOTED(GETTEXT_PACKAGE, "$GETTEXT_PACKAGE", [The gettext package])

AM_GLIB_GNU_GETTEXT

AC_OUTPUT([
Makefile
data/Makefile
src/__init__.py
src/Makefile
scripts/Makefile
po/Makefile.in
])
