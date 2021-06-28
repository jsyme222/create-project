def react_compose(project: str) -> str: return """
 react:
  container_name: "{0}_react_app"
  build:
   context: ./app
  volumes:
   - './app:/app'
   - './app/node_modules:/app/node_modules'
  ports:
   - 3000:3000
  environment:
   - CHOKIDAR_USEPOLLING=true
""".format(project)


react_dockerfile = """FROM node:14
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


COMPOSE = {
    "app": react_compose
}

DOCKERFILE = {
    "app": react_dockerfile
}
