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

import os 
from gettext import gettext as _
import re
import urlparse
import sgmllib

from newton import PIXMAPS_DIR, WIKI_DIR, WIKI_HOME, WIKI_DATA, WIKI_MEDIA, WIKI_STYLES, DATA_DIR
import NewtonUtils
from NewtonConfig import KEY_IGNORE_CAMELCASE, KEY_STYLESHEET
import NewtonWikiText

class WikiEngine:
    def __init__(self, config):
        self.config = config
        if not NewtonUtils.check_path_exists(WIKI_DIR):
            NewtonUtils.make_path(WIKI_DIR)
        if not NewtonUtils.check_path_exists(WIKI_DATA):
            NewtonUtils.make_path(WIKI_DATA)
        if not NewtonUtils.check_path_exists(WIKI_MEDIA):
            NewtonUtils.make_path(WIKI_MEDIA)
        if not NewtonUtils.check_path_exists(WIKI_STYLES):
            NewtonUtils.make_path(WIKI_STYLES)
        if not NewtonUtils.check_path_exists(WIKI_HOME):
            NewtonUtils.write_wiki_file(os.path.join(WIKI_DATA, 'NewtonHome'), 
                    NewtonWikiText.NEWTON_HOME_TEXT)
        # we have to overwrite the default styles and NewtonSyntax to allow extra features
        NewtonUtils.write_wiki_file(os.path.join(WIKI_STYLES, 'Human.css'), 
                NewtonUtils.get_file_contents(os.path.join(DATA_DIR, 'Human.css')).replace("@PIXMAPS_DIR@", PIXMAPS_DIR))
        NewtonUtils.write_wiki_file(os.path.join(WIKI_STYLES, 'Blue.css'), 
                NewtonUtils.get_file_contents(os.path.join(DATA_DIR, 'Blue.css')).replace("@PIXMAPS_DIR@", PIXMAPS_DIR))
        NewtonUtils.write_wiki_file(os.path.join(WIKI_DATA, 'NewtonSyntax'), 
                NewtonWikiText.NEWTON_SYNTAX_TEXT)

        self.parser = TextParser(config)

        self.history = History()

    def get_wiki_content(self, pagename):
        location = os.path.join(WIKI_DATA, pagename)
        data = self.parser.parse_wiki_text(NewtonUtils.get_file_contents(location), pagename)
#        print data[0]
        content = "%s%s%s" % (NewtonWikiText.WIKI_PAGE_HEADER, data[0], NewtonWikiText.WIKI_PAGE_FOOTER)
        content = content.replace("@PAGENAME@", pagename)
        content = content.replace("@MODDATE@", data[1])
        content = content.replace("@PIXMAPS_DIR@", PIXMAPS_DIR)
        content = content.replace("@STYLESHEET@", os.path.join(WIKI_STYLES, self.config.get_string(KEY_STYLESHEET, "Blue") + ".css"))
        return (location, content)

    def transform_arbitrary_string(self, string, pagename):
        data = self.parser.parse_wiki_text(string, pagename)
#        print data[0]
        content = "%s%s%s" % (NewtonWikiText.WIKI_PAGE_HEADER, data[0], NewtonWikiText.WIKI_PAGE_FOOTER)
        content = content.replace("@PAGENAME@", pagename)
        content = content.replace("@MODDATE@", data[1])
        content = content.replace("@PIXMAPS_DIR@", PIXMAPS_DIR)
        content = content.replace("@STYLESHEET@", os.path.join(WIKI_STYLES, self.config.get_string(KEY_STYLESHEET, "Blue") + ".css"))
        return (os.path.join(WIKI_DATA, pagename), content)

    def get_raw_wiki_text(self, pagename):
        location = os.path.join(WIKI_DATA, pagename)
        raw_text = NewtonUtils.get_file_contents(location)
        return raw_text

    def new_location(self, pagename):
        location = os.path.join(WIKI_DATA, pagename)
        data = self.parser.parse_wiki_text(NewtonUtils.get_file_contents(location), pagename)
#        print data[0]
        content = "%s%s%s" % (NewtonWikiText.WIKI_PAGE_HEADER, data[0], NewtonWikiText.WIKI_PAGE_FOOTER)
        content = content.replace("@PAGENAME@", pagename)
        content = content.replace("@MODDATE@", data[1])
        content = content.replace("@PIXMAPS_DIR@", PIXMAPS_DIR)
        content = content.replace("@STYLESHEET@", os.path.join(WIKI_STYLES, self.config.get_string(KEY_STYLESHEET, 'Blue') + ".css"))
        self.history.append(pagename)
        return (location, content)

    def get_search_results(self, pattern):
        results = []
        for root, dirs, files in os.walk(WIKI_DATA):
            for file in files:
                path = os.path.join(root, file)
                contents = NewtonUtils.get_file_contents(path)
                if pattern.lower() in contents.lower():
                    page = path.replace(WIKI_DATA, '').replace('/', '::')
                    results.append(page)
        if len(results):
            result_html = '<p><ol>\n'
            for result in results:
                result_html += '<div class="level2"><li class="level2"><span class="li"><a href="%s" class="wikilink1">%s</a></span></li></div>' % ("data/" + result, result)
            result_html += '</ol></p>'
        else:
            result_html = "<p>No results found.</p>"
        content = "%s%s%s" % (NewtonWikiText.WIKI_PAGE_HEADER, result_html, NewtonWikiText.WIKI_PAGE_FOOTER)
        content = content.replace("@PAGENAME@", 'Search Results: %s' % pattern)
        content = content.replace("@MODDATE@", 'N/A')
        content = content.replace("@PIXMAPS_DIR@", PIXMAPS_DIR)
        content = content.replace("@STYLESHEET@", os.path.join(WIKI_STYLES, self.config.get_string(KEY_STYLESHEET, 'Blue') + ".css"))
        return content

    def get_category_listing(self, catnode):
        list = []
        catpath = NewtonUtils.path_from_nodename(catnode)
        self.get_category_subtree(catpath, list)
        levels = 0
        content = '<h1>Category Contents</h1><div class="level1">\n<p>The following is a listing of all pages and categories within the category <code>%s</code>.' % catnode
        for item in list:
            relpath = item.replace(catpath, '')
            level = relpath.count('/')
            nodename = catnode + item.replace(catpath, '')
            if level == levels:
                if os.path.isdir(item):
                    content += '<li class="category"><span class="li"><a href="%s" class="wikilink1">%s</a></span></li>\n' % ('data/' + nodename.replace("/", '::'), os.path.basename(item))
                else:
                    content += '<li class="page"><span class="li"><a href="%s" class="wikilink1">%s</a></span></li>\n' % ('data/' + nodename.replace("/", '::'), os.path.basename(item))
            elif level > levels:
                if os.path.isdir(item):
                    content += '\n<ul class="catlist">\n<li class="category"><span class="li"><a href="%s" class="wikilink1">%s</a></span></li>\n' % ('data/' + nodename.replace('/', '::'), os.path.basename(item))
                else:
                    content += '\n<ul class="catlist">\n<li class="page"><span class="li"><a href="%s" class="wikilink1">%s</a></span></li>\n' % ('data/' + nodename.replace('/', '::'), os.path.basename(item))
            else:
                content += '\n</ul>\n' * (levels - level)
                if os.path.isdir(item):
                    content += '<li class="category"><span class="li"><a href="%s" class="wikilink1">%s</a></span></li>\n' % ('data/' + nodename.replace('/', '::'), os.path.basename(item))
                else:
                    content += '<li class="page"><span class="li"><a href="%s" class="wikilink1">%s</a></span></li>\n' % ('data/' + nodename.replace('/', '::'), os.path.basename(item))
            levels = level
        content += '\n</ul>\n' * (levels)
        content += '</div>'
        if not len(list):
            content += _('<div class="level2">\n<p>\n<strong>This category is empty.</strong>\n</p>\n</div>')
        content = "%s%s%s" % (NewtonWikiText.WIKI_PAGE_HEADER, content, NewtonWikiText.WIKI_PAGE_FOOTER)
        if catnode == '':
            content = content.replace("@PAGENAME@", 'WikiRoot')
        else:
            content = content.replace("@PAGENAME@", catnode)
        content = content.replace("@MODDATE@", 'N/A')
        content = content.replace("@PIXMAPS_DIR@", PIXMAPS_DIR)
        content = content.replace("@STYLESHEET@", os.path.join(WIKI_STYLES, self.config.get_string(KEY_STYLESHEET, 'Blue') + ".css"))
        return content

    def get_category_subtree(self, top, list):
        for child in os.listdir(top):
            childpath = os.path.join(top, child)
            if os.path.isfile(childpath):
                list.append(childpath)
            elif os.path.isdir(childpath):
                list.append(childpath)
                self.get_category_subtree(childpath, list)

    def go_back(self):
        pagename = self.history.back()
        return self.get_wiki_content(pagename)

    def go_forward(self):
        pagename = self.history.forward()
        return self.get_wiki_content(pagename)

    def can_go_back(self):
        return self.history.can_go_back()

    def can_go_forward(self):
        return self.history.can_go_forward()

class History:
    def __init__(self):
        self.history_list = ['NewtonHome']
        self.index = 0

    def size(self):
        return len(self.history_list)

    def back(self):
        self.index = self.index - 1
        return self.history_list[self.index]

    def forward(self):
        self.index = self.index + 1
        return self.history_list[self.index]

    def append(self, location):
        self.history_list = self.history_list[:self.index + 1]
        self.history_list.append(location)
        self.index = self.index + 1

    def can_go_back(self):
        return not self.index == 0

    def can_go_forward(self):
        return not self.index == len(self.history_list) - 1

class TextParser:
    def __init__(self, config):
        self.config = config
        self.heading1_c = re.compile(r"^\=\s*(.*)")
        self.heading2_c = re.compile(r"^\={2}\s*(.*)")
        self.heading3_c = re.compile(r"^\={3}\s*(.*)")
        self.heading4_c = re.compile(r"^\={4}\s*(.*)")
        self.heading5_c = re.compile(r"^\={5}\s*(.*)")
        self.bold_c = re.compile(r"(\*{2})([^\s].*?)\1")
        self.italic_c = re.compile(r"((?<!:)\/{2})([^\s].*?)\1")
        self.underline_c = re.compile(r"(\_{2})([^\s].*?)\1")
        self.monospace_c = re.compile(r"(\'{2})([^\s].*?)\1")
        self.regulartext_c = re.compile(r"^(\w)|(\<strong)|(\<i)|(\<u)|(\[)")
        self.paragraph_c = re.compile("\s*")
        self.unorderedlist_c = re.compile("(^\*+)(.*)")
        self.orderedlist_c = re.compile("(^#+)(.*)")
        self.codeblock_c = re.compile("(^\s{2})(.*)")
        self.codeblock_framed_c = re.compile("^%%%")
        self.rule_c = re.compile("^\-{4,}.*")
        self.moddate_c = re.compile("^@@@(.*)")
        self.ignore_pass1_c = re.compile(r"(%{2}[^\s].*?%{2})")
        self.ignore_pass2_c = re.compile(r"%{2}([^\s].*?)%{2}")

        self.autoemail_c = re.compile(r"(?<=[ \(])([a-zA-Z0-9._%-]+@[a-zA-Z0-9._%-]+\.[a-zA-Z]{2,4})(?=\b)")
        self.autolink_c = re.compile(r"(?<=[\A \(])(?<!{ )((http|https|ftp):\/\/(\w+\.)+\S+\b)")

        self.link_square_c = re.compile(r"\[{2}(\S.*?\S)\]{2}")
        self.medialink_c = re.compile(r"\{{2}(.*?)\}{2}")
        self.camel_case_c = re.compile(r'[\s\b]((\!?[A-Z*]+[a-z0-9*]+[A-Z0-9*]+\w*(::)*)+)')

    def parse_wiki_text(self, text, pagename):
        data = self.parse_for_syntax(text)
        return data

    def parse_for_syntax(self, text):
        moddate = ""
        open_tags = []

        tags = {
            "level"         : "</div>",
            "p"             : "</p>",
            "ul"            : "</ul>",
            "ol"            : "</ol>",
            "code"          : "</pre>",
            "code_frame"    : "</pre>"
        }

        content = ""
        text = text.split("\n")
        for line in text:

            # take the ignores out
            ignores = []
            match = self.ignore_pass1_c.search(line)
            while match:
                line = self.ignore_pass1_c.sub('@@IGNORE%s@@' % len(ignores), line, 1)
                ignores.insert(0, match.group(1))
                match = self.ignore_pass1_c.search(line)

            # modification date
            match = self.moddate_c.match(line)
            if match:
                moddate = match.group(1)
                continue

            # code block?
            match = self.codeblock_framed_c.match(line)
            if match:
                if "code_frame" in open_tags:
                    open_tags.remove("code_frame")
                    line = '</pre>\n'
                else:
                    open_tags.insert(0, "code_frame")
                    line = '<pre class="pre">\n'
                    content = content + line
                    continue

            if "code_frame" in open_tags:
                line = line.replace('<', '&lt;')
                line = line.replace('>', '&gt;')
                line = line.replace('"', '&quot;')
                content = content + line + '\n'
                continue

            match = self.codeblock_c.match(line)
            if match:
                code = match.group(2).replace('&', '&amp;')
                code = code.replace('<', '&lt;')
                code = code.replace('>', '&gt;')
                code = code.replace('"', '&quot;')
                if "code" not in open_tags:
                    open_tags.insert(0, "code")
                    line = '<pre class="pre">%s' % code
                else:
                    line = code
                line = "%s\n" % line
                content = content + line
                continue
            else:
                if "code" in open_tags:
                    open_tags.remove("code")
                    content += '</pre>\n'

            # horizontal rule
            if self.rule_c.match(line):
                content = content + "<hr />\n"
                continue

            line = self.heading5_c.sub(r'<h5>\1</h5><div class="level5">', line)
            line = self.heading4_c.sub(r'<h4>\1</h4><div class="level4">', line)
            line = self.heading3_c.sub(r'<h3>\1</h3><div class="level3">', line)
            line = self.heading2_c.sub(r'<h2>\1</h2><div class="level2">', line)
            line = self.heading1_c.sub(r'<h1>\1</h1><div class="level1">', line)

            # paragraph tags suck, so this is messy until I draw it out
            # a little nicer
            if line.find('<div class="level') > 0:
                if "level" in open_tags:
                    line = "</div>\n%s" % line
                else:
                    open_tags.insert(0, "level")
                if "p" in open_tags:
                    line = "</p>\n%s" % line
                    open_tags.remove("p")

            if self.regulartext_c.match(line) \
                    or self.italic_c.match(line) \
                    or self.bold_c.match(line) \
                    or self.underline_c.match(line) \
                    or self.monospace_c.match(line):
                if "p" not in open_tags:
                    line = "<p>\n%s" % line
                    open_tags.insert(0, "p")

            if line == "" and "p" in open_tags:
                line = "</p>\n"
                open_tags.remove("p")

            line = self.bold_c.sub(r"<strong>\2</strong>", line)
            line = self.italic_c.sub(r"<em>\2</em>", line)
            line = self.underline_c.sub(r"<u>\2</u>", line)
            line = self.monospace_c.sub(r"<code>\2</code>", line)

            # find lists
            match = self.unorderedlist_c.search(line)
            if match:
                if len(match.group(1)) == open_tags.count("ul"):
                    line = '<li class="level%s"><span class="li"> %s </span></li>' % (len(match.group(1)), match.group(2))
                elif len(match.group(1)) < open_tags.count("ul"):
                    line = '<li class="level%s"><span class="li"> %s </span></li>' % (len(match.group(1)), match.group(2))
                    for i in range(open_tags.count("ul") - len(match.group(1))):
                        line = '</ul>\n%s' % line
                        open_tags.remove("ul")
                elif len(match.group(1)) > open_tags.count("ul"):
                    line = '<ul>\n<li class="level%s"><span class="li"> %s </span></li>' % (len(match.group(1)), match.group(2))
                    open_tags.insert(0, "ul")
            else:
                while "ul" in open_tags:
                    line = '</ul>\n%s' % line
                    open_tags.remove("ul")

            match = self.orderedlist_c.search(line)
            if match:
                if len(match.group(1)) == open_tags.count("ol"):
                    line = '<li class="level%s"><span class="li"> %s </span></li>' % (len(match.group(1)), match.group(2))
                elif len(match.group(1)) < open_tags.count("ol"):
                    line = '<li class="level%s"><span class="li"> %s </span></li>' % (len(match.group(1)), match.group(2))
                    for i in range(open_tags.count("ol") - len(match.group(1))):
                        line = '</ol>\n%s' % line
                        open_tags.remove("ol")
                elif len(match.group(1)) > open_tags.count("ol"):
                    line = '<ol>\n<li class="level%s"><span class="li"> %s </span></li>' % (len(match.group(1)), match.group(2))
                    open_tags.insert(0, "ol")
            else:
                while "ol" in open_tags:
                    line = '</ol>\n%s' % line
                    open_tags.remove("ol")
                
            # find CamelCase links
            if not self.config.get_bool(KEY_IGNORE_CAMELCASE):
                match = self.camel_case_c.search(line)
                while match:
                    if match.group(1)[0] == '!': # escaped CamelCase
                        link = ' %s' % match.group(1)[1:]
                    else:
                        link = self.create_link(match.group(1))
                    first = line[:match.start()]
                    last = line[match.start():]
                    line = first + self.camel_case_c.sub(link, last, 1)
                    match = self.camel_case_c.search(line, match.start() + len(link))

            # find links ([[]])
            match = self.link_square_c.search(line)
            while match:
                link = self.create_link(match.group(1))
                line = self.link_square_c.sub(link, line, 1)
                match = self.link_square_c.search(line)

            # find autolinks
            match = self.autolink_c.search(line)
            while match:
                link = '<a href="%s" class="urlextern">%s</a>' % (match.group(1), match.group(1))
                line = self.autolink_c.sub(link, line, 1)
                match = self.autolink_c.search(line, match.start() + len(link))

            # find autoemails
            match = self.autoemail_c.search(line)
            while match:
                link = ' <a href="mailto:%s" class="mail">%s</a>' % (match.group(1), match.group(1))
                line = self.autoemail_c.sub(link, line, 1)
                match = self.autoemail_c.search(line, match.start() + len(link))

            # find embedded media
            match = self.medialink_c.search(line)
            while match:
                link = self.create_media_link(os.path.expanduser(match.group(1)))
                line = self.medialink_c.sub(link, line, 1)
                match = self.medialink_c.search(line)

            # put the ignores back in
            i = len(ignores) - 1
            for ignore in ignores:
                line = line.replace('@@IGNORE%s@@' % i, ignore)
                i = i - 1
            line = self.ignore_pass2_c.sub(r'\1', line)

            line = "%s\n" % line
            content = content + line
        for tag in open_tags:
            content = content + tags[tag]
#        print content
        return (content, moddate)

    def create_link(self, text):
        components = text.split("|")

        ## mailto?
        if text.find("@") > 0: 
            if len(components) == 1:
                return '<a href="mailto:%s" class="mail">%s</a>' % (text, text)
            elif len(components) == 2:
                return '<a href=mailto:"%s" class="mail">%s</a>' % (components[0], components[1])
            else:
                return text

        # External link?
        if NewtonUtils.is_external_link(components[0]):
            if len(components) == 2:
                return '<a href="%s" class="urlextern" >%s</a>' % (components[0], self.strip_html(components[1]))
            elif len(components) == 1:
                return '<a href="%s">%s</a>' % (text, text)
            else:
                return text
        else: # local wiki link
            if len(components) == 2:
                return ' <a href="%s" class="%s">%s</a>' % ("data/" + components[0].strip(), self.page_exists_class(components[0]), self.strip_html(components[1]))
            elif len(components) == 1:
                if text.strip()[0] == '!': # it is an escaped CamelCase word.
                    return '%s' % text.strip()[1:] # lose the ! and return it with no markup.
                return ' <a href="%s" class="%s">%s</a>' % ("data/" + text.strip(), self.page_exists_class(text.strip()), text.strip())
            else:
                return text

    def create_media_link(self, text):
        components = text.split("|")
        parts = urlparse.urlparse(components[0].strip())
        # image file?
        if parts[2][parts[2].rfind(".")+1:].lower().strip() in ["png", "gif", "jpg", "jpeg"]:
            if parts[0] == 'http': # remote image file
                return self.create_remote_image_link(text)
            attrs = ""
            if parts[4]:
                if parts[4].find("x") > 0:
                    size = parts[4].split("x")
                    attrs += ' width="%s" height="%s"' % (size[0], size[1])
                else:
                    attrs += ' width="%s"' % (parts[4])
            filename = parts[2].strip()
            if len(components) == 1:
                align = self.get_image_alignment(text)
                if align == "mediacenter":
                    return '<div align="center"><img src="%s" align="middle" %s /></div>' % (os.path.expanduser(filename), attrs)
                else:
                    attrs += ' class="%s"' % align
                    return '<img src="%s" align="middle" %s />' % (os.path.expanduser(filename), attrs)
            else: # local image with caption
                align = self.get_image_alignment(text)
                return '<div class="%s"><div class="image-caption"><img src="%s" %s><br/>%s</div></div>' % (align, os.path.expanduser(filename), attrs, components[1])
        else:
            if len(components) == 1:
                return '<a class="%s" href="%s">%s</a>' % (self.media_exists_class(text), text.strip(), text.strip())
            elif len(components) == 2:
                return '<a class="%s" href="%s">%s</a>' % (self.media_exists_class(components[0]), components[0].strip(), components[1].strip())

    def create_remote_image_link(self, text):
        components = text.split("|")

        # find the actuall URL, excluding the ? part if it exists
        index = components[0].find("?")
        if index > 0:
            url = components[0][:components[0].find("?")]
        else:
            url = components[0]

        parts = urlparse.urlparse(components[0])
        attrs = ""
        if parts[4]:
            if parts[4].find("x") > 0:
                size = parts[4].split("x")
                attrs += ' width="%s" height="%s"' % (size[0], size[1])
            else:
                attrs += ' width="%s"' % (parts[4])
        if len(components) == 1:
            align = self.get_image_alignment(text)
            filename = components[0].strip()
            if align == "mediacenter":
                return '<div align="center"><a href="%s" class="media"><img src="%s" %s /></a></div>' % (url, url, attrs)
            else:
                attrs += ' class="%s"' % align
                return '<a href="%s" class="media"><img src="%s" %s /></a>' % (url, url, attrs)
        else: # I think there is a caption if we get here
            align = self.get_image_alignment(text)
            return '<div class="%s"><div class="image-caption"><a href="%s"><img src="%s" %s></a><br/>%s</div></div>' % (align, url, url, attrs, components[1])

    def page_exists_class(self, page):
        if NewtonUtils.check_path_exists(NewtonUtils.path_from_nodename(page)):
            return "wikilink1"
        else:
            return "wikilink2"

    def media_exists_class(self, media):
        if NewtonUtils.check_path_exists(media):
            return "wikilink3"
        else:
            return "wikilink2"

    def get_image_alignment(self, text):
        if text.startswith(" ") and text.endswith(" "):
            return "mediacenter"
        elif text.startswith(" "):
            return "mediaright"
        elif text.endswith(" "):
            return "medialeft"
        else:
            return ""

    def strip_html(self, s):
        parser = StrippingParser()
        parser.feed(s)
        parser.close()
        parser.cleanup()
        return parser.result

class StrippingParser(sgmllib.SGMLParser):

    # These are the HTML tags that we will leave intact
    valid_tags = ()

    from htmlentitydefs import entitydefs # replace entitydefs from sgmllib
    
    def __init__(self):
        sgmllib.SGMLParser.__init__(self)
        self.result = ""
        self.endTagList = [] 
        
    def handle_data(self, data):
        if data:
            self.result = self.result + data

    def handle_charref(self, name):
        self.result = "%s&#%s;" % (self.result, name)
        
    def handle_entityref(self, name):
        if self.entitydefs.has_key(name): 
            x = ';'
        else:
            # this breaks unstandard entities that end with ';'
            x = ''
        self.result = "%s&%s%s" % (self.result, name, x)
    
    def unknown_starttag(self, tag, attrs):
        """ Delete all tags except for legal ones """
        if tag in self.valid_tags:       
            self.result = self.result + '<' + tag
            for k, v in attrs:
                if string.lower(k[0:2]) != 'on' and string.lower(v[0:10]) != 'javascript':
                    self.result = '%s %s="%s"' % (self.result, k, v)
            endTag = '</%s>' % tag
            self.endTagList.insert(0,endTag)    
            self.result = self.result + '>'
                
    def unknown_endtag(self, tag):
        if tag in self.valid_tags:
            self.result = "%s</%s>" % (self.result, tag)
            remTag = '</%s>' % tag
            self.endTagList.remove(remTag)

    def cleanup(self):
        """ Append missing closing tags """
        for j in range(len(self.endTagList)):
                self.result = self.result + self.endTagList[j]    

