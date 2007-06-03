#!/bin/bash

USAGE="Usage : `basename $0` [<directory where to start>] : allows to easily add comment and theme informations in an image tree. Operates from current directory if no argument given."

OWN_DIR=`dirname $0`


if [ -z "$1" ] ; then
	rootDir=`pwd`
else
	rootDir="$1"
	if [ ! -d "$rootDir" ] ; then
		echo "Error, specified image directory ($rootDir) does not exist." 1>&2
		echo "$USAGE"
		exit 5
	fi	
fi


HANDLE_GALLERY=${OWN_DIR}/handleGalleryDirectory.sh
if [ ! -x "$HANDLE_GALLERY" ] ; then
	echo "Error, no executable script to annotate gallery found (${$HANDLE_GALLERY})." 1>&2
	exit 10
fi
	
HANDLE_IMAGE=${OWN_DIR}/handleImage.sh
if [ ! -x "$HANDLE_IMAGE" ] ; then
	echo "Error, no executable script to annotate gallery found (${HANDLE_IMAGE})." 1>&2
	exit 11
fi

GUIDE="\n\tThis script will recursively scan from directory tree <$rootDir> and, for each gallery location and encountered image X.jpeg, will show it to you and will allow you to edit first a comment for it (creating X.txt), then a theme list (creating X.thm)."

echo -e $GUIDE

echo "First commenting galleries"
find $rootDir -type d -a ! -name 'yag-osdl-resources' -exec ${HANDLE_GALLERY} '{}' ';'

echo "Second commenting images"
find $rootDir \( -name '*.jpeg' -o -name '*.jpg' -o -name '*.png' \) -a ! -name '*-thumbnail.jpeg'  -exec ${HANDLE_IMAGE} '{}' ';'

echo "Annotations finished !"

