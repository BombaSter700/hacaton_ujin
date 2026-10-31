FROM python:3.12-slim
WORKDIR /app
COPY integration/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY integration/app ./app
COPY integration/alembic.ini .
COPY integration/migrations ./migrations
COPY integration/docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh
ENTRYPOINT ["/docker-entrypoint.sh"]
