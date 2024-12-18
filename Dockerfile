# Use a base image with Python
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install spaCy language model
RUN python -m spacy download en_core_web_sm

# Copy the entire project directory into the container
COPY . .

# Expose the port your Flask app will run on (default is 5000 for Flask)
EXPOSE 5000

# Command to run the Flask application
CMD ["python", "app.py"]
