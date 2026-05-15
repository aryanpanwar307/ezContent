# Use the official lightweight Python image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Install gunicorn, a production-grade web server for Python
RUN pip install gunicorn

# Copy the rest of the application code into the container
COPY . .

# Hugging Face Spaces requires the app to run on port 7860
ENV PORT=7860
EXPOSE 7860

# Run the application using Gunicorn with a longer timeout for AI requests
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "--timeout", "120", "--workers", "2", "app:app"]
