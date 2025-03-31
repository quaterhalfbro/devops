FROM myapp-system AS final

COPY --from=myapp-build /app .

ARG NODE_PORT
EXPOSE ${NODE_PORT}

CMD ["npm", "start"]