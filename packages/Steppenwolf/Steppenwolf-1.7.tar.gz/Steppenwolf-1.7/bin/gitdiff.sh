#!/usr/bin/env bash

help="\
usage: $(basename $0) <repos...>\n\
\n\
-v verbose\n\
-h help\n\
-r recurse\n\
"

verbose=''
fetch=''
recurse=''

while getopts vhr opt
do
    case $opt in
        v) 
            verbose='-v'
            ;;
        h) 
            echo -e "$help"
            exit 0
            ;;
        r)
            recurse="-r"
            ;;
    esac
done

shift $((OPTIND-1))

repo="$1"

if [ -z "$repo" ] && [ "$recurse" = "-r" ]
then
    find . -name .git -and -type d -exec $0 \
         $verbose \
         $fetch \
         $recurse \
         "{}" \
    \;
else
    if [ "$recurse" = "-r" ]
    then
        repo=$(dirname "$repo")
    else
        repo=.
    fi

    pushd "$repo" > /dev/null
    if [ "$verbose" = "-v" ]
    then
        if ! git status --porcelain | grep -v "^?" | wc -l | grep "^\s*0\s*$" > /dev/null
        then
            horizontal.pl
            echo -e "\033[36m$repo\033[0m"
        fi
    fi

    git diff
    
    popd >/dev/null
fi

