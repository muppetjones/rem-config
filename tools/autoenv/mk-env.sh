#!/bin/sh

NAME="${1}"

if [[ "${NAME}" == "" ]]; then
    echo "\tvenv name is required"
    exit 1
fi

echo "activate jane-py38;\nexport LOG_IN_COLOR=1;\n" > .env
echo "deactivate" > .env.leave;

