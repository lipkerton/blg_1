pipeline {
    agent any
    stages {
        stage('hello') {
	    echo_begin_stage()
            steps {
	    	echo 'hello world!'
            }
        }
	echo "Building ${env.JOB_NAME}"
    }
}


def echo_begin_stage() {
    last = env.STAGE_NAME
    echo "---------------------{$last}---------------------"
}
