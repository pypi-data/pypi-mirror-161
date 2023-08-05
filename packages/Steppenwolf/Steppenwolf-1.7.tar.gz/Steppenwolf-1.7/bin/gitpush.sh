#!/usr/bin/env bash

help="\
usage: $(basename $0) <repos>\n\
\n\
-v verbose\n\
-h help\n\
-r recurse\n\
-O all origins\n\
-B all branches\n\
-a all everything\n\
-o origin\n\
-b branch\n\
-t test only dont execute\n\
"

verbose=''
recurse=''
all_everything=''
all_origins=''
all_branches=''
the_origin=''
the_branch=''
test=''
echo=''

while getopts vhaOBro:b:t opt
do
    case $opt in
        v) verbose='-v';;
        h) echo -e "$help"; exit 0;;
        r) recurse='-r';;
        O) all_origins='-O';;
        B) all_branches='-B';;
        a) all_everything='-a';;
        o) the_origin=$OPTARG;;
        b) the_branch=$OPTARG;;
        t) test='-t'; echo='echo';;
        \?)
            # everything else is invalid
            echo -e "\n$(basename $0): Invalid option -$opt\n\n$help\n" >&2
            exit 1
            ;;
    esac
done

shift $((OPTIND-1))

repo="$1"

if [ -z "$repo" ] && [ "$recurse" = "-r" ]
then
    find . -name .git -and -type d -exec $0 \
         $verbose \
         $all_everything \
         $all_origins \
         $all_branches \
         $recurse \
         $test \
         -o "$the_origin" \
         -b "$the_branch" \
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

    if [ -d '.git' ]
    then

        if [ "$verbose" = "-v" ]
        then
            horizontal.pl
            echo -e "\033[36m$repo\033[0m"
        fi

        source gittree.sh > /dev/null

        if [ "$all_everything" = "-a" ] || [ "$all_origins" = "-O" ]
        then
            origins=$origins
        else
            if [ ! -z "$the_origin" ]
            then
                origins=($the_origin)
            else
                origins=($origin)
            fi
        fi

        if [ "$all_everything" = "-a" ] || [ "$all_branches" = "-B" ]
        then
            branches=$branches
        else
            if [ ! -z "$the_branch" ]
            then
                branches=($the_branch)
            else
                branches=($branch)
            fi
        fi
        
        for o in ${origins[@]}
        do
            if [ ! -z "$0" ]
            then
                for b in ${branches[@]}
                do
                    if [ "$verbose" = "-v" ]
                    then
                        horizontal.pl .
                        echo -e "\033[34m$o->$b\033[0m"
                    fi
                    $echo git push $o $b
                done
            fi
        done
    fi
    
    popd >/dev/null
fi

