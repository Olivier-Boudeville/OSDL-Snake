#!/bin/sh

usage="Usage: $(basename $0) [-h|--help] [DIR_TO_CLEAN]: removes all YAG-OSDL generated files. If no argument is specified, operates from the current directory.
Typically used with the root directory specified in the 'output_directory' entry of the YAG-OSDL configuration file of interest."

yag_created_dir="yag-osdl-resources"

if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then

	echo "${usage}"

	exit 0

fi


if [ -z "$1" ]; then

	root_dir="$(pwd)"

else

	root_dir="$1"

	if [ ! -d "${root_dir}" ]; then
		echo "  Error, the directory to clean ('${root_dir}') does not exist.
${usage}" 1>&2
		exit 5
	fi

fi


hint_dir="${root_dir}/${yag_created_dir}"

if [ ! -d "${root_dir}/${yag_created_dir}" ]; then

	echo "  Error, the target directory ('${root_dir}') does not seem to be a root directory where yag-osdl operated (no '${hint_dir}' found).
${usage}" 1>&2

	exit 10

fi

echo "Warning: will remove all files matching *.html or *-thumbnail.jpeg, and all directories matching yag-osdl-* starting from directory '${root_dir}' (but others, i.e. *.jpeg, *.thm and *.txt, etc. will be kept)."

unset value
read -p "Let's proceed with removal? (y/n) [n]" value

if [ "${value}" = "y" ]; then

	echo "Cleaning from '${root_dir}'..."

	find "${root_dir}" \(  -name '*.html' -o -name '*-thumbnail.jpeg' \) -exec /bin/rm -f '{}' ';'

	find "${root_dir}" -name 'yag-osdl-*' -type d -exec /bin/rm -rf '{}' ';' 2>/dev/null

	echo "... finished"

else

	echo "Cancelled"

fi
