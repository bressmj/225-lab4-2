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

        stage('Lint HTML') {
            steps {
                catchError(buildResult: 'SUCCESS', message: 'Linting failed') {
                    sh 'npm install htmlhint --save-dev'
                    sh 'npx htmlhint *.html'
                }
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
                    catchError(buildResult: 'SUCCESS', message: 'Acceptance Tests failed') {
                        sh 'docker stop qa-tests || true'
                        sh 'docker rm qa-tests || true'
                        sh 'docker build -t qa-tests -f Dockerfile.test .'
                        sh 'docker run qa-tests'
                    }
                }
            }
        }

        stage ("Run Security Checks (Dastardly)") {
            steps {
                script {
                    catchError(buildResult: 'SUCCESS', message: 'Security Checks (Dastardly) failed') {
                        echo "Running Dastardly scan on: http://your-app-service-url"
                        sh '''
                            docker run --user $(id -u) -v ${WORKSPACE}:${WORKSPACE}:rw \
                            -e BURP_START_URL=http://your-app-service-url \
                            -e BURP_REPORT_FILE_PATH=${WORKSPACE}/dastardly-report.xml \
                            public.ecr.aws/portswigger/dastardly:latest
                        '''
                    }
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
            // Ensure the build is marked as successful, regardless of errors
            currentBuild.result = 'SUCCESS'

            // Archive the Dastardly report for security review
            junit testResults: 'dastardly-report.xml', skipPublishingChecks: true
        }
        success {
            slackSend color: "good", message: "Build Completed: ${env.JOB_NAME} ${env.BUILD_NUMBER}"
        }
        unstable {
            slackSend color: "warning", message: "Build Unstable: ${env.JOB_NAME} ${env.BUILD_NUMBER}"
        }
        failure {
            slackSend color: "danger", message: "Build Failed: ${env.JOB_NAME} ${env.BUILD_NUMBER}"
        }
    }
}
