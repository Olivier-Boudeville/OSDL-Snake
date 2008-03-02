#!/bin/bash

USAGE="Usage : `basename $0` [<directory to clean>] : removes all yag-osdl generated files. Operates from current directory if no argument given."

YAG_CREATED_DIR="yag-osdl-resources"


if [ -z "$1" ] ; then
	rootDir=`pwd`
else
	rootDir="$1"
	if [ ! -d "$rootDir" ] ; then
		echo "Error, specified directory to clean ($rootDir) does not exist." 1>&2
		echo "$USAGE"
		exit 5
	fi	
fi


HINT_DIR="$rootDir/$YAG_CREATED_DIR"
if [ ! -d "$rootDir/$YAG_CREATED_DIR" ] ; then
	echo "Error, the specified directory ($rootDir) does not seem to be a root directory where yag-osdl operated (no $HINT_DIR found)." 1>&2
	echo "$USAGE"
	exit 6
fi	
		
echo -e "Warning : will remove all files matching \n\t*.html\n\t*-thumbnail.jpeg\nstarting from directory <${rootDir}>."

unset value
read -p "Let's proceed with removal ? (y/n) [n]" value
if [ "$value" == "y" ]; then
	echo "Cleaning..."
	find "${rootDir}" -name '*.html' -exec rm -f '{}' ';'
	find "${rootDir}" -name '*-thumbnail.jpeg' -exec rm -f '{}' ';'
	
	echo "... finished"
else
	echo "Cancelled"
fi

unset value

