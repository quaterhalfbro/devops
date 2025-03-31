ARG NODE_VERSION

FROM node:${NODE_VERSION}-alpine AS system

RUN addgroup -S appgroup && adduser -S appuser -G appgroup

WORKDIR /app

RUN chown -R appuser:appgroup /app
USER appuser
