pipeline {
    agent any

    environment {
        PROJECT_DIR = 'FastAPI'
        SONAR_PROJECT_KEY = 'fastapi-app'
        SONAR_HOST_URL = 'http://localhost:9000'
        SONAR_TOKEN = credentials('sonar-token') // Ajouté via "Manage Jenkins > Credentials"
    }

    stages {
        stage('Checkout SCM') {
            steps {
                // Clonage sécurisé via Git Jenkins Plugin
                checkout scm
            }
        }

        stage('Docker Compose - Build & Run') {
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
                    // Assure que le conteneur "stage" est lancé avant d'exécuter
                    sh '''
                    if docker ps | grep stage; then
                      docker exec stage pytest --junitxml=report.xml || exit 1
                    else
                      echo "Le conteneur 'stage' n'est pas démarré !"
                      exit 1
                    fi
                    '''
                }
            }
        }

        stage('Analyse de qualité - SonarQube') {
            steps {
                dir("${WORKSPACE}/${PROJECT_DIR}") {
                    withSonarQubeEnv('MySonarServer') {
                        sh """
                            sonar-scanner \
                            -Dsonar.projectKey=${SONAR_PROJECT_KEY} \
                            -Dsonar.sources=. \
                            -Dsonar.host.url=${SONAR_HOST_URL} \
                            -Dsonar.login=${SONAR_TOKEN}
                        """
                    }
                }
            }
        }

        stage("Vérification de l'API") {
            steps {
                dir("${WORKSPACE}/${PROJECT_DIR}") {
                    sh '''
                    for i in {1..10}; do
                      if curl -f http://localhost:8000; then
                        echo "✅ API opérationnelle"
                        break
                      fi
                      echo "⏳ En attente de l'API..."
                      sleep 3
                    done
                    '''
                }
            }
        }

        // (optionnel) : Nexus upload
        stage('Upload artefacts vers Nexus') {
            when {
                expression { fileExists("${WORKSPACE}/${PROJECT_DIR}/dist") }
            }
            steps {
                echo 'Uploading package to Nexus...'
                // Ajoute ici ton script ou plugin si besoin
            }
        }
    }

    post {
        always {
            dir("${WORKSPACE}/${PROJECT_DIR}") {
                // 📄 Publier résultats tests
                script {
                    if (fileExists('report.xml')) {
                        junit 'report.xml'
                    }
                }

                // 🧹 Nettoyage des conteneurs
                sh 'docker-compose down'
            }

            // 🔔 Notification Slack
            script {
                def result = currentBuild.result ?: 'SUCCESS'
                slackSend (
                    channel: '#ci-cd',
                    color: result == 'SUCCESS' ? 'good' : 'danger',
                    message: "Pipeline terminé avec statut: ${result}"
                )
            }

            // (optionnel) Notification email
            mail to: 'saidhassen104@gmail.com',
                 subject: "Build ${currentBuild.fullDisplayName}",
                 body: "Résultat: ${currentBuild.result}\nVoir: ${env.BUILD_URL}"
        }
    }
}
