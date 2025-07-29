pipeline {
    agent any

    environment {
        PROJECT_DIR = 'FastAPI'
        SONAR_HOST_URL = 'http://192.168.136.165:9000'
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
                    sh 'docker-compose down --remove-orphans'
                    sh 'docker-compose up -d'
                }
            }
        }

        stage('Tests unitaires avec pytest') {
            steps {
                dir("${WORKSPACE}/${PROJECT_DIR}") {
                    sh 'mkdir -p test-reports'
                    sh 'docker exec stage pytest --junitxml=/tmp/report.xml || exit 1'
                    sh 'docker cp stage:/tmp/report.xml test-reports/report.xml'
                }
            }
        }

        stage('Analyse SonarQube') {
            steps {
                dir("${WORKSPACE}") {
                    // Nettoyage préalable
                    sh '''
                    docker-compose -f docker-compose.sonar.yml down --remove-orphans || true
                    docker rm -f sonarqube || true
                    '''
                    
                    // Démarrer SonarQube avec plus de ressources
                    sh '''
                    docker-compose -f docker-compose.sonar.yml up -d
                    docker update --memory 2G --memory-swap 3G sonarqube
                    '''
                    
                    // Attente que SonarQube soit vraiment prêt
                    timeout(time: 300, unit: 'SECONDS') {
                        waitUntil {
                            def ready = sh(
                                script: """
                                STATUS=$(curl -s ${SONAR_HOST_URL}/api/system/status || echo "{}")
                                HEALTH=$(curl -s ${SONAR_HOST_URL}/api/system/health || echo "{}")
                                echo "Status: $STATUS"
                                echo "Health: $HEALTH"
                                grep -q '"status":"UP"' <<< "$STATUS" || \
                                grep -q '"status":"GREEN"' <<< "$HEALTH"
                                """,
                                returnStatus: true
                            )
                            sleep 10  // Pause entre les vérifications
                            return (ready == 0)
                        }
                    }
                    
                    // Exécuter l'analyse SonarQube
                    withSonarQubeEnv('sonarqube') {  // Configuration du serveur dans Jenkins
                        dir("${WORKSPACE}/${PROJECT_DIR}") {
                            sh '''
                            sonar-scanner \
                                -Dsonar.projectKey=fastapi_app \
                                -Dsonar.projectName="FastAPI Application" \
                                -Dsonar.sources=app \
                                -Dsonar.python.version=3.11 \
                                -Dsonar.junit.reportPaths=test-reports/report.xml
                            '''
                        }
                    }
                }
            }
        }

        stage('Upload artefact vers Nexus') {
            steps {
                dir("${WORKSPACE}/${PROJECT_DIR}") {
                    sh 'python setup.py sdist'
                    sh 'curl -u admin:admin123 --upload-file dist/*.tar.gz http://localhost:8081/repository/raw-hosted/'
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
                      echo "En attente de l\'API..."
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
                script {
                    if (fileExists('test-reports/report.xml')) {
                        junit 'test-reports/report.xml'
                    }
                    // Nettoyage des conteneurs applicatifs
                    sh 'docker-compose down'
                }
            }

            // 🔥 Nettoyage de SonarQube même si erreur
            script {
                sh '''
                if [ "$(docker ps -aq -f name=^/sonarqube$)" ]; then
                    echo "🧹 Nettoyage du conteneur SonarQube..."
                    docker rm -f sonarqube || true
                fi
                '''
            }

            // Notification email
            script {
                emailext (
                    subject: "Jenkins Build ${currentBuild.currentResult}: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                    body: """\
Bonjour,

Le pipeline '${env.JOB_NAME}' s'est terminé avec le statut : ${currentBuild.currentResult}
Lien vers les logs : ${env.BUILD_URL}

Cordialement,
Jenkins CI/CD
""",
                    to: 'maramhassen22@gmail.com'
                )
            }
        }
    }
}
