pipeline {
    agent any

    environment {
        PROJECT_DIR = 'FastAPI'  // Dossier racine cloné depuis GitHub
    }

    stages {
        stage('Cloner le dépôt') {
            steps {
                git branch: 'main', url: 'https://github.com/maramhassen/FastAPI.git'
            }
        }

        stage('Construire et démarrer') {
            steps {
                dir("${WORKSPACE}/${PROJECT_DIR}") {
                    sh 'docker compose version'
                    sh 'docker compose build'
                    sh 'docker compose up -d'
                }
            }
        }

        stage('Tester l\'API') {
            steps {
                dir("${WORKSPACE}/${PROJECT_DIR}") {
                    sleep 15
                    sh 'curl -f http://localhost:8000 || (echo "Échec du test API" && exit 1)'
                }
            }
        }
    }

    post {
        always {
            dir("${WORKSPACE}/${PROJECT_DIR}") {
                sh 'docker compose down'
            }
        }
    }
}
