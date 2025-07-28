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

        stage('SCM Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Tests unitaires avec pytest') {
            steps {
                dir("${WORKSPACE}/${PROJECT_DIR}") {
                    // Création du répertoire local pour les rapports
                    sh 'mkdir -p test-reports'

                    // Exécution des tests dans le conteneur, sortie dans un répertoire avec droits
                    sh 'docker exec stage pytest --junitxml=/tmp/report.xml || exit 1'

                    // Copie le rapport du conteneur vers l'hôte
                    sh 'docker cp stage:/tmp/report.xml test-reports/report.xml'
                }
            }
        }
        stage('Analyse SonarQube') {
            steps {
                dir("${WORKSPACE}") {
                    sh 'sonar-scanner'
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
            // Rapport de test JUnit
                dir("${WORKSPACE}/${PROJECT_DIR}") {
                    script {
                        if (fileExists('test-reports/report.xml')) {
                            junit 'test-reports/report.xml'
                        }
                    }
                    // Arrêt des services Docker
                        sh 'docker-compose down'
                    }
                }

            // Notification par e-mail
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
