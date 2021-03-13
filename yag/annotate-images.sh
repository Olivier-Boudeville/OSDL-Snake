#!/bin/sh

usage="Usage: $(basename $0) [ROOT_DIR]: allows to easily add comment and theme information through an image tree. If no argument is specified, operates from the current directory."

own_dir="$(dirname $0)"


if [ -z "$1" ]; then

	root_dir="$(pwd)"

else

	root_dir="$1"

	if [ ! -d "${root_dir}" ]; then

		echo "  Error, specified image directory ('${root_dir}') does not exist.
${usage}" 1>&2
		exit 5

	fi

fi


handle_gallery="${own_dir}/handle-gallery-directory.sh"

if [ ! -x "${handle_gallery}" ]; then
	echo "  Error, no executable script to annotate a gallery found ('${handle_gallery}')." 1>&2
	exit 10
fi

handle_image="${own_dir}/handle-image.sh"

if [ ! -x "${handle_image}" ]; then
	echo "Error, no executable script to annotate an image found ('${handle_image}')." 1>&2
	exit 15
fi

guide="
	This script will recursively scan root directory <${root_dir}> and, for each gallery location and encountered image (X.jpeg or X.png), will show it to you, and will allow you to edit first a comment for it (creating X.txt), then a theme list (creating X.thm)."

echo "${guide}"

# Environment variable:
#EDITOR="nedit -create"
EDITOR="emacs"

export EDITOR

echo
echo "* First: commenting galleries"
find ${root_dir} -type d -a ! -name 'yag-osdl-resources' -exec ${handle_gallery} '{}' 2>/dev/null ';'

echo
echo "* Second: commenting images"
find ${root_dir} \( -name '*.jpeg' -o -name '*.jpg' -o -name '*.png' \) -a ! -name '*-thumbnail.jpeg' -exec ${handle_image} '{}' ';'

echo "Annotations finished!"
