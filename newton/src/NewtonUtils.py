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

import sys, os, datetime, urlparse, tarfile
from newton import WIKI_DATA, WIKI_MEDIA, WIKI_DIR

# Miscellaneous functions that don't really fit in any object.

def make_path(path):
	if not os.path.exists(path):
		os.mkdir(path)

def check_read_permissions(filename):
	if filename == None or os.access(filename, os.R_OK) == 0:
		return False
	else:
		return True

def check_write_permissions(filename):
	if filename == None or os.access(os.path.dirname(filename), os.W_OK) != 1:
		return False
	else:
		return True

def build_case_insensitive_regex(pattern):
    regex = '(?<!"search"\>)('
    for letter in pattern.strip():
        regex += "[%s%s]" % (letter, letter.swapcase())
    return regex + ")"

def check_path_exists(path):
	return os.path.exists(path)
		
def note_name_to_file_name(name):
	return name.lower().replace(' ', '_')

def write_wiki_file(filename, content):
    filename = filename.replace('::', os.sep)
    file = open(filename, 'w')
    file.write(content)
    file.close()

def get_file_contents(filename):
    filename = filename.replace('::', os.sep)
    file = open(filename, 'r')
    contents = file.read()
    file.close()
    return contents

def is_external_link(link):
    ext_prefixes = ["http", "ftp"]
    for prefix in ext_prefixes:
        if link.startswith(prefix):
            return True
    return False

def is_media_link(link):
    return not link.startswith('file://' + WIKI_DATA)

def get_datetime():
    d = datetime.date.today()
    today = d.strftime("%B %e,%Y")
    t = datetime.datetime.now()
    now = t.strftime("%r")
    return "%s @%s" % (today, now)

def get_local_path_from_uri(uri):
    parts = urlparse.urlparse(uri)
    return parts[2]

def is_category(nodename):
    path = path_from_nodename(nodename)
    return os.path.isdir(path)

def path_from_nodename(nodename):
    return WIKI_DATA + nodename.replace('::', os.sep)

def nodename_from_path(path):
    path = path[path.rfind(WIKI_DATA):]
    path = path.replace(WIKI_DATA, '')
    return path.replace('/', '::')

def backup_all_data(dest, files):
    try:
        tar = tarfile.open(dest, 'w:gz')
        for file in files:
            tar.add(file)
        tar.close()
    except:
        return False
    return True
    

def escape_text_for_html(text):
    escaped_text = text.replace('&', '&amp;')
    escaped_text = escaped_text.replace('<', '&lt;')
    escaped_text = escaped_text.replace('>', '&gt;')
    escaped_text = escaped_text.replace('"', '&quot;')
    return escaped_text
