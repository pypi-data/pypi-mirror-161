pipeline{
  agent any
  environment {
    https_proxy = "$proxy"
    http_proxy="$proxy"
  }

  options {
    gitLabConnection('gitlab')
  }

  stages{
    stage("Prepare the environment"){
      steps{
        sh '''
	   echo "gitlabActionType is " ${gitlabActionType}\n
           python3 -m venv venv;\
           source venv/bin/activate;\
           pip install --upgrade pip;\
           pip install wheel twine
           '''
      }
    }

    stage("build"){
      steps{
        sh """
           source venv/bin/activate;\
           python setup.py sdist bdist_wheel
           """
      }
    }

    stage("upload to pypi.org"){
      when {expression { gitlabActionType == 'TAG_PUSH'}}
      steps{
        echo "upload pypi.org only if this commit is tagged"
        withCredentials([usernamePassword(credentialsId: 'pypi.org', usernameVariable: 'PYPI_USER', passwordVariable: 'PYPI_PASSWD')]) {
          sh """
             source venv/bin/activate;\
             TWINE_PASSWORD=${PYPI_PASSWD} TWINE_USERNAME=${PYPI_USER} twine upload  dist/*
             """
        }
      }
    }
  }

  post {
    failure {
        updateGitlabCommitStatus name: 'build', state: 'failed'
    }

    success {
        updateGitlabCommitStatus name: 'build', state: 'success'
    }

    always("Clean up build files"){
      cleanWs()
    }
  }
}

