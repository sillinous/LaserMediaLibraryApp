# Use an official Node.js runtime as a parent image
FROM node:20-alpine

# Set the working directory in the container
WORKDIR /app

# Copy package.json and package-lock.json to the working directory
COPY package.json package-lock.json ./

# Install dependencies
# Using "npm ci" is often better in CI/CD for deterministic builds,
# but "npm install" is fine for local development.
RUN npm install

# Copy the rest of the application's code to the working directory
COPY . .

# Vite's default port is 5173. We need to expose it.
EXPOSE 5173

# Command to run the application's development server
# The --host flag is required to expose the server to other services in the Docker network
CMD ["npm", "run", "dev", "--", "--host"]
