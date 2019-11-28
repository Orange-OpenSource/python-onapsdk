#!/bin/sh

INITIAL_FOLDER=${PWD}
INITIAL_BRANCH=$(git rev-parse --abbrev-ref HEAD)

if [ -e requirements.txt ]
then
    pip install -r requirements.txt
fi
if [ -e doc-requirements.txt ]
then
    pip install -r doc-requirements.txt
fi
if [ -e requirements.txt ]
then
    pip install .
fi

set -x
# Generating documentation for each other branch in a subdirectory
for BRANCH in $(git branch --remotes --format '%(refname:lstrip=3)' | grep -Ev '^(HEAD)$'); do
    echo "*** Building doc for branch ${BRANCH} ***"
    git checkout $BRANCH
    cd ${INITIAL_FOLDER}${DOC_PATH}
    make html
    mkdir -p ${INITIAL_FOLDER}/public/$BRANCH
    mv _build/html/ ${INITIAL_FOLDER}/public/$BRANCH
    rm -rf _build/html/
    cd ${INITIAL_FOLDER}
done

# "Develop" is the default branch so we point it as "latest"
# May/Will change to point master
ln public/develop public/latest

git checkout $INITIAL_BRANCH
