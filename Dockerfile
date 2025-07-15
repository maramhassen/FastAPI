FROM jenkins/jenkins:latest

USER root

# Installer Docker CLI (version Debian slim)
RUN apt-get update && apt-get install -y \
    docker.io \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Installer docker-compose (dernière version stable)
RUN curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" \
    -o /usr/local/bin/docker-compose \
    && chmod +x /usr/local/bin/docker-compose

# Vérifier les versions (optionnel)
RUN docker --version && docker-compose --version

USER jenkins
