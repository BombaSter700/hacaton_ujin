FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app
COPY . /app/backend/emulators

USER 10001:10001
EXPOSE 8098-8107

ENTRYPOINT ["python", "-m", "backend.emulators.fleet"]
CMD []
