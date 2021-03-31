#!/bin/sh

# Helper script for annotate-images.sh

if [ ! $# -eq 1 ]; then
	echo "  $(basename $0): error, $# arguments given instead of 1." 1>&2
	exit 20
fi

if [ ! -d "$1" ]; then
	echo "  $(basename $0): error, '$1' is not a directory." 1>&2
	exit 21
fi


gallery_directory="$1"

gallery_name="$(basename ${gallery_directory})"

echo " - please describe now the gallery '${gallery_name}'..."

gallery_comment_filename="yag-gallery-comment.txt"

gallery_comment_file="${gallery_directory}/${gallery_comment_filename}"

if [ ! -f "${gallery_comment_file}" ]; then

	echo "# Replace this text with *comments* regarding the gallery in '${gallery_directory}'." > "${gallery_comment_file}"

fi

${EDITOR} "${gallery_comment_file}"
