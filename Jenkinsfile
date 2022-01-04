pipeline {

    environment {
        image_label = "wc-frontend"
        git_commit_hash ="${sh(returnStdout: true, script: 'git rev-parse HEAD')}"
        image = ""
        repository = "${FRONTEND_REPO_WC}"
        latest = "${FRONTEND_REPO_WC}:latest"
        scannerHome = tool "${SonarQubeScanner}";

    }

    agent any
    stages {
        stage('build') {
            steps {
                script {
                    image = docker.build image_label
                }
            }
        }
        stage('push to registry') {
            steps {
                script {
                    docker.withRegistry(repository, 'ecr:us-west-2:wc-ecr-access') {
                        image.push('latest')
                    }        
                }
            }
        }
        stage ('update') {
            steps {
                sh '(aws ecs describe-task-definition --task-definition frontend-task-WC) | jq ".taskDefinition | \
                {containerDefinitions:.containerDefinitions,        \
                family:.family,                                     \
                executionRoleArn:.executionRoleArn,                 \
                requiresCompatibilities:.requiresCompatibilities,   \
                cpu:.cpu, memory:.memory,                           \
                networkMode:.networkMode}" > task-def.json'     
                sh 'aws ecs register-task-definition --cli-input-json file://task-def.json'
                sh 'aws ecs update-service --cluster utopia-cluster-WC --service frontend-service-WC --task-definition frontend-task-WC'
            }
        }   
    }




}