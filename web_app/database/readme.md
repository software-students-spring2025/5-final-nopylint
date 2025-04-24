# MongoDB in Docker

This guide will help you quickly get MongoDB up and running in Docker with data persistence.

## Prerequisites

- Docker installed on your machine

## Pull the Latest MongoDB Image

```bash
docker pull mongo:latest
```

## Run MongoDB Container

```bash
docker run -d \
  --name my-mongo \
  -p 27017:27017 \
  -v ~/mongo-data:/data/db \
  mongo:latest
```

- `-d` runs the container in detached mode
- `--name my-mongo` gives the container a friendly name
- `-p 27017:27017` maps the host port 27017 to the container port 27017
- `-v ~/mongo-data:/data/db` mounts the local `~/mongo-data` directory for data persistence

## Verifying the Container

```bash
docker ps --filter "name=my-mongo"

docker logs my-mongo
```

## Run sample python file to verify

```bash
python db.py
```