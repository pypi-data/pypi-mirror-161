#!/usr/bin/env bash

private="$1"

if [ -z "$private" ]
then
    echo "usage: $0 <privateKey>"
    exit 1
fi

if [ -f "$private.pub" ]
then
    echo "public key $private.pub already exists, exiting"
    exit 1
fi

ssh-keygen -y -f "$private" > "$private.pub"

chmod 600 "$private.pub"
ls "$private.pub"
