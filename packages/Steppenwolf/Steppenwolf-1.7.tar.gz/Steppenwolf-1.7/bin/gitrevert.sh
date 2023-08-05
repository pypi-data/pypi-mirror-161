#!/usr/bin/env bash

help="\
usage: $(basename $0) <files>\n\
\n\
-v verbose\n\
-h help\n\
-t test\n\
"

verbose=0
test=''

while getopts vht opt
do
    case $opt in
        v) 
            verbose=1
            ;;
        h) 
            echo "$help"
            exit 0
            ;;
        t)
            test='echo '
            ;;
    esac
done

shift $((OPTIND-1))

read -p "are you sure (yes/no) ? " sure

if [ "$sure" != "yes" ]
then
    echo "exiting"
    exit 1
fi

if [ -d .git ]
then
    local=1
    repos=$(pwd)
else
    local=0
    repos=*
fi

for git in $*
do
    $test git checkout $git
done

for repo in $repos
do
    if [ -d "$repo" ] && [ ! "$repo" = "." ]
    then
	    pushd "$repo" > /dev/null

        if [ "$local" = "0" ] || [ "$verbose" = "1" ]
        then
            echo -e "\033[34m$repo\033[0m"
        fi

	    git status --porcelain | cut -c 4- | xargs -n1 $test git checkout

	    popd > /dev/null
    fi
done
