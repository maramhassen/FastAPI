pipeline {
    agent any

    environment {
        PROJECT_DIR = 'FastAPI'  
    }

    stages {
        stage('Cloner le dépôt') {
            steps {
                git branch: 'main', url: 'https://github.com/maramhassen/FastAPI.git'
            }
        }

        stage('Construire et démarrer les services') {
            steps {
                dir("${WORKSPACE}/${PROJECT_DIR}") {
                    sh 'docker-compose version'
                    sh 'docker-compose build'
                    sh 'docker-compose up -d'
                }
            }
        }

        stage('Tests unitaires avec pytest') {
            steps {
                dir("${WORKSPACE}/${PROJECT_DIR}") {
                    // ⚠️ Exécute les tests dans le conteneur nommé "stage"
                    sh 'docker exec stage pytest --junitxml=report.xml || exit 1'
                }
            }
        }

        stage('Vérifier si l\'API répond') {
            steps {
                dir("${WORKSPACE}/${PROJECT_DIR}") {
                    // 🔁 Teste 10 fois avec pause jusqu'à succès
                    sh '''
                    for i in {1..10}; do
                      if curl -f http://localhost:8000; then
                        echo "API opérationnelle !"
                        break
                      fi
                      echo "En attente de l'API..."
                      sleep 3
                    done
                    '''
                }
            }
        }
    }

    post {
        always {
            dir("${WORKSPACE}/${PROJECT_DIR}") {
                // 📄 Publie les résultats pytest si disponibles
                script {
                    if (fileExists('report.xml')) {
                        junit 'report.xml'
                    }
                }

                // 🧹 Arrête et supprime les conteneurs
                sh 'docker-compose down'
            }
        }
    }
}
