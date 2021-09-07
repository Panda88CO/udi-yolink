#!/usr/bin/env bash


mkdir -p profile 
mkdir -p profile/nodedef
mkdir -p profile/nls
mkdir -p profile/editor

#needed for Polisy operation
#sudo pkg install py38-pillow
# only needed for PRi operation

pip install --upgrade pip 

apt-get -y install libxml2-dev libxslt-dev python-dev

#pip install --upgrade pip 
#pip install git+https://github.com/jrester/tesla_powerwall#egg=tesla_powerwall
#pip3 install -r tesla_powerwall --user
#pip install git+https://github.com/maraujop/requests-oauth2#egg=requests-oauth2


#pip install -r svglib 
#pip install -r reportlab
#pip install -r requests

pip install -r requirements_cloud.txt --user