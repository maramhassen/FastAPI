pipeline {
    agent {
        docker {
            image 'node:14-alpine'
            args '-v /tmp:/tmp'
        }
    }

    environment {
        REPO_URL = 'https://github.com/maramhassen/FastAPI.git'
        COMPOSE_PROJECT_NAME = "fastapi_jenkins"
    }

    stages {
        stage('Clone Repository') {
            steps {
                // Cloner ton repo GitHub
                git branch: 'main', url: "${REPO_URL}"
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t fastapi-app:latest .'
            }
        }

        stage('Start Services') {
            steps {
                sh 'docker-compose up -d'
            }
        }

        stage('Run Tests') {
            steps {
                // Adapter cette commande selon tes tests réels
                sh 'docker-compose exec stage pytest tests || true'
            }
        }
    }

    post {
        always {
            sh 'docker-compose down'
        }
    }
}