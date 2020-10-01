#!/bin/bash

#
# You must put 7daystodie/application/Data to 7d2d_app direcotry before execute.
#
#   1. cd THIS_PROJECT_ROOT
#   2. cp -R /opt/7daystodie/application/Data ./7d2d_app
#   3. ls ./7d2d_app
#       > Data
#   4. ./run.sh ./7d2d_app/Data
#

readonly DTAG="7d2d-itemlist"

docker build -t $DTAG:latest .

docker run --rm\
    -v `pwd`:/app \
    -it \
    $DTAG:latest \
    python gen_7d2d_itemlist.py $@

