#!/bin/sh
sudo apt update
sudo apt upgrade
sudo apt install -y git wget python3 python3-pip

wget -qO - https://www.mongodb.org/static/pgp/server-5.0.asc | sudo apt-key add -
echo "deb http://repo.mongodb.org/apt/debian buster/mongodb-org/5.0 main" | sudo tee /etc/apt/sources.list.d/mongodb-org-5.0.list

sudo apt update
sudo apt-get install -y mongodb-org
sudo systemctl start mongod

pip install -r requirements.txt
