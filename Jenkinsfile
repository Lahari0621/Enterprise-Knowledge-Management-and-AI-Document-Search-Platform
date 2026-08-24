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

                    echo "Stopping old CI deployment..."
                    docker-compose -p enterprise-knowledge-management-ci down || true

                    echo "Stopping previous Pipeline deployment..."
                    docker-compose -p enterprise-knowledge-management-pipeline down || true

                    echo "Starting application..."
                    docker-compose up -d

                    echo "Checking container status..."
                    docker-compose ps
                '''
            }
        }

        stage('Wait for Backend') {
            steps {
                sh '''
                    echo "======================================"
                    echo "Waiting for Backend"
                    echo "======================================"

                    for i in 1 2 3 4 5 6 7 8 9 10; do
                        echo "Health check attempt $i..."

                        if curl -f http://host.docker.internal:8000/health; then
                            echo ""
                            echo "Backend is ready!"
                            break
                        fi

                        if [ "$i" -eq 10 ]; then
                            echo ""
                            echo "Backend failed to become ready."
                            echo "Backend container logs:"
                            docker-compose logs backend
                            exit 1
                        fi

                        echo "Backend not ready yet."
                        echo "Waiting 5 seconds..."
                        sleep 5
                    done
                '''
            }
        }

        stage('Health Check') {
            steps {
                sh '''
                    echo "======================================"
                    echo "Testing Application Health"
                    echo "======================================"

                    curl -f http://host.docker.internal:8000/health

                    echo ""
                    echo "Application health check PASSED!"
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

                    echo ""
                    echo "Authentication security test completed."
                '''
            }
        }

        stage('Security Validation') {
            steps {
                sh '''
                    echo "======================================"
                    echo "Document API Security Validation"
                    echo "======================================"

                    STATUS=$(curl -s -o /tmp/doc_response.txt -w "%{http_code}" \
                        http://host.docker.internal:8000/api/documents)

                    echo "HTTP Status: $STATUS"
                    cat /tmp/doc_response.txt
                    echo ""

                    if [ "$STATUS" = "401" ]; then
                        echo "PASS: Document API requires authentication."
                    else
                        echo "FAIL: Document API security validation failed."
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

        always {
            echo 'Jenkins Pipeline execution finished.'
        }
    }
}