FROM nginx:stable-alpine

RUN addgroup -S appgroup && adduser -S appuser -G appgroup
RUN chown -R appuser:appgroup /usr/share/nginx/html
RUN chown -R appuser:appgroup /var/cache/nginx
RUN mkdir /var/run/nginx && chown appuser:appgroup /var/run/nginx

USER appuser

COPY configuration /etc/nginx
EXPOSE 80
