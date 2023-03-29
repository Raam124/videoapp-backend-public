export AWS_PROFILE=videoappuser
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 091995416524.dkr.ecr.us-east-1.amazonaws.com
cd ../../
docker build -t videoapp .
docker tag videoapp:latest 091995416524.dkr.ecr.us-east-1.amazonaws.com/videoapp:latest
docker push 091995416524.dkr.ecr.us-east-1.amazonaws.com/videoapp:latest