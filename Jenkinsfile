// pipeline {
//   agent {
//     kubernetes {
//       yaml '''
// apiVersion: v1
// kind: Pod
// spec:
//   containers:

//   - name: dind
//     image: docker:28-dind
//     securityContext:
//       privileged: true
//     env:
//       - name: DOCKER_TLS_CERTDIR
//         value: ""
//     command:
//       - dockerd-entrypoint.sh
//     args:
//       - "--storage-driver=overlay2"
//       - "--insecure-registry=nexus-service-for-docker-hosted-registry.nexus.svc.cluster.local:8085"
//     volumeMounts:
//       - name: docker-graph-storage
//         mountPath: /var/lib/docker

//   - name: sonar-scanner
//     image: sonarsource/sonar-scanner-cli
//     command: ["sleep"]
//     args: ["99d"]
//     tty: true

//   - name: kubectl
//     image: bitnami/kubectl:latest
//     command: ["sleep"]
//     args: ["99d"]
//     tty: true
//     env:
//       - name: KUBECONFIG
//         value: /kube/config
//     volumeMounts:
//       - name: kubeconfig-secret
//         mountPath: /kube/config
//         subPath: kubeconfig

//   volumes:
//     - name: docker-graph-storage
//       emptyDir: {}

//     - name: kubeconfig-secret
//       secret:
//         secretName: kubeconfig-secret
// '''
//     }
//   }

//   environment {
//     IMAGE_NAME = "ai-health-assistant"
//     IMAGE_TAG  = "v1"
//     REGISTRY   = "nexus-service-for-docker-hosted-registry.nexus.svc.cluster.local:8085"
//     REPO_PATH = "2401031"

//     K8S_NAMESPACE = "2401031"

//     SONAR_PROJECT_KEY = "2401031_HealthAssistant"
//     SONAR_HOST_URL    = "http://my-sonarqube-sonarqube.sonarqube.svc.cluster.local:9000"
//     SONAR_LOGIN       = credentials('sonar-token-2401031')   // 🔐 create this in Jenkins
//   }

//   stages {

//     stage('Checkout Code') {
//       steps {
//         checkout scm
//       }
//     }

//     stage('Build Docker Image') {
//       steps {
//         container('dind') {
//           sh '''
//             echo "Waiting for Docker daemon..."
//             for i in $(seq 1 30); do
//               docker info && break
//               sleep 2
//             done

//             docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .
//           '''
//         }
//       }
//     }

//     stage('SonarQube Analysis') {
//       steps {
//         container('sonar-scanner') {
//           sh '''
//             sonar-scanner \
//               -Dsonar.projectKey=${SONAR_PROJECT_KEY} \
//               -Dsonar.sources=. \
//               -Dsonar.host.url=${SONAR_HOST_URL} \
//               -Dsonar.login=${SONAR_LOGIN}
//           '''
//         }
//       }
//     }

//     stage('Login to Nexus') {
//       steps {
//         container('dind') {
//           sh '''
//             docker login ${REGISTRY} -u admin -p Changeme@2025
//           '''
//         }
//       }
//     }

//     stage('Push Image to Nexus') {
//       steps {
//         container('dind') {
//           sh '''
//             docker tag ${IMAGE_NAME}:${IMAGE_TAG} \
//               ${REGISTRY}/${REPO_PATH}/${IMAGE_NAME}:${IMAGE_TAG}

//             docker push ${REGISTRY}/${REPO_PATH}/${IMAGE_NAME}:${IMAGE_TAG}
//           '''
//         }
//       }
//     }

//     stage('Deploy to Kubernetes') {
//       steps {
//         container('kubectl') {
//           sh '''
//             kubectl apply -f k8s/deployment.yaml -n 2401031
//             kubectl apply -f k8s/service.yaml -n 2401031
//             kubectl apply -f k8s/ingress.yaml -n 2401031
//           '''
//         }
//       }
//     }

//     stage('Kubernetes Debug (IMPORTANT)') {
//       steps {
//         container('kubectl') {
//           sh '''
//             echo "=== Pods ==="
//             kubectl get pods -n 2401031

//             echo "=== Describe Pods ==="
//             kubectl describe pods -n 2401031 || true

//             echo "=== Services ==="
//             kubectl get svc -n 2401031
//           '''
//         }
//       }
//     }
//   }

//   post {
//     success {
//       echo "✅ Pipeline completed successfully"
//     }
//     failure {
//       echo "❌ Pipeline failed — check logs above"
//     }
//   }
// }

properties([
  durabilityHint('PERFORMANCE_OPTIMIZED')
])

pipeline {

  agent {
    kubernetes {
      yaml """
apiVersion: v1
kind: Pod
spec:
  containers:

  - name: docker
    image: docker:28-dind
    securityContext:
      privileged: true
    command: ["dockerd-entrypoint.sh"]
    args:
      - "--host=tcp://0.0.0.0:2375"
      - "--storage-driver=overlay2"
      - "--insecure-registry=nexus-service-for-docker-hosted-registry.nexus.svc.cluster.local:8085"
    env:
      - name: DOCKER_TLS_CERTDIR
        value: ""
    volumeMounts:
      - name: docker-storage
        mountPath: /var/lib/docker
      - name: workspace-volume
        mountPath: /home/jenkins/agent

  - name: sonar-scanner
    image: sonarsource/sonar-scanner-cli
    command: ["cat"]
    tty: true
    volumeMounts:
      - name: workspace-volume
        mountPath: /home/jenkins/agent

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
      - name: workspace-volume
        mountPath: /home/jenkins/agent

  volumes:
    - name: docker-storage
      emptyDir: {}
    - name: workspace-volume
      emptyDir: {}
    - name: kubeconfig-secret
      secret:
        secretName: kubeconfig-secret
"""
    }
  }

  options {
    skipDefaultCheckout()
  }

  environment {
    IMAGE_NAME = "ai-health-assistant"
    IMAGE_TAG  = "v1"

    REGISTRY_HOST = "nexus-service-for-docker-hosted-registry.nexus.svc.cluster.local:8085"
    REGISTRY      = "${REGISTRY_HOST}/2401031"

    K8S_NAMESPACE = "2401031"

    SONAR_PROJECT_KEY = "2401031_HealthAssistant"
    SONAR_HOST_URL    = "http://my-sonarqube-sonarqube.sonarqube.svc.cluster.local:9000"

    // ✅ MUST EXIST IN JENKINS → Secret Text
    SONAR_TOKEN = credentials('sonar-token-2401031')
  }

  stages {

    stage('Checkout Code') {
      steps {
        sh '''
          rm -rf *
          git clone https://github.com/Piyush2k03/AI-Health-Assistant.git .
        '''
      }
    }

    stage('Build Docker Image') {
      steps {
        container('docker') {
          sh '''
            echo "⏳ Waiting for Docker..."
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
              -Dsonar.token=${SONAR_TOKEN}
          '''
        }
      }
    }

    stage('Login to Nexus') {
      steps {
        container('docker') {
          sh '''
            docker login ${REGISTRY_HOST} -u admin -p Changeme@2025
          '''
        }
      }
    }

    stage('Push Image to Nexus') {
      steps {
        container('docker') {
          sh '''
            docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}
            docker push ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}
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
            kubectl apply -f k8s/ingress.yaml -n ${K8S_NAMESPACE}

            kubectl rollout status deployment/ai-health-assistant-deployment -n ${K8S_NAMESPACE}
          '''
        }
      }
    }

    stage('Kubernetes Debug') {
      steps {
        container('kubectl') {
          sh '''
            kubectl get pods -n ${K8S_NAMESPACE}
            kubectl get svc  -n ${K8S_NAMESPACE}
          '''
        }
      }
    }
  }

  post {
    success {
      echo "✅ AI Health Assistant CI/CD Pipeline SUCCESS"
    }
    failure {
      echo "❌ Pipeline FAILED — check logs"
    }
    always {
      echo "🔄 Pipeline finished"
    }
  }
}

