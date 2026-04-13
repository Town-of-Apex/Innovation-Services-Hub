FROM python:3.13-slim

WORKDIR /app

# Install dependencies using Python's package manager
COPY pyproject.toml .
RUN pip install "fastapi>=0.111.0" "uvicorn[standard]>=0.30.0" "jinja2>=3.1.4" "sqlalchemy>=2.0.30" "python-multipart>=0.0.9"

# Copy the rest of the application
COPY . .

# Expose the specific port requested
EXPOSE 10000

# Run the app via uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
