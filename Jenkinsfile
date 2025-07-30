pipeline {
    agent any

    environment {
        SONAR_HOST_URL = 'http://192.168.136.165:9000'
    }

    stages {
        stage('Checkout SCM') {
            steps {
                echo '📦 Clonage du dépôt à partir de la configuration du job Jenkins...'
                checkout scm
                sh 'ls -la'
            }
        }

        stage('Build & Start Services') {
            steps {
                dir("${WORKSPACE}") {
                    sh 'docker-compose version'
                    sh 'docker-compose down --remove-orphans || true'
                    sh 'docker-compose build'
                    sh 'docker-compose up -d'
                }
            }
        }

        stage('Unit Tests with Pytest') {
            steps {
                dir("${WORKSPACE}") {
                    sh 'mkdir -p test-reports'
                    sh 'docker exec stage pytest --junitxml=/tmp/report.xml || exit 1'
                    sh 'docker cp stage:/tmp/report.xml test-reports/report.xml'
                }
            }
        }

        stage('SonarQube Analysis') {
            steps {
                dir("${WORKSPACE}") {
                    sh '''
                        docker-compose -f docker-compose.sonar.yml down --remove-orphans || true
                        docker rm -f sonarqube || true
                        docker-compose -f docker-compose.sonar.yml up -d
                        docker update --memory 2G --memory-swap 3G sonarqube
                    '''

                    script {
                        timeout(time: 5, unit: 'MINUTES') {
                            waitUntil {
                                def ready = sh(
                                    script: '''
                                        STATUS=$(curl -s ${SONAR_HOST_URL}/api/system/status || echo "{}")
                                        HEALTH=$(curl -s ${SONAR_HOST_URL}/api/system/health || echo "{}")
                                        echo "$STATUS" | grep -q '"status":"UP"' || echo "$HEALTH" | grep -q '"status":"GREEN"'
                                    ''',
                                    returnStatus: true
                                )
                                sleep 10
                                return (ready == 0)
                            }
                        }
                    }

                    withCredentials([string(credentialsId: 'SONAR_TOKEN', variable: 'SONAR_TOKEN')]) {
                        sh '''
                            echo "📂 Répertoire courant :"
                            ls -la
                            echo "📂 Dossier app :"
                            ls -la app || echo "Dossier app introuvable !"

                            sonar-scanner \
                                -Dsonar.projectKey=fastapi_app \
                                -Dsonar.projectName="FastAPI Application" \
                                -Dsonar.sources=app \
                                -Dsonar.python.version=3.11 \
                                -Dsonar.junit.reportPaths=test-reports/report.xml \
                                -Dsonar.host.url=${SONAR_HOST_URL} \
                                -Dsonar.login=${SONAR_TOKEN}
                        '''
                    }
                }
            }
        }

        stage('Upload to Nexus') {
            steps {
                dir("${WORKSPACE}") {
                    sh 'python setup.py sdist'
                    sh 'curl -u admin:admin123 --upload-file dist/*.tar.gz http://localhost:8081/repository/raw-hosted/'
                }
            }
        }

        stage('Check FastAPI Availability') {
            steps {
                dir("${WORKSPACE}") {
                    sh '''
                        for i in {1..10}; do
                          if curl -f http://localhost:8000; then
                            echo "🚀 API opérationnelle !"
                            break
                          fi
                          echo "⏳ En attente de l'API..."
                          sleep 3
                        done
                    '''
                }
            }
        }
    }

    post {
        always {
            dir("${WORKSPACE}") {
                script {
                    if (fileExists('test-reports/report.xml')) {
                        junit 'test-reports/report.xml'
                    }
                    sh 'docker-compose down || true'
                }
            }

            script {
                sh '''
                    if [ "$(docker ps -aq -f name=^/sonarqube$)" ]; then
                        echo "🧹 Nettoyage de SonarQube..."
                        docker rm -f sonarqube || true
                    fi
                '''
            }

            script {
                emailext (
                    subject: "Jenkins Build ${currentBuild.currentResult}: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                    body: """\
Bonjour,

Le pipeline '${env.JOB_NAME}' s'est terminé avec le statut : ${currentBuild.currentResult}
🔗 Voir les logs : ${env.BUILD_URL}

Cordialement,  
Jenkins CI/CD
""",
                    to: 'maramhassen22@gmail.com'
                )
            }
        }
    }
}
