#!/usr/bin/env python


"""
  This is yag-osdl (OSDL's YAG), a thematical GPL-licensed HTML multimedia
  gallery generator.
  
  YAG stands for Yet Another Gallery, and yag-osdl is derived from the following
  work: YAG, Copyright (C) 2002 Stas Z
  (see http://home.planet.nl/~stas.linux/python/yag/)
  
  To use yag-osdl easily, one should source included 'yag-osdl-environment.sh'
  to have one's shell variables correctly checked and set.
  Or, even better, use 'run-yag-osdl.sh'
  
  This script is named yagosdl.py and not yag-osdl.py since '-' are not 
  allowed in the name of python modules.
  
  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  Usage: yagosdl.py [content directory] [-h]

    -h  Help. Displays this usage message and exits.

    -v Version. Shows yag-osdl's version and exits.
	
  The following arguments override the options from the configuration file.

    -rc name. Alternative configuration file to be used. 
        If it cannot be found the standard yag-osdl.conf file will be used.

    -th name.  Name of the theme to be used. If the theme can't be found,
        or if it's not in the right format, the theme from the standard
        configuration file will be used.
		
		
	This program is free software; you can redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation.

	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License
	along with this program; see the file COPYING. If not, write to
	the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.

	yag-osdl creates a static html gallery consisting of a index pages with 
	thumbnails links to pages with the original pictures, and adds pages 
	allowing to browse the image repository through thematical collections.	
		
"""


# Imports standard python modules:
import os, os.path, sys, string, shutil, tempfile, ConfigParser, time

# PIL (Picture Image Library, see http://www.pythonware.com/library/pil/handbook/index.htm)
import Image

# Imports self-made generic modules:
from toolbox import *

# Imports basic common services:
import generalUtils

# Imports file extended services:
import fileUtils

# Imports data services for trees of themes:
import dataUtils



yag_osdl_version = 0.6

yag_general_theme_file = 'yag-overall-themes.thm'
yag_general_theme_page = 'yag-theme-map.html'
htmlExtension    = '.html'
jpegExtension    = '.jpeg'
commentExtension = '.txt'
themeExtension   = '.thm'


# if you change it, change it too in template files:
resourceDirectoryName = 'yag-osdl-resources'
themeDirectoryName    = 'yag-osdl-parsed-themes'

galleryCommentFilename = 'yag-gallery-comment.txt'


class YagException( ApplicationException ):
    """Base class for exceptions raised in yag-osdl module."""
     

class NodeTheme( dataUtils.Node ):
	"""
	Describes a theme, whose children are sub-themes, whose content is the theme name.
	Each NodeTheme carries to a list of tuples (content name, content's full web page) 
	corresponding to all media content belonging to this theme.
	"""
	
	
	def __init__( self, name ):
		dataUtils.Node.__init__( self )
		self.referencedContent = []
		self.content = name


	def addContent( self, contentName, contentpageFileName ):
		"""
		Adds a tuple (content name, content's full web page) corresponding 
		to media content belonging to this theme.
		""" 
		# As contentpageFileName is an absolute path it has to be converted 
		# in a relative one:
		new_relative_path = '..' + contentpageFileName.replace( mainDic[ 'content_directory' ], '' )
		self.referencedContent.append( (contentName, new_relative_path ) )
		
		
	def getName( self ):
		return self.content
		
			
	def generateHTMLReferencedContent( self ):
		"""
		Returns the HTML code corresponding to the referenced content belonging
		to this theme.
		"""
		
		res = "<p>"
		if len( self.referencedContent ):
			res += "This theme references following content:\n<ul>"
			for t in self.referencedContent:
				content_name, content_page_file = t
		 		res += '\t<li><a href="%s">%s</a></li>' % ( content_page_file, content_name )
			res += "</ul>"
		else:
			res += "This theme does not reference directly any content."
		return res + "</p>"	



	def generateHTMLSubThemes( self ):
		"""Returns the HTML code corresponding to the referenced content belonging to this theme."""
		
		res = "<p>"
		if len( self.getChildren() ):	
			if len( self.getChildren() ) == 1:
				res += 'This theme has ony one sub-theme: <a href="%s">%s</a>' % ( convertThemeToFilename( self.children[0].getName() ), self.children[0].getName() )
			else:
				res += "This theme has following sub-themes:\n<ul>"
				for c in self.getChildren():
		 			res += '\t<li><a href="%s">%s</a></li>' % ( convertThemeToFilename( c.getName() ), c.getName() )
				res += "</ul>"
		else:
			res += "This theme has no sub-theme."
		return res + "</p>"	
	


def initTokenDic():
	"""Put hardcoded default values in token dictionary."""
	
	global tokenDic	
	
	# Token dictionary keeps current value:
	
	tokenDic = { 
		'YAG-OSDL-TOKEN-PROJECT-NAME'     : mainDic[ 'project_name' ],	
		'YAG-OSDL-TOKEN-DATE'             : time.strftime( '%A, %d %B %Y', time.localtime() ),
		'YAG-OSDL-TOKEN-GENERATOR'        : str(yag_osdl_version),
		'YAG-OSDL-TOKEN-CONTENT-DIRECTORY': mainDic[ 'content_directory' ],	
		'YAG-OSDL-TOKEN-OUTPUT-DIRECTORY' : mainDic[ 'output_directory' ],
		'YAG-OSDL-TOKEN-THEME'            : mainDic[ 'theme' ],
		'YAG-OSDL-TOKEN-ROOT-PATH'        : None,
		'YAG-OSDL-CURRENT-CONTENT-RAW'    : None,
		'YAG-OSDL-CURRENT-CONTENT-TXT'    : None,
		'YAG-OSDL-CURRENT-THEME'          : None,
		'YAG-OSDL-GALLERY-LICENSE'        : '',
		'YAG-OSDL-GALLERY-INFO'           : '',
		'YAG-OSDL-THEME-TREE'             : ''
	} 
	
	if mainDic[ 'author' ]:
		tokenDic[ 'YAG-OSDL-TOKEN-AUTHOR' ] = mainDic[ 'author' ]
	else:
		tokenDic[ 'YAG-OSDL-TOKEN-AUTHOR' ] = '(no author was specified)'
	
	if mainDic[ 'author_mail' ]:
		tokenDic[ 'YAG-OSDL-TOKEN-CONTACT' ] = mainDic[ 'author_mail' ]
	else:
		tokenDic[ 'YAG-OSDL-TOKEN-CONTACT' ] = '(no mail address was specified)'
	
	license_file = mainDic[ 'gallery_license_file' ]
	if license_file:
		if os.path.isfile( license_file ):
			outputDevice.debug( 'Gallery license file found (<%s>).' % ( license_file, ) )
			tokenDic[ 'YAG-OSDL-GALLERY-LICENSE' ] = '<br><h2>Gallery license</h2><p>' + file( license_file, 'r' ).read() + '</p>'
		else:
			outputDevice.debug( 'Gallery license file not found (<%s>).' % ( license_file, ) )
			
	else:
		outputDevice.debug( 'No gallery license file specified.' )			
	
	info_file = mainDic[ 'gallery_info_file' ]
	if info_file:
		if os.path.isfile( info_file ):
			outputDevice.debug( 'Gallery information file found (<%s>).' % ( info_file, ) )
			tokenDic[ 'YAG-OSDL-GALLERY-INFO' ] = '<br><h2>Gallery recommended usage &amp; hints</h2><p>' + file( info_file, 'r' ).read() + '</p><br>'
		else:
			outputDevice.debug( 'Gallery information file not found (<%s>).' % ( info_file, ) )
	else:
		outputDevice.debug( 'No gallery information file specified.' )			

	
						
def generateThumbnail( imageFilename, thumbnailSizePair ):
	"""
	Generates a JPEG thumbnail for specified image, no matter its original format. 
	The thumbnail will be no bigger than specified size, aspect ratio is preserved.
	Ex: generateThumbnail( 'MyPicture.png', (100, 120) ).
	"""
	
	thumbnailFile = os.path.join( tokenDic[ 'YAG-OSDL-TOKEN-OUTPUT-DIRECTORY' ], os.path.splitext( imageFilename )[0] + '-thumbnail.jpeg' )
	
	#outputDevice.debug( 'Thumbnailing <%s> in <%s> with size %s.' % ( imageFilename, thumbnailFile, `thumbnailSizePair` ) )
	
	outputDevice.info( 'Thumbnailing <%s> with size %s.' % ( imageFilename, `thumbnailSizePair` ) )
	
	imageFilename = os.path.join( tokenDic[ 'YAG-OSDL-TOKEN-OUTPUT-DIRECTORY' ], imageFilename )
	
	if not os.path.exists( imageFilename ):
		raise YagException, 'generateThumbnail: image file <%s> not found.' %  ( imageFilename, )
	try:
		image = Image.open( imageFilename )
		if image.mode != 'RGB':
			image = img.convert('RGB')
		image.thumbnail( thumbnailSizePair, Image.ANTIALIAS )
		image.save( thumbnailFile, 'JPEG' )
	except IOError:
		raise YagException, 'Cannot create thumbnail for <%s> (I/O error).' %  ( imageFilename, )
	except:
		raise YagException, 'Cannot create thumbnail for <%s>.' %  ( imageFilename, )



def getFullPageFilenameFromGraphic( graphicFileName ):
	"""Returns a file name corresponding to the specified graphic file."""
	return os.path.join( tokenDic[ 'YAG-OSDL-TOKEN-OUTPUT-DIRECTORY' ], convertIntoFileName( graphicFileName ) + htmlExtension )
	
	
	
def updateFromTokenDic( aString ):
	"""Replaces in specified string all key listed in token dictionary by their value."""
	for ( k, v ) in tokenDic.items():
		#outputDevice.debug( 'Replacing token <%s> by <%s>.' % ( k, v ) )
		if type( v ) == type( 'a string'):
			aString = aString.replace( k, v )
		else:	
			aString = aString.replace( k, `v` )
	return aString
	
	
def convertThemeToFilename( theme ):
	"""Converts specified theme name into the full filename of its dedicated page."""
	return os.path.join( tokenDic[ 'YAG-OSDL-TOKEN-ROOT-PATH' ], themeDirectoryName, convertIntoFileName( theme ) + htmlExtension )

	
def handleTheme( themeName, contentName, contentFileName ):
	"""Take care of specified theme: link it to others, records its elements."""
	foundTheme = mainDic[ 'themes' ].searchContent( themeName )
	# Theme not found, create it at the root of the theme tree:
	if not foundTheme:
		foundTheme = NodeTheme( themeName )
		mainDic[ 'themes' ].addChild( foundTheme )
	# We've got to provide to addContent not the contentFileName but its page:
	foundTheme.addContent( contentName, convertIntoFileName( contentFileName ) 
		+ htmlExtension )


def registerSimpleTheme( theme_name ):
	"""Registers, if necessary, in theme tree specified theme."""
	# If already found in theme tree, nothing to do.
	# Otherwise, create it just under the tree root.
	if not mainDic[ 'themes' ].searchContent( theme_name ):
		mainDic[ 'themes' ].addChild( NodeTheme( theme_name ) )
	
	
def registerLinkedThemes( father_theme_name, son_theme_name ):
	"""
	Registers, if necessary, in theme tree specified theme with its father.	
	"""		
	# First, do so that father theme exists:
	fatherTheme = mainDic[ 'themes' ].searchContent( father_theme_name )
	if not fatherTheme:
		# Father not existing ? Create it at the root.
		#print "Creating father theme %s at the root" % (father_theme_name,)
		fatherTheme = NodeTheme( father_theme_name )
		mainDic[ 'themes' ].addChild( fatherTheme )
	# Here the father exists in all cases.
		
	# Second, do so that son theme exists:
	sonTheme = mainDic[ 'themes' ].searchContent( son_theme_name )
	#print "sonTheme = %s" % (sonTheme,)
	if not sonTheme:
		#print "Creating non-already existing child theme %s and adding it to its father" % (son_theme_name,)
		fatherTheme.addChild( NodeTheme( son_theme_name ) )
	else:
		#print "Child theme %s already existing" % (son_theme_name,)
		if not fatherTheme.searchChildren( son_theme_name ):
			outputDevice.debug( "Relinking theme '%s' to be a son of theme '%s'." % ( son_theme_name, father_theme_name ) )
			# Here, a is to be b's father but b is currently not his child.
			path = mainDic[ 'themes' ].searchPathToContent( son_theme_name )
			previous_father = path[1]
			#print 'Adding node <%s> to node <%s>' % ( sonTheme, fatherTheme )
			fatherTheme.addChild( sonTheme )
			
			#print 'Cutting node <%s> from node <%s>.' % ( sonTheme, previous_father)
			#print 'Removing <%s> from list <%s>' % ( sonTheme, previous_father.children )
			previous_father.removeChild( sonTheme )
				
			#print 'Cut list is <%s>' % (previous_father.children,)
			
	
def updateThemeTree( themes_list ):
	"""
	Gets a list of theme lines and updates accordingly the theme tree.
	"""	
	
	for t in themes_list:
		current_theme = None
		parent_theme  = None
		last = None
		
		# Gets non-empty themes: 'ee: rr:: nn' -> ['ee', 'rr', 'nn']
		themes_in_line = [ e.strip() for e in t.split( ':' ) if e.strip() != '' ]

		#print "themes_in_line = %s" % (themes_in_line,)
		
		if len( themes_in_line ) != 0:
			last = themes_in_line.pop()
			registerSimpleTheme( last )
			 
		while len( themes_in_line ) > 0:
			newLast = themes_in_line.pop()
			registerLinkedThemes( newLast, last )
			last = newLast
	
	
def handleThemesFor( graphicFileName, themes_list ):
	"""
	Returns a string made to be added in a graphics's full page in order 
	to link to spotted themes. Creates new themes if necessary.
	"""	
	direct_theme_dir = os.path.join( tokenDic[ 'YAG-OSDL-TOKEN-ROOT-PATH' ],
		resourceDirectoryName )
	# Put 'T' image:
	theme_text = '<p><img src="' + os.path.join( direct_theme_dir, 'theme.png' ) + '" alt="[Themes]" width="16"></img> This image belongs to the following themes:<ul>'
	
	updateThemeTree( themes_list )

	# Add bullet for each spotted theme:
	for t in themes_list:	
		#print "handleThemesFor: managing theme '%s'" % (t,)		
		theme_text += '<li><a href="' + convertThemeToFilename( t ) + '">%s</a></li>\n' % ( t, )
		# Register content in this theme (with absolute content filename):
		handleTheme( t, graphicFileName, os.path.join( tokenDic [ 'YAG-OSDL-TOKEN-CONTENT-DIRECTORY' ], graphicFileName ) )
	theme_text += '</ul></p>'
	
	return theme_text		



def getThemeHTMLSubTree( node, offset = 0, nextOffset = 0, isFirstChild = True ):
	"""
	Returns a stringified description of the tree, in HTML format.

	__ a __ b
		  |_ c __ d __ e
					|_ f
		  |_ g

	offset is the current position where to write
	nextOffset is the position where children should begin	
	""" 
	res= ""

	# The two branches must have the same length:
	#branchFirst = 'x__x'
	#branchOther = 'y|_y'
	branchFirst = '<ul><li>  '
	branchOther = '</li><li> '
	branchEnd   = '</li></ul>'
    
	if node.content != 'RootTheme':
		internal_text = '<a href="' + convertThemeToFilename( node.content ) + '">' + node.content + '</a>'
		# Useless:
		#subthemes_count = len( node.children )
		#if subthemes_count:			   
		#	internal_text += '[%s]' % ( subthemes_count,) 
				
		content_count = len( node.referencedContent )
		if content_count:			   
			internal_text += ' (%s)' % ( content_count,) 
				
		node_text = string.ljust( internal_text, nextOffset - offset + 1 )	
	else:
		node_text = string.ljust( 'Root theme', nextOffset - offset + 1 )	
						
	if isFirstChild:
		res += branchFirst + node_text
	else:
		#res =  offset  * 'z' + branchOther + node_text
		res =  offset  * ' ' + branchOther + node_text
       
	if len( node.children ):
		newOffset = offset + len( branchFirst ) + len(node_text)
       
		# Compute max child content total length:
		extraLength = 0
		for child in node.children:
			child_size = len( child.content )
			if child_size > extraLength:
				extraLength = child_size
		newNextOffset = offset + len( branchFirst ) + extraLength
		res += getThemeHTMLSubTree( node.children[0], newOffset, newNextOffset, True )
		for c in node.children[1:]:
			res += '\n' + getThemeHTMLSubTree( c, newOffset, newNextOffset, False )		  
		res += branchEnd
	return res  



def generateThemeMainPage():
	"""Generates the theme main page, i.e. the theme tree portal."""
	#outputDevice.debug( 'Showing HTML theme tree:\n%s' % ( getThemeHTMLSubTree( mainDic[ 'themes' ] ), ) ) 
	main_theme_file = file( os.path.join( mainDic[ 'template_directory' ], 'MainPageTheme.template.html' ), 'r' )
	content = main_theme_file.read()
	tokenDic[ 'YAG-OSDL-THEME-TREE' ] = getThemeHTMLSubTree( mainDic[ 'themes' ] )
	content = updateFromTokenDic( content )
	file( os.path.join( mainDic[ 'output_directory' ], yag_general_theme_page ), 'w' ).write( content )


	
def	generateFirstThemeMenu():
	"""
	Generates alternate first menu, which displays theme map instead of 
	first gallery comment.
	"""
	first_original_menu = os.path.join( mainDic[ 'content_directory' ], os.path.basename( mainDic[ 'content_directory' ] ) + 'Menu.html' )
	
	content = file( first_original_menu, 'r' ).read()
	new_content = content.replace( 'Overview.html', yag_general_theme_page )
	
	theme_menu_file = file( os.path.join( mainDic[ 'content_directory' ], os.path.basename( mainDic[ 'content_directory' ] ) + 'Menu-theme.html' ), 'w' )
	
	theme_menu_file.write( new_content )
	
	
def generateThemePages():
	"""Generates each theme page and links them together."""	
	outputDevice.info( 'Generating theme pages' )
	
	themeDir = os.path.join( mainDic[ 'output_directory' ], themeDirectoryName )
	if not os.path.exists( themeDir ):
		os.mkdir( themeDir )

	tokenDic[ 'YAG-OSDL-TOKEN-ROOT-PATH' ] = ".."
	
	theme_list = mainDic[ 'themes' ].listDepthFirst()
	for theme in theme_list:
		generateThemePage( theme )
		
	tokenDic[ 'YAG-OSDL-TOKEN-ROOT-PATH' ] = "."
		
	generateThemeMainPage()

	generateFirstThemeMenu()


def generateThemePage( theme ):
	""" Generates page for specified theme."""
	outputDevice.info( 'Generating page for theme <%s>.' % ( theme.getName(), ) ) 
	template_dir = mainDic[ 'template_directory' ]
	header_theme_file = file( os.path.join( template_dir, 'HeaderTheme.template.html' ), 'r' )
	footer_theme_file = file( os.path.join( template_dir, 'FooterTheme.template.html' ), 'r' )
	
	content = header_theme_file.read()
	
	# List referenced content:
	content += theme.generateHTMLReferencedContent()
		
	# List subthemes:
	content += theme.generateHTMLSubThemes()
			
	content += footer_theme_file.read()
	
	tokenDic[ 'YAG-OSDL-CURRENT-THEME' ] = theme.getName()
	content = updateFromTokenDic( content )
	
	file( os.path.join( mainDic[ 'output_directory' ], themeDirectoryName, convertIntoFileName( theme.getName() ) + htmlExtension ), 'w' ).write( content ) 
		
	
	
def preloadThemes():
	"""Preloads a standalone theme file defining the main theme inheritances."""
	standalone_theme_file = os.path.join( mainDic[ 'output_directory' ], yag_general_theme_file )
	if os.path.exists( standalone_theme_file ):
		outputDevice.info( 'Using standalone theme file <%s>.' % ( standalone_theme_file, ) )	
		themes_with_eof = file( standalone_theme_file, 'r' ).readlines()
		themes = []
		for t in themes_with_eof:
			themes.append( t[:-1].strip() )
		updateThemeTree( themes )		
	else:
		outputDevice.debug( 'No standalone theme file (<%s>) found.' % ( standalone_theme_file, ) )	
		

def showThemes():
	"""Prints the theme tree."""
	print "Theme tree is:\n%s" % ( mainDic[ 'themes' ].toString(),)
	
	
def getLeafThemesFrom( themes ):
	"""Returns a list whose elements are the child themes of specified list,
	which may include elements such as 'a: b': for them we need 'b' to be 
	returned.
	"""
	res=[]
	for t in themes:
		# Appends last theme:
		res.append( [ e.strip() for e in t.split( ':' ) if e.strip() != '' ].pop() )
	return res
			
			
def generateFullPageForGraphic( previousFileName, graphicFileName, nextFileName, overview_count ):
	"""Generates the specified graphic's full web page."""
	outputDevice.info( 'Generating a full web page for graphic file <%s>.' % ( graphicFileName, ) ) 
	graphFile = file( getFullPageFilenameFromGraphic( graphicFileName ), 'w+' )
	template_dir = mainDic[ 'template_directory' ]
	#outputDevice.debug( 'Using <%s> as template directory.' % ( template_dir, ) )
	
	header_page_file = file( os.path.join( template_dir, 'HeaderImage.template.html' ), 'r' )
	footer_page_file = file( os.path.join( template_dir, 'FooterImage.template.html' ), 'r' )
	
	content = header_page_file.read()
	
	direct_theme_dir = os.path.join( tokenDic[ 'YAG-OSDL-TOKEN-ROOT-PATH' ], resourceDirectoryName )
	
	# Manage comments:
	comment_file = os.path.join( tokenDic[ 'YAG-OSDL-TOKEN-CONTENT-DIRECTORY' ], convertIntoFileName( graphicFileName ) + commentExtension )
	if os.path.isfile( comment_file ):
		outputDevice.info( 'Using comment file <%s>.' % ( comment_file, ) )
		comment = file( comment_file ).read()
		if len( comment.strip() ):
			content += '<br><br><p><img src="' + os.path.join( direct_theme_dir, 'comment.png' ) + '" alt="[Comment]" width="16"></img> ' + comment + '</p><br><br>'
	else:
		#outputDevice.debug( 'No comment file found (tried <%s>).' % ( comment_file, ) )
		pass
		
	# Manage theme:
	theme_file = os.path.join( tokenDic[ 'YAG-OSDL-TOKEN-CONTENT-DIRECTORY' ],
		convertIntoFileName( graphicFileName ) + themeExtension )
		
	if os.path.isfile( theme_file ):
		outputDevice.info( 'Using theme file <%s>.' % ( theme_file, ) )
		themes_with_eof = file( theme_file ).readlines()
		themes = []
		for t in themes_with_eof:
			themes.append( t[:-1].strip() )
		updateThemeTree( themes )
		
		# In the theme file of this image, there may be sub-themes declared 
		# as 'a: b'. It means that this image actually belong to child theme b:
		leaf_themes = getLeafThemesFrom( themes )	
		if len( leaf_themes ):
			content += handleThemesFor( graphicFileName, leaf_themes )		
	else:
		#outputDevice.debug( 'No theme file found (tried <%s>).' % ( theme_file, ) )
		pass
	
	content += '<p><center>'
	
	if previousFileName: 	
		content += '<a href="' + os.path.basename( getFullPageFilenameFromGraphic( previousFileName ) ) + '"><img src="' + os.path.join( tokenDic[ 'YAG-OSDL-TOKEN-ROOT-PATH' ], resourceDirectoryName, 'previous.png' ) + '" border="0" alt="[Previous]"></img></a> ' 
	
	# Guess to which overview page this page should be linked:
	
	if overview_count == 0:	
		content += ' <a href="Overview.html' + '"><img src="' + os.path.join( tokenDic[ 'YAG-OSDL-TOKEN-ROOT-PATH' ], resourceDirectoryName, 'up.png' ) + '" border="0" alt="[Up]"></img></a> '
	else:
		content += ' <a href="Overview-' + `overview_count` + '.html' + '"><img src="' + os.path.join( tokenDic[ 'YAG-OSDL-TOKEN-ROOT-PATH' ], resourceDirectoryName, 'up.png' ) + '" border="0" alt="[Up]"></img></a> '
	
	if nextFileName: 	
		content += ' <a href="' + os.path.basename( getFullPageFilenameFromGraphic( nextFileName ) ) + '"><img src="' + os.path.join( tokenDic[ 'YAG-OSDL-TOKEN-ROOT-PATH' ], resourceDirectoryName, 'next.png' ) + '" border="0" alt="[Next]"></img></a> '
	
	
	
	content += "</center></p><br><br>"
		
	content += footer_page_file.read()
	
	tokenDic[ 'YAG-OSDL-CURRENT-CONTENT-TXT' ] = graphicFileName
	tokenDic[ 'YAG-OSDL-CURRENT-CONTENT-RAW' ] = graphicFileName
	
	content = updateFromTokenDic( content )
	
	graphFile.write( content )
	graphFile.close()
	
	
def getMenuFilenameFromDir( directoryName ):
	"""Returns menu filename corresponding to provided directory."""
	#print 'getMenuFilenameFromDir: get <%s>, returned <%s>.' % ( directoryName, os.path.join( directoryName, directoryName + 'Menu' + htmlExtension ) )
	return os.path.join( directoryName, os.path.basename( directoryName ) + 'Menu' + htmlExtension )



def handleMenuName( menuName ):
	"""
	Modify, if requested, menu name according to settings.
	Ex: dash_is_space_in_menu is handled.
	"""
	if mainDic[ 'dash_is_space_in_menu' ] == 'False':	
		return menuName
	else:
		return 	menuName.replace( '-', ' ' )


def generateMenuForDirectory( rootLevel ):
	"""Generates menu frame file for a directory."""
	
	directories_list, files_list = getDirectoryElements( tokenDic[ 'YAG-OSDL-TOKEN-CONTENT-DIRECTORY' ] )
	
	menu_filename = getMenuFilenameFromDir( tokenDic[ 'YAG-OSDL-TOKEN-CONTENT-DIRECTORY' ] )
	outputDevice.debug( "Creating menu file <%s>." % ( menu_filename, ) )
	
	template_dir = mainDic[ 'template_directory' ]
	#outputDevice.debug( 'Using <%s> as template directory.' % ( template_dir, ) )
	
	# Avoid a back button leading to nowhere:
	if rootLevel:
		header_menu_file = file( os.path.join( template_dir, 'HeaderFirstMenu.template.html' ), 'r' )
	else:
		header_menu_file = file( os.path.join( template_dir, 'HeaderMenu.template.html' ), 'r' )
			
	footer_menu_file = file( os.path.join( template_dir, 'FooterMenu.template.html' ), 'r' )
	
	menuFile = file( menu_filename, 'w' )

	tokenDic[ 'YAG-OSDL-TOKEN-SHORT-CONTENT-DIRECTORY' ] = handleMenuName( os.path.basename( tokenDic[ 'YAG-OSDL-TOKEN-CONTENT-DIRECTORY' ] ) )
		
	menuFile.write( updateFromTokenDic( header_menu_file.read() ) ) 
	
	text_one = '<tr>\n<td align="right"><a href="'
	text_two = updateFromTokenDic( '" onclick="parent.mainFrame.location=&#39;YAG-OSDL-TOKEN-ROOT-PATH/yag-osdl-resources/black.html&#39;">' )
	
	text_three= '</a></td>\n<td width="15"><a href="'
	
	text_four = updateFromTokenDic( '"<img src="YAG-OSDL-TOKEN-ROOT-PATH/yag-osdl-resources/Arrow.png" border="0" alt=""></a></td>\n</tr>\n' )
	
	for d in directories_list:
		if d not in [ resourceDirectoryName, themeDirectoryName ]:
			menuFile.write( text_one + d + '/' + d + 'Menu.html' + text_two + handleMenuName( d ) + text_three + d + '/' + d + 'Menu.html' + text_four )
	
	menuFile.write( updateFromTokenDic( footer_menu_file.read() ) ) 
	
	menuFile.close()

	
	
def generateOverview( graphics, pageCount = 0, totalPageCount = None, comment = None):	
	"""Generates content overview for current directory."""
	
	if pageCount != 0:
		overview_file = file( os.path.join( tokenDic[ 'YAG-OSDL-TOKEN-OUTPUT-DIRECTORY' ], 'Overview-' + `pageCount` + htmlExtension ), 'w' )
	else:
		overview_file = file( os.path.join( tokenDic[ 'YAG-OSDL-TOKEN-OUTPUT-DIRECTORY' ], 'Overview' + htmlExtension ), 'w' )

	images_per_overview = int( mainDic[ 'images_by_column' ] ) * int( mainDic[ 'images_by_row' ] )

	if len( graphics ) > images_per_overview:
		managed   = graphics[:images_per_overview]
		remainder = graphics[images_per_overview:]
	else:
		managed = graphics
		remainder = []
	
	template_dir = mainDic[ 'template_directory' ]
	
	header_page_file = file( os.path.join( template_dir, 'HeaderGallery.template.html' ), 'r' )
	footer_page_file = file( os.path.join( template_dir, 'FooterGallery.template.html' ), 'r' )
	
	overview_file.write( updateFromTokenDic( header_page_file.read() ) )

	if not len( managed ):
		overview_file.write( updateFromTokenDic( footer_page_file.read() ) )
		return
		
	# Computes the number of sub-galleries: 
	if not totalPageCount:
		totalPageCount = len( graphics ) / images_per_overview
		if len( graphics ) % images_per_overview:
			totalPageCount += 1
			
	if comment:
		overview_file.write( '<br><br><p><img src="' + os.path.join( tokenDic[ 'YAG-OSDL-TOKEN-ROOT-PATH' ], resourceDirectoryName, 'comment.png' ) + '" width="16" alt="[C]"></img> ' + comment + '</p><br><br>' )

	if totalPageCount > 1:
		overview_file.write( 'Sub-gallery %s out of %s for gallery %s<br><br> ' % ( pageCount + 1, totalPageCount, tokenDic[ 'YAG-OSDL-TOKEN-SHORT-CONTENT-DIRECTORY' ] ) )
	else:
		overview_file.write( '(Gallery %s has no sub-gallery)<br><br> ' % ( tokenDic[ 'YAG-OSDL-TOKEN-SHORT-CONTENT-DIRECTORY' ], ) )
		
		
	if pageCount:
		if pageCount == 1:
			overview_file.write( ' [<a href="Overview.html">First sub-gallery</a>] ' )	
		else:
			overview_file.write( ' [<a href="Overview-' + `pageCount-1` + '.html">Previous sub-gallery</a>] ' )	
	if len( remainder ):
		if pageCount +2 == totalPageCount:
			overview_file.write( ' [<a href="Overview-' + `pageCount+1` + '.html">Last sub-gallery</a>] ' )	
		else:
			overview_file.write( ' [<a href="Overview-' + `pageCount+1` + '.html">Next sub-gallery</a>] ' )	
		

	overview_file.write( updateFromTokenDic( '<br><br><table border="1" summary="Thumbnails for YAG-OSDL-TOKEN-SHORT-CONTENT-DIRECTORY"><caption>Thumbnails for gallery YAG-OSDL-TOKEN-SHORT-CONTENT-DIRECTORY, click to enlarge</caption>' ) )
		
	for g in managed:
		size = int( mainDic[ 'thumbsize' ] )
		generateThumbnail( g, ( size, size ) )
		
	# Clone the list:
	graphics_to_pop = managed[:]
	graphics_to_pop.reverse()
	
	if len( graphics_to_pop ):
		for y in range( int( mainDic[ 'images_by_column' ] ) ):
			overview_file.write( '<tr>\n' )
			for x in range( int( mainDic[ 'images_by_row' ] ) ):
				if len( graphics_to_pop ):
					imgFileName = graphics_to_pop.pop()
					overview_file.write( '<td><center><a href="' + os.path.basename( getFullPageFilenameFromGraphic( imgFileName ) ) + '"><img src="' + os.path.splitext( imgFileName )[0] + '-thumbnail.jpeg" alt="Thumbnail for image ' + imgFileName + ' not available"></img><br>' )
					
					comment_filename = os.path.join( tokenDic[ 'YAG-OSDL-TOKEN-CONTENT-DIRECTORY' ], convertIntoFileName( imgFileName ) + commentExtension )
					if os.path.isfile( comment_filename ):
						comment = file( comment_filename ).read()
						if len( comment.strip() ):
							overview_file.write( '<img src="' + os.path.join( tokenDic[ 'YAG-OSDL-TOKEN-ROOT-PATH' ], resourceDirectoryName, 'comment.png' ) + '" width="16" alt="[C]"></img> ' )
						
					if os.path.isfile( os.path.join( tokenDic[ 'YAG-OSDL-TOKEN-CONTENT-DIRECTORY' ], convertIntoFileName( imgFileName ) + themeExtension ) ):
						overview_file.write( '<img src="' + os.path.join( tokenDic[ 'YAG-OSDL-TOKEN-ROOT-PATH' ], resourceDirectoryName, 'theme.png' ) + '" width="16" alt="[T]"></img>' )
						
					overview_file.write( '</a></center></td>\n' )

				else:
					break				
			overview_file.write( '</tr>\n' ) 
			if not len( graphics_to_pop ):
				break

		overview_file.write( '</table></center></p><br><br><p><b>Quick nav-by-name tab</b>:<br><br><ul>' )
		for g in managed:
			overview_file.write( '<li>[<a href="' + convertIntoFileName( g ) + '.html">' + g + '</a>]</li>' )
		overview_file.write( '</ul></p>' )
		overview_file.write( updateFromTokenDic( footer_page_file.read() ) )
	if len( remainder ):
		pageCount += 1
		generateOverview( remainder, pageCount, totalPageCount, comment = comment )
	
	
	
def removeThumbnailsFrom( fileList ):
	"""
	Removes the thumbnails from the list, in order not to generate thumbnails for thumbnails in case of multiple yag-osdl runs.
	"""	
	return [ f for f in fileList if string.find( f, '-thumbnail.jpeg' ) == -1 ]
	
	
	
def processDirectory( rootLevel = False ):
	"""Generates all informations for specified directory."""
	
	if os.path.basename( tokenDic[ 'YAG-OSDL-TOKEN-CONTENT-DIRECTORY' ] ) == resourceDirectoryName:
		print "Ignoring yag's own resource directory <%s>." % ( resourceDirectoryName, )
	outputDevice.debug( 'Processing %s' % ( tokenDic[ 'YAG-OSDL-TOKEN-CONTENT-DIRECTORY' ], ) )
	generateMenuForDirectory( rootLevel )
	graphics, sounds, unknown = scanDirectoryForContent( tokenDic[ 'YAG-OSDL-TOKEN-CONTENT-DIRECTORY' ] )
	
	graphics = removeThumbnailsFrom( graphics )
		
	previous, current = None, None
	image_count = 0
	overview_count = 0
	images_per_overview = int( mainDic[ 'images_by_column' ] ) * int( mainDic[ 'images_by_row' ] )
	for next in graphics:
		if current:
			image_count += 1		
			if image_count == images_per_overview + 1:
				overview_count += 1
				image_count = 1
			generateFullPageForGraphic( previous, current, next, overview_count )
		previous = current 
		current = next
		next = None
		
	if current:			
		if image_count == images_per_overview + 1:
			overview_count += 1
		generateFullPageForGraphic( previous, current, next, overview_count )
	
	comment_file = os.path.join( tokenDic[ 'YAG-OSDL-TOKEN-CONTENT-DIRECTORY' ], galleryCommentFilename )
	
	gallery_comment = None
	
	if os.path.isfile( comment_file ):
			gallery_comment = file( comment_file, 'r' ).read()
			
	generateOverview( graphics, comment = gallery_comment )	
	
	
	
def scanContent( contentDir, outputDir, rootPath = '.' ):
	"""
	Scans content from specified directory. Will be first called with only one argument,
	then will recursing will add a second order, to keep track of base directory.
	"""
	print
	outputDevice.debug( 'Scanning from content directory <%s>, will write in <%s>, with root directory being <%s>...' % ( contentDir, outputDir, rootPath ) )

	# Updating the token directory:
	tokenDic[ 'YAG-OSDL-TOKEN-CONTENT-DIRECTORY' ] = contentDir
	tokenDic[ 'YAG-OSDL-TOKEN-OUTPUT-DIRECTORY' ]  = outputDir
	tokenDic[ 'YAG-OSDL-TOKEN-ROOT-PATH' ]         = rootPath	
		
	outputDevice.debug( 'Processing content directory' )		
	#outputDevice.debug( 'Subdirectories are %s.' % ( fileUtils.getChildrenDirectories( contentDir ), ) )
	processDirectory( rootPath == '.' )
	
	# Recursing:
	for d in fileUtils.getChildrenDirectories( contentDir ):
		# Do not index our own resource directory ! (it has however to be self-contained in
		# output directory.
		if d != resourceDirectoryName:
			print 'scanContent: recursing in %s' % ( d,)
			tokenDic[ 'YAG-OSDL-TOKEN-PARENT-DIRECTORY' ] = outputDir
			tokenDic[ 'YAG-OSDL-TOKEN-PARENT-SHORT-DIRECTORY' ] = os.path.basename( outputDir )
			scanContent( os.path.join( contentDir, d ), os.path.join( outputDir, d ), os.path.join( rootPath, '..' ) )



def installHelperFiles():
	"""Install helper file in output directory."""
	# Install the helper files (ex: css):
	target_helper_dir = os.path.join( mainDic[ 'output_directory' ], resourceDirectoryName ) 

	outputDevice.debug( 'Installing helper files from <%s> to <%s>.' % ( mainDic[ 'helper_files_directory' ], target_helper_dir ) )
	if os.path.exists( target_helper_dir ):
		outputDevice.debug( 'Deleting previously existing resource directory.' )
		shutil.rmtree( target_helper_dir )
	shutil.copytree( mainDic[ 'helper_files_directory' ], target_helper_dir )
	for f in fileUtils.getFilesInDir( os.path.join( mainDic[ 'theme_directory' ], 'Images' ) ):
		shutil.copy( os.path.join( mainDic[ 'theme_directory' ], 'Images', f ), target_helper_dir ) 
	shutil.copy( os.path.join( target_helper_dir, 'Page.css' ), os.path.join( target_helper_dir, mainDic[ 'theme' ] ) + '.css' )
	
	
	
def generateGalleryMainPage():
	"""Generates main page for gallery."""
	target_filename = os.path.join( mainDic[ 'output_directory' ], 'Main' + mainDic[ 'project_name'] + htmlExtension )
	outputDevice.debug( 'Gallery main page will be <%s>.' % ( target_filename, ) )
	shutil.copy( os.path.join( mainDic[ 'theme_directory' ], 'Templates', 'MainPageGallery.template.html' ), target_filename )
	updated_content = file( target_filename, 'r' ).read()
		 	
	file( target_filename, 'w' ).write( updateFromTokenDic( updated_content ) )
	


def generateGalleryFrameset():
	"""Generates frame set for gallery."""
	target_filename = os.path.join( mainDic[ 'output_directory' ], mainDic[ 'project_name'] + htmlExtension )
	target_filename_theme = os.path.join( mainDic[ 'output_directory' ], mainDic[ 'project_name'] + '-theme' + htmlExtension )
	outputDevice.debug( 'Gallery frameset will be <%s>.' % ( target_filename, ) )
	tokenDic[ 'YAG-OSDL-TOKEN-FIRST-MENU' ] = os.path.basename( tokenDic[ 'YAG-OSDL-TOKEN-MENU' ] )
	shutil.copy( os.path.join( mainDic[ 'theme_directory' ], 'Templates', 'FrameSet.template.html' ), target_filename )
	shutil.copy( os.path.join( mainDic[ 'theme_directory' ], 'Templates', 'FrameSet.template.html' ), target_filename_theme )

	updated_content = updateFromTokenDic( file( target_filename, 'r' ).read() )
	file( target_filename, 'w' ).write( updated_content )
	
	save = tokenDic[ 'YAG-OSDL-TOKEN-FIRST-MENU' ]
	tokenDic[ 'YAG-OSDL-TOKEN-FIRST-MENU' ] = save.replace( '.html', '-theme.html' )
	
	updated_content = updateFromTokenDic( file( target_filename_theme, 'r' ).read() )
	file( target_filename_theme, 'w' ).write( updated_content )
	
	tokenDic[ 'YAG-OSDL-TOKEN-FIRST-MENU' ] = save

	

	
def generateLoadingPage():
	"""Generates frame set for gallery."""
	target_filename = os.path.join( mainDic[ 'output_directory' ], resourceDirectoryName, 'black.html' )
	#outputDevice.debug( 'Loading page will be <%s>.' % ( target_filename, ) )	
	source_file = os.path.join( mainDic[ 'theme_directory' ], 'Templates', 'Black.template.html' )
	#outputDevice.debug( 'Copy from <%s> to <%s>.' % ( source_file, target_filename ) )	
	shutil.copy( source_file, target_filename )
	updated_content = updateFromTokenDic( file( target_filename, 'r' ).read() )
	file( target_filename, 'w' ).write( updated_content )



def main( contentDir = None, configFilename = None ):
	"""
		Main function, controler of the yag-osdl.
    	Must be called with:
			- content_directory, the name of the directory with content to scan,			
			- optionnally, configFilename, the filename of the configuration file.
			
		Other main informations such as:			
			- themeName, the name of the theme to be used,
			- resource_directory, the name of the directory containing resources such as templates
		and images necessary to generate the content website, etc. 
		are to be found from configFilename, otherwise will take default values.
	"""
    	 
	global mainDic, tokenDic
	 
	global outputDevice
	
	# Select log output:
	outputDevice = generalUtils.ScreenDisplay()
	
		
    # Original hardcoded dictionary for the defaults:
	mainDic = { 
		'project_name'         : 'Project name not specified',
		'content_directory'    : contentDir, 
		'resource_directory'   : os.path.join( os.getcwd(), 'Resources' ),
		'output_in_content'    : 'False',
		'output_directory'     : os.path.join( os.getcwd(), 'output' ),
    	'theme'                : 'Default-theme', 
		'thumbsize'            : '60',
		'images_by_row'        : '3',
		'images_by_column'     : '3',
		'dash_is_space_in_menu': 'False',
		'author'	           : 'Author not specified', 
		'author_mail'          : 'Author mail not specified',
		'gallery_license_file' : None,
		'gallery_info_file'    : None,
		'themes'               : NodeTheme( "RootTheme" )		
	}
   
	if configFilename:
		if not os.path.isfile( configFilename ):
	 		raise YagException, 'Specified configuration file %s does not exist.' % ( configFilename, )
		outputDevice.info( 'Using configuration file <%s>.' % ( configFilename, ) )
		updateConfigurationFromFile( mainDic, configFilename )
	else:
		outputDevice.info( 'No configuration file supplied, using hardcoded defaults.' )
	
	if not mainDic[ 'content_directory' ]:
		raise YagException, 'No content directory to scan has been specified, neither through command line nor configuration file.'

	# Avoid any slash at the end of path:
	mainDic[ 'content_directory' ] = os.path.normpath( 
		mainDic[ 'content_directory' ] )
		
	if not os.path.isdir( mainDic[ 'content_directory' ] ):
		raise YagException, 'Content directory <%s> not found.' % ( mainDic[ 'content_directory' ], )				
		
	outputDevice.debug( 'Checking resource directories...' )
	
	resource_directory = checkDirectory( mainDic[ 'resource_directory' ] )

	theme_directory        = checkDirectory( os.path.join( resource_directory, 'Themes', mainDic[ 'theme' ] ) )
	image_directory        = checkDirectory( os.path.join( theme_directory, 'Images' ) )
	template_directory     = checkDirectory( os.path.join( theme_directory, 'Templates' ) )
	helper_files_directory = checkDirectory( os.path.join( theme_directory, 'HelperFiles' ) )
		
	mainDic[ 'theme_directory' ]        = theme_directory 
	mainDic[ 'image_directory' ]        = image_directory
	mainDic[ 'template_directory' ]     = template_directory
	mainDic[ 'helper_files_directory' ] = helper_files_directory
	
	mainDic[ 'output_directory' ]       = fileUtils.findNextNewDirectoryName( mainDic[ 'output_directory' ] )
			
	
	# Show the settings:
	generalUtils.displayDic( mainDic )
	
	# If an image is not available, alternative text will be displayed. 	
	navigation_images = addPrefixToFileList( image_directory, [ 'index.png', 'next.png', 'previous.png', 'up.png', 'down.png', 'root.png' ] )
	
	# All templates files must be here.
	templates_files = addPrefixToFileList( template_directory, [ 'HeaderMenu.template.html', 'FooterMenu.template.html', 'HeaderGallery.template.html', 'FooterGallery.template.html', 'HeaderImage.template.html', 'FooterImage.template.html' ] )
	
	if not filesAllExist( templates_files ):
		raise YagException, 'Not all template files available in template directory %s.' % ( template_directory, )
	
	outputDevice.debug( 'All template files found.' )
	
	# Will work even if those are not found.	
	html_files = addPrefixToFileList( helper_files_directory, [ 'Menu.css', 'Page.css' ] )
		       
	# By construction, output_directory should point to a non-existing directory.
	# Creating it unconditionnally if we are not to create website among existing content:
	
	# 'False' and False are different !
	if mainDic[ 'output_in_content' ] == 'False':
		os.mkdir( mainDic[ 'output_directory' ] )
	else:	
		mainDic[ 'output_directory' ] = mainDic[ 'content_directory' ]

	resourceDir = os.path.join( mainDic[ 'output_directory' ], resourceDirectoryName )
	if not os.path.exists( resourceDir ):
		os.mkdir( resourceDir )
		
	initTokenDic()

	# Show the token substitutions:
	generalUtils.displayDic( tokenDic )

	preloadThemes()

	# Start the recursive indexing:
	scanContent( mainDic[ 'content_directory' ], mainDic[ 'output_directory' ] )
	
	# Do it last to avoid it is indexed too !
	
	# Updates token:
	tokenDic[ 'YAG-OSDL-TOKEN-ROOT-PATH' ] = '.'

	tokenDic[ 'YAG-OSDL-TOKEN-OUTPUT-DIRECTORY' ] = mainDic[ 'output_directory' ]
	tokenDic[ 'YAG-OSDL-TOKEN-MENU' ] = os.path.join( mainDic[ 'output_directory' ], os.path.basename( mainDic[ 'output_directory' ] ) ) + 'Menu' + htmlExtension 

	installHelperFiles()
	generateLoadingPage()
	generateGalleryMainPage()
	generateGalleryFrameset()
	generateThemePages()
	
	shutil.copy( os.path.join( mainDic[ 'output_directory' ], 'Main' + mainDic[ 'project_name' ] + htmlExtension ), os.path.join( mainDic[ 'output_directory' ], 'index.html' ) )
	
	print 
	print	
	print "You can browse your new gallery from file://%s"  % ( os.path.join( mainDic[ 'output_directory' ], 'index.html' ), )
	print
	print "      Enjoy !"
	print
			
######## End of functions #########



#### Beginning of top-level code. ####

#import atexit
# Clean up at any exit.
#atexit.register( cleanUp )  


if __name__ == '__main__':

	import os, sys, shutil, Image, tempfile, ConfigParser, time
	
	# Be user-friendly !
	generalUtils.activateNameCompletion()
	
	# Checks command line arguments. 
	# In case of error or wrong syntax, use defaults. 
	# Commmand line defaults:
	defaultConfigFile = 'yag-osdl.conf'
	configFile = None    
	source  = false
	
	help_options    = [ '-h',  '--help' ]
	config_options  = [ '-rc', '--config' ]
	version_options = [ '-v',  '--version' ]
	
	options = help_options + config_options + version_options

	contentDir = None
	
	option_start = 1
	
	#print 'Arguments specified are <%s>.' % ( sys.argv, )
	
	if len( sys.argv ) > 1 and sys.argv[ 1 ] not in options:
		contentDir = sys.argv[ 1 ] 
		option_start = 2
		
	item_count = option_start
	
	for item in sys.argv[ option_start: ]:

		#print 'Examining argument %s.' % ( item, )
		item_count += 1
		
		if item in help_options:
		    print __doc__ 
		    sys.exit( 0 )
									
		if item in config_options:
			print 'Configuration option detected.'
			try:
				configFile = sys.argv[ item_count ]
			except IndexError:
				configFile = defaultConfigFile
			print 'Configuration file will be <%s>.' % ( configFile, )	

		if item in version_options:
		    print "This is yag-osdl version %s." % ( yag_osdl_version, )
		    sys.exit( 0 )
        
	# Start with main():
	
	if contentDir:
		print 'Content directory specified through command line is <%s>.' % ( contentDir, )
	else:
		print 'No content directory specified through command line.'

	if configFile:
		print 'Configuration file specified through command line is <%s>.' % ( configFile, )
	else:
		print 'No configuration file specified through command line.'
	
	main( contentDir, configFile )
	
