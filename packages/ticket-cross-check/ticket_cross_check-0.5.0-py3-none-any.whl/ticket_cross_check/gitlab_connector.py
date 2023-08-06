import os
import sys
from typing import Any

import gitlab
import requests
from loguru import logger

from ticket_cross_check.gitlab_models import GitlabIssue


class GitlabConnector:
    gitlab_baseurl = "https://gitlab.com/api/"
    api_version = "v4"

    def __init__(self, personal_api_token: str, project_id: str):
        assert personal_api_token  # is needed
        assert project_id  # is needed
        self.__personal_api_token = personal_api_token  # protect the token internally
        self.project_id = project_id

        self.gitlab = gitlab.Gitlab(private_token=personal_api_token)

    @staticmethod
    def factory() -> "GitlabConnector":
        personal_api_token = os.environ['PRIVATE_TOKEN']
        project_id = os.getenv('PROJECT_ID')
        if not project_id:
            # if project is not defined, assume current project
            project_id = os.environ['CI_PROJECT_ID']
        return GitlabConnector(personal_api_token, project_id)

    def _get(self, url: str) -> Any:
        """
        Raw getter, retrieves and checks API responses
        Exits hard on 401
        Raises ImportError on type mismatch
        """
        if '?' in url:
            url = f'{url}&private_token={self.__personal_api_token}'
        else:
            url = f'{url}?private_token={self.__personal_api_token}'

        result = requests.get(self.get_project_url(url))
        json = result.json()
        if result.status_code == 401:
            logger.error('API TOKEN invalid. Got 401')
            sys.exit(1)
        if result.status_code == 404:
            logger.error(f'URL not found {url}')
            sys.exit(1)
        return json

    def get_project_url(self, postfix: str = "") -> str:
        return self.gitlab_baseurl + self.api_version + f"/projects/{self.project_id}{postfix}"

    def get_issues_raw(self) -> list[dict]:
        """Get raw (full json) issues from gitlab via API"""
        return self._get('/issues')

    def get_issues(self) -> set[GitlabIssue]:
        return self._convert_issues(self.get_issues_raw())

    @staticmethod
    def _convert_issues(issue_json: list[dict]) -> set[GitlabIssue]:
        result = set()
        for raw_req in issue_json:
            result.add(GitlabIssue(**raw_req))
        return result

    def get_project_info_raw(self) -> dict:
        """Get raw project info from API"""
        return self._get(f'/projects/{self.project_id}', dict)

    def get_project(self):  # -> gitlab.v4.objects.projects.Project:
        """Get GitlabProject info from API"""
        rpi = self.gitlab.projects.get(self.project_id)
        return rpi
