#!/bin/bash

mkdir /tmp/cp1/replays
cd /tmp/cp1/replays
git clone /afs/andrew/course/15/441-641/$1/$1-15-441-project-1
cd $1-15-441-project-1
git checkout tags/checkpoint-1
cp ./replay.out ../$1-replay.out
cp ./replay.test ../$1-replay.test
cd ../
rm -rf /tmp/cp1/replays/$1-15-441-project-1