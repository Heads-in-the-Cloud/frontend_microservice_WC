pipeline {

    environment {
        service_name = "FrontendService"
        task_def_name = "frontend-task-WC"
        image_label = "wc-frontend"
        git_commit_hash ="${sh(returnStdout: true, script: 'git rev-parse HEAD')}"
        image = ""
        repository = "${FRONTEND_REPO_WC}"
        latest = "${FRONTEND_REPO_WC}:latest"
        scannerHome = tool "${SonarQubeScanner}";

    }

    agent any
    stages {

        stage('Setup parameters') {
                    steps {
                        script { 
                            properties([
                                parameters([
                                    choice(
                                        choices: ['eks', 'cf'], 
                                        name: 'cluster'
                                    )
                                ])
                            ])
                        }
                    }
                }


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
        stage ('Update CloudFormation') {
            when {
                expression { 
                return params.cluster == 'cf'
                }
            }
            steps {
                script {
                    cluster_name=sh ( script: "aws ecs list-clusters  | grep ${CF_STACK_WC}", returnStdout: true).trim()
                    service_name=sh ( script: "aws ecs list-services --cluster ${cluster_name} | grep ${service_name}", returnStdout: true).trim()
                    sh "(aws ecs describe-task-definition --task-definition ${task_def_name}) | jq '.taskDefinition | \
                    {containerDefinitions:.containerDefinitions,        \
                    family:.family,                                     \
                    executionRoleArn:.executionRoleArn,                 \
                    requiresCompatibilities:.requiresCompatibilities,   \
                    cpu:.cpu, memory:.memory,                           \
                    networkMode:.networkMode}' > task-def.json"
                    sh 'aws ecs register-task-definition --cli-input-json file://task-def.json'
                    sh "aws ecs update-service --cluster ${cluster_name} --service ${service_name} --task-definition ${task_def_name}"
                }
            }
        } 

        stage ('update Elastic Kubernetes Service'){
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
    post {
        cleanup {
            script {
                if(built) {
                    sh "docker rmi $image_label"
                }
            }
        }
    }
}