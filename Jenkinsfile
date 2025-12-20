pipeline {
  agent {
    kubernetes {
      yaml '''
apiVersion: v1
kind: Pod
spec:
  containers:

  - name: dind
    image: docker:28-dind
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

  volumes:
    - name: docker-graph-storage
      emptyDir: {}

    - name: kubeconfig-secret
      secret:
        secretName: kubeconfig-secret
'''
    }
  }

  environment {
    IMAGE_NAME = "ai-health-assistant"
    IMAGE_TAG  = "v1"
    REGISTRY   = "nexus-service-for-docker-hosted-registry.nexus.svc.cluster.local:8085"
    REPO_PATH = "2401031"

    K8S_NAMESPACE = "2401031"

    SONAR_PROJECT_KEY = "2401031_AI_Health_Assistant"
    SONAR_HOST_URL    = "http://my-sonarqube-sonarqube.sonarqube.svc.cluster.local:9000"
    SONAR_LOGIN       = credentials('sqp_35292295fac737f6f82bb734ad4957822aaa4026')   // 🔐 create this in Jenkins
  }

  stages {

    stage('Checkout Code') {
      steps {
        checkout scm
      }
    }

    stage('Build Docker Image') {
      steps {
        container('dind') {
          sh '''
            echo "Waiting for Docker daemon..."
            for i in $(seq 1 30); do
              docker info && break
              sleep 2
            done

            docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .
          '''
        }
      }
    }

    stage('SonarQube Analysis') {
      steps {
        container('sonar-scanner') {
          sh '''
            sonar-scanner \
              -Dsonar.projectKey=${SONAR_PROJECT_KEY} \
              -Dsonar.sources=. \
              -Dsonar.host.url=${SONAR_HOST_URL} \
              -Dsonar.login=${SONAR_LOGIN}
          '''
        }
      }
    }

    stage('Login to Nexus') {
      steps {
        container('dind') {
          sh '''
            docker login ${REGISTRY} -u admin -p Changeme@2025
          '''
        }
      }
    }

    stage('Push Image to Nexus') {
      steps {
        container('dind') {
          sh '''
            docker tag ${IMAGE_NAME}:${IMAGE_TAG} \
              ${REGISTRY}/${REPO_PATH}/${IMAGE_NAME}:${IMAGE_TAG}

            docker push ${REGISTRY}/${REPO_PATH}/${IMAGE_NAME}:${IMAGE_TAG}
          '''
        }
      }
    }

    stage('Deploy to Kubernetes') {
      steps {
        container('kubectl') {
          sh '''
            kubectl apply -f k8s/deployment.yaml -n ${K8S_NAMESPACE}
            kubectl apply -f k8s/service.yaml -n ${K8S_NAMESPACE}
          '''
        }
      }
    }

    stage('Kubernetes Debug (IMPORTANT)') {
      steps {
        container('kubectl') {
          sh '''
            echo "=== Pods ==="
            kubectl get pods -n ${K8S_NAMESPACE}

            echo "=== Describe Pods ==="
            kubectl describe pods -n ${K8S_NAMESPACE} || true

            echo "=== Services ==="
            kubectl get svc -n ${K8S_NAMESPACE}
          '''
        }
      }
    }
  }

  post {
    success {
      echo "✅ Pipeline completed successfully"
    }
    failure {
      echo "❌ Pipeline failed — check logs above"
    }
  }
}
