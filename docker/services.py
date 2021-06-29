def react_compose(project: str) -> str: return """
 react:
  container_name: "{0}_react_app"
  build:
   context: ./app
  volumes:
   - './app:/app'
  ports:
   - 3000:3000
  environment:
   - CHOKIDAR_USEPOLLING=true
""".format(project)


def fastapi_compose(project: str) -> str: return """
 api:
  container_name: "{0}_fastapi"
  build:
   context: ./api
  command: bash -c 'while !</dev/tcp/db/5432; do sleep 1; done; uvicorn api.main:app --host 0.0.0.0'
  volumes:
   - './api:/api'
  ports:
   - 8000:8000
  environment:
   - DATABASE_URL=postgresql://postgres:postgres@db:5432/postgres
  depends_on:
   - db
 db:
  image: postgres:13-alpine
  volumes:
   - ./postgres_data:/var/lib/postgresql/data/
  expose:
   - 5432
  environment:
   - POSTGRES_USER=postgres
   - POSTGRES_PASSWORD=postgres
   - POSTGRES_DB=postgres

""".format(project)


react_dockerfile = """FROM node:14-slim-buster
WORKDIR /app
ENV PATH /app/node_modules/.bin:$PATH
COPY package.json ./
COPY yarn.lock ./
RUN yarn install --silent
RUN yarn global add react-scripts@4.0.3 sass
COPY . /app/
EXPOSE 3000
CMD [ "yarn", "start" ]
"""

fastapi_dockerfile = """# Dockerfile

# pull the official docker image
FROM python:3.9.5-slim

# set work directory
WORKDIR /api

# set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# copy project
COPY . .
"""

COMPOSE = {
    "app": react_compose,
    "api": {
        "fastapi": fastapi_compose
    }
}

DOCKERFILE = {
    "app": react_dockerfile,
    "api": {
        "fastapi": fastapi_dockerfile
    }
}
