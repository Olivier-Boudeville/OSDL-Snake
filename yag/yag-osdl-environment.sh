# Sets the shell environment to use yag-osdl easily.


# yag-osdl has three prerequesites:
#	- a not too ancient python interpreter
#	- Ceylan generic python scripts
#	- Python Imaging Library (PIL)


SCRIPT_NAME=yag-osdl-environment.sh
HELPER_SCRIPT=yag-osdl-debug-helper.py


# Change this setting according to the python version (in /usr/lib/python*):
PYTHON_VERSION=2.5


echo  "
Initializing shell environnment for yag-osdl."

if [ "$0" = "${SCRIPT_NAME}" ] ; then
	echo "Wrong use: this script (${SCRIPT_NAME}) is meant to be sourced, not directly executed. It sets the shell environment so that yag-osdl can be conveniently used. Use 'source ${SCRIPT_NAME}' or '. ${SCRIPT_NAME}' instead." 2>&1
	exit 1
fi



# First: check for python

PYTHON_INFOS="yag-osdl needs an executable python interpreter to be run. The interpreter can be downloaded from: http://www.python.org/. Once available, update PATH environment variable so that the interpreter can be found thanks to 'which python', and relaunch this script."

PYTHON_INTERPRETER="`which python`"

if [ ! -x ${PYTHON_INTERPRETER} ] ; then
	echo "Python interpreter not found in PATH (not found, nothing done). ${PYTHON_INFOS}" 1>&2
	return
else
	echo "    + Python interpreter found, using <${PYTHON_INTERPRETER}>"	
fi



# Second: check for the Python Imaging Library (PIL)

PIL_INFOS="yag-osdl needs the Python Imaging Library (PIL) for its image handling features. It can be downloaded from: http://www.pythonware.com/products/pil/. Once available, either update PIL_ROOT in this script, or put it in your shell environment (for instance, export PIL_ROOT=<where it is installed>, such as export PIL_ROOT=/usr/lib/python${PYTHON_VERSION}/site-packages/PIL). With gentoo, use 'emerge imaging', with Debian-based distributions use 'apt-get install python-imaging'. "

if [ -z "${PIL_ROOT}" ] ; then
	# Change this setting according to the place where you installed PIL:
	PIL_ROOT=/usr/lib/python${PYTHON_VERSION}/site-packages/PIL
fi

if [ ! -d ${PIL_ROOT} ] ; then
	echo "
	Python Imaging Library (PIL) not found, expected directory ${PIL_ROOT} to exist (not found, nothing done). ${PIL_INFOS}" 1>&2
	return
else	

	echo "    + Python Imaging Library (PIL) found, using <${PIL_ROOT}>"	
	
	# Allows to debug yag-osdl directly from the python command line (python -i yag-osdl.py):
	export PYTHONSTARTUP=${HELPER_SCRIPT}

	# Needed to find PIL:
	export PYTHONPATH=${PIL_ROOT}:${PYTHONPATH}
fi	



# Third: check for the Ceylan scripts
	
CEYLAN_INFOS="yag-osdl needs the Ceylan Library for its generic-purpose python scripts. It can be downloaded from: http://osdl.sourceforge.net. Once available, either update CEYLAN_ROOT in this script, or put it in your shell environment (for instance, export CEYLAN_ROOT=<where it is installed>, such as export CEYLAN_ROOT=${HOME}/Projects/LOANI-repository/ceylan/Ceylan."

if [ -z "${CEYLAN_ROOT}" ] ; then
	# Change this setting according to the place where you installed Ceylan: 
	CEYLAN_ROOT=${HOME}/Projects/LOANI-repository/ceylan/Ceylan
fi

if [ ! -d ${CEYLAN_ROOT} ] ; then
	echo "Ceylan not found, expected directory ${CEYLAN_ROOT} to exist (not found, nothing done). ${CEYLAN_INFOS}" 1>&2
	return
	
else
	echo "    + Ceylan library found, using <${CEYLAN_ROOT}>"
	
	# Needed to find Ceylan scripts (ex: toolbox.py):
	export PYTHONPATH=${CEYLAN_ROOT}/trunk/src/code/scripts/python:${PYTHONPATH}

	echo "Shell environment successfully set."
fi	
	
# That's it !	

