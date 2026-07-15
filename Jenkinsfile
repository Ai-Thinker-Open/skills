pipeline {
    agent any

    stages {
        stage('Validate') {
            steps {
                docker.image('public/docker/nodejs:18').inside {
                    sh 'node --version && npm --version'
                    sh 'pwd && ls -la'
                    sh 'npm run validate'
                }
            }
        }

        stage('Build') {
            steps {
                docker.image('public/docker/nodejs:18').inside {
                    sh 'npm run build'
                }
            }
        }

        stage('Sync to GitHub') {
            steps {
                docker.image('public/docker/nodejs:18').inside {
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
}
