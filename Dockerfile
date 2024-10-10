# Use Python 3.10 base image
FROM python:3.10

# Set working directory
WORKDIR /app

# Install OpenGL libraries
RUN apt-get update && \
    apt-get install -y libgl1-mesa-glx

# Copy the application files
COPY src/app.py requirements.txt /app
ADD src/scripts /app/scripts

# Install dependencies
RUN pip install --default-timeout=100 \
-i https://pypi.tuna.tsinghua.edu.cn/simple \
--no-cache-dir -r requirements.txt

# Run the application
CMD ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:8050", "app:server"]



