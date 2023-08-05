#!/usr/bin/env bash

usage="\
usage: $0 \n\
    -h         help\n\
    -o         use existing origin url\n\
    -t         test only don\'t execute\n\
"

echo=''
origin=''

while getopts hto: opt
do
    case $opt in
        h) echo -e "$usage"; exit;;
        o) origin=$OPTARG; echo "origin=$origin" 1>&2;;
        t) echo='echo '; echo "testing only, won\'t execute" 1>&2;;
    esac
done

shift $((OPTIND-1))

if [ ! -d ".git" ]
then
    echo ".git doesn't exist"
    exit 1
fi

if [ -z "$origin" ]
then
    echo "plese specifiy origin with -o"
    exit 1
fi

$echo git remote add origin "$origin"
$echo git push origin master
$echo git branch --set-upstream-to=origin/master master
$echo gitpush.sh

