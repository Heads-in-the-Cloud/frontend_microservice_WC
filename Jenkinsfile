pipeline {

    environment {
        service_name            = "FrontendService"
        task_def_name           = "frontend-task-WC"
        image_label             = "${FRONTEND_REPO_WC}"
        git_commit_hash         ="${sh(returnStdout: true, script: 'git rev-parse --short=8 HEAD').trim()}"
        image                   = ""
        repository              = "${ORG_ACCOUNT_NUM}.dkr.ecr.${REGION_WC}.amazonaws.com/${image_label}"
        latest                  = "${FRONTEND_REPO_WC}:latest"
        scannerHome             = tool "${SonarQubeScanner}";
        built                   = false
        environment             = "dev"
        microservice            = "frontend"
        ART_REPO_NAME           = credentials("WC_ART_REPO")
        ART_REPO_LOGIN          = credentials("WC_ARTIFACTORY_LOGIN")
        ART_REPO_LOC            = "${ART_REPO_NAME}/docker/${microservice}-api"

    }

    agent any
    stages {

        // stage ('scan') {
        //     steps {
        //         withSonarQubeEnv('sonarqube-WC'){
        //         sh "${scannerHome}/bin/sonar-scanner -D'sonar.projectKey=WC-frontend-microservice'"
        //         }
        //         timeout(time: 5, unit: 'MINUTES') {
        //             sleep(10)
        //             waitForQualityGate abortPipeline: true
        //         }
        //     }
        // }

        stage('build') {
            steps {
                script {
                    image = docker.build image_label
                }
            }
            post {
                success {
                    script {
                        built = true
                    }
                }
            }
        }
        stage('push to ECR') {
            steps {
                script {
                    sh "echo $git_commit_hash"
                    sh 'aws ecr get-login-password --region ${REGION_WC} | docker login --username AWS --password-stdin ${ORG_ACCOUNT_NUM}.dkr.ecr.${REGION_WC}.amazonaws.com'

                    sh "docker tag ${image_label} ${repository}:${git_commit_hash}"
                    sh "docker tag ${image_label} ${repository}:latest"
                    sh "docker push ${repository}:${git_commit_hash}"
                    sh "docker push ${repository}:latest"   
                }
            }
        }
        // stage('push to Jfrog Artifactory') {
        //     steps {
        //         echo 'logging in via docker login'
        //         sh "echo ${ART_REPO_LOGIN_PSW} | docker login ${ART_REPO_NAME} --username ${ART_REPO_LOGIN_USR} --password-stdin"
        //         sh "docker tag ${image_label}:latest ${ART_REPO_LOC}:latest"
        //         sh "docker tag ${image_label}:latest ${ART_REPO_LOC}:${git_commit_hash}"

        //         sh "docker push ${ART_REPO_LOC}:latest"
        //         sh "docker push ${ART_REPO_LOC}:${git_commit_hash}"
        //     }
        // }
        stage('Update EKS via Ansible Tower'){
            options {
                timeout(time: 60, unit: 'SECONDS') 
            }
            steps{
                catchError(buildResult: 'SUCCESS', stageResult: 'ABORTED') { 
                    script {
                        try {
                            results=ansibleTower(
                                towerServer: 'Tower 1',
                                jobTemplate: "EKS-update-$microservice-$environment",
                                extraVars: '''
                                CLUSTER_NAME: "$CLUSTER_NAME_WC"
                                REGION: "$REGION_WC"
                                ''',
                                verbose: true)
                        }
                        catch (Throwable e){
                            currentBuild.result = "SUCCESS"
                            echo 'Ansible Tower update skipped. Ansible Tower may not be running or configured correctly'
                        }
                    }
                }
            }
        }
        stage("Update ECS via ecs-cli"){
            steps {
                build job: 'ECS Docker Compose Pipeline Up', parameters: [
                string(name: 'action', value: 'update'),
                string(name: 'container', value: 'frontend')
                ]
            }
        }
    }
    post {
        cleanup {
            script {
                if(built) {
                    sh "docker rmi ${repository}:${git_commit_hash}"
                    sh "docker rmi ${repository}:latest"
                    // sh "docker rmi ${ART_REPO_LOC}:latest"
                    // sh "docker rmi ${ART_REPO_LOC}:${git_commit_hash}"
                    sh "docker rmi ${image_label}"                
                    }
            }
        }
    }
}