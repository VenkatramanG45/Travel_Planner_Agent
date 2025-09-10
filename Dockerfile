# Choose a Python base image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Install curl and gnupg for adding new repositories
RUN apt-get update && apt-get install -y curl gnupg

# Add Node.js 20 repository and install it
RUN curl -sL https://deb.nodesource.com/setup_20.x | bash -
RUN apt-get install -y nodejs

# Copy the project files to the working directory
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port Streamlit runs on
EXPOSE 8501

# Set the command to run the Streamlit app
# The --server.enableCORS=false and --server.enableXsrfProtection=false flags are often needed for embedding in HF Spaces
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.enableCORS=false", "--server.enableXsrfProtection=false"]
