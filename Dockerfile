FROM python:3.12-slim

WORKDIR /opt/mqm

COPY mq-dev/ /opt/mqm/

ENV MQ_INSTALLATION_PATH=/opt/mqm
ENV LD_LIBRARY_PATH=/opt/mqm/lib64
ENV PATH=/opt/mqm/bin:$PATH

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc g++ make && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir pymqi==1.12.13

COPY src/ ./src/

CMD ["python", "src/healthcheck.py"]
