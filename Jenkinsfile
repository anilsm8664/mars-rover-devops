pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
        skipDefaultCheckout(true)
        buildDiscarder(logRotator(numToKeepStr: '20'))
        timeout(time: 30, unit: 'MINUTES')
    }

    environment {
        IMAGE_NAME = 'mars-rover'
        IMAGE_TAG = "${BUILD_NUMBER}"
    }

    stages {
        stage('1. Checkout and Setup') {
            steps {
                checkout scm
                sh 'python3 --version && docker --version && trivy --version'
            }
        }

        stage('2. Code Validation / Lint') {
            steps {
                sh '''
                    python3 -m venv .venv
                    . .venv/bin/activate
                    python -m pip install --upgrade pip
                    python -m pip install -r requirements-dev.txt
                    ruff check rover.py tests
                '''
            }
        }

        stage('3. Unit Tests') {
            steps {
                sh '''
                    . .venv/bin/activate
                    pytest -q --junitxml=test-results.xml \\
                      --cov=rover --cov-report=term-missing \\
                      --cov-report=xml:coverage.xml
                '''
            }
            post {
                always {
                    junit testResults: 'test-results.xml', allowEmptyResults: false
                }
            }
        }

        stage('4. SonarQube Analysis') {
            steps {
                withSonarQubeEnv('sonarqube') {
                    sh '''
                        sonar-scanner \\
                          -Dsonar.projectKey=mars-rover-devops \\
                          -Dsonar.sources=rover.py \\
                          -Dsonar.tests=tests \\
                          -Dsonar.python.version=3.12 \\
                          -Dsonar.python.coverage.reportPaths=coverage.xml
                    '''
                }
            }
        }

        stage('4b. SonarQube Quality Gate') {
            steps {
                timeout(time: 10, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage('5. Container Build') {
            steps {
                sh 'docker build --pull --tag "${IMAGE_NAME}:${IMAGE_TAG}" .'
            }
        }

        stage('6. Container Smoke Test') {
            steps {
                sh '''
                    set -eu
                    docker run --rm \\
                      -v "$PWD/examples/input.txt:/input.txt:ro" \\
                      "${IMAGE_NAME}:${IMAGE_TAG}" /input.txt > actual-output.txt
                    printf '1 3 N\\n5 1 E\\n' > expected-output.txt
                    diff -u expected-output.txt actual-output.txt
                '''
            }
            post {
                always {
                    sh 'rm -f actual-output.txt expected-output.txt || true'
                }
            }
        }

        stage('6b. Container Vulnerability Scan') {
            steps {
                sh '''
                    trivy image \\
                      --severity HIGH,CRITICAL \\
                      --ignore-unfixed \\
                      --exit-code 1 \\
                      "${IMAGE_NAME}:${IMAGE_TAG}"
                '''
            }
        }

        stage('7. Publish to Artifactory') {
            when {
                allOf {
                    branch 'main'
                    expression {
                        return env.ARTIFACTORY_REGISTRY?.trim() && env.ARTIFACTORY_REPOSITORY?.trim()
                    }
                }
            }
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'artifactory-docker',
                    usernameVariable: 'ARTIFACTORY_USERNAME',
                    passwordVariable: 'ARTIFACTORY_PASSWORD'
                )]) {
                    sh '''
                        set -eu
                        IMAGE="${ARTIFACTORY_REGISTRY}/${ARTIFACTORY_REPOSITORY}/mars-rover:${BUILD_NUMBER}"
                        echo "$ARTIFACTORY_PASSWORD" | docker login "$ARTIFACTORY_REGISTRY" \\
                          --username "$ARTIFACTORY_USERNAME" --password-stdin
                        docker tag "${IMAGE_NAME}:${IMAGE_TAG}" "$IMAGE"
                        docker push "$IMAGE"
                        docker logout "$ARTIFACTORY_REGISTRY"
                    '''
                }
            }
        }
    }

    post {
        always {
            sh 'docker image rm "${IMAGE_NAME}:${IMAGE_TAG}" || true'
            deleteDir()
        }
    }
}
