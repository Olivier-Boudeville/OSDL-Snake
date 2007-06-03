#!/bin/bash

# Helper script for annotate-images.sh

if [ "$#" != "1" ] ; then
	echo "handleGalleryDirectory.sh : error, $# arguments given instead of 1" 1>&2
	exit 5
fi

if [ ! -d "$1" ] ; then
	echo "handleGalleryDirectory.sh : error, <$1> is not a file." 1>&2
	exit 5	
fi

EDITOR="nedit -create"

GALLERY_DIRECTORY="$1"

GALLERY_COMMENT_FILENAME='yag-gallery-comment.txt'

$EDITOR $GALLERY_DIRECTORY/$GALLERY_COMMENT_FILENAME
