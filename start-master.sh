sudo docker run -itd \
		-p 7077:7077 \
                -p 8080:8080 \
                --name spark-master \
                --hostname spark-master \
                spark/multinode:1.0

sudo docker exec -it spark-master bash

