FROM python:3.12-slim
WORKDIR /app
COPY auth/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY auth/app ./app
COPY auth/alembic.ini .
COPY auth/migrations ./migrations
COPY auth/docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh
ENTRYPOINT ["/docker-entrypoint.sh"]
