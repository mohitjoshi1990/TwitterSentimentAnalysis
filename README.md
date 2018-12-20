Group Members:

Mohit Joshi	mjoshi7	


To start the application.


1. Edit the config/nodes file and add the slave and master IP and ssh port

2. bash build-image.sh

3. bash start-master.sh 
[ Inside container, bash /tmp/setHosts.sh ]

4. bash start-slave.sh HOSTNAME SSH-PORT

5. docker cp sentpy/* spark-master:/usr/local/spark/

6. Start spark-master, 
cd /usr/local/spark/
./bin/spark-submit --master spark://spark-master:7077 sentiment.py
