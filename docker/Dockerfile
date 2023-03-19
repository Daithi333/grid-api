FROM python:3.11

# Install Postgres dependencies
RUN apt-get update && \
    apt-get install -y libpq-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install LibreOffice Calc and its dependencies
RUN apt-get update && \
    apt-get install -y default-jre libreoffice-calc libreoffice-java-common && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install wait-for-it (only needed for docker compose)
ADD https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh /usr/local/bin/wait-for-it
RUN chmod +x /usr/local/bin/wait-for-it

WORKDIR /app

COPY Pipfile* .

RUN pip install --no-cache-dir pipenv && \
    pipenv install --system --deploy --ignore-pipfile

COPY src .
COPY docker/start.sh .

EXPOSE 5000

# Set the entrypoint to the start script
ENTRYPOINT ["bash", "start.sh"]
