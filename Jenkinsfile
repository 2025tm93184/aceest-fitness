pipeline {
  agent any
  environment {
    IMAGE = "2025tm93184/aceest-fitness"
  }
  stages {
    stage('Checkout') {
      steps { checkout scm }
    }
    stage('Test') {
      steps {
        sh '''
          python3 -m venv .venv
          . .venv/bin/activate
          pip install -r requirements.txt pytest
          pytest -q
        '''
      }
    }
    stage('Docker build and push') {
      steps {
        sh 'docker build -t ${IMAGE}:v1.0 .'
        sh 'docker push ${IMAGE}:v1.0'
      }
    }
  }
}
