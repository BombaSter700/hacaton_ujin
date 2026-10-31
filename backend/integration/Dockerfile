FROM python:3.12-slim
WORKDIR /app

RUN apt-get update && apt-get install -y wget && \
    wget -O /wait-for-it.sh https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh && \
    chmod +x /wait-for-it.sh && \
    apt-get remove -y wget && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

COPY integration/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY integration/app ./app
COPY integration/alembic.ini .
COPY integration/migrations ./migrations

COPY integration/docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]
