docker build -t robot-quick-start .
docker run --env-file .env -p 8080:8080 -it robot-quick-start
