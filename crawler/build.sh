#!/usr/bin/env bash
# this script creates a aws lambda deployment package zip which can be uploaded to aws. 
rm -rf ./dist

mkdir -p ./dist

cp crawl.py lambda_function.py ./dist

cd dist

pip install --target ./package requests

cd ./package

zip -r ../lambda_deployment.zip .

cd ../ 

zip ./lambda_deployment.zip ./crawl.py 

zip ./lambda_deployment.zip ./lambda_function.py

cd ../
