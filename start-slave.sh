#!/bin/bash

if [ $# != 2 ]
then
        echo "Please specify the hostname and ssh port number for slave"
	echo "Options-- ./start-slave.sh HOSTNAME PORT_NUM "
        exit 1
fi

HOSTNAME=$1
PORT=$2

sudo docker run -itd \
			-p $PORT:22 \
                        --name $HOSTNAME \
                        --hostname $HOSTNAME \
                        spark/multinode:1.0

