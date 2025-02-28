pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = 'estategenius-ai'
        DOCKER_TAG = "${env.BUILD_NUMBER}"
        CONTAINER_NAME = 'estategenius-app'
        SERVER_DATA_DIR = '/opt/estategenius/data'
        ENV_FILE = credentials('estategenius-env-file')
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Prepare Environment') {
            steps {
                // Ensure data directories exist on the host
                sh '''
                    mkdir -p ${SERVER_DATA_DIR}/database
                    mkdir -p ${SERVER_DATA_DIR}/uploaded_images
                    mkdir -p ${SERVER_DATA_DIR}/reports
                    mkdir -p ${SERVER_DATA_DIR}/logs
                    
                    # Set proper permissions
                    chmod -R 777 ${SERVER_DATA_DIR}
                '''
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    // Build the Docker image
                    sh "docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} ."
                    sh "docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:latest"
                }
            }
        }
        
        stage('Deploy') {
            steps {
                script {
                    // Stop and remove existing container if it exists
                    sh "docker stop ${CONTAINER_NAME} || true"
                    sh "docker rm ${CONTAINER_NAME} || true"
                    
                    // Copy the .env file to the server
                    sh "cp ${ENV_FILE} .env"
                    
                    // Run the new container with volume mounts for persistent data
                    sh '''
                        docker run -d \
                            --name ${CONTAINER_NAME} \
                            -p 8501:8501 \
                            -v ${SERVER_DATA_DIR}/database:/app/data/database \
                            -v ${SERVER_DATA_DIR}/uploaded_images:/app/uploaded_images \
                            -v ${SERVER_DATA_DIR}/reports:/app/reports \
                            -v ${SERVER_DATA_DIR}/logs:/app/logs \
                            -v $(pwd)/.env:/app/.env \
                            ${DOCKER_IMAGE}:${DOCKER_TAG}
                    '''
                }
            }
        }
        
        stage('Clean Up') {
            steps {
                // Remove unused Docker images to save space (keep the last 3)
                sh '''
                    docker image prune -f
                    # Keep only the 3 most recent versions and remove the rest
                    docker images --format "{{.ID}} {{.Repository}}" | grep ${DOCKER_IMAGE} | sort -k 2 | head -n -3 | awk '{print $1}' | xargs -r docker rmi -f
                '''
            }
        }
    }
    
    post {
        success {
            echo 'Deployment successful!'
        }
        failure {
            echo 'Deployment failed!'
        }
    }
}