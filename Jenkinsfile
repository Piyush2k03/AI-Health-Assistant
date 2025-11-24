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
      command: ["cat"]
      tty: true

    - name: kubectl
      image: bitnami/kubectl:latest
      command: ["cat"]
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
      args: ["--storage-driver=overlay2",
             "--insecure-registry=nexus-service-for-docker-hosted-registry.nexus.svc.cluster.local:8085"]
      securityContext:
        privileged: true
      env:
        - name: DOCKER_TLS_CERTDIR
          value: ""
  volumes:
    - name: kubeconfig-secret
      secret:
        secretName: kubeconfig-secret
'''
        }
    }

    environment {
        REGISTRY        = "nexus-service-for-docker-hosted-registry.nexus.svc.cluster.local:8085"
        REPO_PATH       = "2401031"                // 👈 change if your repo name is different
        IMAGE_NAME      = "ai-health-assistant"
        IMAGE_TAG       = "v1"

        K8S_NAMESPACE   = "2401031"

        SONAR_PROJECT_KEY = "2401031_AI-Health-Assistant"
        SONAR_HOST_URL    = "http://my-sonarqube-sonarqube.sonarqube.svc.cluster.local:9000"

        // 👇 put your real Sonar token here (the sqp_xxx from SonarQube)
        SONAR_LOGIN       = "sqp_b4150b4d3c8363c7f1daa109bf504c95d5681bdc"
    }

    stages {

        /* For Python/Streamlit we don't need npm build, so we skip that stage */

        stage('Build Docker Image') {
            steps {
                container('dind') {
                    sh '''
                        echo "=== Building Docker image for AI Health Assistant ==="
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
                        echo "=== Logging in to Nexus Docker registry ==="
                        docker login ${REGISTRY} -u admin -p Changeme@2025
                    '''
                }
            }
        }

        stage('Push Image to Nexus') {
            steps {
                container('dind') {
                    sh '''
                        echo "=== Tagging and pushing image to Nexus ==="
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
                        echo "=== Files in workspace ==="
                        ls -la
                        ls -la k8s

                        echo "=== Applying Kubernetes manifests ==="
                        kubectl apply -f k8s/deployment.yaml -n ${K8S_NAMESPACE}
                        kubectl apply -f k8s/service.yaml -n ${K8S_NAMESPACE}

                        echo "=== Checking resources in namespace ${K8S_NAMESPACE} ==="
                        kubectl get all -n ${K8S_NAMESPACE}

                        echo "=== Waiting for deployment rollout ==="
                        kubectl rollout status deployment/ai-health-assistant-deployment -n ${K8S_NAMESPACE}
                    '''
                }
            }
        }

        stage('Debug Pods') {
            steps {
                container('kubectl') {
                    sh '''
                        echo "[DEBUG] Listing Pods in ${K8S_NAMESPACE}..."
                        kubectl get pods -n ${K8S_NAMESPACE}

                        echo "[DEBUG] Describing first pods..."
                        kubectl describe pods -n ${K8S_NAMESPACE} | head -n 200 || true
                    '''
                }
            }
        }
    }
}
