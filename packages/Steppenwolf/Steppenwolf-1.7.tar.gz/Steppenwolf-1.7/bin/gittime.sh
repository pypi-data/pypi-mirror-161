#!/usr/bin/env bash

IFS=$'\n'

rev=HEAD

declare -a files

files=$*

if [ -z "$files" ]
then
	files=$(git ls-tree -r -t --full-name --name-only "$rev")
fi

for f in ${files[@]}
do
	dts=$(git log --pretty=format:%cd --date=format:%Y%m%d%H%m.%S -1 "$rev" -- "$f")
	echo "$f" "$dts"
	touch -t "$dts" "$f"
done

