pipeline {
    
    agent any
    
    stages {
        
        stage("Clear directory") {
            steps {
                script {
                    sh 'rm -rf ${WORKSPACE}/*'
                }
            }
        }
        
        stage('Clone docker files') {
            steps {
                dir("${WORKSPACE}"){
                    checkout([
                        $class: 'GitSCM',
                        branches: [[name: 'master']],
                        userRemoteConfigs: [[
                            credentialsId: 'b562eea5-2921-42ee-8ee1-0fa3b8750da6',
                            url: 'git@github.com:am42saturday/final_project_mail_devops.git']]
                    ])
                }
            }
        }
        
        stage('Run and configure myapp via docker-compose') {
            steps {
                step([
                    $class: 'DockerComposeBuilder', 
                    dockerComposeFile: 'docker-compose.yml', 
                    option: [$class: 'StartAllServices'], 
                    useCustomDockerComposeFile: true
                ])
            }
        }
        
        stage('Run tests') {
            steps {
                def run_tests_command = 'cd /home/mary/Download/final_project_tests && python3 -m pytest'
                
                if("${MARK_TESTS}" != 'all'){
                    run_tests_command += " -m ${MARK_TESTS}"
                }
                
                sh (run_tests_command)                
            }
        }
        
        stage('Stop myapp') {
            steps {
                step([
                    $class: 'DockerComposeBuilder',
                    dockerComposeFile: 'docker-compose.yml',
                    option: [$class: 'StopAllServices'],
                    useCustomDockerComposeFile: true
                ])
            }
        }
    }
    
    post {
        always{
            dir(' /home/mary/Download/final_project_tests'){
                allure 
                includeProperties: false,
                jdk: '',
                results: [[path: 'report']]
            }
        }
    }
} 
