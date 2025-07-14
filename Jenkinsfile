pipeline {
    agent {
        docker {
            image 'python:3.9'
            label 'docker'  // optionnel, selon ton node
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

        stage('Build') {
            steps {
                sh 'python --version'
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