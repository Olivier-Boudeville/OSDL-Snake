#!/bin/sh

# Helper script for annotate-images.sh

if [ "$#" != "1" ] ; then
	echo "handleGalleryDirectory.sh: error, $# arguments given instead of 1" 1>&2
	exit 20
fi

if [ ! -d "$1" ] ; then
	echo "handleGalleryDirectory.sh: error, <$1> is not a file." 1>&2
	exit 21
fi


GALLERY_DIRECTORY="$1"

GALLERY_NAME=$(basename $GALLERY_DIRECTORY)

echo " - please describe now the gallery '$GALLERY_NAME'..."

GALLERY_COMMENT_FILENAME='yag-gallery-comment.txt'

$EDITOR $GALLERY_DIRECTORY/$GALLERY_COMMENT_FILENAME
