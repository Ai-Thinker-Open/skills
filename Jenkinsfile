pipeline {
    agent any

    stages {
        stage('Setup') {
            steps {
                sh '''
                    curl -fsSL https://nodejs.org/dist/v18.20.4/node-v18.20.4-linux-x64.tar.xz | tar -xJ
                    export PATH=$PWD/node-v18.20.4-linux-x64/bin:$PATH
                    node --version
                    npm --version
                '''
            }
        }

        stage('Validate') {
            steps {
                sh '''
                    export PATH=$PWD/node-v18.20.4-linux-x64/bin:$PATH
                    npm run validate
                '''
            }
        }

        stage('Build') {
            steps {
                sh '''
                    export PATH=$PWD/node-v18.20.4-linux-x64/bin:$PATH
                    npm run build
                '''
            }
        }

        stage('Sync to GitHub') {
            when {
                branch 'master'
            }
            steps {
                withCredentials([string(credentialsId: 'github-token', variable: 'TOKEN')]) {
                    sh '''
                        export PATH=$PWD/node-v18.20.4-linux-x64/bin:$PATH
                        git remote set-url --push origin "https://${TOKEN}@github.com/Ai-Thinker-Open/skills.git"
                        git push origin master
                    '''
                }
            }
        }

        stage('Release') {
            when {
                tag pattern: "v\\d+\\.\\d+\\.\\d+", comparator: "REGEXP"
            }
            steps {
                withCredentials([string(credentialsId: 'github-token', variable: 'TOKEN')]) {
                    sh '''
                        export PATH=$PWD/node-v18.20.4-linux-x64/bin:$PATH
                        npm install -g gh
                        echo "${TOKEN}" | gh auth login --with-token
                        gh release create "${TAG_NAME}" \
                            --repo "Ai-Thinker-Open/skills" \
                            --title "Release ${TAG_NAME}" \
                            --generate-notes \
                            dist/**/*
                    '''
                }
            }
        }
    }
}
