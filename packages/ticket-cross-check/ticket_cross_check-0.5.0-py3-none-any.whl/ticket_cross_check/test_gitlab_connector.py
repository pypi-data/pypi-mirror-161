import os

import pytest

from ticket_cross_check.gitlab_connector import GitlabConnector
from ticket_cross_check.gitlab_models import GitlabIssue


def need_token(func):
    @pytest.mark.skipif(os.getenv('PRIVATE_TOKEN') is None, reason="Need gitlab private token")
    def myfunc(*args, **kwargs):
        return func(*args, **kwargs)

    return myfunc


@need_token
def test_init_from_env():
    gc = GitlabConnector(personal_api_token=os.getenv('PRIVATE_TOKEN'), project_id=os.getenv('PROJECT_ID'))
    assert isinstance(gc, GitlabConnector)


@need_token
def test_factory():
    gc = GitlabConnector.factory()
    assert isinstance(gc, GitlabConnector)


@need_token
def test_get_issues():
    gc = GitlabConnector.factory()
    result = gc.get_issues()
    assert result
    assert isinstance(result, set)
    assert isinstance(result.pop(), GitlabIssue)
