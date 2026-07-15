pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                sh '''
                    cd /root/workspace
                    git clone git@e.coding.net:axk/anxinkeskill/skills.git .
                '''
            }
        }

        stage('Setup') {
            steps {
                sh '''
                    cd /root/workspace
                    curl -fsSL https://nodejs.org/dist/v16.20.2/node-v16.20.2-linux-x64.tar.xz | tar -xJ
                    export PATH=$PWD/node-v16.20.2-linux-x64/bin:$PATH
                    node --version && npm --version
                '''
            }
        }

        stage('Validate') {
            steps {
                sh '''
                    cd /root/workspace
                    export PATH=$PWD/node-v16.20.2-linux-x64/bin:$PATH
                    npm run validate
                '''
            }
        }

        stage('Build') {
            steps {
                sh '''
                    cd /root/workspace
                    export PATH=$PWD/node-v16.20.2-linux-x64/bin:$PATH
                    npm run build
                '''
            }
        }

        stage('Sync to GitHub') {
            steps {
                withCredentials([string(credentialsId: 'github-token', variable: 'TOKEN')]) {
                    sh '''
                        cd /root/workspace
                        export PATH=$PWD/node-v16.20.2-linux-x64/bin:$PATH
                        git remote add github "https://${TOKEN}@github.com/Ai-Thinker-Open/skills.git" || true
                        git push github master
                    '''
                }
            }
        }
    }
}
