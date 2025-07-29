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
                    // Supprimer SonarQube s’il existe
                    sh '''
                    if [ "$(docker ps -aq -f name=^/sonarqube$)" ]; then
                        echo "➡️  Suppression du conteneur existant sonarqube..."
                        docker stop sonarqube || true
                        docker rm sonarqube || true
                    fi
                    '''
                    sh 'docker-compose -f docker-compose.sonar.yml down --remove-orphans'
                    sh 'docker-compose -f docker-compose.sonar.yml up -d'

                    // Attente que SonarQube soit UP
                    timeout(time: 300, unit: 'SECONDS') {
                        waitUntil {
                            def status = sh(script: """
                                curl -s http://sonarqube:9000/api/system/health | \
                                grep -q '"status":"GREEN"' || \
                                curl -s http://sonarqube:9000/api/system/status | \
                                grep -q '"status":"UP"'
                                """,
                                returnStatus: true
                            )
                            return (status == 0)
                        }
                    }

                    sh 'sonar-scanner -Dsonar.host.url=http://sonarqube:9000'
                    sh 'docker-compose -f docker-compose.sonar.yml down --remove-orphans'
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
