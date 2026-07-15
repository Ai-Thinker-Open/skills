pipeline {
    agent any

    environment {
        GITHUB_TOKEN = credentials('github-token')
    }

    stages {
        stage('Setup Node.js') {
            steps {
                sh '''
                    curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
                    apt-get install -y nodejs
                    node --version
                    npm --version
                '''
            }
        }

        stage('Validate') {
            steps {
                sh 'npm run validate'
            }
        }

        stage('Build') {
            steps {
                sh 'npm run build'
            }
        }

        stage('Sync to GitHub') {
            when {
                branch 'master'
            }
            steps {
                sh '''
                    git remote set-url --push origin "https://${GITHUB_TOKEN}@github.com/Ai-Thinker-Open/skills.git"
                    git push origin master
                '''
            }
        }

        stage('Release') {
            when {
                tag pattern: "v\\d+\\.\\d+\\.\\d+", comparator: "REGEXP"
            }
            steps {
                script {
                    sh '''
                        echo "${GITHUB_TOKEN}" | gh auth login --with-token
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
