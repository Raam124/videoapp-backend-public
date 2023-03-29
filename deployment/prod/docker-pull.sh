aws ecr get-login-password --region us-east-1 | sudo docker login --username AWS --password-stdin 091995416524.dkr.ecr.us-east-1.amazonaws.com
docker pull 091995416524.dkr.ecr.us-east-1.amazonaws.com/videoapp:latest
docker compose pull server
docker compose stop server
docker compose rm -y server
docker compose up -d server