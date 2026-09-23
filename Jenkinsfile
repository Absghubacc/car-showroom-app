pipeline {
    agent any
    environment {
        // 1. UPDATE: Your actual Docker Hub Username
        DOCKER_HUB_USER = 'abhishaccount'
        IMAGE_NAME      = 'car-showroom-app'
        BUILD_TAG       = "${BUILD_NUMBER}"
        SONAR_SCANNER   = 'SonarQube'
    }
    stages {
        stage('Checkout Code') {
            steps {
                checkout scm
            }
        }
        stage('OWASP Dependency Check') {
            steps {
                    dependencyCheck additionalArguments: '--scan ./ --autoUpdate false', odcInstallation: 'DP-Check'
                    dependencyCheckPublisher pattern: '**/dependency-check-report.xml'
                  }
                }
        stage('SonarQube Quality Scan') {
           steps {
           // Ensure the string matches the Name field in Manage Jenkins -> System
               withSonarQubeEnv('SonarQube') { 
                bat 'sonar-scanner -Dsonar.projectKey=car-showroom -Dsonar.sources=.'
              }
            }
        }
        stage('SonarQube Quality Scan') {
          steps {
                  script {
                     // Replace 'SonarScanner' with the tool name defined under Manage Jenkins -> Tools -> SonarQube Scanner
                        def scannerHome = tool 'SonarScanner' 
                        withSonarQubeEnv('SonarQube') {
                        bat "${scannerHome}/bin/sonar-scanner -Dsonar.projectKey=car-showroom -Dsonar.sources=."
                         }
                    }
                }
              }
        stage('Build & Push Docker Image') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'docker-credentials', usernameVariable: 'USER', passwordVariable: 'PASS')]) {
                    bat "docker build -t %DOCKER_HUB_USER%/%IMAGE_NAME%:%BUILD_TAG% ."
                    bat "docker build -t %DOCKER_HUB_USER%/%IMAGE_NAME%:latest ."
                    bat "echo %PASS% | docker login -u %USER% --password-stdin"
                    bat "docker push %DOCKER_HUB_USER%/%IMAGE_NAME%:%BUILD_TAG%"
                    bat "docker push %DOCKER_HUB_USER%/%IMAGE_NAME%:latest"
                }
            }
        }
        stage('Container Vulnerability Scan (Trivy)') {
            steps {
                bat "trivy image --severity HIGH,CRITICAL %DOCKER_HUB_USER%/%IMAGE_NAME%:latest"
            }
        }
        stage('Execute Infrastructure Code (Terraform)') {
            steps {
                dir('terraform') {
                    bat "terraform init"
                    bat "terraform apply -auto-approve"
                }
            }
        }
        stage('Update Kubernetes Manifests for GitOps') {
            steps {
                withCredentials([string(credentialsId: 'github-token', variable: 'GH_TOKEN')]) {
                    bat """
                    git config user.name "Jenkins CI"
                    git config user.email "jenkins@local.com"
                    @rem 3. FIX: Updated 'k8s' to 'K8s' to match actual folder capitalization
                    git add K8s/app-deployment.yaml
                    git commit -m "Automated image update build #${BUILD_NUMBER}" || exit 0
                    @rem 4. UPDATE: Replace YOUR_GITHUB_USERNAME with your GitHub handle
                    git push https://%GH_TOKEN%@github.com/Absghubacc/car-showroom-app.git HEAD:main
                    """
                }
            }
        }
    }
    post {
        always {
            emailext (
                subject: "Jenkins Build ${currentBuild.fullDisplayName} - ${currentBuild.result}",
                body: """
                <h2>Build Report</h2>
                <p>Status: <b>${currentBuild.result}</b></p>
                <p>Job: ${env.JOB_NAME}</p>
                <p>Build Number: ${env.BUILD_NUMBER}</p>
                <p>Check SonarQube & Grafana Dashboards for details.</p>
                """,
                // 5. UPDATE: Put your target notification email address here
                to: 'abapptestingpurpose@gmail.com',
                mimeType: 'text/html'
            )
        }
    }
}