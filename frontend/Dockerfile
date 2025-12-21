FROM node:18-alpine AS builder

WORKDIR /app

ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

COPY package*.json ./

RUN npm install --legacy-peer-deps

COPY . .

RUN npm run build

FROM node:18-alpine AS runtime

WORKDIR /app

COPY package*.json ./
COPY vite.config.ts ./

RUN npm install --legacy-peer-deps

COPY --from=builder /app/dist ./dist

EXPOSE 8080

CMD ["sh", "-c", "npx vite preview --host 0.0.0.0 --port ${PORT:-8080}"]
