pipeline {
    agent any

    environment {
        IMAGE_NAME    = "movie-recommender"
        TAG           = "latest"
        DOCKER_REPO   = "narlarushikesh/movie-recommender"
        TERRAFORM_DIR = "terraform"
        ANSIBLE_DIR   = "ansible"
    }

    stages {

        /* ------------------------------------------------------
           1. Clone Repository
        ------------------------------------------------------ */
        stage("Clone Code") {
            steps {
                echo "Cloning GitHub repository"
                git url: "https://github.com/NarlaRushikesh/Movie-Recommendation-System.git", branch: "master"
            }
        }

        /* ------------------------------------------------------
           2. Terraform: Create Azure VMs
        ------------------------------------------------------ */
        stage("Terraform Apply - Create VM Infra") {
            steps {
                echo "Provisioning Azure VMs using Terraform"
                dir("${TERRAFORM_DIR}") {
                    bat """
                        terraform init
                        terraform validate
                        terraform plan -out=tfplan
                        terraform apply -auto-approve
                    """
                }
            }
        }

        /* ------------------------------------------------------
           3. Fetch VM IPs From Terraform Outputs
        ------------------------------------------------------ */
        stage("Fetch VM Public IPs from Terraform") {
            steps {
                script {
                    echo "Fetching VM public IPs..."

                    VM1_IP = sh(
                        script: "cd terraform && terraform output -raw vm1_public_ip",
                        returnStdout: true
                    ).trim()

                    VM2_IP = sh(
                        script: "cd terraform && terraform output -raw vm2_public_ip",
                        returnStdout: true
                    ).trim()

                    echo "VM1 IP: ${VM1_IP}"
                    echo "VM2 IP: ${VM2_IP}"
                }
            }
        }

        /* ------------------------------------------------------
           4. Build Docker Image
        ------------------------------------------------------ */
        stage("Build Docker Image") {
            steps {
                echo "Building Docker Image"
                bat "docker build -t %IMAGE_NAME%:%TAG% ."
            }
        }

        /* ------------------------------------------------------
           5. Push Docker Image to Docker Hub
        ------------------------------------------------------ */
        stage("Push to Docker Hub") {
            steps {
                echo "Pushing Docker Image to Docker Hub"
                withCredentials([
                    usernamePassword(
                        credentialsId: "docker-hub-credentials",
                        usernameVariable: "docker_user",
                        passwordVariable: "docker_pass"
                    )
                ]) {
                    bat """
                        docker login -u %docker_user% -p %docker_pass%
                        docker tag %IMAGE_NAME%:%TAG% %DOCKER_REPO%:%TAG%
                        docker push %DOCKER_REPO%:%TAG%
                    """
                }
            }
        }

        /* ------------------------------------------------------
           6. Ansible Deployment to Azure VMs
        ------------------------------------------------------ */
        stage("Deploy App using Ansible") {
            steps {
                echo "Deploying app on Azure VMs via Ansible"

                sh """
                    cd ${ANSIBLE_DIR}
                    echo "[azure_vms]" > hosts
                    echo "vm1 ansible_host=${VM1_IP} ansible_user=azureuser ansible_ssh_private_key_file=~/.ssh/id_rsa" >> hosts
                    echo "vm2 ansible_host=${VM2_IP} ansible_user=azureuser ansible_ssh_private_key_file=~/.ssh/id_rsa" >> hosts

                    ansible-playbook -i hosts deploy.yaml
                """
            }
        }

        /* ------------------------------------------------------
           7. Ansible: Configure NRPE For Nagios Monitoring
        ------------------------------------------------------ */
        stage("Setup Nagios NRPE on VMs") {
            steps {
                echo "Configuring NRPE & Nagios plugins on VMs"

                sh """
                    cd ${ANSIBLE_DIR}
                    ansible-playbook -i hosts setup_nagios.yaml
                """
            }
        }

        /* ------------------------------------------------------
           8. Monitoring: Nagios NRPE Check via SSH
        ------------------------------------------------------ */
        stage("Nagios Monitoring Check") {
            steps {
                echo "Running NRPE health check via Nagios Server"

                sshagent(['nagios-ssh']) {
                    sh """
                        ssh -o StrictHostKeyChecking=no nagios@${NAGIOS_SERVER} \
                        "/usr/local/nagios/libexec/check_nrpe -H ${VM1_IP} -c check_http"
                    """
                }
            }
        }

    } // end stages

    post {
        always {
            echo "🎬 Pipeline completed."
        }
        failure {
            echo "❌ Pipeline failed. Check logs!"
        }
    }
}



