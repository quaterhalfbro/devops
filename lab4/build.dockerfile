FROM myapp-system AS build

COPY *.json ./

RUN npm install && npm cache clean --force

COPY . .
RUN npm run build

RUN npm prune --production