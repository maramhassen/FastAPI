FROM jenkins/jenkins:lts

USER root

# Installer docker CLI (si besoin)
RUN apt-get update && apt-get install -y docker.io

# Installer docker-compose (version récente en binaire)
RUN curl -L "https://github.com/docker/compose/releases/download/v2.20.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose \
    && chmod +x /usr/local/bin/docker-compose

# Vérifier version (optionnel)
RUN docker-compose --version

USER jenkins
