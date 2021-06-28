FROM node:14
WORKDIR /app
ENV PATH /app/node_modules/.bin:$PATH
COPY package.json ./
COPY yarn.lock ./
RUN yarn install --silent
RUN yarn global add react-scripts@4.0.3
COPY . /app/
EXPOSE 3000
CMD [ "yarn", "start" ]
