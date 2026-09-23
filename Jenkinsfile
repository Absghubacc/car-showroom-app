pipeline {
    agent any

    environment {
        DOCKER_HUB_USER = 'abhishaccount'
        BASE_IMAGE_NAME = 'car-showroom-base'
        IMAGE_NAME      = 'car-showroom-app'
        BUILD_TAG       = "${BUILD_NUMBER}"
    }

    stages {
        stage('Checkout Code') {
            steps {
                checkout scm
            }
        }

        stage('Build & Push Base Image') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'docker-credentials', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    bat '''
                    echo Logging in to Docker Hub...
                    echo %DOCKER_PASS% | docker login -u %DOCKER_USER% --password-stdin

                    echo Building Base Image...
                    docker build -t %DOCKER_HUB_USER%/%BASE_IMAGE_NAME%:latest -f dockerfile.base .

                    echo Pushing Base Image...
                    docker push %DOCKER_HUB_USER%/%BASE_IMAGE_NAME%:latest
                    '''
                }
            }
        }

        stage('Build & Push App Image') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'docker-credentials', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    bat '''
                    echo Building App Image... 
                    docker build -t %DOCKER_HUB_USER%/%IMAGE_NAME%:%BUILD_TAG% -t %DOCKER_HUB_USER%/%IMAGE_NAME%:latest .

                    echo Pushing App Images...
                    docker push %DOCKER_HUB_USER%/%IMAGE_NAME%:%BUILD_TAG%
                    docker push %DOCKER_HUB_USER%/%IMAGE_NAME%:latest
                    '''
                }
            }
        }

       stage('Update Kubernetes Manifests for GitOps') {
            steps {
                withCredentials([string(credentialsId: 'github-token', variable: 'GH_TOKEN')]) {
                    bat """
                    powershell -Command "(Get-Content K8s/app-deployment.yaml) -replace 'image: %DOCKER_HUB_USER%/%IMAGE_NAME%:.*', 'image: %DOCKER_HUB_USER%/%IMAGE_NAME%:%BUILD_TAG%' | Set-Content K8s/app-deployment.yaml"
                    
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
            cleanWs()
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