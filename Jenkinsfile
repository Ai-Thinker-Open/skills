pipeline {
    agent {
        docker {
            image 'public/docker/nodejs:18'
            registryUrl 'https://coding-public-docker.pkg.coding.net'
        }
    }

    stages {
        stage('Debug') {
            steps {
                sh 'pwd && ls -la && find / -name "package.json" -maxdepth 4 2>/dev/null'
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
