#!/usr/bin/env bash

target=$(basename $(pwd))
echo "# $target" | tee README.md

git init
git add README.md
git commit -m "first commit"
git remote add origin "git@github.com:eddo888/$target.git"
git push -u origin master
