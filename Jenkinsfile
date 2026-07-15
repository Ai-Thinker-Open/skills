pipeline {
    agent {
        docker {
            image 'public/docker/nodejs:18'
            registryUrl 'https://coding-public-docker.pkg.coding.net'
        }
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Validate') {
            steps {
                sh 'node --version && npm --version'
                sh 'npm run validate'
            }
        }

        stage('Build') {
            steps {
                sh 'npm run build'
            }
        }

        stage('Sync to GitHub') {
            steps {
                withCredentials([string(credentialsId: 'github-token', variable: 'TOKEN')]) {
                    sh '''
                        git remote set-url --push origin "https://${TOKEN}@github.com/Ai-Thinker-Open/skills.git"
                        git push origin master
                    '''
                }
            }
        }
    }
}
