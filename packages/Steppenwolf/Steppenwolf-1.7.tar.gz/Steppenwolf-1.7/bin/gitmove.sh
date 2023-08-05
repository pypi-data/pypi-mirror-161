#!/usr/bin/env bash

help="\
usage: $(basename $0)\n\
\n\
-v verbose\n\
-h help\n\
-t test only, don't execute\n\
-d this dir\n\
-o old repo. mandatory\n\
-n new repo. mandatory\n\
-p prefix only\n\
"

verbose=''
test=''
dir=''
old=''
new=''
prefix=''

while getopts vhtd:o:n:p opt
do
    case $opt in
        v) verbose='-v';;
        h) echo -e "$help"; exit 0;;
        t) test='-t';;
        d) dir=$OPTARG;;
        o) old=$OPTARG;;
        n) new=$OPTARG;;
        p) prefix='-p';;
    esac
done

shift $((OPTIND-1))

if [ -z "$old" ]
then
    echo -e "$help" | colourize.py -r "old repo"
    exit 1
fi

if [ -z "$new" ]
then
    echo -e "$help" | colourize.py -r "new repo"
    exit 1
fi

if [ -z "$dir" ]
then
    if [ "$verbose" = '-v' ]
    then
        echo $(basename $0) $verbose $test $prefix -o "$old" -n "$new"
    fi
    
    find . -name .git -and -type d -exec $0 \
         $verbose \
         $test \
         $prefix \
         -d "{}" \
         -o "$old" \
         -n "$new" \
    \;
else
    dir=$(dirname "$dir")

    pushd "$dir" > /dev/null

    if [ "$verbose" = '-v' ]
    then
        horizontal.pl
        echo -e "\033[36m$dir\033[0m"
    fi

    declare -A repos
    
    while read line; do
        IFS=' ' read name repo type <<< $line
        if [ "$type" = "(fetch)" ]
        then
            repos["$name"]="$repo"
            export repos
        fi
    done < <(git remote -v) 

    if [ "$test" = "-t" ]
    then
        echo=echo
    else
        echo=''
    fi
    
    for name in "${!repos[@]}"
    do
        repo=${repos[$name]}

        if [ "$prefix" = "-p" ]
        then
            rhs=${repo#$old}
            lhs=${repo%$rhs}
            if [ "$lhs" = "$old" ] && [ "$lhs$rhs" = "$repo" ]
            then
                pnew="$new$rhs"
                echo "$old->$pnew"
                $echo git remote remove $name
                $echo git remote add $name $pnew
            fi
        else
            if [ "$repo" = "$old" ]
            then
                echo "$old->$new"
                $echo git remote remove $name
                $echo git remote add $name $new
            fi
        fi
    done
    
    popd >/dev/null
fi

