pipeline {
    agent any

    environment {
        PATH = "/usr/bin:${env.PATH}"
        COMPOSE_FILE = 'docker-compose.yml'
    }

    stages {
        stage('Cloner le dépôt') {
            steps {
                git branch: 'main', url: 'https://github.com/maramhassen/FastAPI.git'
            }
        }

        stage('Construire et démarrer les services Docker') {
            steps {
                echo '🔧 Construction et démarrage des services Docker...'
                // Build des images
                sh 'docker-compose -f docker-compose.yml build'
                // Démarrage des services en arrière-plan
                sh 'docker-compose -f docker-compose.yml up -d'
            }
        }

        stage('Tester l\'API FastAPI') {
            steps {
                echo '🧪 Test de l\'accessibilité de l\'API...'
                // Attente pour laisser le temps aux conteneurs de démarrer
                sh 'sleep 15'
                // Test de l'endpoint racine, exit code 1 si échec
                sh 'curl -f http://localhost:8000 || (echo "Erreur d\'API" && exit 1)'
            }
        }
    }

    post {
        always {
            echo '🧹 Nettoyage des ressources Docker...'
            // Arrêt et suppression des conteneurs et réseaux créés par compose
            sh 'docker-compose -f docker-compose.yml down'
        }
    }
}
