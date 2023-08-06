import os
from dataclasses import dataclass
from typing import Optional

from ticket_cross_check.gitlab_models import GitlabIssue

GITLAB_BASE_URL = os.getenv('GITLAB_BASE_URL', 'https://gitlab.com')


@dataclass
class IssueFileMatch:
    iid: int
    filename: str
    line_nr: int
    matched_issue: Optional[GitlabIssue]

    def get_issue_link(self):
        """

        :return: https://gitlab.com/exb/engineering/example-project/-/issues/
        """
        return self.matched_issue.get_issue_link()

    def get_deep_link(self, branch: str, baseLink: str = None):
        """
        returns
        the main project link is extracted from the issue
        and main as branch
        :param prefix:
        :param branch:
        :return: https://gitlab.com/exb/engineering/example-project/-/blob/main/metrics.py#L3
        """
        if not baseLink:
            prefix = self.matched_issue.references.get_project_url()
        else:
            prefix = baseLink
        return f"{GITLAB_BASE_URL}/{prefix}/-/blob/{branch}/{self.filename}#L{self.line_nr}"

    def __hash__(self):
        return self.iid * 10000 + self.line_nr
