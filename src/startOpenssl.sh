#! /bin/bash

if [ "$1" = "" ];
then
    workroot=`pwd`
else
    workroot=$1
    cd $workroot
fi
export PYTHONPATH="."
PROCESS_NUM=`ps -ef | grep "python $workroot/openssl" | grep -v "grep" | wc -l`
if [ $PROCESS_NUM -gt 0 ];
then
    echo "the Service is already running!"
    exit 1
else
    if [ -f "$workroot/openssl.pyc" ]; then
        nohup python $workroot/openssl.pyc >$workroot/main.out &
    else
        nohup python $workroot/openssl.py >$workroot/main.out &
    fi
    echo "--------------started---------------"

fi
