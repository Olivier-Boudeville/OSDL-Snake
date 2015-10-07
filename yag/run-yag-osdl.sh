#!/bin/sh

if [ "$1" = "--debug" ] ; then
	do_debug=0
	shift
else
	do_debug=1
fi


DEBUG()
# Displays a debug message if debug mode is activated (do_debug=true).
# Usage: DEBUG "message 1" "message 2" ...
{
	[ $do_debug -eq 1 ] || echo "Debug: $*"
}


YAG_ROOT=$(dirname $0)
YAG_OSDL_EXEC=${YAG_ROOT}/"yagosdl.py"

USAGE="

	Usage: $(basename $0) [--debug] [flags to pass to ${YAG_OSDL_EXEC}]

	This script manages everything so that yag-osdl is successfully run, or informs in case of errors."


YAG_OSDL_ENV_SCRIPT=${YAG_ROOT}/yag-osdl-environment.sh

if [ ! -f "${YAG_OSDL_ENV_SCRIPT}" ] ; then
	echo "No yag-osdl environment file found (no ${YAG_OSDL_ENV_SCRIPT}), aborting." 1>&2
	exit 2
fi

CEYLAN_SNAKE_ROOT=${CEYLAN_SNAKE}

if [ -z "${CEYLAN_SNAKE}" ] ; then
	echo "Error, no CEYLAN_SNAKE environment variable defined." 1>&2
	exit 3
fi

if [ ! -d "${CEYLAN_SNAKE}" ] ; then
	echo "Error, non-existing CEYLAN_SNAKE directory (${CEYLAN_SNAKE})." 1>&2
	exit 4
fi

export PYTHONPATH="${CEYLAN_SNAKE}:${PYTHONPATH}"


. ${YAG_OSDL_ENV_SCRIPT}

PIL_MODULE="Image.py"



if [ ! -x "${YAG_OSDL_EXEC}" ] ; then
	echo "
	Error, no executable yag-osdl script available (no executable <${YAG_OSDL_EXEC}> found).
	$USAGE"
	exit 10
fi

if [ ! -f "${PIL_ROOT}/${PIL_MODULE}" ] ; then
	# With gentoo: emerge imaging; arch: pacman -S python-imaging
	echo "
	Error, no PIL module available (no <${PIL_ROOT}/${PIL_MODULE}> file found).
	$USAGE"
	exit 15
fi



DEBUG "Running $YAG_OSDL_EXEC..."

if [ "$do_debug" -eq 0 ] ; then
	/bin/python2 -i ${YAG_OSDL_EXEC} $*
else
	${YAG_OSDL_EXEC} $*
fi
