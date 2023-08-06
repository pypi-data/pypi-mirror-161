#!/bin/bash

# USAGE:
# $ ./status_dumper.sh

###########################
# Find the component home #
###########################
SCRIPT_FILE=$0
SCRIPT_DIR=`(cd \`dirname ${SCRIPT_FILE}\`; pwd)`
# If the script file is a symbolic link
if [[ -L "${SCRIPT_FILE}" ]]
then
    SCRIPT_FILE=`ls -la ${SCRIPT_FILE} | cut -d">" -f2`
    SCRIPT_DIR=`(cd \`dirname ${SCRIPT_FILE}\`; pwd)`
fi
# Remove the '..' in the path (if using a link or a source)
export APPLICATION_HOME="$(dirname "${SCRIPT_DIR}")"

# Disable export keywords
set -o allexport
# Load the config file 'env.conf'
. ${SCRIPT_DIR}/env.conf

echo "-------------------------------"
echo -e "- Status of job '${BLUE}${JOB_NAME}${NC}'"
echo "-------------------------------"

EXISTING_PID=$(_getExistingPid)
if [[ "${EXISTING_PID}" = "" ]]; then
    echo -e "Job is ${RED}not running${NC} !"
else
    echo -e "${GREEN}Job alive${NC}: Process ID = ${EXISTING_PID}"
fi
echo ""
