#!/bin/bash --login

# Make bashline configurations.
set -e
RESET='\033[0m'
COLOR='\033[1;32m'
COLOR_ERR='\033[1;31m'

function msg {
    echo -e "${COLOR}$(date): $1${RESET}"
}

function msg_err {
    echo -e "${COLOR_ERR}$(date): $1${RESET}"
}

function fail {
    msg_err "Error : $?"
    exit 1
}

function mcd {
    mkdir -p "$1" || fail
    cd "$1" || fail
}

function nvm_has {
    type "$1" > /dev/null 2>&1
}

if nvm_has "python"; then
    PYTHON=python
else
    if nvm_has "python3"; then
        PYTHON=python3
    else
        msg_err "Fail to find Python3 in the base image, stop the build."
        exit 1
    fi
fi

SCRIPT_PATH="$(dirname "$(readlink -f "$0")")"

# Check the OS version
NAME_OS=$(lsb_release -is)

if [ "x${NAME_OS}" = "xUbuntu" ] || [ "x${NAME_OS}" = "xDebian" ]; then
	msg "Pass the OS check. Current OS: ${NAME_OS}."
else
	msg_err "The base image is an unknown OS, this dockerfile does not support it: ${NAME_OS}."
fi
