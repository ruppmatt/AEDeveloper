#!/bin/bash

args="$@"
sudo sh -c ". venv/bin/activate ; python create_user.py $1 $2 \"$3\" $4"
