FROM nginx:stable-alpine

COPY ./configuration /etc/nginx
EXPOSE 80