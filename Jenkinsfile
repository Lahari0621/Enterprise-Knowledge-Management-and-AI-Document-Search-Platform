pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Validate Project') {
            steps {
                sh '''
                    echo "======================================"
                    echo "Validating Project"
                    echo "======================================"

                    test -f README.md
                    test -f docker-compose.yml
                    test -d backend
                    test -d frontend

                    echo "All basic project checks passed."
                '''
            }
        }

        stage('Build Docker Images') {
            steps {
                sh '''
                    echo "======================================"
                    echo "Building Docker Images"
                    echo "======================================"

                    docker-compose build
                '''
            }
        }

        stage('Deploy Application') {
            steps {
                sh '''
                    echo "======================================"
                    echo "Deploying Application"
                    echo "======================================"

                    docker-compose down || true
                    docker-compose up -d

                    docker-compose ps
                '''
            }
        }

        stage('Wait for Backend') {
            steps {
                sh '''
                    echo "Waiting for backend..."
                    sleep 10
                '''
            }
        }

        stage('Health Check') {
            steps {
                sh '''
                    echo "======================================"
                    echo "Testing Application Health"
                    echo "======================================"

                    curl -i http://host.docker.internal:8000/health
                '''
            }
        }

        stage('Authentication Test') {
            steps {
                sh '''
                    echo "======================================"
                    echo "Testing Authentication Security"
                    echo "======================================"

                    echo "Testing /api/me..."
                    curl -i http://host.docker.internal:8000/api/me

                    echo ""
                    echo "Testing /api/documents..."
                    curl -i http://host.docker.internal:8000/api/documents
                '''
            }
        }

        stage('Security Validation') {
            steps {
                sh '''
                    echo "======================================"
                    echo "Document API Security Validation"
                    echo "======================================"

                    STATUS=$(curl -s -o /tmp/doc_response.txt \
                        -w "%{http_code}" \
                        http://host.docker.internal:8000/api/documents)

                    echo "HTTP Status: $STATUS"
                    cat /tmp/doc_response.txt

                    if [ "$STATUS" = "401" ]; then
                        echo "PASS: Document API requires authentication."
                    else
                        echo "FAIL: Unexpected HTTP status."
                        exit 1
                    fi
                '''
            }
        }

        stage('Final Status') {
            steps {
                sh '''
                    echo "======================================"
                    echo "Final Docker Container Status"
                    echo "======================================"

                    docker-compose ps

                    echo "======================================"
                    echo "Pipeline Deployment Completed"
                    echo "======================================"
                '''
            }
        }
    }

    post {
        success {
            echo 'CI/CD Pipeline completed successfully!'
        }

        failure {
            echo 'CI/CD Pipeline failed. Check the console output.'
        }
    }
}