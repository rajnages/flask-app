pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = 'my-flask-app'
        DOCKER_TAG = 'latest'
        GIT_REPO = 'https://github.com/yourusername/your-repo.git'  // Replace with your repo URL
        GIT_BRANCH = 'main'  // or 'master' depending on your default branch
    }
    
    stages {
        stage('Git Checkout') {
            steps {
                // Clean workspace before checkout
                cleanWs()
                
                git branch: "${GIT_BRANCH}",
                    url: "${GIT_REPO}"
                    // If using private repository, add credentials:
                    // credentialsId: 'your-credentials-id'
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    docker.build("${DOCKER_IMAGE}:${DOCKER_TAG}")
                }
            }
        }
        
        stage('Deploy Container') {
            steps {
                script {
                    // Stop existing container if running
                    sh 'docker ps -f name=flask-container -q | xargs --no-run-if-empty docker container stop'
                    sh 'docker container ls -a -fname=flask-container -q | xargs -r docker container rm'
                    
                    // Run new container
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
            // Clean up workspace
            cleanWs()
        }
    }
}