pipeline {
    agent any

    environment {
        PROJECT_DIR = 'FastAPI'
        IMAGE_NAME = 'fastapi-app'
        NEXUS_REPO = 'nexus.local:8082'
        SONAR_TOKEN = credentials('sonar-token') // Ajouter ce secret Jenkins
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
                    sh 'docker-compose build'
                    sh 'docker-compose up -d'
                }
            }
        }

        stage('Tests unitaires avec Pytest') {
            steps {
                dir("${WORKSPACE}/${PROJECT_DIR}") {
                    sh 'docker exec stage pytest --junitxml=report.xml || exit 1'
                }
            }
        }

        stage('Analyse de code avec SonarQube') {
            steps {
                dir("${WORKSPACE}/${PROJECT_DIR}") {
                    withSonarQubeEnv('SonarQube') {
                        sh 'sonar-scanner'
                    }
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

        stage('Tag & Push vers Nexus') {
            steps {
                dir("${WORKSPACE}/${PROJECT_DIR}") {
                    sh """
                        docker tag ${IMAGE_NAME} ${NEXUS_REPO}/${IMAGE_NAME}
                        docker push ${NEXUS_REPO}/${IMAGE_NAME}
                    """
                }
            }
        }

        stage('Déploiement') {
            steps {
                sh '''
                docker rm -f fastapi-app || true
                docker run -d -p 8000:8000 --name fastapi-app ${IMAGE_NAME}
                '''
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
                sh 'docker-compose down || true'
            }

            // 🔔 Notification Email
            emailext(
                to: 'admin@example.com',
                subject: "Build ${currentBuild.fullDisplayName}",
                body: "Résultat: ${currentBuild.currentResult}"
            )

            // 🔔 Slack
            slackSend(channel: '#ci-cd', message: "Pipeline Jenkins: ${currentBuild.currentResult}")
        }
    }
}
