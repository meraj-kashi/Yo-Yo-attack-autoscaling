#!/bin/bash

sudo yum update
sudo yum install python3
sudo amazon-linux-extras install nginx1.12

sudo touch /etc/systemd/system/app.service
sudo cp app.service /etc/systemd/system/app.service

sudo systemctl daemon-reload
sudo systemctl start app.service
sudo systemctl enable app.service

# add Nginx configuration:  /etc/nginx/nginx.conf

sudo usermod -a -G ec2-user nginx
chmod 710 /home/ec2-user
sudo nginx -t
sudo systemctl enable nginx
sudo systemctl start nginx