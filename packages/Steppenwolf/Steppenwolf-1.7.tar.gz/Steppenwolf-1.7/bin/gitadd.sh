#!/usr/bin/env bash

help="\
usage: $(basename $0) <files>\n\
\n\
-v verbose\n\
-h help\n\
-t test\n\
-r recurse\n\
-d delete\n\
-a add\n\
"

verbose=''
test=''
addopt=''
delopt=''
matchers=('.M' '.T')
recurse=''

while getopts vhtrda opt
do
    case $opt in
        v) verbose='-v';;
        h) echo -e "$help";exit 0;;
        t) test='-t';;
        r) recurse='-r';;
        d) delopt='-d';matchers+=('.D');;
        a) addopt='-a';matchers+=('\?\?');;
    esac
done

shift $((OPTIND-1))

repo="$1"

if [ -z "$repo" ] && [ "$recurse" = "-r" ]
then
    find . -name .git -and -type d -exec $0 \
         $verbose \
         $test \
         $recurse \
         $delopt \
         $addopt \
         "{}" \
    \;
else
    if [ "$recurse" = "-r" ]
    then
        repo=$(dirname "$repo")
    else
        repo=.
    fi
    
    function join { 
        local IFS="$1" 
        shift
        echo "$*" 
    }
    
    query=$(join \| ${matchers[@]} )
    
    pushd "$repo" > /dev/null

    if [ ! -d .git ]
    then
        echo "not in root of git tree"
        exit 1
    fi

    if [ "$verbose" = "-v" ]
    then
        horizontal.pl
        echo -e "\033[36m$repo\033[0m"
    fi

    if [ "$test" = "-t" ]
    then
        test='echo'
    fi
    
    git status --porcelain \
        | egrep "$query" \
        | cut -c 4- \
        | perl -pe 's/ ->.*$//' \
        | xargs -n1 -I FILE $test git add "FILE"
    
    
    git status --porcelain
    
    popd >/dev/null
fi



