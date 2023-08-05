#!/usr/bin/env bash

envr=github.com
user=eddo888
pass=$(passwords.py -e $envr -a git -u $user)

ppwd=$(basename $(dirname $(pwd)))
ownr=$(basename $(pwd))
echo $ppwd/$ownr >&2

if [ "$ppwd" != "github.com" ]
then
  ownr=$user
fi

gitrepos.py -u $user -p $pass -o $ownr $*

