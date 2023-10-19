#!/usr/bin/env python

import dataclasses
import json
import os
import sys
import time
from urllib.parse import urlparse, urlunsplit

import jenkins  # https://python-jenkins.readthedocs.io/en/latest/index.html


@dataclasses.dataclass
class Jenkins:
    QUIET_PERIOD = 5
    EXPECTED_BUILD_RESULT = "SUCCESS"

    jenkins_token: str
    jenkins_user: str

    job_url: str
    job_params: str = "{}"

    _short_job_name: str = dataclasses.field(init=False)
    _jenkins_url: str = dataclasses.field(init=False)

    def __post_init__(self):
        u = urlparse(self.job_url)

        self._short_job_name = "".join(u.path.split("job/"))[1:]

        self._jenkins_url = urlunsplit((u.scheme, u.netloc, "", "", ""))

    def _j(self):
        return jenkins.Jenkins(self._jenkins_url, self.jenkins_user, self.jenkins_token)

    def print_auth(self):
        user_id = self._j().get_whoami()["id"]

        print(f"Authenticated with {self._jenkins_url} as {user_id}")
        print()

    def queue_job(self):
        return self._j().build_job(
            self._short_job_name,
            parameters=json.loads(self.job_params),
            token=self.jenkins_token,
        )

    def get_run_number(self, queue_id):
        # `executable` shows up when the build has started
        # https://python-jenkins.readthedocs.io/en/latest/api.html?highlight=build_job#jenkins.Jenkins.get_queue_item
        while "executable" not in (q_item := self._j().get_queue_item(queue_id)):
            # "The returned dict will have a “why” key if the queued item is still waiting for an executor."
            print(f"Waiting for {q_item['task']['url']} because: {q_item['why']}")
            print()

            time.sleep(self.QUIET_PERIOD)

        return q_item["executable"]["number"]

    def wait_for_build_to_finish(self, number) -> dict:
        JOB_POLLING_RATE = 30

        # `building` is true until all stages are done (including `post`)
        while (
            build_info := self._j().get_build_info(
                name=self._short_job_name, number=number
            )
        ).get("building"):
            print(f"{build_info['fullDisplayName']} is running at {build_info['url']}")
            print()

            time.sleep(JOB_POLLING_RATE)

        return build_info


# https://docs.github.com/en/actions/using-workflows/workflow-commands-for-github-actions#environment-files
def set_gh_env_file(file: str, msg: str):
    try:
        with open(os.environ[file], "a") as fh:
            print(msg, file=fh)
    except KeyError:
        print(f"Failed to append {msg} to ${file}")
        print()


if __name__ == "__main__":
    token = sys.argv[2]
    print(f"::add-mask::{token}")

    j = Jenkins(
        job_url=sys.argv[1],
        jenkins_token=sys.argv[2],
        jenkins_user=sys.argv[3],
        job_params=sys.argv[4],
    )

    print()

    # print(j)
    # print()

    j.print_auth()

    q_id = j.queue_job()
    print(f"In queue for {j.job_url} with ID {q_id}")
    print()

    print(f"Waiting {j.QUIET_PERIOD} seconds until Jenkins' quiet period has ended.")
    print()
    time.sleep(j.QUIET_PERIOD)

    run_number = j.get_run_number(q_id)

    build_result = j.wait_for_build_to_finish(run_number)["result"]

    set_gh_env_file("GITHUB_OUTPUT", f"build_result={build_result}")
    set_gh_env_file("GITHUB_STEP_SUMMARY", build_result)

    if build_result != j.EXPECTED_BUILD_RESULT:
        exit(1)
