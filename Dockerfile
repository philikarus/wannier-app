# Use Python 3.10 base image
FROM python:3.10

# Set working directory
WORKDIR /app

# Install OpenGL libraries
RUN apt-get update && \
    apt-get install -y libgl1-mesa-glx

# Copy the application files
COPY app.py requirements.txt /app
ADD scripts /app/scripts

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the application
CMD ["python", "app.py"]


