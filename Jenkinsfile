pipeline {
    agent {
        docker {
            image 'docker/compose:latest'
            args '-v /var/run/docker.sock:/var/run/docker.sock --privileged'
        }
    }

    stages {
        stage('Cloner le dépôt') {
            steps {
                git branch: 'main', url: 'https://github.com/maramhassen/FastAPI.git'
            }
        }

        stage('Construire et démarrer') {
            steps {
                sh 'docker compose version'  // Vérification
                sh 'docker compose build'
                sh 'docker compose up -d'
            }
        }

        stage('Tester l\'API') {
            steps {
                sleep 15
                sh 'curl -f http://localhost:8000 || (echo "Échec du test API" && exit 1)'
            }
        }
    }

    post {
        always {
            sh 'docker compose down'
        }
    }
}