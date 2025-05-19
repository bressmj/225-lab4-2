pipeline {
    agent any 

    environment {
        DOCKER_CREDENTIALS_ID = 'roseaw-dockerhub'
        DOCKER_IMAGE = 'cithit/bressmj'                            //<------replace with your MiamiID
        IMAGE_TAG = "build-${BUILD_NUMBER}"
        GITHUB_URL = 'https://github.com/bressmj/225-lab5-1.git'    //<------replace with your MiamiID
        KUBECONFIG = credentials('bressmj-225')                     //<------replace with your MiamiID
        SLACK_CHANNEL = '#your-channel'                             //<------replace with your Slack channel
    }

    stages {
        stage('Checkout') {
            steps {
                cleanWs()
                checkout([$class: 'GitSCM', branches: [[name: '*/main']],
                          userRemoteConfigs: [[url: "${GITHUB_URL}"]]])
            }
        }

        stage('Lint HTML') {
            steps {
                sh 'npm install htmlhint --save-dev'
                sh 'npx htmlhint *.html'
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    docker.build("${DOCKER_IMAGE}:${IMAGE_TAG}", "-f Dockerfile.build .")
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                script {
                    docker.withRegistry('https://index.docker.io/v1/', "${DOCKER_CREDENTIALS_ID}") {
                        docker.image("${DOCKER_IMAGE}:${IMAGE_TAG}").push()
                    }
                }
            }
        }

        stage('Deploy to Dev Environment') {
            steps {
                script {
                    // Set up Kubernetes configuration using the specified KUBECONFIG
                    def kubeConfig = readFile(KUBECONFIG)
                    // Update deployment-dev.yaml to use the new image tag
                    sh "sed -i 's|${DOCKER_IMAGE}:latest|${DOCKER_IMAGE}:${IMAGE_TAG}|' deployment-dev.yaml"
                    sh "kubectl apply -f deployment-dev.yaml"
                }
            }
        }

         stage("Run Acceptance Tests") {
            steps {
                script {
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
                    // Ensure Dastardly image is pulled
                    sh 'docker pull public.ecr.aws/portswigger/dastardly:latest'

                    // Run Dastardly security scan (change to the correct URL of your app in Kubernetes or dev environment)
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
                    // Set up Kubernetes configuration using the specified KUBECONFIG
                    sh "sed -i 's|${DOCKER_IMAGE}:latest|${DOCKER_IMAGE}:${IMAGE_TAG}|' deployment-prod.yaml"
                    sh "cd .."
                    sh "kubectl apply -f deployment-prod.yaml"
                }
            }
        }

        stage('Check Kubernetes Cluster') {
            steps {
                script {
                    sh "kubectl get all"
                }
            }
        }
    }
    
    post {
        always {
            // Archive the Dastardly report for security review
            junit testResults: 'dastardly-report.xml', skipPublishingChecks: true
        }
        success {
            slackSend(channel: "${SLACK_CHANNEL}", color: "good", message: "Build Completed: ${env.JOB_NAME} ${env.BUILD_NUMBER} - Success")
        }
        unstable {
            slackSend(channel: "${SLACK_CHANNEL}", color: "warning", message: "Build Unstable: ${env.JOB_NAME} ${env.BUILD_NUMBER}")
        }
        failure {
            slackSend(channel: "${SLACK_CHANNEL}", color: "danger", message: "Build Failed: ${env.JOB_NAME} ${env.BUILD_NUMBER}")
        }
    }
}
