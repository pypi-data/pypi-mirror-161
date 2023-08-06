from pathlib import Path

import pytest

from ticket_cross_check.gitlab_connector import GitlabConnector
from ticket_cross_check.gitlab_models import GitlabIssue, References
from ticket_cross_check.issue_finder import scan_files
from ticket_cross_check.matcher import analyze_issues_vs_code, render, generate_base_matrix
from ticket_cross_check.models import IssueFileMatch
from ticket_cross_check.test_issue_finder import get_absolute_sample_dir

from_gitlab_api = [{'_links': {'award_emoji': 'https://gitlab.com/api/v4/projects/38031020/issues/2/award_emoji',
                               'closed_as_duplicate_of': None,
                               'notes': 'https://gitlab.com/api/v4/projects/38031020/issues/2/notes',
                               'project': 'https://gitlab.com/api/v4/projects/38031020',
                               'self': 'https://gitlab.com/api/v4/projects/38031020/issues/2'},
                    'assignee': {'avatar_url': 'https://gitlab.com/uploads/-/system/user/avatar/10605926/avatar.png',
                                 'id': 10605926,
                                 'name': 'Christoph Becker',
                                 'state': 'active',
                                 'username': 'christoph.becker',
                                 'web_url': 'https://gitlab.com/christoph.becker'},
                    'assignees': [{'avatar_url': 'https://gitlab.com/uploads/-/system/user/avatar/10605926/avatar.png',
                                   'id': 10605926,
                                   'name': 'Christoph Becker',
                                   'state': 'active',
                                   'username': 'christoph.becker',
                                   'web_url': 'https://gitlab.com/christoph.becker'}],
                    'author': {'avatar_url': 'https://gitlab.com/uploads/-/system/user/avatar/10605926/avatar.png',
                               'id': 10605926,
                               'name': 'Christoph Becker',
                               'state': 'active',
                               'username': 'christoph.becker',
                               'web_url': 'https://gitlab.com/christoph.becker'},
                    'blocking_issues_count': 0,
                    'closed_at': None,
                    'closed_by': None,
                    'confidential': False,
                    'created_at': '2022-07-28T13:20:34.987Z',
                    'description': '- Find all #[0-9]+ occurrances in text files and generate a '
                                   'list of them (issue; list of locations with '
                                   'full_path:line_nr)\n'
                                   '- match the found locations with issues\n'
                                   '- generate lists: \n'
                                   '  - Issues w/o file matches\n'
                                   '  - Issues w file matches\n'
                                   '  - Issues in files w/o issues (errors)',
                    'discussion_locked': None,
                    'downvotes': 0,
                    'due_date': None,
                    'epic': None,
                    'epic_iid': None,
                    'has_tasks': False,
                    'id': 112364275,
                    'iid': 2,
                    'issue_type': 'issue',
                    'iteration': None,
                    'labels': [],
                    'merge_requests_count': 1,
                    'milestone': None,
                    'moved_to_id': None,
                    'project_id': 38031020,
                    'references': {'full': 'exb/engineering/ticket-cross-check#2',
                                   'relative': '#2',
                                   'short': '#2'},
                    'service_desk_reply_to': None,
                    'severity': 'UNKNOWN',
                    'state': 'opened',
                    'task_completion_status': {'completed_count': 0, 'count': 0},
                    'time_stats': {'human_time_estimate': None,
                                   'human_total_time_spent': None,
                                   'time_estimate': 0,
                                   'total_time_spent': 0},
                    'title': 'Match found issues in code and documentation with list from gitlab',
                    'type': 'ISSUE',
                    'updated_at': '2022-07-28T13:20:34.987Z',
                    'upvotes': 0,
                    'user_notes_count': 0,
                    'web_url': 'https://gitlab.com/exb/engineering/ticket-cross-check/-/issues/2',
                    'weight': None},
                   {'_links': {'award_emoji': 'https://gitlab.com/api/v4/projects/38031020/issues/1/award_emoji',
                               'closed_as_duplicate_of': None,
                               'notes': 'https://gitlab.com/api/v4/projects/38031020/issues/1/notes',
                               'project': 'https://gitlab.com/api/v4/projects/38031020',
                               'self': 'https://gitlab.com/api/v4/projects/38031020/issues/1'},
                    'assignee': {'avatar_url': 'https://gitlab.com/uploads/-/system/user/avatar/10605926/avatar.png',
                                 'id': 10605926,
                                 'name': 'Christoph Becker',
                                 'state': 'active',
                                 'username': 'christoph.becker',
                                 'web_url': 'https://gitlab.com/christoph.becker'},
                    'assignees': [{'avatar_url': 'https://gitlab.com/uploads/-/system/user/avatar/10605926/avatar.png',
                                   'id': 10605926,
                                   'name': 'Christoph Becker',
                                   'state': 'active',
                                   'username': 'christoph.becker',
                                   'web_url': 'https://gitlab.com/christoph.becker'}],
                    'author': {'avatar_url': 'https://gitlab.com/uploads/-/system/user/avatar/10605926/avatar.png',
                               'id': 10605926,
                               'name': 'Christoph Becker',
                               'state': 'active',
                               'username': 'christoph.becker',
                               'web_url': 'https://gitlab.com/christoph.becker'},
                    'blocking_issues_count': 0,
                    'closed_at': '2022-07-28T13:16:42.402Z',
                    'closed_by': {'avatar_url': 'https://gitlab.com/uploads/-/system/user/avatar/10605926/avatar.png',
                                  'id': 10605926,
                                  'name': 'Christoph Becker',
                                  'state': 'active',
                                  'username': 'christoph.becker',
                                  'web_url': 'https://gitlab.com/christoph.becker'},
                    'confidential': False,
                    'created_at': '2022-07-28T09:10:30.673Z',
                    'description': 'Retrieve all gitlab issues of a project via gitlab API using '
                                   'a personal token\n'
                                   '\n'
                                   '## Requirements\n'
                                   '- accept personal token as input\n'
                                   '- get all issues as json\n'
                                   '- get all issues as struture / python object',
                    'discussion_locked': None,
                    'downvotes': 0,
                    'due_date': None,
                    'epic': None,
                    'epic_iid': None,
                    'has_tasks': False,
                    'id': 112351387,
                    'iid': 1,
                    'issue_type': 'issue',
                    'iteration': None,
                    'labels': [],
                    'merge_requests_count': 0,
                    'milestone': None,
                    'moved_to_id': None,
                    'project_id': 38031020,
                    'references': {'full': 'exb/engineering/ticket-cross-check#1',
                                   'relative': '#1',
                                   'short': '#1'},
                    'service_desk_reply_to': None,
                    'severity': 'UNKNOWN',
                    'state': 'closed',
                    'task_completion_status': {'completed_count': 0, 'count': 0},
                    'time_stats': {'human_time_estimate': None,
                                   'human_total_time_spent': None,
                                   'time_estimate': 0,
                                   'total_time_spent': 0},
                    'title': 'get issues from gitlab via api and personal token',
                    'type': 'ISSUE',
                    'updated_at': '2022-07-28T13:16:42.413Z',
                    'upvotes': 0,
                    'user_notes_count': 0,
                    'web_url': 'https://gitlab.com/exb/engineering/ticket-cross-check/-/issues/1',
                    'weight': None}]


def test_matcher():
    gitlab_issues = GitlabConnector._convert_issues(from_gitlab_api)
    file_issues = scan_files(get_absolute_sample_dir())
    problems, unsolved, solved = analyze_issues_vs_code(file_issues, gitlab_issues)
    assert problems
    assert isinstance(unsolved, set)
    assert solved


@pytest.fixture
def writepath():
    path = Path('allinone.json')
    path.unlink(missing_ok=True)
    return path


def test_render_empty():
    baselink = '/baselink/'
    solved: set[IssueFileMatch] = set()
    unsolved: set[GitlabIssue] = set()
    problems: list[IssueFileMatch] = []

    data = render(solved, unsolved, problems, baselink)

    assert [] == data


def test_render():
    baselink = '/baselink/'
    solved: set[IssueFileMatch] = {
        IssueFileMatch(iid=1, filename='file1.py', line_nr=111,
                       matched_issue=GitlabIssue(
                           id=1, iid=1234, title='title', state='open', labels=[],
                           references=References(short='#1', full='full/ref/1')))
    }
    unsolved: set[GitlabIssue] = {GitlabIssue(
        id=2, iid=2234, title='title', state='open', labels=[],
        references=References(short='#2', full='full/ref/2'))}
    problems: list[IssueFileMatch] = [
        IssueFileMatch(iid=3, filename='file3.py', line_nr=333, matched_issue=None)
    ]

    data = render(solved, unsolved, problems, baselink)

    assert 3 == len(data)
    assert 1 == data[0][0]  # first elem = id
    assert 'file1.py' in data[0][2]  # file link
    assert 111 == data[0][3]  # linenr
    assert 'solved' == data[0][4]  # state


def test_generate_base_matrix():
    matrix = generate_base_matrix(gitlab_issues=set(), dirs=[])
    assert {'_subdirs': []} == matrix

    matrix = generate_base_matrix(gitlab_issues=set(), dirs=['dir1', 'dir2'])
    assert {'_subdirs': ['dir1', 'dir2']} == matrix


def test_generate_base_matrix_with_issues():
    gli = GitlabIssue(
        id=12344, iid=1, title='title', state='open', labels=[],
        references=References(short='#1', full='full/ref/1'))
    glis = set()
    glis.add(gli)
    matrix = generate_base_matrix(gitlab_issues=glis, dirs=['dir1', 'dir2'])
    assert {
        '_subdirs': ['dir1', 'dir2'],
        gli.iid: {'counts': [0, 0], 'iid': gli.iid, 'issue': gli}
    } == matrix
