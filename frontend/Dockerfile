# Use an official Node runtime as a parent image
FROM node:14

# Set the working directory to /app
WORKDIR /app

# Copy package.json
COPY ./frontend/package.json /app/package.json

# Install any needed packages specified in package.json
RUN npm install

# Copy the current directory contents into the container at /app
COPY ./frontend /app
# Make port 3000 available to the world outside this container
EXPOSE 3000

# Run npm start when the container launches
CMD ["npm", "start"]
