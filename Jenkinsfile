pipeline {
    agent {
        label "debian"
    }
    stages {
        stage("compose up") {
            steps {
                int timer = 60
                timeout(time: timer, unit: "MINUTES") {
                    sh """#!/bin/bash
                        docker compose up -d --build
                    """
                }
            }
        }
        stage("migrations") {
            steps {
                int timer = 60
                timeout(time: timer, unit: "MINUTES") {
                    sh """#!/bin/bash
                        docker exec blog-blg_1-1 alembic upgrade head
                    """
                }
            }
        }
        stage("tests") {
            steps {
                int timer = 60
                timeout(time: timer, unit: "MINUTES") {
                    sh """#!/bin/bash
                        docker exec blog-blog_1-1 pytest py_tests/
                    """
                }
            }
        }
        stage("compose down") {
            steps {
                int timer = 60
                timeout(time: timer, unit: "MINUTES") {
                    sh """#!/bin/bash
                        docker compose down
                    """
                }
            }
        }
    }
}
