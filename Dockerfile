# run the first one if the container does not exist
# remove this and add it to the README later
# docker build -t uav-telemetry .
# docker run uav-telemetry

FROM python:3.12-slim

WORKDIR /app

EXPOSE 5005/udp

COPY pyproject.toml .

COPY src/ ./src/

RUN pip install .

CMD ["python", "-m", "src.receiver"]