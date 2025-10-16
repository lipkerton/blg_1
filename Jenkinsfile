pipeline {
    agent any
    stages {
        stage('hello') {
            steps {
	    	echo 'hello world!'
            }
        }
    }
}


def echo_begin_stage() {
    last = env.STAGE_NAME
    echo "---------------------{$last}---------------------"
}
