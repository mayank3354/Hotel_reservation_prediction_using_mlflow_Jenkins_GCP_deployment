pipeline{
    agent any

    environment{
        VENV_DIR = 'venv'
        GCP_PROJECT = 'clear-shadow-456404-i1'
        GCLOUD_PATH = '/var/jenkins_home/google-cloud-sdk/bin'
    }
    stages{
        stage('Cloning Github repo to Jenkins'){
            steps{
                script{
                    echo 'Cloning Github repo to Jenkins........'
                    checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: 'github-token', url: 'https://github.com/mayank3354/Hotel_reservation_prediction_using_mlflow_Jenkins_GCP_deployment.git']])
                    }
                }
            }
        stage('Setting up virtual environment and installing dependencies'){
            steps{
                script{
                    echo 'Setting up virtual environment and installing dependencies........'
                    sh '''
                    python -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    pip install --upgrade pip
                    pip install -e .
                    '''
                }
            }
        }
        stage('Building and pushing Docker image to GCR'){
            steps{
                withCredentials([file(credentialsId: 'gcp-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS')])
                {
                    script{
                        sh '''
                        export PATH=$PATH:${GCLOUD_PATH}    
                        gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}
                        
                        gcloud config set project ${GCP_PROJECT}
                        gcloud auth configure-docker --quiet
                        docker build -t gcr.io/${GCP_PROJECT}/hotel-reservation-prediction:latest .
                        docker push gcr.io/${GCP_PROJECT}/hotel-reservation-prediction:latest
                        
                        ''' 
                    }
                }
            }
        }
         stage('Deploy to Google Cloud Run'){
            steps{
                withCredentials([file(credentialsId: 'gcp-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS')])
                {
                    script{
                        sh '''
                        export PATH=$PATH:${GCLOUD_PATH}    
                        gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}
                        
                        gcloud config set project ${GCP_PROJECT}
                        gcloud run deploy hotel-reservation-prediction --image gcr.io/${GCP_PROJECT}/hotel-reservation-prediction:latest --platform managed --region us-central1 --allow-unauthenticated
                        
                        ''' 
                    }
                }
            }
        }
    }
}