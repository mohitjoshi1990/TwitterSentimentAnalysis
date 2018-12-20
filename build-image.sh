#!/bin/bash

echo -e "\nbuild docker spark image\n"
sudo docker build -t spark/multinode:1.0 .
