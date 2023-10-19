# Build jenkins job docker action

This action runs a Jenkins job at a given URL with optional parameters.

## Inputs

```
inputs:
  job_url:
    description: 'URL for the Jenkins job. i.e. http://jenkins.company.io/job/some-folder/job/test'
    required: true
  jenkins_token:
    description: 'Jekins API Token. 34 characters.'
    required: true
  jenkins_user:
    description: 'Your Jenkins User ID.'
    required: true
  job_params:
    description: 'JSON string of job parameters. i.e "{"foo": "bar", "baz": true, "qux": 3}" '
    required: false
    default: "{}"
```

## Outputs

```
outputs:
  build_result:
    description: 'Result of the Jenkins build; SUCCESS UNSTABLE FAILURE NOT_BUILT ABORTED'
```

###  `build_result`

- SUCCESS
- UNSTABLE
- FAILURE
- NOT_BUILT
- ABORTED

[source](https://github.com/jenkinsci/jenkins/blob/6c07309cb1467f44413c58452cf99c42cfcf84ff/core/src/main/java/hudson/model/Result.java#L51)

## example
```
  - uses: HoldenLucas/build-jenkins-job@v1
    id: build
    with:
      job_url: ${{ secrets.JENKINS_URL }}/job/some-folder/job/test
      jenkins_token: ${{ secrets.JENKINS_TOKEN }}
      jenkins_user: ${{ secrets.JENKINS_USER }}
      job_params: "{"foo": "bar", "baz": true, "qux": 3}"

  - run: echo "Result: ${{ steps.build.outputs.build_result }}"
```
