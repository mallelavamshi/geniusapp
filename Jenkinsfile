pipeline {
    agent any
    
    environment {
        // Define container name and image tags as variables for consistency
        CONTAINER_NAME = 'estategenius-app'
        IMAGE_NAME = 'estategenius-ai'
        IMAGE_TAG = "${env.BUILD_NUMBER}"
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Prepare Environment') {
            steps {
                // Create necessary directories
                sh 'mkdir -p /opt/estategenius/data/database'
                sh 'mkdir -p /opt/estategenius/data/uploaded_images'
                sh 'mkdir -p /opt/estategenius/data/reports'
                sh 'mkdir -p /opt/estategenius/data/logs'
                
                // Verify directories are writable
                sh '''
                    [ ! -w /opt/estategenius/data/database ] && echo "Database directory not writable" && exit 1
                    [ ! -w /opt/estategenius/data/uploaded_images ] && echo "Uploads directory not writable" && exit 1
                    [ ! -w /opt/estategenius/data/reports ] && echo "Reports directory not writable" && exit 1
                    [ ! -w /opt/estategenius/data/logs ] && echo "Logs directory not writable" && exit 1
                    exit 0
                '''
            }
        }
        
        stage('Build Docker Image') {
            steps {
                // Build the Docker image
                sh "docker build -t ${IMAGE_NAME}:${IMAGE_TAG} ."
                sh "docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${IMAGE_NAME}:latest"
            }
        }
        
        stage('Deploy') {
            steps {
                // Stop and remove existing container if it exists
                sh "docker stop ${CONTAINER_NAME} || true"
                sh "docker rm ${CONTAINER_NAME} || true"
                
                // Deploy with credentials passed as environment variables
                withCredentials([
                    string(credentialsId: 'IMGBB_API_KEY', variable: 'IMGBB_API_KEY'),
                    string(credentialsId: 'SEARCHAPI_API_KEY', variable: 'SEARCHAPI_API_KEY'),
                    string(credentialsId: 'ANTHROPIC_API_KEY', variable: 'ANTHROPIC_API_KEY')
                ]) {
                    sh """
                        docker run -d -p 8501:8501 --name ${CONTAINER_NAME} \
                        -v /opt/estategenius/data:/app/data \
                        -e IMGBB_API_KEY=${IMGBB_API_KEY} \
                        -e SEARCHAPI_API_KEY=${SEARCHAPI_API_KEY} \
                        -e ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY} \
                        ${IMAGE_NAME}:latest
                    """
                }
            }
        }
        
        stage('Clean Up') {
            steps {
                // Remove old images to save space
                sh "docker image prune -f"
            }
        }
    }
    
    post {
        success {
            echo "Deployment successful!"
        }
        failure {
            echo "Deployment failed!"
        }
    }
}