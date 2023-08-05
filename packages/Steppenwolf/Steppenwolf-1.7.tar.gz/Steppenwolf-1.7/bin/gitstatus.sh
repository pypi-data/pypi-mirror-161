#!/usr/bin/env bash

help="\
usage: $(basename $0) <repos...>\n\
\n\
-v verbose\n\
-h help\n\
-a all\n\
-f fetch\n\
-r recurse\n\
"

verbose=''
all=''
fetch=''
recurse=''

while getopts vhafr opt
do
    case $opt in
        v) verbose='-v';;
        h) echo -e "$help"; exit 0;;
        a) all='-a';;
        f) fetch='-f';;
        r) recurse='-r';;
    esac
done

shift $((OPTIND-1))

repo="$1"

if [ -z "$repo" ] && [ "$recurse" = '-r' ]
then
    find . -name .git -and -type d -exec $0 \
         $verbose \
         $all \
         $fetch \
         $recurse \
         "{}" \
    \;
else
    if [ "$recurse" = '-r' ]
    then
        repo=$(dirname "$repo")
    else
        repo=.
    fi

    pushd "$repo" > /dev/null

    cmd="git status --porcelain"

    if [ "$all" != '-a' ]
    then
        cmd="$cmd | grep -v '^?'"
    fi
    
    if [ "$verbose" = '-v' ]
    then
        if ! eval $cmd | wc -l | grep '^\s*0\s*$' > /dev/null
        then
            horizontal.pl
            echo -e "\033[36m$repo\033[0m: $(gitbranch.sh)"
        fi
    fi

    if [ "$fetch" = '-f' ] 
    then
        git fetch
    fi
    eval $cmd
    
    popd >/dev/null
fi

