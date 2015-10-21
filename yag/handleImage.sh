#!/bin/sh

# Helper script for annotate-images.sh

if [ "$#" != "1" ] ; then
	echo "handleImage.sh: error, $# arguments given instead of 1" 1>&2
	exit 30
fi

if [ ! -f "$1" ] ; then
	echo "handleImage.sh: error, <$1> is not a file." 1>&2
	exit 31
fi

VIEWER_EXEC=$(which xv 2>/dev/null)

if [ -x "$VIEWER_EXEC" ]; then
	IMAGE_VIEWER="${VIEWER_EXEC} -geometry 500"
else
	VIEWER_EXEC=$(which eog 2>/dev/null)
	if [ -x "$VIEWER_EXEC" ]; then
		IMAGE_VIEWER="${VIEWER_EXEC} -g"
	else
		echo "handleImage.sh: error, no image viewer found (tried xv and eog)." 1>&2
		exit 32
	fi
fi

IMAGE_FILE="$1"

echo "    Showing $IMAGE_FILE"
$IMAGE_VIEWER "$IMAGE_FILE" 1>/dev/null 2>&1 &

# Suppress everything after a point not followed by a .
# (remove only the file extension, even if there are dots before)
#BASE_NAME=`echo $IMAGE_FILE | sed 's|\..[^\.]$||g'`

IMAGE_DIRECTORY=$(dirname $IMAGE_FILE)

BEGIN_OF_NAME=$(basename $IMAGE_FILE | sed 's|\.|-|g')


#echo "First part of name is <$BEGIN_OF_NAME>."

$EDITOR $IMAGE_DIRECTORY/$BEGIN_OF_NAME.txt
$EDITOR $IMAGE_DIRECTORY/$BEGIN_OF_NAME.thm
