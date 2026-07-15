pipeline {
    agent {
        docker {
            image 'node:18-slim'
        }
    }

    stages {
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
                withCredentials([string(credentialsId: 'github-token', variable: 'TOKEN')]) {
                    sh '''
                        apt-get update && apt-get install -y git
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
                        apt-get update && apt-get install -y gh
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
