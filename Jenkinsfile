pipeline {
    agent any

    stages {
        stage('Setup') {
            steps {
                sh '''
                    cd $WORKSPACE
                    curl -fsSL https://nodejs.org/dist/v16.20.2/node-v16.20.2-linux-x64.tar.xz | tar -xJ
                    export PATH=$PWD/node-v16.20.2-linux-x64/bin:$PATH
                    node --version && npm --version
                '''
            }
        }

        stage('Validate') {
            steps {
                sh '''
                    cd $WORKSPACE
                    export PATH=$PWD/node-v16.20.2-linux-x64/bin:$PATH
                    npm run validate
                '''
            }
        }

        stage('Build') {
            steps {
                sh '''
                    cd $WORKSPACE
                    export PATH=$PWD/node-v16.20.2-linux-x64/bin:$PATH
                    npm run build
                '''
            }
        }

        stage('Sync to GitHub') {
            steps {
                withCredentials([string(credentialsId: 'github-token', variable: 'TOKEN')]) {
                    sh '''
                        cd $WORKSPACE
                        export PATH=$PWD/node-v16.20.2-linux-x64/bin:$PATH
                        git remote set-url --push origin "https://${TOKEN}@github.com/Ai-Thinker-Open/skills.git"
                        git push origin master
                    '''
                }
            }
        }
    }
}
