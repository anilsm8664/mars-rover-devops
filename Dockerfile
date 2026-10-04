FROM python:3.12-slim
RUN groupadd --system --gid 10001 rover \
    && useradd --system --uid 10001 --gid 10001 --home-dir /app --shell /usr/sbin/nologin rover
WORKDIR /app
COPY --chown=rover:rover rover.py /app/rover.py
USER rover
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
ENTRYPOINT ["python", "/app/rover.py"]
