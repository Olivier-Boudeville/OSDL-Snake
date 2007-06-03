#!/bin/bash

if [ "$1" == "--debug" ] ; then
	do_debug=true
	shift 
else
	do_debug=false
fi


function DEBUG
# Displays a debug message if debug mode is activated (do_debug=true).
# Usage : DEBUG "message 1" "message 2" ...
{
	[ "$do_debug" == "false" ] || echo "Debug : $*"
}


USAGE="Usage : `basename $0` [--debug] [flags to pass to ${YAG_OSDL_EXEC}]\nThis script manages everything so that yag-osdl is successfully run, or informs in case of errors."

YAG_ROOT=`dirname $0`

YAG_OSDL_ENV_SCRIPT=${YAG_ROOT}/yag-osdl-environment.sh

if [ ! -f "${YAG_OSDL_ENV_SCRIPT}" ] ; then
	echo "No yag-osdl environment file found (no ${YAG_OSDL_ENV_SCRIPT}), aborting." 1>&2
	exit 2
fi

YAG_OSDL_EXEC=${YAG_ROOT}/"yagosdl.py"

source ${YAG_OSDL_ENV_SCRIPT}

PIL_MODULE="Image.py"



if [ ! -x "${YAG_OSDL_EXEC}" ] ; then
	echo -e "Error, no executable yag-osdl script available (no executable <${YAG_OSDL_EXEC}> found). $USAGE"
	exit 4
fi	

if [ ! -f "${PIL_ROOT}/${PIL_MODULE}" ] ; then
	# With gentoo : emerge imaging
	echo -e "Error, no PIL module available (no <${PIL_ROOT}/${PIL_MODULE}> file found). $USAGE"
	exit 8
fi


DEBUG "Running $YAG_OSDL_EXEC..."

if [ "$do_debug" == "true" ] ; then
	python -i ${YAG_OSDL_EXEC} $*
else
	${YAG_OSDL_EXEC} $*
fi
