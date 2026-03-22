# Use python:3.14.3-slim as the base image
FROM python:3.14.3-slim

# Goes to the app directory
WORKDIR /usr/src/app

# Copy the requirements.txt file to the working directory
# Install the dependencies specified in requirements.txt
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the working directory
COPY . .

# Run the application using uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]