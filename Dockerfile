# Use an official Python runtime as a parent image
FROM python:3.11

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY ./TruckPool_Django /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port Django runs on
EXPOSE 5000

# Run Django migrations and collect static files
#RUN python manage.py migrate
RUN python manage.py collectstatic --noinput

# Command to run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:5000"]
