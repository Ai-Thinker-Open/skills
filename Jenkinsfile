pipeline {
    agent {
        docker {
            image 'public/docker/nodejs:18'
            registryUrl 'https://coding-public-docker.pkg.coding.net'
        }
    }

    stages {
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
            when {
                branch 'master'
            }
            steps {
                withCredentials([string(credentialsId: 'github-token', variable: 'TOKEN')]) {
                    sh '''
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
