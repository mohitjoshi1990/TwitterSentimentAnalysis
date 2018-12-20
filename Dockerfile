FROM ubuntu:16.04

MAINTAINER Mohit Joshi <mohit139145@gmail.com>

WORKDIR /root

# install openssh-server, python, wget, openjdk and scala
RUN apt-get update && apt-get install -y openssh-server wget python-software-properties scala software-properties-common vim

# install spark
RUN wget http://www-us.apache.org/dist/spark/spark-2.3.1/spark-2.3.1-bin-hadoop2.7.tgz && \
    tar -xzvf spark-2.3.1-bin-hadoop2.7.tgz && \
    mv spark-2.3.1-bin-hadoop2.7 /usr/local/spark && \
    rm spark-2.3.1-bin-hadoop2.7.tgz

# set environment variable
ENV SPARK_HOME=/usr/local/spark
ENV PATH=$PATH:/usr/local/spark/bin:/usr/local/spark/sbin 

# ssh without key
RUN ssh-keygen -t rsa -f ~/.ssh/id_rsa -P '' && \
    cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys

COPY config/* /tmp/

RUN mv /tmp/spark-env.sh /usr/local/spark/conf/ && \
    mv /tmp/slaves.sh /usr/local/spark/sbin/slaves.sh && \
    mv /tmp/ssh_config ~/.ssh/config && \
    mv /tmp/start-master.sh /usr/local/spark/sbin/start-master.sh && \
    cp /tmp/authorized_keys ~/.ssh/ && \
    cp /tmp/id_rsa ~/.ssh/ && \
    cp /tmp/id_rsa.pub ~/.ssh/

RUN chmod +x /usr/local/spark/sbin/slaves.sh && \
    chmod +x /usr/local/spark/sbin/start-master.sh && \
    chmod 600 ~/.ssh/id_rsa && \
    chmod 644 ~/.ssh/authorized_keys && \
    chmod 644 ~/.ssh/config && \
    chmod 600 ~/.ssh/ && \
    chmod 644 ~/.ssh/id_rsa.pub

CMD [ "sh", "-c", "service ssh start; bash"]

# apt-get install python-pip
# apt-get install lynx
# lynx http://localhost:8080 

# ./bin/spark-submit --master spark://spark-master:7077 examples/src/main/python/wordcount.py /usr/local/spark/LICENSE
