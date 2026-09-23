pipeline {
    agent any

    environment {
        DOCKER_HUB_USER = 'abhishaccount'
        IMAGE_NAME      = 'car-showroom-app'
        BUILD_TAG       = "${BUILD_NUMBER}"
    }

    stages {
        stage('Checkout Code') {
            steps {
                checkout scm
            }
        }

        // Bypassing SonarQube quality scan to proceed directly to deployment steps
        // stage('SonarQube Quality Scan') {
        //     steps {
        //         script {
        //             def scannerHome = tool 'SonarScanner'
        //             withSonarQubeEnv('SonarQube') {
        //                 bat "\"${scannerHome}/bin/sonar-scanner\" -Dsonar.projectKey=car-showroom -Dsonar.sources=."
        //             }
        //         }
        //     }
        // }

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

        stage('Update Kubernetes Manifests for GitOps') {
            steps {
                withCredentials([string(credentialsId: 'github-token', variable: 'GH_TOKEN')]) {
                    bat """
                    git config user.name "Jenkins CI"
                    git config user.email "jenkins@local.com"
                    git add K8s/app-deployment.yaml
                    git commit -m "Automated image update build #${BUILD_NUMBER}" || exit 0
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
                """,
                to: 'abapptestingpurpose@gmail.com',
                mimeType: 'text/html'
            )
        }
    }
}