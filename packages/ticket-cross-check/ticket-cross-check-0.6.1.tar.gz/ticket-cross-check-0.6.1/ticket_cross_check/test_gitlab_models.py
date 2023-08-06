from ticket_cross_check.gitlab_models import GitlabIssue, References


def test_convert_issue():
    """convert a single issue from gitlab - this is a marhalling check"""

    from_gitlab_api = [{'_links': {'award_emoji': 'https://gitlab.com/api/v4/projects/38031020/issues/1/award_emoji',
                                   'closed_as_duplicate_of': None,
                                   'notes': 'https://gitlab.com/api/v4/projects/38031020/issues/1/notes',
                                   'project': 'https://gitlab.com/api/v4/projects/38031020',
                                   'self': 'https://gitlab.com/api/v4/projects/38031020/issues/1'},
                        'assignee': {
                            'avatar_url': 'https://gitlab.com/uploads/-/system/user/avatar/10605926/avatar.png',
                            'id': 10605926,
                            'name': 'Christoph Becker',
                            'state': 'active',
                            'username': 'christoph.becker',
                            'web_url': 'https://gitlab.com/christoph.becker'},
                        'assignees': [
                            {'avatar_url': 'https://gitlab.com/uploads/-/system/user/avatar/10605926/avatar.png',
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
                        'created_at': '2022-07-28T09:10:30.673Z',
                        'description': 'Retrieve all gitlab issues of a project via gitlab API using '
                                       'a personal token\n'
                                       '\n'
                                       '## Requirements\n'
                                       '- accept personal token as input\n'
                                       '- get all issues as json',
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
                        'state': 'opened',
                        'task_completion_status': {'completed_count': 0, 'count': 0},
                        'time_stats': {'human_time_estimate': None,
                                       'human_total_time_spent': None,
                                       'time_estimate': 0,
                                       'total_time_spent': 0},
                        'title': 'get issues from gitlab via api and personal token',
                        'type': 'ISSUE',
                        'updated_at': '2022-07-28T11:36:43.147Z',
                        'upvotes': 0,
                        'user_notes_count': 0,
                        'web_url': 'https://gitlab.com/exb/engineering/ticket-cross-check/-/issues/1',
                        'weight': None}]
    gi = GitlabIssue(**from_gitlab_api[0])
    assert 1 == gi.iid
    assert 112351387 == gi.id
    assert 'get issues from gitlab via api and personal token' == gi.title
    assert 'opened' == gi.state
    assert [] == gi.labels
    assert References(short='#1', full='exb/engineering/ticket-cross-check#1') == gi.references


def test_references():
    r = References(short='#1', full='exb/engineering/ticket-cross-check#1')
    assert 'exb/engineering/ticket-cross-check' == r.get_project_url()
