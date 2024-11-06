pipeline {
    agent any
    
    environment {
        DOCKERHUB_CREDENTIALS = credentials('dockercred') // Jenkins credentials ID
        DOCKER_IMAGE = 'rajnages/my-flask-app' // Replace with your Docker Hub username
        DOCKER_TAG = "${BUILD_NUMBER}" // Using Jenkins BUILD_NUMBER for versioning
        GIT_REPO = 'https://github.com/rajnages/flask-app.git'
        GIT_BRANCH = 'main'
    }
    
    stages {
        stage('Git Checkout') {
            steps {
                cleanWs()
                git branch: "${GIT_BRANCH}",
                    url: "${GIT_REPO}"
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    // Build with both latest and build number tags
                    docker.build("${DOCKER_IMAGE}:${DOCKER_TAG}")
                    docker.build("${DOCKER_IMAGE}:latest")
                }
            }
        }
        
        stage('Login to DockerHub') {
            steps {
                script {
                    // Login to Docker Hub
                    sh "echo ${DOCKERHUB_CREDENTIALS_PSW} | docker login -u ${DOCKERHUB_CREDENTIALS_USR} --password-stdin"
                }
            }
        }
        
        stage('Push to DockerHub') {
            steps {
                script {
                    // Push both tags
                    sh "docker push ${DOCKER_IMAGE}:${DOCKER_TAG}"
                    sh "docker push ${DOCKER_IMAGE}:latest"
                }
            }
        }
        
        stage('Deploy Container') {
            steps {
                script {
                    // Stop existing container if running
                    sh 'docker ps -f name=flask-container -q | xargs --no-run-if-empty docker container stop'
                    sh 'docker container ls -a -fname=flask-container -q | xargs -r docker container rm'
                    
                    // Run new container with the specific version
                    sh "docker run -d -p 5000:5000 --name flask-container ${DOCKER_IMAGE}:${DOCKER_TAG}"
                }
            }
        }
    }
    
    post {
        success {
            echo 'Pipeline succeeded! Application deployed successfully.'
        }
        failure {
            echo 'Pipeline failed! Check the logs for details.'
        }
        always {
            // Logout from Docker Hub and clean workspace
            sh 'docker logout'
            cleanWs()
        }
    }
}