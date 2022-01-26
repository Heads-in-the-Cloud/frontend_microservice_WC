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

        stage ('scan') {
            steps {
                withSonarQubeEnv('sonarqube-WC'){
                sh "${scannerHome}/bin/sonar-scanner -D'sonar.projectKey=frontend-api'"
                }
            }
        }

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
                    docker.withRegistry(repository, "ecr:${region}:wc-ecr-access") {
                        image.push('latest')
                    }        
                }
            }
        }
        stage ('update') {
            when {
                expression { 
                return params.cluster == 'terraform'
                }
            }
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

        stage ('update EKS'){
            when {
                expression { 
                return params.cluster == 'eks'
                }
            }
            steps {
                sh "aws eks --region ${region} update-kubeconfig --name ${CLUSTER_NAME_WC}"
                sh 'kubectl rollout restart deployment/frontend-deployment'
            }
        }
    }
}