import json
from pathlib import Path

from loguru import logger

from ticket_cross_check.gitlab_models import GitlabIssue
from .models import IssueFileMatch


def _get_unmatched_issues_from_files(issues_in_files: dict[list[IssueFileMatch]], issues: set[GitlabIssue]) \
        -> list[IssueFileMatch]:
    unmatched = []
    iids = [int(issue.iid) for issue in issues]
    for iid in issues_in_files.keys():
        logger.trace(iid)
        if iid not in iids:
            logger.debug(issues_in_files[iid])
            unmatched += issues_in_files[iid]
    return unmatched


def _get_un_and_solved_issued(issues_in_files: dict[list[IssueFileMatch]], issues: set[GitlabIssue]) \
        -> tuple[set[GitlabIssue], set[IssueFileMatch]]:
    """

    :param issues_in_files:
    :param issues:
    :return: unsolved_issue set, solved_issue set
    """
    unsolved = set()
    solved = set()

    for issue in issues:
        if issue.iid not in issues_in_files:
            unsolved.add(issue)
        else:
            for iif in issues_in_files[issue.iid]:
                iif.matched_issue = issue
                solved.add(iif)
    return unsolved, solved


def analyze_issues_vs_code(issues_in_files: dict[list[IssueFileMatch]], issues: set[GitlabIssue]):
    # Unsolved Requirement: issues not in files
    # Problem: file-issues without real issues
    # Solved: issue in file(s)
    unsolved, solved = _get_un_and_solved_issued(issues_in_files, issues)
    problems = _get_unmatched_issues_from_files(issues_in_files, issues)
    return problems, unsolved, solved


def _write_json2file(path: Path, data: dict):
    with path.open(mode='w') as ofile:
        ofile.write(json.dumps(data, indent=2))


def render(
        solved: set[IssueFileMatch],
        unsolved: set[GitlabIssue],
        problems: list[IssueFileMatch],
        base_link: str,
        search_dir: str = ""
):
    data = []
    for ifm in solved:
        data.append([
            ifm.iid,
            f"<a href='{ifm.get_issue_link()}'>{ifm.matched_issue.title}</a>",
            f"<a href='{ifm.get_deep_link('main')}'>{ifm.filename}</a>",
            ifm.line_nr,
            "solved",
            search_dir
        ])

    status = "unsolved"
    for issue in unsolved:
        data.append([
            issue.iid,
            f"<a href='{issue.get_issue_link()}'>{issue.title}</a>",
            '',
            '',
            status,
            search_dir
        ])

    status = "problem"
    _id = "<span style='color: red'>%s</a>"
    for ifm in problems:
        data.append([
            _id % ifm.iid,
            '',
            f"<a href='{ifm.get_deep_link('main', base_link)}'>{ifm.filename}</a>",
            ifm.line_nr,
            status,
            search_dir
        ])

    return data
    # result = {
    #     'data': data,
    # }
    # _write_json2file(path, result)


def generate_base_matrix(gitlab_issues: set[GitlabIssue], dirs: list):
    matrix = {'_subdirs': dirs}

    for issue in gitlab_issues:
        matrix[issue.iid] = {'issue': issue, 'iid': issue.iid, 'counts': [0] * len(dirs)}
    return matrix


def build_issue_matrix(
        matrix_in: dict,
        solved: set[IssueFileMatch],
        search_dir: str = ""
):
    """
    returns {1: {'counts': [<count for first dir>, <count for second dir>],
     'iid': 1,
     'issue': GitlabIssue(id=112351387, iid=1, title='get issues from gitlab via api and personal token',
     state='closed', labels=[], references=References(short='#1', full='exb/engineering/ticket-cross-check#1'),
      GITLAB_BASE_URL='https://gitlab.com')},

    :param matrix_in:
    :param solved:
    :param search_dir:
    :return:
    """
    matrix = matrix_in.copy()
    count_index = matrix['_subdirs'].index(search_dir)
    for ifm in solved:
        issue_id = ifm.matched_issue.iid
        matrix[issue_id]['counts'][count_index] += 1
    return matrix


def render_matrix(matrix: dict):
    data = []
    issuelink = None
    for issue, value in matrix.items():
        if isinstance(issue, str):
            continue
        if not issuelink:
            end = value['issue'].get_issue_link().rfind('/')
            issuelink = value['issue'].get_issue_link()[:end]
        data.append(
            [
                issue,
                value['issue'].title,
            ] + value['counts']
        )

    return {
        "title": matrix['_subdirs'],
        "issuelink": issuelink,
        "data": data
    }
