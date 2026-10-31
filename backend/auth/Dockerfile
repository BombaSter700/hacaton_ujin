FROM python:3.12-slim
WORKDIR /app

# Install wait-for-it script
RUN apt-get update && apt-get install -y wget && \
    wget -O /wait-for-it.sh https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh && \
    chmod +x /wait-for-it.sh && \
    apt-get remove -y wget && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

# Copy service requirements and install dependencies
COPY auth/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy service code
COPY auth/app ./app
COPY auth/alembic.ini .
COPY auth/migrations ./migrations

# Copy and setup entrypoint
COPY auth/docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Код будет монтироваться через volumes в docker-compose
ENTRYPOINT ["/docker-entrypoint.sh"]
