# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /aprrp

# Install required system packages for Chrome and SeleniumRUN apt-get update && apt-get install -y \
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    libnss3 \
    libgconf-2-4 \
    libxss1 \
    libasound2 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libx11-xcb1 \
    libxcomposite1 \
    libxrandr2 \
    libxi6 \
    libxtst6 \
    libgl1-mesa-glx \
    fonts-liberation \
    libappindicator3-1 \
    libnspr4 \
    && rm -rf /var/lib/apt/lists/*


# Download and install Chrome
RUN wget https://storage.googleapis.com/chrome-for-testing-public/129.0.6668.58/linux64/chrome-linux64.zip && \
    unzip chrome-linux64.zip -d /opt && \
    rm chrome-linux64.zip

# Download and install Chrome Headless
RUN wget https://storage.googleapis.com/chrome-for-testing-public/129.0.6668.58/linux64/chrome-headless-shell-linux64.zip && \
    unzip chrome-headless-shell-linux64.zip -d /opt && \
    rm chrome-headless-shell-linux64.zip

# Set up environment variable for Chrome
ENV PATH="/opt/chrome-linux64:${PATH}"
ENV PATH="/opt/chrome-headless-shell-linux64:${PATH}"

# Copy requirements.txt into the container
COPY requirements.txt .

# Install any dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container
COPY . .

# Set environment variables
ENV HOSTING_DOMAIN=http://applee.me
ENV SCRIPT_URL=https://script.google.com/macros/s/your-script-id/dev

# Expose the port the app runs on
EXPOSE 8000

# Command to run the FastAPI app using Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
