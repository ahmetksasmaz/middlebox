#!/bin/bash

$(python3 main.py >& /proc/1/fd/1)

while true; 
    do sleep 0.01;
    done