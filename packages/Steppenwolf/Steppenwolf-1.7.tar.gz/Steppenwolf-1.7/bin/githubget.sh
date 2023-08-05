#!/usr/bin/env bash

path="$1"

if [ -z "$path" ]; then
	pwd=$(pwd)
	here=$(basename $pwd)
	there='eddo888'
	if [ "$here" != "$there" ]; then
		echo "looks like you are not in $there directory"
	else
		echo "you are in $there"
		githubapi.py list | xargs -n1 $0
	fi
else
    if [ -e "../$path" ]; then
		pushd "../$path" > /dev/null
		pwd
		git checkout develop
		git pull
		popd > /dev/null
    else
		git clone git@github.com:${path}.git
    fi
fi
