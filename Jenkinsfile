pipeline {
    agent any
    stages {
        stage('hello') {
            steps {
	    	echo_begin_stage()
	    	echo 'hello world!'
		echo "Building ${env.JOB_NAME}"
            }
        }
    }
}


def echo_begin_stage() {
    last = env.STAGE_NAME
    echo "---------------------{$last}---------------------"
}
