pipeline {
    agent any

    environment {
        PROJECT_DIR = 'FastAPI' 
        IMAGE_NAME = 'fastapi_app'
        NEXUS_URL = '192.168.136.164:8082'
        NEXUS_REPO = 'docker-hosted'
        NEXUS_USER = 'admin'
        NEXUS_PASSWORD = '0d8fa22d-2743-495d-9ba4-915e0293e326'
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
                    sh 'docker exec stage pytest --junitxml=report.xml || exit 1'
                }
            }
        }

        stage('Vérifier si l\'API répond') {
            steps {
                dir("${WORKSPACE}/${PROJECT_DIR}") {
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

        stage('Release - Nexus') {
            steps {
                dir("${WORKSPACE}/${PROJECT_DIR}") {
                    sh '''
                        echo "📦 Tag de l'image Docker vers Nexus"
                        docker tag fastapi_app ${NEXUS_URL}/${NEXUS_REPO}/fastapi_app

                        echo "🔐 Connexion à Nexus via HTTP"
                        docker login ${NEXUS_URL} -u ${NEXUS_USER} -p ${NEXUS_PASSWORD}

                        echo "🚀 Poussée de l'image vers Nexus"
                        docker push ${NEXUS_URL}/${NEXUS_REPO}/fastapi_app
                    '''
                }
            }
        }
    }

    post {
        always {
            dir("${WORKSPACE}/${PROJECT_DIR}") {
                script {
                    if (fileExists('report.xml')) {
                        junit 'report.xml'
                    }
                }
                sh 'docker-compose down'
            }
        }
    }
}
