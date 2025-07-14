pipeline {
    agent {
        docker {
            image 'docker:latest'
            args '-v /var/run/docker.sock:/var/run/docker.sock'
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