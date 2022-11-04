#!/bin/sh

echo "Creating docker image repositories"
aws cloudformation create-stack --stack-name ecr-repos-ddosudpflooder --template-body file://./ecr-repos.json

