FROM python:3.11

# Create work directory
WORKDIR /
RUN mkdir -p /logs

# Install poetry env, project dependency and model files
COPY ./poetry.lock ./pyproject.toml ./
RUN pip install --no-cache-dir poetry==1.7.1 \
    && poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Copy application files
COPY ./ ./

# Expose port and run application
EXPOSE 8000

ENTRYPOINT ["/bin/sh", "-c", "uvicorn main:app --host 0.0.0.0"]