# Use the official Python image from the Docker Hub (Alpine variant)
FROM python:3.11-alpine

# Install necessary build dependencies
RUN apk add --no-cache build-base

# Set the working directory inside the container
WORKDIR /app

# Copy the content of the local directory to the /app directory in the container
COPY . /app

# Install the required dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port that Streamlit will use
EXPOSE 8501

# Command to run the Streamlit app when the container starts
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.headless=true"]
