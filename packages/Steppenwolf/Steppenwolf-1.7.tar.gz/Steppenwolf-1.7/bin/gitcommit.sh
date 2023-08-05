#!/usr/bin/env bash

help="\
usage: $(basename $0)\n\
\n\
-v verbose\n\
-h help\n\
-r recurse\n\
-t test\n\
-m comment\n\
"

verbose=''
echo=''
test=''
recurse=''
comment=''

while getopts vhtrm: opt
do
    case $opt in
        v) 
            verbose="-v"
            ;;
        h) 
            echo "$help"
            exit 0
            ;;
        t)
            test='-t'
            echo='echo'
            ;;
        r)
            recurse='-r'
            ;;
        m)
            comment=$OPTARG
            ;;
    esac
done

shift $((OPTIND-1))

if [ -z "$comment" ]
then
    comment=$(dateStamp.sh)
fi

repo="$1"

if [ -z "$repo" ] && [ "$recurse" = "-r" ]
then
    find . -name .git -and -type d -exec $0 \
         $verbose \
         $recurse \
         $test \
         -m "$comment" \
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
        horizontal.pl =
        echo -e "\033[36m$repo\033[0m"
    fi

    if [ -d '.git' ]
    then
        lines=$(echo $(git status --porcelain | wc -l))
        if [ ! "$lines" = "0" ]
        then
            $echo git commit -m "$comment"
        fi
    fi
    
    popd >/dev/null
fi
