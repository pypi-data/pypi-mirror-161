#!/bin/bash

# USAGE:
# $ ./bin/stop.sh ${JOB_NAME}

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


EXISTING_PID=$(_getExistingPid)
echo "-------------"
if [[ "${EXISTING_PID}" = "" ]]; then
  echo -e "No Job ${BLUE}${JOB_NAME}${NC} is currently running"
else
  kill $EXISTING_PID
  echo "Job ${JOB_NAME} with processID $EXISTING_PID was killed"
fi
echo
