#!/usr/bin/env bash

existing=0
base="/Volumes/ORICO/Repository"
user=$(whoami)
host=localhost

usage="\
usage: $0 \n\
    -h         help\n\
    -e         use existing repo as source\n\
    -r         test only don\'t execute\n\
    -b base    git base dir\n\
"

echo=''

while getopts hetb: opt
do
    case $opt in
        h) echo -e "$usage"; exit;;
        e) existing=1; echo "upload existing" 1>&2;;
        t) echo='echo '; echo "testing only, won\'t execute" 1>&2;;
        b) base=$OPTARG; echo "base=$base" 1>&2;;
    esac
done

shift $((OPTIND-1))

repo="$1"

if [ -z "$repo" ] 
then
    echo "usage: $0 <repo>"
    exit 1
fi

if [ "$repo" == "." ]
then
    repo=$(basename $(pwd))
fi

repo=$(echo "$repo" | perl -pe 's|/$||')

if [ -e "$base/$repo.git" ]
then
    echo "$base/$repo.git already exists"
    exit 1
fi

pushd "$base"
$echo mkdir -p "$repo.git"
$echo cd "$repo.git"
$echo git init --bare
popd

function pushit {
    $echo git remote add origin "$base/$repo.git"
    $echo git push origin master
    $echo git branch --set-upstream-to=origin/master master
    $echo gitpush.sh
}

if [ $existing == 1 ] && [ -e "$repo/.git" ] 
then
    pushd "$repo"
    pushit
    popd
else
    pushd "$TEMP"
    $echo mkdir -p "$repo"
    $echo cd "$repo"
    $echo git init
    $echo echo target >> .gitignore
    $echo echo "# $repo" > README.md
    $echo gitadd.sh -a
    $echo gitcommit.sh -m 'moved remote'
    pushit
    popd
fi

