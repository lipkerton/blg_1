pipeline {
    agent { docker { image 'python:3.13-slim' } }
    stages {
        stage('build') {
            steps {
                sh 'python --version'
            }
        }
    }
}
