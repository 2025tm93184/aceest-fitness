pipeline {
    agent any
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Build and test') {
            steps {
                sh '''
                  python3 -m pip install --user -r requirements.txt
                  python3 -m py_compile app.py
                  python3 -m pytest -q
                '''
            }
        }
    }
}

