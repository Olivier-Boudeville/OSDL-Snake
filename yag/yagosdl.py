#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""This is yag-osdl (OSDL's YAG), a thematical GPL-licenced HTML gallery
  generator.

  YAG stands for Yet Another Gallery, and yag-osdl is derived from the following
  work: YAG, copyright (C) 2002 Stas Z
  (see http://home.planet.nl/~stas.linux/python/yag/)
  yag-osdl is copyright (C) 2007-2021 Olivier Boudeville
  (olivier (dot) boudeville (at) esperide (dot) com)

  To use yag-osdl easily, one should source the included
  'yag-osdl-environment.sh' to have one's shell variables correctly checked and
  set. Or, even better, use 'run-yag-osdl.sh'.

  This script is named yagosdl.py and not yag-osdl.py since '-' is not allowed
  in the name of python modules.

  This program is distributed in the hope that it will be useful, but WITHOUT
  ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
  details.

  Usage: yagosdl.py [content directory] [-h] [-v]

    -h or --help: displays this usage message and exits

    -v or --version: displays yag-osdl's version and exits
    help_options    = ['-h',  '--help']
    config_options  = ['-rc', '--config']
    version_options = ['-v',  '--version']

  The following arguments override the options from the configuration file.

    -rc FILENAME or --config FILENAME: alternative configuration file to be
        used. If none is specified, a default yag-osdl.conf file will be looked
        up

    -th name: name of the theme to be used. If the theme cannot be found, or if
        it is not in the right format, the theme from the standard configuration
        file will be used.

        This program is free software; you can redistribute it and/or modify it
        under the terms of the GNU General Public License as published by the
        Free Software Foundation.

        This program is distributed in the hope that it will be useful, but
        WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
        General Public License for more details.

        You should have received a copy of the GNU General Public License along
        with this program; see the file COPYING. If not, write to the Free
        Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.

        yag-osdl creates a static html gallery consisting of a index pages with
        thumbnails links to pages with the original pictures, and adds pages
        allowing to browse the image repository through thematical collections.

"""


# Imports standard python modules:
import os, os.path, sys, string, distutils.util, shutil, tempfile, time, locale

# For Python2:
#import ConfigParser

# For Python3:
import configparser


# PIL (Picture Image Library, see
# http://www.pythonware.com/library/pil/handbook/index.htm) and run-yag-osdl.sh
# for installation details (pip, virtual env, etc.)
#
from PIL import Image


# Imports self-made generic modules:
from toolbox import *

# Imports basic common services:
import general_utils

# Imports file extended services:
import file_utils

# Imports data services for trees of themes:
import data_utils



yag_osdl_version = 0.8

yag_general_theme_file = 'yag-overall-themes.thm'
yag_general_theme_page = 'yag-theme-map.html'


# Extensions:

html_extension    = '.html'
jpeg_extension    = '.jpeg'
comment_extension = '.txt'
theme_extension   = '.thm'

yag_encoding = 'utf-8'


# If you change it, change it too in template files:
resource_directory_name = 'yag-osdl-resources'
theme_directory_name = 'yag-osdl-parsed-themes'

gallery_comment_filename = 'yag-gallery-comment.txt'


class YagException(ApplicationException):
    """Base class for exceptions raised in yag-osdl module."""


class NodeTheme(data_utils.Node):
    """
    Describes a theme, whose children are sub-themes, whose content is the theme
    name.
    Each NodeTheme carries to a list of tuples (content name, content's full web
    page) corresponding to all media content belonging to this theme.
    """


    def __init__(self, name):
        super().__init__(name)
        self.referenced_content = []


    def add_content(self, content_name, content_page_filename):
        """
        Adds a (content name, content's full web page) pair corresponding
        to media content belonging to this theme.
        """
        # As content_page_filename is an absolute path it has to be converted
        # in a relative one:
        new_relative_path = '..' + content_page_filename.replace(main_dic['content_directory'], '')
        self.referenced_content.append((content_name, new_relative_path))


    def get_name(self):
        return self.content


    def generate_html_referenced_content(self):
        """
        Returns the HTML code corresponding to the referenced content belonging
        to this theme.
        """

        res = "<p>"
        if self.referenced_content:
            if main_dic['language'] == 'French':
                res += u'Ce thème référence les contenus suivants :\n<ul>'
            else:
               res += u'This theme references following content:\n<ul>'

            for t in self.referenced_content:
                content_name, content_page_file = t
                res += '\t<li><a href="%s">%s</a></li>' % (content_page_file, content_name)
            res += "</ul>"
        else:
            if main_dic['language'] == 'French':
                res += u'Ce thème ne référence directement aucun contenu.'
            else:
                res += u'This theme does not reference directly any content.'

        return res + "</p>"



    def generate_html_sub_themes(self):
        """
        Returns the HTML code corresponding to the referenced content belonging
        to this theme.
        """

        res = "<p>"
        len = self.get_children()
        if len:
            if len == 1:
                if main_dic['language'] == 'French':
                    res += u'Ce thème comporte un seul sous-thème: <a href="%s">%s</a>' % (convert_theme_to_filename(self.children[0].get_name()), self.children[0].get_name())
                else:
                    res += u'This theme has ony one sub-theme: <a href="%s">%s</a>' % (convert_theme_to_filename(self.children[0].get_name()), self.children[0].get_name())
            else:
                 if main_dic['language'] == 'French':
                     res += u'Ce thème inclut les sous-thèmes suivants :\n<ul>'
                 else:
                     res += u'This theme has following sub-themes:\n<ul>'

                 for c in self.get_children():
                     res += '\t<li><a href="%s">%s</a></li>' % (convert_theme_to_filename(c.get_name()), c.get_name())
                     res += "</ul>"
        else:
            if main_dic['language'] == 'French':
                res += u'Ce thème ne comporte aucun sous-thème.'
            else:
                res += "This theme has no sub-theme."

        return res + "</p>"




def init_token_dic():
    """Sets default values in token dictionary."""

    global token_dic

    # Token dictionary keeps the current values during recursion, as opposed to
    # the main dic:

    # Use 'locale -a' to check supported locales:
    if main_dic['language'] == 'French':
        locale.setlocale(locale.LC_TIME, "fr_FR.utf8")
        date = time.strftime('%A %d %B %Y', time.localtime())
    else:
        date = time.strftime('%A, %d %B %Y', time.localtime())

    project_name = main_dic['project_name']

    token_dic = {
        'YAG-OSDL-TOKEN-PROJECT-NAME'     : project_name,
        'YAG-OSDL-TOKEN-PROJECT-URL-NAME' : to_filename(project_name),
        'YAG-OSDL-TOKEN-DATE'             : date,
        'YAG-OSDL-TOKEN-GENERATOR'        : str(yag_osdl_version),
        'YAG-OSDL-TOKEN-CONTENT-DIRECTORY': main_dic['content_directory'],
        'YAG-OSDL-TOKEN-OUTPUT-DIRECTORY' : main_dic['output_directory'],
        'YAG-OSDL-TOKEN-THEME'            : main_dic['theme'],
        'YAG-OSDL-TOKEN-ROOT-PATH'        : None,
        'YAG-OSDL-CURRENT-CONTENT-RAW'    : None,
        'YAG-OSDL-CURRENT-CONTENT-TXT'    : None,
        'YAG-OSDL-CURRENT-THEME'          : None,
        'YAG-OSDL-GALLERY-LICENSE'        : '',
        'YAG-OSDL-GALLERY-INFO'           : '',
        'YAG-OSDL-THEME-TREE'             : ''
    }

    if main_dic['author']:
        token_dic['YAG-OSDL-TOKEN-AUTHOR'] = main_dic['author']
    else:
        token_dic['YAG-OSDL-TOKEN-AUTHOR'] = '(no author was specified)'

    if main_dic['author_mail']:
        token_dic['YAG-OSDL-TOKEN-CONTACT'] = main_dic['author_mail']
    else:
        token_dic['YAG-OSDL-TOKEN-CONTACT'] = '(no mail address was specified)'

    license_file = main_dic['gallery_license_file']
    if license_file:
        if os.path.isfile(license_file):
            output_device.debug("Gallery license file found ('%s')." % (license_file,))
            with open(license_file, 'r', encoding=yag_encoding) as f:
                token_dic['YAG-OSDL-GALLERY-LICENSE'] = '<br><h2>Gallery license</h2><p>' + f.read() + '</p>'
        else:
            output_device.debug("Gallery license file not found ('%s')." % (license_file,))

    else:
        output_device.debug("No gallery license file specified.")

    info_filepath = main_dic['gallery_info_file']
    if info_filepath:
        if os.path.isfile(info_filepath):
            output_device.debug("Gallery information file found ('%s')." % (info_filepath,))
            with open(info_filepath, 'r', encoding=yag_encoding) as f:
                token_dic['YAG-OSDL-GALLERY-INFO'] = '<br><h2>Gallery recommended usage &amp; hints</h2><p>' + f.read() + '</p><br>'
        else:
            output_device.debug("Gallery information file not found ('%s')." % (info_filepath,))
    else:
        output_device.debug("No gallery information file specified.")



def generate_thumbnail(image_filename, thumbnail_size_pair):
    """Generates a JPEG thumbnail for specified image, no matter its original
    format.

    The thumbnail will be no bigger than specified size, aspect ratio is
    preserved.

    Copies as well the original images if the output is not to be made in
    content.

    Ex: generate_thumbnail('MyPicture.png', (100, 120)).
    """

    output_dir = main_dic['output_directory']

    image_abs_path = os.path.join(output_dir, image_filename)

    content_base_dir = main_dic['content_directory']

    image_new_abs_path = image_abs_path.replace(content_base_dir, output_dir, 1)

    thumbnailFile = os.path.splitext(image_new_abs_path)[0] + '-thumbnail.jpeg'

    #output_device.debug("Thumbnailing '%s' in '%s' with size %s." % (image_abs_path, thumbnailFile, repr(thumbnail_size_pair)))

    #output_device.info("Thumbnailing '%s' with size %s>." % (image_abs_path, repr(thumbnail_size_pair)))

    if not os.path.exists(image_abs_path):
        raise YagException("generate_thumbnail: image file '%s' not found." % (image_abs_path,))

    if not main_dic['output_in_content']:
        shutil.copy(image_abs_path, image_new_abs_path)

    image = Image.open(image_abs_path)

    if image.mode != 'RGB':
        image = image.convert('RGB')

    image.thumbnail(thumbnail_size_pair, Image.ANTIALIAS)

    image.save(thumbnailFile, 'JPEG')

#   except IOError as e:
#       raise YagException("Cannot create thumbnail for '%s' (I/O error: %s)." % (image_filename, e.strerror))
#   except:
#       raise YagException("Cannot create thumbnail for '%s'." % (image_filename,))



def get_full_page_filename_from_graphic(graphic_filename):
    """Returns a file name corresponding to the specified graphic file."""
    return os.path.join(token_dic['YAG-OSDL-TOKEN-OUTPUT-DIRECTORY'], convert_into_filename(graphic_filename) + html_extension)



def update_from_token_dic(a_string):
    """Replaces in specified string all key listed in token dictionary by their
value."""

    for (k, v) in token_dic.items():
        #output_device.debug("Replacing token '%s' by '%s'." % (k, v))
        if isinstance(v, str):
            a_string = a_string.replace(k, v)
        else:
            a_string = a_string.replace(k, repr(v))
    return a_string


def convert_theme_to_filename(theme):
    """Converts specified theme name into the full filename of its dedicated
page."""
    return os.path.join(token_dic['YAG-OSDL-TOKEN-ROOT-PATH'], theme_directory_name, convert_into_filename(theme) + html_extension)


def handle_theme(theme_name, content_name, content_filename):
    """
    Takes care of specified theme: links it to others, records its elements.
    """
    found_theme = main_dic['themes'].search_content(theme_name)
    # Theme not found, create it at the root of the theme tree:
    if not found_theme:
        found_theme = NodeTheme(theme_name)
        main_dic['themes'].add_child(found_theme)
    # We've got to provide to add_content not the content_filename but its page:
    found_theme.add_content(content_name, convert_into_filename(content_filename) + html_extension)


def register_simple_theme(theme_name):
    """Registers, if necessary, in theme tree specified theme."""
    # If already found in theme tree, nothing to do.
    # Otherwise, create it just under the tree root.
    if not main_dic['themes'].search_content(theme_name):
        main_dic['themes'].add_child(NodeTheme(theme_name))


def register_linked_themes(father_theme_name, son_theme_name):
    """Registers, if necessary, in theme tree specified theme with its father.
    """
    # First, do so that father theme exists:
    father_theme = main_dic['themes'].search_content(father_theme_name)
    if not father_theme:
        # Father not existing? Create it at the root.
        #print("Creating father theme '%s' at the root." % (father_theme_name,))
        father_theme = NodeTheme(father_theme_name)
        main_dic['themes'].add_child(father_theme)

    # Here the father exists in all cases.

    # Second, do so that son theme exists:
    son_theme = main_dic['themes'].search_content(son_theme_name)
    #print("son_theme = %s" % (son_theme,))
    if not son_theme:
        #print("Creating non-already existing child theme '%s' and adding it to its father." % (son_theme_name,))
        father_theme.add_child(NodeTheme(son_theme_name))
    else:
        #print("Child theme %s already existing." % (son_theme_name,))
        if not father_theme.search_children(son_theme_name):
            #output_device.debug("Relinking theme '%s' to be a son of theme '%s'." % (son_theme_name, father_theme_name))
            # Here, a is to be b's father but b is currently not his child.
            path = main_dic['themes'].search_path_to_content(son_theme_name)
            previous_father = path[1]
            #print("Adding node '%s' to node '%s'." % (son_theme, father_theme)
            father_theme.add_child(son_theme)

            #print("Cutting node '%s' from node '%s'." % (son_theme, previous_father))
            #print("Removing '%s' from list '%s'." % (son_theme, previous_father.children))
            previous_father.remove_child(son_theme)

            #print("Cut list is '%s'." % (previous_father.children,)


def update_theme_tree(themes_list):
    """
    Gets a list of theme lines and updates accordingly the theme tree.
    """

    for t in themes_list:
        current_theme = None
        parent_theme  = None
        last = None

        # Gets non-empty themes: 'ee: rr:: nn' -> ['ee', 'rr', 'nn']
        themes_in_line = [e.strip() for e in t.split(':') if e.strip() != '']

        #print("themes_in_line = '%s'." % (themes_in_line,))

        if themes_in_line:
            last = themes_in_line.pop()
            register_simple_theme(last)

        while themes_in_line:
            newLast = themes_in_line.pop()
            register_linked_themes(newLast, last)
            last = newLast


def handle_themes_for(graphic_filename, themes_list):
    """
    Returns a string made to be added in a graphics's full page in order
    to link to spotted themes. Creates new themes if necessary.
    """
    direct_theme_dir = os.path.join(token_dic['YAG-OSDL-TOKEN-ROOT-PATH'], resource_directory_name)

    # Put 'T' image:
    if main_dic['language'] == 'French':
        theme_text = u'<p><img src="' + os.path.join(direct_theme_dir, 'theme.png') + '" alt="[Themes]" width="16"></img> :<ul>'
    else:
        theme_text = '<p><img src="' + os.path.join(direct_theme_dir, 'theme.png') + '" alt="[Themes]" width="16"></img> This image belongs to the following themes:<ul>'

    update_theme_tree(themes_list)

    # Add bullet for each spotted theme:
    for t in themes_list:
        #print("handle_themes_for: managing theme '%s'." % (t,))
        theme_text += '<li><a href="' + convert_theme_to_filename(t) + '">%s</a></li>\n' % (t,)
        # Register content in this theme (with absolute content filename):
        handle_theme(t, graphic_filename, os.path.join(token_dic['YAG-OSDL-TOKEN-CONTENT-DIRECTORY'], graphic_filename))

    theme_text += '</ul></p>'

    return theme_text



def get_theme_html_subtree(node, offset=0, next_offset=0, is_first_child=True):
    """
    Returns a stringified description of the tree, in HTML format.

    __ a __ b
              |_ c __ d __ e
                   |_ f
              |_ g

    offset is the current position where to write
    next_offset is the position where children should begin
    """
    res = ""

    # The two branches must have the same length:
    #branch_first = 'x__x'
    #branch_other = 'y|_y'
    branch_first = '<ul><li>  '
    branch_next = '</li><li> '
    branch_last   = '</li></ul>'

    if node.content != 'RootTheme':
        internal_text = '<a href="' + convert_theme_to_filename(node.content) + '">' + node.content + '</a>'
        # Useless:
        #subthemes_count = len(node.children)
        #if subthemes_count:
        #    internal_text += '[%s]" % (subthemes_count,)

        content_count = len(node.referenced_content)
        if content_count:
            internal_text += ' (%s)' % (content_count,)
        this_text = internal_text
    else:
        if main_dic['language'] == 'French':
            this_text = u'Thème racine'
        else:
            this_text = u'Root theme'

    node_text = this_text.ljust(next_offset - offset + 1)

    if is_first_child:
        res += branch_first + node_text
    else:
        #res = offset  * 'z' + branch_next + node_text
        res = offset  * ' ' + branch_next + node_text

    if node.children:
        new_offset = offset + len(branch_first) + len(node_text)

        # Compute max child content total length:
        extra_len = 0
        for child in node.children:
            child_size = len(child.content)
            if child_size > extra_len:
                extra_len = child_size
        new_next_offset = offset + len(branch_first) + extra_len
        res += get_theme_html_subtree(node.children[0], new_offset, new_next_offset, True)
        for c in node.children[1:]:
            res += '\n' + get_theme_html_subtree(c, new_offset, new_next_offset, False)
        res += branch_last
    return res



def generate_theme_main_page():
    """Generates the theme main page, i.e. the theme tree portal."""

    #output_device.debug("Showing HTML theme tree:\n%s" % (get_theme_html_subtree(main_dic['themes']),))
    main_theme_path = os.path.join(main_dic['template_directory'], 'main-page-theme.template.html')

    with open(main_theme_path, 'r', encoding=yag_encoding) as f:
        content = f.read()
    token_dic['YAG-OSDL-THEME-TREE'] = get_theme_html_subtree(main_dic['themes'])
    content = update_from_token_dic(content)
    gen_theme_path = os.path.join(main_dic['output_directory'], yag_general_theme_page)
    with open(gen_theme_path, 'w', encoding=yag_encoding) as f:
        f.write(content)



def generate_first_theme_menu():
    """
    Generates alternate first menu, which displays theme map instead of
    first gallery comment.
    """
    output_dir = main_dic['output_directory']
    first_original_menu = get_menu_path_from_dir(output_dir)

    with open(first_original_menu, 'r', encoding=yag_encoding) as f:
        content = f.read()
    new_content = content.replace('Overview-0.html', yag_general_theme_page)

    theme_menu_path = os.path.join(output_dir, os.path.basename(output_dir) + 'Menu-theme' + html_extension)

    with open(theme_menu_path, 'w', encoding=yag_encoding) as f:
        f.write(new_content)



def generate_all_theme_pages():
    """Generates each theme page and links them together."""
    output_device.info('Generating theme pages')

    theme_dir = os.path.join(main_dic['output_directory'], theme_directory_name)
    if not os.path.exists(theme_dir):
        os.mkdir(theme_dir)

    token_dic['YAG-OSDL-TOKEN-ROOT-PATH'] = ".."

    theme_list = main_dic['themes'].list_depth_first()
    for theme in theme_list:
        generate_theme_pages(theme)

    token_dic['YAG-OSDL-TOKEN-ROOT-PATH'] = "."

    generate_theme_main_page()

    generate_first_theme_menu()


def generate_theme_pages(theme):
    """ Generates page for specified theme."""
    #output_device.info('Generating page for theme '%s'." % (theme.get_name(),))
    template_dir = main_dic['template_directory']

    header_theme_path = os.path.join(template_dir, 'header-theme.template.html')
    with open(header_theme_path, 'r', encoding=yag_encoding) as f:
        content = f.read()

    # List referenced content:
    content += theme.generate_html_referenced_content()

    # List subthemes:
    content += theme.generate_html_sub_themes()

    footer_theme_path = os.path.join(template_dir, 'footer-theme.template.html')

    with open(footer_theme_path, 'r', encoding=yag_encoding) as f:
        content = f.read()

    token_dic['YAG-OSDL-CURRENT-THEME'] = theme.get_name()
    content = update_from_token_dic(content)

    gen_theme_path = os.path.join(main_dic['output_directory'], theme_directory_name, convert_into_filename(theme.get_name()) + html_extension)

    with open(gen_theme_path, 'w', encoding=yag_encoding) as f:
        f.write(content)



def preload_themes():
    """Preloads a standalone theme file defining the main theme
    inheritances."""

    standalone_theme_path = os.path.join(main_dic['content_directory'], yag_general_theme_file)
    if os.path.exists(standalone_theme_path):
        output_device.info("Using standalone theme file '%s'." % (standalone_theme_path,))
        themes_with_eof = []
        with open(standalone_theme_path, 'r', encoding=yag_encoding) as f:
            themes_with_eof = f.readlines()
        decoded_themes = [th for th in themes_with_eof]
        themes = []
        for t in decoded_themes:
            themes.append(t[:-1].strip())
        update_theme_tree(themes)
    else:
        output_device.debug("No standalone theme file ('%s') found." % (standalone_theme_path,))


def show_themes():
    """Prints the theme tree."""
    print("Theme tree is:\n%s" % (main_dic['themes'].to_string(),))


def get_leaf_themes_from(themes):
    """
    Returns a list whose elements are the child themes of specified list, which
    may include elements such as 'a: b': for them we need 'b' to be returned.
    """
    res = []
    for t in themes:
        # Appends last theme:
        res.append([e.strip() for e in t.split(':') if e.strip() != ''].pop())
    return res


def generate_full_page_for_graphic(prev_filename, graphic_filename, next_filename, overview_count):
    """Generates the specified graphic's full web page."""

    #output_device.info("Generating a full web page for graphic file '%s'." % (graphic_filename,))
    template_dir = main_dic['template_directory']
    #output_device.debug("Using '%s' as template directory." % (template_dir,))

    header_page_path = os.path.join(template_dir, 'header-image.template.html')
    with open(header_page_path, 'r', encoding=yag_encoding) as f:
        content = f.read()

    direct_theme_dir = os.path.join(token_dic['YAG-OSDL-TOKEN-ROOT-PATH'], resource_directory_name)

    # Manage comments:
    comment_path = os.path.join(token_dic['YAG-OSDL-TOKEN-CONTENT-DIRECTORY'], convert_into_filename(graphic_filename) + comment_extension)
    if os.path.isfile(comment_path):
        #output_device.info("Using comment file '%s'." % (comment_path,))
        with open(comment_path, 'r', encoding=yag_encoding) as f:
            comment = f.read()
        if comment.strip():
            content += '<br><br><p><img src="' + os.path.join(direct_theme_dir, 'comment.png') + '" alt="[Comment]" width="16"></img> ' + comment + '</p><br><br>'
    else:
        #output_device.debug("No comment file found (tried '%s')." % (comment_path,))
        pass

    # Manage theme:
    theme_path = os.path.join(token_dic['YAG-OSDL-TOKEN-CONTENT-DIRECTORY'], convert_into_filename(graphic_filename) + theme_extension)

    if os.path.isfile(theme_path):
        #output_device.info("Using theme file '%s'." % (theme_path,))
        with open(theme_path, 'r', encoding=yag_encoding) as f:
            themes_with_eof = f.readlines()
        decoded_themes= [th for th in themes_with_eof]
        themes = []
        for t in decoded_themes:
            themes.append(t[:-1].strip())
        update_theme_tree(themes)

        # In the theme file of this image, there may be sub-themes declared as
        # 'a: b'. It means that this image actually belong to child theme b:
        #
        leaf_themes = get_leaf_themes_from(themes)
        if leaf_themes:
            content += handle_themes_for(graphic_filename, leaf_themes)
    else:
        #output_device.debug("No theme file found (tried '%s')." % (theme_file,))
        pass

    content += '<p><center>'

    if prev_filename:
        content += '<a href="' + os.path.basename(get_full_page_filename_from_graphic(prev_filename)) + '"><img src="' + os.path.join(token_dic['YAG-OSDL-TOKEN-ROOT-PATH'], resource_directory_name, 'previous.png') + '" border="0" alt="[Previous]"></img></a> '

    content += ' <a href="Overview-' + repr(overview_count) + '.html' + '"><img src="' + os.path.join(token_dic['YAG-OSDL-TOKEN-ROOT-PATH'], resource_directory_name, 'up.png') + '" border="0" alt="[Up]"></img></a> '

    if next_filename:
        content += ' <a href="' + os.path.basename(get_full_page_filename_from_graphic(next_filename)) + '"><img src="' + os.path.join(token_dic['YAG-OSDL-TOKEN-ROOT-PATH'], resource_directory_name, 'next.png') + '" border="0" alt="[Next]"></img></a> '

    content += "</center></p><br><br>"

    footer_page_path = os.path.join(template_dir, 'footer-image.template.html')

    with open(footer_page_path, 'r', encoding=yag_encoding) as f:
        content += f.read()

    token_dic['YAG-OSDL-CURRENT-CONTENT-TXT'] = graphic_filename
    token_dic['YAG-OSDL-CURRENT-CONTENT-RAW'] = graphic_filename

    content = update_from_token_dic(content)

    with open(get_full_page_filename_from_graphic(graphic_filename), 'w+', encoding=yag_encoding) as f:
        f.write(content)



def get_menu_path_from_dir(directory_name):
    """Returns menu filename corresponding to provided directory."""

    # Translating content path to output one:
    #content_base = token_dic['YAG-OSDL-TOKEN-CONTENT-DIRECTORY']
    #output_path = token_dic['YAG-OSDL-TOKEN-OUTPUT-DIRECTORY']
    #base_path = directory_name.replace(content_base, output_path, 1)
    #menu_path = os.path.join(base_path, os.path.basename(directory_name) + 'Menu' + html_extension)
    menu_path = os.path.join(directory_name, os.path.basename(directory_name) + 'Menu' + html_extension)
    #print("get_menu_path_from_dir: got '%s', returned '%s'." % (directory_name, menu_path))
    return menu_path



def handle_menu_name(menu_name):
    """
    Modifies, if requested, menu name according to settings.
    Ex: dash_is_space_in_menu is handled.
    """
    if not main_dic['dash_is_space_in_menu']:
        return menu_name
    else:
        return menu_name.replace('-', ' ')

    

def generate_menu_for_dir(root_level):
    """Generates menu frame file for a directory."""

    directories, files = get_dir_elements(token_dic['YAG-OSDL-TOKEN-CONTENT-DIRECTORY'])

    target_dir = token_dic['YAG-OSDL-TOKEN-OUTPUT-DIRECTORY']
    menu_path = get_menu_path_from_dir(target_dir)

    if not os.path.exists(target_dir):
        os.mkdir(target_dir)

    output_device.debug("Creating menu file '%s'." % (menu_path,))

    template_dir = main_dic['template_directory']
    #output_device.debug("Using '%s' as template directory." % (template_dir,))

    # Avoids a back button leading to nowhere:

    default_menu_path = handle_menu_name(os.path.basename(token_dic['YAG-OSDL-TOKEN-CONTENT-DIRECTORY']))

    if root_level:
        header_menu_path = os.path.join(template_dir, 'header-first-menu.template.html')
        if main_dic['output_in_content']:
            token_dic['YAG-OSDL-TOKEN-SHORT-CONTENT-DIRECTORY'] = default_menu_path
        else:
            token_dic['YAG-OSDL-TOKEN-SHORT-CONTENT-DIRECTORY'] = os.path.basename(main_dic['output_directory'])
    else:
        header_menu_path = os.path.join(template_dir, 'header-menu.template.html')
        token_dic['YAG-OSDL-TOKEN-SHORT-CONTENT-DIRECTORY'] = default_menu_path

    with open(header_menu_path, 'r', encoding=yag_encoding) as f:
        header_menu_content = f.read()

    footer_menu_path = os.path.join(template_dir, 'footer-menu.template.html')

    with open(footer_menu_path, 'r', encoding=yag_encoding) as f:
        footer_menu_content = f.read()

    with open(menu_path, 'w', encoding=yag_encoding) as f:
        f.write(update_from_token_dic(header_menu_content))

        text_one = '<tr>\n<td align="right"><a href="'
        text_two = update_from_token_dic('" onclick="parent.mainFrame.location=&#39;YAG-OSDL-TOKEN-ROOT-PATH/yag-osdl-resources/black.html&#39;">')

        text_three= '</a></td>\n<td width="15"><a href="'

        text_four = update_from_token_dic('"<img src="YAG-OSDL-TOKEN-ROOT-PATH/yag-osdl-resources/Arrow.png" border="0" alt=""></a></td>\n</tr>\n')

        for d in directories:
            if d not in [resource_directory_name, theme_directory_name]:
                to_write = text_one + d + '/' + d + 'Menu.html' + text_two + handle_menu_name(d) + text_three + d + '/' + d + 'Menu.html' + text_four
                f.write(to_write )

        f.write(update_from_token_dic(footer_menu_content))



def generate_overview(graphics, page_count, total_page_count, comment, root_level):
    """Generates content overview for current directory."""

    #output_device.debug("Generate overview: graphics = %s, page_count = %s, total_page_count = %s." % (graphics, page_count, total_page_count))

    images_per_overview = int(main_dic['images_by_column']) * int(main_dic['images_by_row'])

    if len(graphics) > images_per_overview:
        managed   = graphics[:images_per_overview]
        remainder = graphics[images_per_overview:]
    else:
        managed = graphics
        remainder = []

    template_dir = main_dic['template_directory']

    #print("###### managed = %s" % (managed,))

    header_page_path = os.path.join(template_dir, 'header-gallery.template.html')
    with open(header_page_path, 'r', encoding=yag_encoding) as f:
        header_content = f.read()

    footer_page_path = os.path.join(template_dir, 'footer-gallery.template.html')
    with open(footer_page_path, 'r', encoding=yag_encoding) as f:
        footer_content = f.read()

    overview_path = os.path.join(token_dic['YAG-OSDL-TOKEN-OUTPUT-DIRECTORY'], 'Overview-' + repr(page_count) + html_extension)

    with open(overview_path, 'w', encoding=yag_encoding) as f:
        f.write(update_from_token_dic(header_content))

        if root_level:
            if main_dic['language'] == 'French':
                f.write(u'<p>Sélectionner dans le menu de gauche le mode de navigation que vous préférez, ou toute galerie que vous souhaitez consulter.</p>')
            else:
                f.write(u'<p>Select in the left panel your preferred browsing scheme and any gallery you want to display.</p>')

        if not managed:
            f.write(update_from_token_dic(footer_content))
            return

        graph_count = len(graphics)

        # Computes the number of sub-galleries:
        if not total_page_count:
            total_page_count = graph_count // images_per_overview
            # Last one will not be full:
            if graph_count % images_per_overview:
                total_page_count += 1

        if comment:
            to_write = '<br><br><p><img src="' + os.path.join(token_dic['YAG-OSDL-TOKEN-ROOT-PATH'], resource_directory_name, 'comment.png') + '" width="16" alt="[C]"></img> ' + comment + '</p><br><br>'
            f.write(to_write)

        if total_page_count > 1:
            if page_count == 0:
                if main_dic['language'] == 'French':
                    f.write("Ceci est la première sous-galerie (%s sur %s), pour la galerie %s<br><br> " % (page_count + 1, total_page_count, token_dic['YAG-OSDL-TOKEN-SHORT-CONTENT-DIRECTORY']))
                else:
                    f.write("First sub-gallery (%s out of %s) for gallery %s<br><br> " % (page_count + 1, total_page_count, token_dic['YAG-OSDL-TOKEN-SHORT-CONTENT-DIRECTORY']))
            else:
                if page_count+1 == total_page_count:
                    if main_dic['language'] == 'French':
                        f.write("Ceci est la dernière sous-galerie (%s sur %s), pour la galerie %s<br><br> " % (page_count + 1, total_page_count, token_dic['YAG-OSDL-TOKEN-SHORT-CONTENT-DIRECTORY']))
                    else:
                        f.write("Last sub-gallery (%s out of %s) for gallery %s<br><br> " % (page_count + 1, total_page_count, token_dic['YAG-OSDL-TOKEN-SHORT-CONTENT-DIRECTORY']))
                else:
                    if main_dic['language'] == 'French':
                        f.write(("Ceci est la sous-galerie %s sur %s, pour la galerie %s<br><br> " % (page_count + 1, total_page_count, token_dic['YAG-OSDL-TOKEN-SHORT-CONTENT-DIRECTORY'])))
                    else:
                        f.write(("Sub-gallery %s out of %s for gallery %s<br><br> " % (page_count + 1, total_page_count, token_dic['YAG-OSDL-TOKEN-SHORT-CONTENT-DIRECTORY'])))

        # Not useful enough:
        #else:
        #   f.write((('(Gallery %s has no sub-gallery)<br><br> " % (token_dic['YAG-OSDL-TOKEN-SHORT-CONTENT-DIRECTORY'],))))

        if page_count:
            if page_count == 1:
                if main_dic['language'] == 'French':
                    f.write(u'[<a href="Overview-0.html">Première sous-galerie</a>]')
                else:
                    f.write('[<a href="Overview-0.html">First sub-gallery</a>]')
            else:
               if main_dic['language'] == 'French':
                   f.write((u'[<a href="Overview-' + repr(page_count-1) + '.html">Sous-galerie précédente</a>]'))
               else:
                   f.write(('[<a href="Overview-' + repr(page_count-1) + '.html">Previous sub-gallery</a>]'))

        if remainder:
            if page_count+2 == total_page_count:
                if main_dic['language'] == 'French':
                    f.write((u'[<a href="Overview-' + repr(page_count+1) + '.html">Dernière sous-galerie</a>]'))
                else:
                    f.write((u'[<a href="Overview-' + repr(page_count+1) + '.html">Last sub-gallery</a>]'))
            else:
                if main_dic['language'] == 'French':
                    f.write((u'[<a href="Overview-' + repr(page_count+1) + '.html">Sous-galerie suivante</a>]'))
                else:
                    f.write(('[<a href="Overview-' + repr(page_count+1) + '.html">Next sub-gallery</a>]'))

        if main_dic['language'] == 'French':
            # Removed: '[vignettes] de la galerie
            # YAG-OSDL-TOKEN-SHORT-CONTENT-DIRECTORY':
            #
            f.write(update_from_token_dic(u'<br><br><table border="1" summary="Vignettes pour YAG-OSDL-TOKEN-SHORT-CONTENT-DIRECTORY"><caption>Cliquer sur une des vignettes pour l\'agrandir</caption>'))
        else:
            f.write(update_from_token_dic('<br><br><table border="1" summary="Thumbnails for YAG-OSDL-TOKEN-SHORT-CONTENT-DIRECTORY"><caption>Click a thumbnail to display full version</caption>'))

        for g in managed:
            full_path = os.path.join(token_dic['YAG-OSDL-TOKEN-CONTENT-DIRECTORY'], g)
            size = int(main_dic['thumbsize'])
            generate_thumbnail(full_path, (size, size))

        # Clone the list:
        graphics_to_pop = managed[:]
        graphics_to_pop.reverse()

        if graphics_to_pop:
            for y in range( int(main_dic['images_by_column']) ):
                f.write('<tr>\n')
                for x in range( int(main_dic['images_by_row']) ):
                    if graphics_to_pop:
                        img_filename = graphics_to_pop.pop()
                        to_write = '<td><center><a href="' + os.path.basename(get_full_page_filename_from_graphic(img_filename)) + '"><img src="' + os.path.splitext(img_filename)[0] + '-thumbnail.jpeg" alt="Thumbnail for image ' + img_filename + ' not available"></img><br>'
                        f.write( to_write )

                        comment_filepath = os.path.join(token_dic['YAG-OSDL-TOKEN-CONTENT-DIRECTORY'], convert_into_filename(img_filename) + comment_extension)
                        if os.path.isfile(comment_filepath):
                            with open(comment_filepath, 'r', encoding=yag_encoding) as f:
                                comment = f.read()
                            if comment.strip():
                                to_write = '<img src="' + os.path.join(token_dic['YAG-OSDL-TOKEN-ROOT-PATH'], resource_directory_name, 'comment.png') + '" width="16" alt="[C]"></img> '
                                f.write(to_write)

                        thm_filepath = os.path.join(token_dic['YAG-OSDL-TOKEN-CONTENT-DIRECTORY'], convert_into_filename(img_filename) + theme_extension)
                        if os.path.isfile(thm_filepath):
                            to_write = '<img src="' + os.path.join(token_dic['YAG-OSDL-TOKEN-ROOT-PATH'], resource_directory_name, 'theme.png') + '" width="16" alt="[T]"></img>'
                            f.write(to_write)

                        f.write('</a></center></td>\n')
                    else:
                        break
                f.write('</tr>\n')
                if not graphics_to_pop:
                    break

            if main_dic['language'] == 'French':
                f.write('</table></center></p><br><br><p><b>Navigation rapide selon les noms</b> :<br><br><ul>')
            else:
                f.write('</table></center></p><br><br><p><b>Quick nav-by-name tab</b>:<br><br><ul>')

            for g in managed:
                to_write = '<li>[<a href="' + convert_into_filename(g) + '.html">' + g + '</a>]</li>'
                f.write(to_write)

            f.write('</ul></p>')
            f.write(update_from_token_dic(footer_content))

        if remainder:
            page_count += 1
            generate_overview(remainder, page_count, total_page_count, comment, False)



def remove_thumbnails_from(filenames):
    """Removes the thumbnails from the list of filenames, in order not to generate
    thumbnails for thumbnails in case of multiple yag-osdl runs.
    """
    # PNG or JPEG:
    return [f for f in filenames if f.find('-thumbnail.') == -1]



def process_dir(root_level):
    """Generates all information regarding the specified directory."""

    if os.path.basename(token_dic['YAG-OSDL-TOKEN-CONTENT-DIRECTORY']) == resource_directory_name:
        print("Ignoring yag's own resource directory '%s'." % (resource_directory_name,))

    output_device.debug("Processing %s." % (token_dic['YAG-OSDL-TOKEN-CONTENT-DIRECTORY'],))
    generate_menu_for_dir(root_level)
    graphics, sounds, unknown = scan_dir_for_content(token_dic['YAG-OSDL-TOKEN-CONTENT-DIRECTORY'])

    graphics = remove_thumbnails_from(graphics)

    # Allows to sort images according to lexical order:
    graphics.sort()

    previous, current = None, None
    image_count = 0
    overview_count = 0
    images_per_overview = int(main_dic['images_by_column']) * int(main_dic['images_by_row'])
    for next in graphics:
        if current:
            image_count += 1
            if image_count == images_per_overview + 1:
                overview_count += 1
                image_count = 1
            generate_full_page_for_graphic(previous, current, next, overview_count)
        previous = current
        current = next
        next = None

    if current:
        if image_count == images_per_overview + 1:
            overview_count += 1
        generate_full_page_for_graphic(previous, current, next, overview_count)

    comment_filepath = os.path.join(token_dic['YAG-OSDL-TOKEN-CONTENT-DIRECTORY'], gallery_comment_filename)

    gallery_comment = None

    if os.path.isfile(comment_filepath):
        with open(comment_filepath, 'r', encoding=yag_encoding) as f:
            gallery_comment = f().read()

    generate_overview(graphics, 0, None, gallery_comment, root_level)



def scan_content(content_dir, output_dir, root_path):
    """Scans content from specified directory. Will be first called with only
    one argument, then will recursing will add a second order, to keep track of
    base directory.
    """
    output_device.debug("Scanning from content directory '%s', will write in '%s', with root directory being '%s'..." % (content_dir, output_dir, root_path))

    # Updating the token directory:
    token_dic['YAG-OSDL-TOKEN-CONTENT-DIRECTORY'] = content_dir
    token_dic['YAG-OSDL-TOKEN-OUTPUT-DIRECTORY']  = output_dir
    token_dic['YAG-OSDL-TOKEN-ROOT-PATH']         = root_path

    output_device.debug("Processing content directory")
    #output_device.debug("Subdirectories are '%s'." % (file_utils.get_children_dirs(content_dir),))
    process_dir(root_path == '.')

    # Recursing:
    for d in file_utils.get_children_dirs(content_dir):
        # Do not index our own resource directory! (it has however to be
        # self-contained in output directory)
        if d != resource_directory_name:
            #print("scan_content: recursing in '%s'." % (d,))
            token_dic['YAG-OSDL-TOKEN-PARENT-DIRECTORY'] = output_dir
            token_dic['YAG-OSDL-TOKEN-PARENT-SHORT-DIRECTORY'] = os.path.basename(output_dir)
            scan_content(os.path.join(content_dir, d), os.path.join(output_dir, d), os.path.join(root_path, '..'))



def install_helper_files():
   """Installs helper file in output directory."""
   # Install the helper files (ex: css):
   target_helper_dir = os.path.join(main_dic['output_directory'], resource_directory_name)

   output_device.debug("Installing helper files from '%s' to '%s'." % (main_dic['helper_files_directory'], target_helper_dir))
   if os.path.exists(target_helper_dir):
       output_device.debug("Deleting previously existing resource directory.")
       shutil.rmtree(target_helper_dir)
   shutil.copytree(main_dic['helper_files_directory'], target_helper_dir)
   for f in file_utils.get_files_in_dir(os.path.join(main_dic['theme_directory'], 'images')):
       shutil.copy(os.path.join(main_dic['theme_directory'], 'images', f), target_helper_dir)
   shutil.copy(os.path.join(target_helper_dir, 'Page.css'), os.path.join(target_helper_dir, main_dic['theme']) + '.css')



def generate_gallery_main_page():
    """Generates main page for gallery."""
    target_filepath = os.path.join(main_dic['output_directory'], 'Main' + to_filename(main_dic['project_name']) + html_extension)
    output_device.debug("Gallery main page will be '%s'." % (target_filepath,))
    shutil.copy(os.path.join(main_dic['theme_directory'], 'templates', 'main-page-gallery.template.html'), target_filepath)
    with open(target_filepath, 'r', encoding=yag_encoding) as f:
        updated_content = f.read()

    with open(target_filepath, 'w', encoding=yag_encoding) as f:
        f.write(update_from_token_dic(updated_content))



def generate_gallery_frameset():
    """Generates frameset for gallery."""
    output_dir = main_dic['output_directory']
    target_filepath = os.path.join(output_dir, to_filename(main_dic['project_name']) + html_extension)
    output_device.debug("Gallery frameset will be '%s'." % (target_filepath,))
    token_dic['YAG-OSDL-TOKEN-FIRST-MENU'] = os.path.basename(token_dic['YAG-OSDL-TOKEN-MENU'])

    frameset_template = os.path.join(main_dic['theme_directory'], 'templates', 'frameset.template.html')

    shutil.copy(frameset_template, target_filepath)

    with open(target_filepath, 'r', encoding=yag_encoding) as f:
        updated_content = update_from_token_dic(f.read())

    with open(target_filepath, 'w', encoding=yag_encoding) as f:
        f.write( updated_content )

    save = token_dic['YAG-OSDL-TOKEN-FIRST-MENU']
    token_dic['YAG-OSDL-TOKEN-FIRST-MENU'] = save.replace('.html', '-theme.html')

    target_filepath_thm = os.path.join(output_dir, to_filename(main_dic['project_name']) + '-theme' + html_extension)
    shutil.copy(frameset_template, target_filepath_thm)

    with open(target_filepath_thm, 'r', encoding=yag_encoding) as f:
        updated_content = update_from_token_dic(f.read())

    with open(target_filepath_thm, 'w', encoding=yag_encoding) as f:
        f.write(updated_content)

    token_dic['YAG-OSDL-TOKEN-FIRST-MENU'] = save



def generate_loading_page():
    """Generates the gallery loading page."""
    source_filepath = os.path.join(main_dic['theme_directory'], 'templates', 'black.template.html')
    target_filepath = os.path.join(main_dic['output_directory'], resource_directory_name, 'black.html')
    #output_device.debug("Loading page will be '%s'." % (target_filepath,))
    #output_device.debug("Copy from '%s' to '%s'." % (source_filepath, target_filepath))
    shutil.copy(source_filepath, target_filepath)

    with open(target_filepath, 'r', encoding=yag_encoding) as f:
        updated_content = update_from_token_dic(f.read())

    with open(target_filepath, 'w', encoding=yag_encoding) as f:
        f.write(updated_content)



def main(content_dir=None, config_filename=None):
    """Main function, controller of the yag-osdl.
    Must be called with:
        - content_directory, the name of the directory with content to scan
        - optionally, config_filename, the filename of the configuration file

    Other main information such as:
        - theme_name, the name of the theme to be used
        - resource_directory, the name of the directory containing resources
    such as templates and images necessary to generate the content website, etc.
    are to be found from config_filename, otherwise will take default values.
    """

    global main_dic, token_dic
    global output_device

    # Select log output:
    output_device = general_utils.ScreenDisplay()

    current_dir = os.getcwd()

    # Original hardcoded dictionary for the defaults:
    main_dic = {
            'project_name'         : 'Project name not specified',
            'content_directory'    : content_dir,
            'resource_directory'   : os.path.join(current_dir, 'resources'),
            'output_in_content'    : "False",
            'output_directory'     : os.path.join(current_dir, 'output'),
            'language'             : 'English',
            'theme'                : 'Default-theme',
            'thumbsize'            : '60',
            'images_by_row'        : '3',
            'images_by_column'     : '3',
            'dash_is_space_in_menu': "False",
            'author'               : 'Author not specified',
            'author_mail'          : 'Author mail not specified',
            'gallery_license_file' : None,
            'gallery_info_file'    : None,
            'themes'               : NodeTheme("RootTheme")
    }

    if config_filename:
        if not os.path.isfile(config_filename):
            raise YagException("Specified configuration file '%s' does not exist." % (config_filename,))
        output_device.info("Using configuration file '%s'." % (config_filename,))
        update_config_from_file(main_dic, config_filename)
    else:
        output_device.info("No configuration file supplied, using hardcoded defaults.")

    # Converts booleans-as-strings into actual booleans (ex: from "False" to
    # False):

    output_in_c_bool = bool( distutils.util.strtobool( main_dic['output_in_content'] ) )
    main_dic['output_in_content'] = output_in_c_bool

    dash_bool = bool( distutils.util.strtobool( main_dic['dash_is_space_in_menu'] ) )
    main_dic['dash_is_space_in_menu'] = dash_bool


    # Avoid any slash at the end of path:
    content_dir = os.path.normpath( main_dic['content_directory'] )

    if not content_dir:
        raise YagException("No content directory to scan has been specified, neither through command line nor configuration file.")

    if not os.path.isdir(content_dir):
        raise YagException("Content directory '%s' not found." % (content_dir,))

    main_dic['content_directory'] = content_dir


    output_device.debug("Checking resource directories...")

    resource_directory = check_directory(main_dic['resource_directory'])

    theme_directory = check_directory(os.path.join(resource_directory, 'themes', main_dic['theme']))

    image_directory        = check_directory(os.path.join(theme_directory, 'images'))
    template_directory     = check_directory(os.path.join(theme_directory, 'templates'))
    helper_files_directory = check_directory(os.path.join(theme_directory, 'helper-files'))

    main_dic['theme_directory']        = theme_directory
    main_dic['image_directory']        = image_directory
    main_dic['template_directory']     = template_directory
    main_dic['helper_files_directory'] = helper_files_directory

    # Now we prefer raising an exception if generating output outside of content
    # whereas the corresponding directory already exists (done later):
    #
    #main_dic['output_directory'] = file_utils.find_next_new_dir_name(main_dic['output_directory'])

    output_device.debug("Showing the validated settings...")
    general_utils.display_dic(main_dic)

    # If an image is not available, alternative text will be displayed.
    navigation_images = add_prefix_to_filenames(image_directory, ['index.png', 'next.png', 'previous.png', 'up.png', 'down.png', 'root.png'])

    # All templates files must be here:
    templates_files = add_prefix_to_filenames(template_directory, ['header-menu.template.html', 'footer-menu.template.html', 'header-gallery.template.html', 'footer-gallery.template.html', 'header-image.template.html', 'footer-image.template.html'])

    if not do_all_files_exist(templates_files):
        raise YagException("Not all template files available in template directory %s." % (template_directory,))

    output_device.debug("All template files found.")

    # Will work even if those are not found:
    #html_files = add_prefix_to_filenames(helper_files_directory, ['Menu.css', 'Page.css'])

    # By construction, output_directory should point to a non-existing
    # directory. Creating it unconditionnally if we are not to create website
    # among existing content:
    #
    if main_dic['output_in_content']:
        output_dir = main_dic['content_directory']
        output_device.debug("Setting output directory to content one, '%s'." % (output_dir,))
        main_dic['output_directory'] = output_dir
    else:
        output_dir = main_dic['output_directory']
        if os.path.exists(output_dir):
            raise YagException("Output directory '%s' already exists, please remove it first." % (output_dir,))
        else:
            output_device.debug("Creating output directory '%s'." % (output_dir,))
            os.mkdir(output_dir)

    resource_dir = os.path.join(main_dic['output_directory'], resource_directory_name)
    if not os.path.exists(resource_dir):
        os.mkdir(resource_dir)

    init_token_dic()

    # Shows the token substitutions:
    #general_utils.display_dic(token_dic)

    preload_themes()

    # Starts the recursive indexing:
    root_path = '.'
    scan_content(content_dir, output_dir, root_path)

    token_dic['YAG-OSDL-TOKEN-MENU'] = os.path.join(output_dir, os.path.basename(output_dir))  + 'Menu' + html_extension

    install_helper_files()
    generate_loading_page()
    generate_gallery_main_page()
    generate_gallery_frameset()
    generate_all_theme_pages()

    homepage = os.path.join(output_dir, 'index.html')

    shutil.copy( os.path.join(output_dir, 'Main' + to_filename(main_dic['project_name']) + html_extension), homepage )
    print("\n    You can browse your new gallery from file://%s\n    Enjoy!\n"  % (homepage,))


######## End of functions #########



#### Beginning of top-level code. ####

#import atexit
# Clean up at any exit.
#atexit.register(cleanUp)


if __name__ == '__main__':

    #import os, sys, shutil, Image, tempfile, time

    #from PIL import Image

    # Python2:
    #import ConfigParser

    # Python3:
    #import configparser

    # Be user-friendly!
    general_utils.activate_name_completion()

    # Checks command line arguments.
    # In case of error or wrong syntax, use defaults.
    # Commmand line defaults:
    #
    default_config_file = 'yag-osdl.conf'
    config_file = None
    source  = False

    help_opts    = ['-h',  '--help']
    config_opts  = ['-rc', '--config']
    version_opts = ['-v',  '--version']

    all_opts = help_opts + config_opts + version_opts

    content_dir = None

    option_start = 1

    #print("Specified arguments are '%s'." % (sys.argv,))

    if len(sys.argv) > 1 and sys.argv[1] not in all_opts:
        content_dir = sys.argv[1]
        option_start = 2

    item_count = option_start

    for item in sys.argv[option_start:]:

        #print("Examining argument '%s'." % (item,)
        item_count += 1

        if item in help_opts:
            print(__doc__)
            sys.exit(0)

        if item in config_opts:
            print("Configuration option detected.")
            try:
                config_file = sys.argv[item_count]
            except IndexError:
                config_file = default_config_file
            print("Configuration file will be '%s'." % (config_file,))

        if item in version_opts:
            print("This is yag-osdl version %s." % (yag_osdl_version,))
            sys.exit(0)

    if not config_file:
        if os.path.exists(default_config_file):
            print("No configuration file specified; found and using default one, '%s'." % (default_config_file,))
            config_file = default_config_file

    # Start with main():

    if content_dir:
        print("Content directory specified through command line is '%s'." % (content_dir,))
    else:
        print("No content directory specified through command line.")

    if config_file:
        print("Configuration file is '%s'." % (config_file,))
    else:
        print("No configuration file found.")

    main(content_dir, config_file)
