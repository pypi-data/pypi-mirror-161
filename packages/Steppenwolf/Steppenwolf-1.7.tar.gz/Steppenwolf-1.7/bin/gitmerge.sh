#!/usr/bin/env bash

read -d '' help <<EOF
usage: $(basename $0)

-v verbose
-h help
-T trial run
-y yes to ok
-r refresh origin
-i ignore uncommited
-o origin       default=origin
-f from branch  default=develop
-t to branch    default=master

EOF

verbose=""
yes=""
refresh=""
trial=""
ignore=""
origin="origin"
from="develop"
to="master"

while getopts hvyrTio:f:t: opt
do
    case $opt in
        h) echo "$help"; exit 0;;
        y) yes="-y";;
        r) refresh="-r";;
        v) verbose="-v";;
        T) trial="echo ";;
        i) ignore="-i";;
        o) origin=$OPTARG;;
        f) from=$OPTARG;;
        t) to=$OPTARG;;
    esac
done

shift $((OPTIND-1))

if [ "$yes" != "-y" ]
then
    read -p "are you sure (yes/no) ? " sure

    if [ "$sure" != "yes" ]
    then
        echo "exiting"
        exit 1
    fi
fi

if [ ! -d .git ]
then
    echo "not in the git root directory"
    exit 1
fi

if [ "$ignore" != "-i" ]
then
    if ! git status --porcelain | wc -l | grep "^\s*0\s*$" > /dev/null
    then
        echo "uncommited files, exiting"
        exit 1
    fi
fi


if [ "$refresh" == "-r" ]
then
    $trial git pull $origin $from
    $trial git push $origin $from
    
    $trial git pull $origin $to
    $trial git push $origin $to
fi

$trial git checkout $to
$trial git merge $from
$trial git checkout $from

$trial git push -u $origin $to


