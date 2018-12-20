#!/usr/bin/env bash

host=$(hostname)
grep -wq $host /usr/local/spark/conf/slaves
if [ $? -ne 0 ]
then
	echo "$ip       $host" >> /usr/local/spark/conf/slaves
fi

while read line; do

	host=$(echo $line  | awk -F ' ' {'print $1'} | xargs)
	ip=$(echo $line  | awk -F ' ' {'print $2'} | awk -F ':' {'print $1'} | xargs)

	grep -wq $host /etc/hosts
	if [ $? -ne 0 ]
	then
		echo "$ip	$host" >> /etc/hosts
	fi

	grep -wq $host /usr/local/spark/conf/slaves
        if [ $? -ne 0 ]
        then
                echo "$host" >> /usr/local/spark/conf/slaves
        fi

done </tmp/nodes

