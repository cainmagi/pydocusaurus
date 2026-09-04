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

BASH=false

# Pass options from command line
for ARGUMENT in "$@"
do
    KEY=$(echo $ARGUMENT | cut -f1 -d=)
    if [[ $KEY != '--*' ]]
    then
        VALUE=$(echo $ARGUMENT | cut -f2 -d=)   
    fi
    case "$KEY" in
        --bash)         BASH=true ;;
        *)   
    esac
done

if $BASH
then
    msg "pyDocusaurus experimental environment."
    exec bash
    exit 0
fi

msg "pyDocusaurus example server."

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

# Run the app.
msg "Start the Python program."
${PYTHON} -m pytest || fail
