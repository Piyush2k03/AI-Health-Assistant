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

        stage('Build Docker Image') {
            steps {
                container('dind') {
                    sh '''
                        echo "=== Building Docker image ==="
                        docker info
                        docker build -t ${IMAGE_NAME}:latest .
                    '''
                }
            }
        }

        stage('SonarQube Analysis') {
            steps {
                container('sonar-scanner') {
                    sh '''
                        echo "=== Running SonarQube Analysis ==="
                        sonar-scanner \
                          -Dsonar.projectKey=${SONAR_PROJECT_KEY} \
                          -Dsonar.sources=. \
                          -Dsonar.host.url=${SONAR_HOST_URL} \
                          -Dsonar.login=${SONAR_LOGIN}
                    '''
                }
            }
        }

        stage('Login to Nexus Registry') {
            steps {
                container('dind') {
                    sh '''
                        echo "=== Logging in to Nexus registry ==="
                        docker login ${REGISTRY} -u admin -p Changeme@2025
                    '''
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                container('dind') {
                    sh '''
                        echo "=== Tag & Push Docker Image ==="
                        docker tag ${IMAGE_NAME}:latest ${REGISTRY}/${REPO_PATH}/${IMAGE_NAME}:${IMAGE_TAG}
                        docker push ${REGISTRY}/${REPO_PATH}/${IMAGE_NAME}:${IMAGE_TAG}
                    '''
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                container('kubectl') {
                    sh '''
                        set -x

                        echo "=== Applying Deployment and Service ==="
                        kubectl apply -f k8s/deployment.yaml -n ${K8S_NAMESPACE}
                        kubectl apply -f k8s/service.yaml -n ${K8S_NAMESPACE}

                        echo "=== Checking Resources ==="
                        kubectl get all -n ${K8S_NAMESPACE}

                        echo "=== Waiting for Deployment Rollout ==="
                        kubectl rollout status deployment/ai-health-assistant-deployment -n ${K8S_NAMESPACE}
                    '''
                }
            }
        }

        stage('Debug Pods') {
            steps {
                container('kubectl') {
                    sh '''
                        echo "[DEBUG] Pods in namespace: ${K8S_NAMESPACE}"
                        kubectl get pods -n ${K8S_NAMESPACE}

                        echo "[DEBUG] Describe pods:"
                        kubectl describe pods -n ${K8S_NAMESPACE} | head -n 200 || true
                    '''
                }
            }
        }
    }
}
