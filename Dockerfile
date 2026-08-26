
FROM python:3.12-slim

WORKDIR /app

EXPOSE 5005/udp

COPY pyproject.toml .

COPY src/ ./src/

RUN pip install .

CMD ["python", "-m", "src.receiver"]