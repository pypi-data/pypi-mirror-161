#!/usr/bin/env bash

# https://datasift.github.io/gitflow/GitFlowForGitHub.html
# https://github.com/datasift/gitflow

exit 0

git hf init

# create new feature
git hf feature start #f1#
# or if already exists
git hf feature checkout #f1#

git hf push

git hf update
git merge develop

git hf push
git hf pull

git hf feature finish

git hf release start #version#
git hf release finish #version#
