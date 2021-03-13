#!/bin/sh

# Helper script for annotate-images.sh

if [ ! $# -eq 1 ]; then
	echo "  $(basename $0): error, $# arguments given instead of 1." 1>&2
	exit 10
fi

if [ ! -f "$1" ] ; then
	echo "  $(basename $0): error, '$1' is not a file." 1>&2
	exit 11
fi

#viewer_exec="$(which xv 2>/dev/null)"
viewer_exec="$(which eog 2>/dev/null)"

if [ -x "${viewer_exec}" ]; then
	# Was for xv: image_viewer="${viewer_exec} -geometry 500"
	image_viewer="${viewer_exec}"
else
	viewer_exec=$(which geeqie 2>/dev/null)
	if [ -x "${viewer_exec}" ]; then
		image_viewer="${viewer_exec} -g"
	else
		echo "  $(basename $0): error, no image viewer found (tried eog and geeqie)." 1>&2
		exit 32
	fi
fi

image_file="$1"

echo "    Showing ${image_file}"
${image_viewer} "${image_file}" 1>/dev/null 2>&1 &

# Suppress everything after a point not followed by a .
# (remove only the file extension, even if there are dots before)
#base_name="$(echo ${image_file} | sed 's|\..[^\.]$||g')"

image_directory="$(dirname ${image_file})"

beginning_of_name="$(basename ${image_file} | sed 's|\.|-|g')"


#echo "First part of name is '${beginning_of_name}'."

$EDITOR ${image_directory}/${beginning_of_name}.txt
$EDITOR ${image_directory}/${beginning_of_name}.thm
