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

APT_OPTIONS="-o Acquire::Retries=5 -o Acquire::http::timeout=20 -o Acquire::https::timeout=20"

# Required packages
msg "Install dependencies by APT."
apt-get -y update || fail && apt-get $APT_OPTIONS -y install \
    apt-utils apt-transport-https curl wget \
    gnupg2 lsb-release libffi-dev build-essential sudo || fail

if ! nvm_has "lsb_release"; then
    msg_err "lsb_release does not exist. This should not happen. Please contact the author for technical supports."
    exit 1
fi

# Check the OS version
NAME_OS=$(lsb_release -is)

if [ "x${NAME_OS}" = "xUbuntu" ] || [ "x${NAME_OS}" = "xDebian" ]; then
	msg "Pass the OS check. Current OS: ${NAME_OS}."
else
	msg_err "The base image is an unknown OS, this dockerfile does not support it: ${NAME_OS}."
fi

msg "Install developer's dependencies by APT."
apt-get -y upgrade || fail
apt-get -y update -qq || fail
apt-get $APT_OPTIONS -y install git-core procps || fail
msg "Successfully install developer's dependencies."

# Finalizing the APT installations.
apt-get -y update || fail && apt-get -y upgrade || fail && apt-get -y \
    dist-upgrade || fail && apt-get -y autoremove || fail && apt-get -y \
    autoclean || fail

${PYTHON} -m pip install --compile --no-cache-dir pip wheel setuptools build --upgrade || fail

msg "Install developer's Python Packages."
${PYTHON} -m pip install --compile --no-cache-dir -r requirements-docker.txt -r requirements/all.txt -r tests/requirements.txt || fail

# Install Node.js and Yarn.
mcd /app || fail
wget -O- https://gist.githubusercontent.com/cainmagi/f028e8ac4b06c3deefaf8ec38d5a7d8f/raw/install-nodejs.sh | bash -s -- --all || fail
