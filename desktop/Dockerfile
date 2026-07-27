# syntax=docker/dockerfile:1
FROM node:20-slim AS frontend-build

WORKDIR /app

COPY desktop/package.json desktop/package-lock.json ./
RUN npm ci

COPY desktop/ .
RUN npm run build

FROM node:20-slim AS frontend
WORKDIR /app
COPY --from=frontend-build /app/dist ./dist
RUN npm install -g serve
EXPOSE 5173
CMD ["serve", "-s", "dist", "-l", "5173"]