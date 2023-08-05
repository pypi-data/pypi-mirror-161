#!/usr/bin/env bash

git branch -vv | perl -ne 'print "$1\n" if (/^\*\s+\S+\s+\S+\s\[([^\]]*)\/.*\].*/);'
