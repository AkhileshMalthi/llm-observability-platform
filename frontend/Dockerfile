FROM node:20-alpine

WORKDIR /app

# Alpine comes with busybox wget, but we can make sure it's available or install if needed.
# Just installing basic requirements to prevent node module mount errors.
COPY package.json .
RUN npm install

COPY . .

CMD ["npm", "run", "dev"]
