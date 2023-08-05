#!/usr/bin/env bash


origins=$(git remote|xargs)
echo "origins=(${origins[@]})"

origin=$(git branch -vv | perl -ne 'print "$1\n" if (/^\*\s+\S+\s+\S+\s\[([^\]]*)\/.*\].*/);') 
echo "origin=$origin"

branches=$(git branch | cut -c 3- | xargs)
echo "branches=(${branches[@]})"

branch=$(git branch -vv | perl -ne 'print "$1\n" if (/^\*\s+(\S+)\s+/);')
echo "branch=$branch"
