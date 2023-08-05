#############################
# Find the application home #
#############################
SCRIPT_FILE=$0
SCRIPT_DIR=`(cd \`dirname ${SCRIPT_FILE}\`; pwd)`
# Remove the '..' in the path (if using a link or a source)
export APPLICATION_HOME="$(dirname "${SCRIPT_DIR}")"
# Disable export keywords
set -o allexport
# Load the config file 'env.conf'
. ${SCRIPT_DIR}/env.conf

APP_CMD="${VIRTUAL_ENV}/bin/python -u ${APPLICATION_HOME}/job/${JOB_NAME}.py"

echo
EXISTING_PID=$(_getExistingPid)
if [[ "${EXISTING_PID}" = "" ]]; then
    nohup ${APP_CMD} </dev/null 2>${ERR_FILE} > ${NOHUP_FILE} &

    echo -e "Application ${BLUE}${JOB_NAME}${NC} successfully ${GREEN}started${NC}!"
else
    echo -e "A Job ${BLUE}${JOB_NAME}${NC} is already running with with Process ID = ${EXISTING_PID}"
fi
echo
