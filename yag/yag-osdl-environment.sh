# Sets the shell environment to use yag-osdl easily.


# yag-osdl has three prerequesites:
# - a not too ancient Python3 interpreter
# - Ceylan-Snake generic Python scripts
# - Python Imaging Library (PIL) [now managed thanks to pip and a virtual
# - environment]


script_name="yag-osdl-environment.sh"
helper_script="yag-osdl-debug-helper.py"


# Ony may change this setting according to the python version (in
# /usr/lib/python*), yet one shall rely on pip nowadays:
#
python_version=3.9


echo  "
Initializing shell environnment for yag-osdl."

if [ "$0" = "${script_name}" ]; then

	echo "Incorrect use: this script (${script_name}) is meant to be sourced, not directly executed. It sets the shell environment so that yag-osdl can be conveniently used. Use 'source ${script_name}' or '. ${script_name}' instead." 2>&1

	exit 1

fi



# First: check for python

python_info="yag-osdl needs an executable python interpreter to be run. The interpreter can be downloaded from http://www.python.org/, yet your distribution should manage it first hand. Once available, update the PATH environment variable so that the interpreter (in version at least ${python_version}) can be found thanks to 'which python', and relaunch this script."

python_interpreter=$(which python${python_version} 2>/dev/null)

if [ ! -x ${python_interpreter} ]; then

	echo "Python interpreter not found in PATH in version ${python_version} (not found, nothing done). ${python_info}" 1>&2
	return

else

	echo "    + Python interpreter found, using '${python_interpreter}'"

fi



# Second: check for the Python Imaging Library (PIL)
# Disabled since using pip and a virtual env for that

#pil_info="yag-osdl needs the Python Imaging Library (PIL) for its image handling features. It can be downloaded from: http://www.pythonware.com/products/pil/. Once available, either update pil_root in this script, or put it in your shell environment (for instance, export pil_root=<where it is installed>, such as export pil_root=/usr/lib/python${python_version}/site-packages/PIL). With gentoo, use 'emerge imaging', with Debian-based distributions use 'apt-get install python-imaging', with Arch Linux use 'pacman -S python-imaging'."

#if [ -z "${pil_root}" ]; then
#
#	# Change this setting according to the place where you installed PIL:
#	pil_root=/usr/lib/python${python_version}/site-packages/PIL
#
#fi

#if [ ! -d "${pil_root}" ]; then
#
#	echo "  Error, Python Imaging Library (PIL) not found, expected directory '${pil_root}' does not exist (not found, nothing done). ${pil_info}" 1>&2
#	return
#
#else
#
#	echo "    + Python Imaging Library (PIL) found, using '${pil_root}'."
#
#	# Allows to debug yag-osdl directly from the python command line (python -i
#	# yag-osdl.py):
#	#
#	export PYTHONSTARTUP="${helper_script}"
#
#	# Needed to find PIL:
#	export PYTHONPATH="${pil_root}:${PYTHONPATH}"
#
#	if [ -n "${CEYLAN_SNAKE}" ]; then
#		export PYTHONPATH="${CEYLAN_SNAKE}:${PYTHONPATH}"
#	fi
#
#fi


# Third: check for the Ceylan scripts

ceylan_info="yag-osdl needs the Ceylan Library for its generic-purpose python scripts. It can be downloaded from: http://osdl.sourceforge.net. Once available, either update CEYLAN_ROOT in this script, or put it in your shell environment (for instance, export CEYLAN_ROOT=<where it is installed>, such as export CEYLAN_ROOT=${HOME}/Projects/LOANI-repository/ceylan/Ceylan."

if [ -z "${CEYLAN_ROOT}" ]; then
	# Change this setting according to the place where you installed Ceylan:
	CEYLAN_ROOT="${HOME}/Projects/LOANI-repository/ceylan/Ceylan"
fi

if [ ! -d ${CEYLAN_ROOT} ]; then

	echo "Ceylan not found, expected directory '${CEYLAN_ROOT}' does not exist (not found, nothing done). ${ceylan_info}" 1>&2
	return

else

	echo "    + Ceylan library found, using '${CEYLAN_ROOT}'."

	# Needed to find Ceylan scripts (ex: toolbox.py):
	export PYTHONPATH=${CEYLAN_ROOT}/trunk/src/code/scripts/python:${PYTHONPATH}

	echo "Shell environment successfully set."
fi

# That's it!
