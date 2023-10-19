all: build test

build: Dockerfile entrypoint.py
	docker build -t build-jenkins-job .

test: entrypoint.py
	docker run -it build-jenkins-job '${JOB_URL}' '${JENKINS_TOKEN}' '${JENKINS_USER}' '${JOB_PARAMS}'
