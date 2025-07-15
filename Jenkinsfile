pipeline {
    agent any

    environment {
        // Mise à jour du PATH pour inclure /usr/local/bin (où docker-compose sera installé)
        PATH = "/usr/local/bin:/usr/bin:${env.PATH}"
        COMPOSE_FILE = 'docker-compose.yml'
    }

    stages {
        // Étape 1: Clonage du dépôt Git
        stage('Cloner le dépôt') {
            steps {
                echo '📥 Clonage du dépôt Git...'
                git branch: 'main', url: 'https://github.com/maramhassen/FastAPI.git'
            }
        }

        // Étape 2: Installation de Docker Compose (si nécessaire)
        stage('Préparation Environnement') {
            steps {
                echo '🛠️ Installation de Docker Compose...'
                script {
                    try {
                        // Vérifie si docker-compose est déjà installé
                        sh 'docker-compose --version'
                        echo '✅ Docker Compose est déjà installé'
                    } catch (Exception e) {
                        // Installation si absent
                        sh '''
                            sudo curl -L "https://github.com/docker/compose/releases/download/v2.23.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
                            sudo chmod +x /usr/local/bin/docker-compose
                            docker-compose --version || (echo "Échec de l'installation" && exit 1)
                        '''
                        echo '✅ Docker Compose installé avec succès'
                    }
                }
            }
        }

        // Étape 3: Construction et démarrage des containers
        stage('Construire et démarrer les services Docker') {
            steps {
                echo '🔧 Construction des images Docker...'
                sh 'docker-compose build --no-cache'

                echo '🚀 Démarrage des services...'
                sh 'docker-compose up -d'
            }
        }

        // Étape 4: Tests de l'API
        stage('Tester l\'API FastAPI') {
            steps {
                echo '🧪 Vérification de l\'API...'
                sleep(time: 15, unit: 'SECONDS')  // Attente plus élégante
                
                script {
                    def response = sh(
                        script: 'curl -s -o /dev/null -w "%{http_code}" http://localhost:8000',
                        returnStdout: true
                    ).trim()

                    if (response != "200") {
                        error "❌ L'API a retourné le code HTTP ${response}"
                    } else {
                        echo "✅ API accessible (HTTP 200)"
                    }
                }
            }
        }
    }

    // Nettoyage final (toujours exécuté, même en cas d'échec)
    post {
        always {
            echo '🧹 Nettoyage des ressources...'
            sh 'docker-compose down --remove-orphans'
        }
        success {
            echo '🎉 Pipeline exécuté avec succès!'
        }
        failure {
            echo '❌ Échec du pipeline'
        }
    }
}