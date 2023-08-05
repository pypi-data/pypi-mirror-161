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

for file in $*
do
    $test git filter-branch --tree-filter "rm -f \"$file\"" HEAD
done
