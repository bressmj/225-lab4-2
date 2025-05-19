pipeline {
    agent any

    environment {
        DOCKER_CREDENTIALS_ID = 'roseaw-dockerhub'
        DOCKER_IMAGE = 'cithit/bressmj'                            //<------replace with your MiamiID
        IMAGE_TAG = "build-${BUILD_NUMBER}"
        GITHUB_URL = 'https://github.com/bressmj/225-lab5-1.git'    //<------replace with your MiamiID
        KUBECONFIG = credentials('bressmj-225')                     //<------replace with your MiamiID
    }

    stages {
        stage('Checkout') {
            steps {
                cleanWs()
                checkout([$class: 'GitSCM', branches: [[name: '*/main']],
                          userRemoteConfigs: [[url: "${GITHUB_URL}"]]])
            }
        }

        // Linting Stage
        stage('Linting') {
            steps {
                script {
                    echo "Running Linting for HTML and Python..."

                    // Run HTML linting (htmlhint)
                    sh 'npm install htmlhint --save-dev'
                    sh 'npx htmlhint *.html'

                    // Run Python linting (flake8) if required
                    sh 'pip install flake8'
                    sh 'flake8 .'
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    echo "Building Docker Image..."
                    docker.build("${DOCKER_IMAGE}:${IMAGE_TAG}", "-f Dockerfile.build .")
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                script {
                    echo "Pushing Docker Image..."
                    docker.withRegistry('https://index.docker.io/v1/', "${DOCKER_CREDENTIALS_ID}") {
                        docker.image("${DOCKER_IMAGE}:${IMAGE_TAG}").push()
                    }
                }
            }
        }

        stage('Deploy to Dev Environment') {
            steps {
                script {
                    echo "Deploying to Dev Environment..."
                    def kubeConfig = readFile(KUBECONFIG)
                    sh "sed -i 's|${DOCKER_IMAGE}:latest|${DOCKER_IMAGE}:${IMAGE_TAG}|' deployment-dev.yaml"
                    sh "kubectl apply -f deployment-dev.yaml"
                }
            }
        }

        stage("Run Acceptance Tests") {
            steps {
                script {
                    echo "Running Acceptance Tests..."
                    sh 'docker stop qa-tests || true'
                    sh 'docker rm qa-tests || true'
                    sh 'docker build -t qa-tests -f Dockerfile.test .'
                    sh 'docker run qa-tests'
                }
            }
        }

        stage ("Run Security Checks (Dastardly)") {
            steps {
                script {
                    echo "Running Dastardly scan on: http://10.48.10.146"
                    sh '''
                        docker run --user $(id -u) -v ${WORKSPACE}:${WORKSPACE}:rw \
                        -e BURP_START_URL=http://10.48.10.146 \
                        -e BURP_REPORT_FILE_PATH=${WORKSPACE}/dastardly-report.xml \
                        public.ecr.aws/portswigger/dastardly:latest
                    '''
                }
            }
        }

        stage('Deploy to Prod Environment') {
            steps {
                script {
                    echo "Deploying to Prod Environment..."
                    sh "sed -i 's|${DOCKER_IMAGE}:latest|${DOCKER_IMAGE}:${IMAGE_TAG}|' deployment-prod.yaml"
                    sh "cd .."
                    sh "kubectl apply -f deployment-prod.yaml"
                }
            }
        }

        stage('Check Kubernetes Cluster') {
            steps {
                script {
                    echo "Checking Kubernetes Cluster..."
                    sh "kubectl get all"
                }
            }
        }
    }

    post {
        success {
            slackSend color: "good", message: "Build Completed: ${env.JOB_NAME} ${env.BUILD_NUMBER}"
        }
        failure {
            slackSend color: "danger", message: "Build Failed: ${env.JOB_NAME} ${env.BUILD_NUMBER}"
        }
    }
}
