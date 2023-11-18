# Use an official Python runtime as a parent image
FROM python:3.10

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY ./backend /app

# Create the directory for SQLite data
RUN mkdir /data

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install SQLite dependencies
RUN apt-get update && \
    apt-get install -y sqlite3 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Make port 1234 available to the world outside this container
EXPOSE 1234

# Define environment variable
ENV FLASK_APP=main.py

# Run main.py when the container launches
CMD ["python3", "main.py"]
