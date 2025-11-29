pipeline {

    agent {
        kubernetes {
            yaml '''
apiVersion: v1
kind: Pod
spec:
  containers:

    - name: sonar-scanner
      image: sonarsource/sonar-scanner-cli
      command: ["sleep"]
      args: ["99d"]
      tty: true

    - name: kubectl
      image: bitnami/kubectl:latest
      command: ["sleep"]
      args: ["99d"]
      tty: true
      securityContext:
        runAsUser: 0
        readOnlyRootFilesystem: false
      env:
        - name: KUBECONFIG
          value: /kube/config
      volumeMounts:
        - name: kubeconfig-secret
          mountPath: /kube/config
          subPath: kubeconfig

    - name: dind
      image: docker:dind
      securityContext:
        privileged: true
      env:
        - name: DOCKER_TLS_CERTDIR
          value: ""
      command:
        - dockerd-entrypoint.sh
      args:
        - "--storage-driver=overlay2"
        - "--insecure-registry=nexus-service-for-docker-hosted-registry.nexus.svc.cluster.local:8085"
      volumeMounts:
        - name: docker-graph-storage
          mountPath: /var/lib/docker
        - name: dind-sock
          mountPath: /var/run

  volumes:
    - name: kubeconfig-secret
      secret:
        secretName: kubeconfig-secret

    - name: docker-graph-storage
      emptyDir: {}

    - name: dind-sock
      emptyDir: {}
'''
        }
    }


    environment {
        REGISTRY        = "nexus-service-for-docker-hosted-registry.nexus.svc.cluster.local:8085"
        REPO_PATH       = "2401031"
        IMAGE_NAME      = "ai-health-assistant"
        IMAGE_TAG       = "v1"

        K8S_NAMESPACE   = "2401031"

        SONAR_PROJECT_KEY = "2401031_AI-Health-Assistant"
        SONAR_HOST_URL    = "http://my-sonarqube-sonarqube.sonarqube.svc.cluster.local:9000"
        SONAR_LOGIN       = "sqp_b4150b4d3c8363c7f1daa109bf504c95d5681bdc"
    }

    stages {


        /* -----------------------------------------
           BUILD DOCKER IMAGE
        ------------------------------------------*/
        stage('Build Docker Image') {
            steps {
                container('dind') {
                    sh '''
                        echo "=== Waiting for Docker daemon ==="
                        for i in $(seq 1 30); do
                          if docker info >/dev/null 2>&1; then
                            echo "Docker is READY!"
                            break
                          fi
                          echo "Docker not ready... $i/30"
                          sleep 2
                        done

                        echo "=== Building AI Health Assistant image ==="
                        docker build -t ${IMAGE_NAME}:latest .
                    '''
                }
            }
        }


        /* -----------------------------------------
           SONARQUBE ANALYSIS
        ------------------------------------------*/
        stage('SonarQube Analysis') {
            steps {
                container('sonar-scanner') {
                    sh '''
                        echo "=== Running SonarQube Scan ==="
                        sonar-scanner \
                          -Dsonar.projectKey=${SONAR_PROJECT_KEY} \
                          -Dsonar.sources=. \
                          -Dsonar.host.url=${SONAR_HOST_URL} \
                          -Dsonar.login=${SONAR_LOGIN}
                    '''
                }
            }
        }


        /* -----------------------------------------
           LOGIN TO NEXUS
        ------------------------------------------*/
        stage('Login to Nexus Registry') {
            steps {
                container('dind') {
                    sh '''
                        docker login ${REGISTRY} -u admin -p Changeme@2025
                    '''
                }
            }
        }


        /* -----------------------------------------
           PUSH DOCKER IMAGE
        ------------------------------------------*/
        stage('Push Docker Image') {
            steps {
                container('dind') {
                    sh '''
                        docker tag ${IMAGE_NAME}:latest ${REGISTRY}/${REPO_PATH}/${IMAGE_NAME}:${IMAGE_TAG}
                        docker push ${REGISTRY}/${REPO_PATH}/${IMAGE_NAME}:${IMAGE_TAG}
                    '''
                }
            }
        }


        /* -----------------------------------------
           NEW STAGE: CREATE NAMESPACE
        ------------------------------------------*/
        stage('Create Namespace') {
            steps {
                container('kubectl') {
                    sh '''
                        echo "=== Creating Namespace ${K8S_NAMESPACE} if not exists ==="
                        kubectl get namespace ${K8S_NAMESPACE} || kubectl create namespace ${K8S_NAMESPACE}
                    '''
                }
            }
        }


        /* -----------------------------------------
           DEPLOY TO KUBERNETES
        ------------------------------------------*/
        stage('Deploy to Kubernetes') {
            steps {
                container('kubectl') {
                    sh '''
                        set -x

                        echo "=== Deploying to Kubernetes ==="
                        kubectl apply -f k8s/deployment.yaml -n ${K8S_NAMESPACE}
                        kubectl apply -f k8s/service.yaml -n ${K8S_NAMESPACE}

                        kubectl get all -n ${K8S_NAMESPACE}

                        echo "=== Waiting for deployment rollout ==="
                        kubectl rollout status deployment/ai-health-assistant-deployment -n ${K8S_NAMESPACE}
                    '''
                }
            }
        }


        /* -----------------------------------------
           DEBUG PODS
        ------------------------------------------*/
        stage('Debug Pods') {
            steps {
                container('kubectl') {
                    sh '''
                        echo "=== POD LIST ==="
                        kubectl get pods -n ${K8S_NAMESPACE}

                        echo "=== POD DETAILS ==="
                        kubectl describe pods -n ${K8S_NAMESPACE} | head -n 200 || true
                    '''
                }
            }
        }

    }
}
