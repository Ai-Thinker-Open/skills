pipeline {
    agent any

    stages {
        stage('Debug') {
            steps {
                sh '''
                    cd /root/workspace
                    ls -la
                    echo "=== looking for package.json ==="
                    find /root -name "package.json" -maxdepth 5 2>/dev/null
                    echo "=== checking PWD ==="
                    pwd
                '''
            }
        }
    }
}
