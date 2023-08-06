import os

from pydantic import BaseModel


class References(BaseModel):
    short: str
    full: str

    def get_project_url(self):
        return self.full.split('#')[0]


class GitlabIssue(BaseModel):
    id: int
    iid: int
    title: str
    state: str
    labels: list[str]
    references: References

    GITLAB_BASE_URL = os.getenv('GITLAB_BASE_URL', 'https://gitlab.com')

    def __hash__(self):
        """
        makes this object hashable
        :return:
        """
        return self.id

    def get_issue_link(self):
        """

        :return: https://gitlab.com/foo/group/project/-/issues/
        """
        prefix = self.references.get_project_url()
        return f"{self.GITLAB_BASE_URL}/{prefix}/-/issues/{self.iid}"
