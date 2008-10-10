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

from newton import VERSION
from gettext import gettext as _

line1 = _("This is your NewtonHome page. You may edit this page however you like, but you can **not** delete it. This page will be loaded each time [[http://newton.sf.net|Newton]] is started.\n\n")

line2 = _("[[http://newton.sf.net|Newton]] is a serverless wiki applet for the GNOME2 Desktop Environment. It is meant to be easy to use, with little or no setup.\n\n")

line3 = _("Please remember that [[http://newton.sf.net|Newton]] is in its early stages of development. Bugs and feature requests should be sent to the [[newton-users@lists.sourceforge.net|newton-users]] mailing list.\n\n")

line4 = _("To add pages, add links to an existing page, then click on those links. Alternatively, click the //New// button.\n")

newton_home_strings = [
            line1,
            line2,
            line3,
            line4
            ]

NEWTON_HOME_TEXT = '@@@Never\n'
for string in newton_home_strings:
    NEWTON_HOME_TEXT += string


ns_intro = \
_("""= Document Formatting Syntax

[[http://newton.sf.net|Newton]] supports many types of document formatting through the use of a simple markup language. The markup language is easy to learn so that you can start formatting your documents very quickly. This page contains a description of all formatting supported by [[http://newton.sf.net|Newton]]. Each description will consist of both the wiki syntax needed for that formatting, and the formatted result.
""")

ns_basic = \
_("""== Basic Text Formatting

[[http://newton.sf.net|Newton]] supports **bold**, ''monospaced'', //italic//, <del>strikethrough</del>, and __underlined__ text. These can also be done in **//__combination__//**!

  Newton supports **bold**, ''monospaced'', //italic//, <del>strikethrough</del>, and __underlined__ text. These can also be done in **//__combination__//**!

You can also make <sub>subscripts</sub> and <sup>superscripts</sup>!

  You can also make <sub>subscripts</sub> and <sup>superscripts</sup>!
""")

ns_lists = \
_("""== Unordered and Ordered Lists

Both ordered (//ie. numbered//) and unordered (//ie. bulleted//) lists are supported. Start a line with a ''#'' to add a ordered item and a ''*'' to add an unordered item. The number of ''#'''s or ''*'''s starting the line determines the level of the item in the list. For example,

  * First level unordered item 1
  * First level unordered item 2
  ** This is a second level item
  * First level item 3

Produces this output:

* First level unordered item 1
* First level unordered item 2
** This is a second level item
* First level item 3

Similarly, for an ordered list,

  # First level ordered item 1
  # First level ordered item 2
  ## This is a second level item
  # First level item 3

Produces this output:

# First level ordered item 1
# First level ordered item 2
## This is a second level item
# First level item 3
""")

ns_headings = \
_("""== Headings or Sections

[[http://newton.sf.net|Newton]] supports up to five levels of headings. Start a line with ''='' for a first level heading, ''=='' for a second level heading, ''==='' for a third level, and so on.

  = Heading 1
  Some text.
  == Heading 2
  Some more text.
  === Heading 3
  And so on...

= Heading 1
Some text.
== Heading 2
Some more text.
=== Heading 3
And so on...
""")

ns_links = \
_("""== Internal and External Links

Links can be created to other [[http://newton.sf.net|Newton]] pages or to webpages on the Internet. Internal links can be created by simply typing a word in "camelcase" format. Like this, NewtonHome. If the wiki page that the link points to exists, it will appear green like the case of NewtonHome. Otherwise it will appear red like NonExistantPage.

You can make external links like [[http://www.pygtk.org|this]] or like this http://www.pygtk.org.

  You can make external links like [[http://www.pygtk.org|this]] or like this http://www.pygtk.org.

Email is simple too! An email link is as easy as this [[dcraven@gmail.com|dcraven]] or this [[dcraven@gmail.com]].

  Email is simple too! An email link is as easy as this [[dcraven@gmail.com|dcraven]] or this [[dcraven@gmail.com]].
""")

ns_images = \
_("""== Embedded Images

{{ http://www.google.ca/intl/en_ca/images/logo.gif|I'm the Google Logo}}
Both local images and remote (on the Internet) images can be embedded into your documents easily with a simple syntax. There is also a GUI dialog available in the edit screen to make it even easier!

For example, if you are connected to the Internet right now, you should see the Google logo to the right of this text. It also has a caption!

To embed this image, I used the following syntax:
  {{ http://www.google.ca/intl/en_ca/images/logo.gif|I'm the Google Logo}}

Notice the space to the left of the URL where there is none on the right side in the above example? That means that we want the image to "float right". With this syntax, the image will appear on the right side of the document while the text neatly wraps around it. Think of it like this; there is a space on the left, because the image has been //shoved// to the right. The same works to make the image "float left" by simply putting the space on the right. The text after the ''|'' symbol is the caption.

If you want the image to appear centered in your document, put a space on both sides like this:
  {{ http://www.google.ca/intl/en_ca/images/logo.gif }}

And now the image appears centered. {{ http://www.google.ca/intl/en_ca/images/logo.gif?200 }}

That image appears smaller though because I also used the simple image scaling syntax. The syntax that I used for the centered image looks like this:
  {{ http://www.google.ca/intl/en_ca/images/logo.gif?200 }}

Notice the "''?200''" part after the URL? This means that you want the image to appear 200 pixels wide, and scale the height automatically so that the image doesn't look stretched. If you **do** want to //stretch// the image, you can specify both width **and** height like this:

{{ http://www.google.ca/intl/en_ca/images/logo.gif?500x50 }}
  {{ http://www.google.ca/intl/en_ca/images/logo.gif?500x50 }}

That means you want the image to be scaled to 500 pixels wide by 50 pixels high.

Locally stored (images on your own computer) can be embedded as well. Just specify the local path to the image file instead of a URL. For example, I could enter:

  {{ /home/dcraven/newton.png }}

And that would display the image called ''newton.png'', centered in my document. The same scaling and positioning syntax that applied for remote images still applies exactly the same way for local images.
""")

ns_media = \
_("""== Embedding Other Media Files

[[http://newton.sf.net|Newton]] can also embed links to other types of media files such as mp3, pdf, word processor documents, or even plain text documents. When you click on the embedded link, the document will be opened using your default viewer.

To embed a PDF file called ''myfile.pdf'', simply put the file's path between sets of double curly braces. Just like we did with images. For example,

{{/home/dcraven/myfile.pdf}}
  {{/home/dcraven/myfile.pdf}}

If the file does not exist in the location specified, it will be red (like the one above) and [[http://newton.sf.net|Newton]] will tell you the file doesn't exist when you click on it. Otherwise it will appear in grey. You can also give the link a name in case you don't want the whole file path to appear in your document. 

{{/home/dcraven/myfile.pdf|My PDF File}}
  {{/home/dcraven/myfile.pdf|My PDF File}}
""")

ns_misc = \
_("""== Miscellaneous Formatting

* New paragraphs are created by adding a blank line.
* Horizontal rules or lines are made by putting four or more dashes on a line by themselves. Like this,
  ----

----
* Code blocks (sections with wiki markup ignored, like the examples above) are created by starting a line with two spaces.
""")

# add '@@@Never' as the very first line
newton_syntax_strings = [
            ns_intro, 
            ns_basic, 
            ns_lists, 
            ns_headings,
            ns_links,
            ns_images,
            ns_media,
            ns_misc
            ]

NEWTON_SYNTAX_TEXT = '@@@Never\n'
for string in newton_syntax_strings:
    NEWTON_SYNTAX_TEXT += string


WIKI_PAGE_HEADER = \
'''
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en" dir="ltr">
    <head>
        <title>@PAGENAME@</title>
        <link rel="stylesheet" media="screen" type="text/css" href="@STYLESHEET@" />
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        <meta name="generator" content="Newton %s " />
        <style type="text/css">@STYLE@</style>

    </head>
    <body>
        <div class="all">
            <div class="stylehead">
                <div class="header">
                    <div class="pagename">
                        [[<span class="pagename">@PAGENAME@</span>]]
                    </div>
                </div>

                <div class="bar" id="bar_top">
                </div>
                <div class="modified">
                    %s: @MODDATE@
                </div>
            </div>
'''  % (VERSION, _('Last modified'))

WIKI_PAGE_FOOTER = \
'''
        <div class="clearer">&nbsp;</div>
        <div class="stylefoot">
            <div class="bar" id="bar_bottom">
                <div class="bar-left" id="bar_bottomleft">
                </div>
                <div class="bar-right" id="bar_bottomright">
                </div>
            </div>
            <div align="center" class="footerinc">
            </div>
        </div>
    </div>
    </body>
</html>
'''

