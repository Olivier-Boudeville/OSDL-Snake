#!/bin/sh


yag_root="$(dirname $0)"
yag_osdl_exec="${yag_root}/yagosdl.py"

usage="Usage: $(basename $0) [-h|--help] [--debug] [flags to pass to ${yag_osdl_exec}]
  Notable flag: --config MY_CONFIG_FILE (see yag-osdl.conf.sample for an example) to define a configuration file (default one: 'yag-osdl.conf')
  This script manages everything so that yag-osdl is successfully run, otherwise reports any error."


if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
	echo "${usage}"
	exit 0
fi


if [ "$1" = "--debug" ]; then
	do_debug=0
	shift
else
	do_debug=1
fi


debug()
# Displays a debug message if debug mode is activated (do_debug=true).
# Usage: debug "message 1" "message 2" ...
{
	[ $do_debug -eq 1 ] || echo "Debug: $*"
}



yag_osdl_env_script="${yag_root}/yag-osdl-environment.sh"

if [ ! -f "${yag_osdl_env_script}" ]; then
	echo "  No yag-osdl environment file found (no '${yag_osdl_env_script}'), aborting." 1>&2
	exit 50
fi

if [ -z "${CEYLAN_SNAKE}" ]; then
	echo "Error, no CEYLAN_SNAKE environment variable defined." 1>&2
	exit 55
fi


if [ ! -d "${CEYLAN_SNAKE}" ]; then
	echo "  Error, non-existing CEYLAN_SNAKE directory ('${CEYLAN_SNAKE}')." 1>&2
	exit 60
fi

export PYTHONPATH="${CEYLAN_SNAKE}:${PYTHONPATH}"


. ${yag_osdl_env_script}


# Python2 deprecated in favor of Python3.
# PIL deprecated in favor of Pillow.
# easy_install deprecated in favor of pip.


# We use a virtual environment first, that have been created based on
# https://docs.python.org/3/tutorial/venv.html#creating-virtual-environments:
# python3 -m venv yagosdl-env

# Activating it:
. yagosdl-env/bin/activate

# Done to install Pillow
# (cf. https://pillow.readthedocs.io/en/stable/installation.html), knowing that
# many distributions offer the 'python-imaging' package for that:
#
# python3 -m pip install --upgrade pip
# python3 -m pip install --upgrade Pillow
#
# For users, it is just a matter of entering:
# python -m pip install -r requirements.txt
#
# This file has been generated thanks to 'pip freeze > requirements.txt' and put
# in version control.

if [ ! -x "${yag_osdl_exec}" ]; then
	echo "  Error, no executable yag-osdl script available (no executable '${yag_osdl_exec}' found). ${usage}" 1>&2
	exit 70
fi

#pil_module="Image.py"
#
#if [ ! -f "${pil_root}/${pil_module}" ]; then
#	# With Gentoo: emerge imaging; with Arch: pacman -S python-imaging
#	echo "  Error, no PIL module available (no '${pil_root}/${pil_module}' file found). ${usage}" 1>&2
#	exit 75
#fi



debug "Running ${yag_osdl_exec}..."

if [ $do_debug -eq 0 ]; then
	/bin/python3 -i ${yag_osdl_exec} $*
else
	${yag_osdl_exec} $*
fi
