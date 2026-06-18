FROM node:20-alpine

WORKDIR /app

# Copy package config and install dependencies
COPY ../package.json ../package-lock.json ./
RUN npm ci --only=production

# Copy application code
COPY . .

# Use non-root user
RUN addgroup -S cortexgroup && adduser -S cortexuser -G cortexgroup && chown -R cortexuser:cortexgroup /app
USER cortexuser

EXPOSE 4242

CMD ["node", "payment_gateway/server.js"]
