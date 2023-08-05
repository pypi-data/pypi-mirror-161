#!/bin/bash -ex 
(nohup flask run 1>/dev/null 2>&1) &
mypid=$!
echo "- pid: $mypid" > /Users/ben/git/ansible_events/tests/facts.yml

