"""
Ticket Cross Checker
Find tickets (issues) in files and match them against the issue tracker (gitlab)
"""
import argparse
import os.path
import shutil
import sys
from pathlib import Path

from loguru import logger

from ticket_cross_check.gitlab_connector import GitlabConnector
from ticket_cross_check.issue_finder import scan_files
from ticket_cross_check.matcher import analyze_issues_vs_code, render, _write_json2file, generate_base_matrix, \
    build_issue_matrix, render_matrix


@logger.catch
def discover():
    parser = argparse.ArgumentParser()
    parser.add_argument('dirs', metavar='dir', type=str, nargs='+',
                        help='Sapce separated list of directories to process')
    parser.add_argument('-q', '--quiet', action='store_true', help="Show only warnigns and errors")
    parser.add_argument('-d', '--debug', action='store_true', help="Show more context")
    parser.add_argument('-t', '--trace', action='store_true', help="Show even more context / trace")
    parser.add_argument('-o', '--output', type=str, default='public', help="Where to write the output files")
    parser.add_argument('-e', '--exclude', type=str, default='', help="Comma separated list of dirnames to exclude")
    args = parser.parse_args()

    _setup_logger(args)

    file_issues = dict()
    for _dir in args.dirs:
        logger.info(f"--> Processing directory: {_dir} ({Path(_dir).absolute()})")
        file_issues[_dir] = scan_files(Path(_dir), exclude_dirs=args.exclude.split(','))
        logger.debug(f"<-- done with {_dir}")

    gitlab = GitlabConnector.factory()
    gitlab_issues = gitlab.get_issues()
    gitlab_project = gitlab.get_project()

    data = []
    issue_matrix = generate_base_matrix(gitlab_issues, args.dirs)
    for _dir in args.dirs:
        problems, unsolved, solved = analyze_issues_vs_code(file_issues[_dir], gitlab_issues)
        data += render(solved, unsolved, problems, base_link=gitlab_project.web_url, search_dir=str(_dir))
        issue_matrix = build_issue_matrix(issue_matrix, solved, search_dir=str(_dir))

    matrix_data = render_matrix(issue_matrix)

    output_dir = args.output
    os.makedirs(output_dir, exist_ok=True)
    full_json = Path(output_dir) / 'allinone.json'
    full_matrix = Path(output_dir) / 'matrix.json'
    # copy index template
    copy_resource('index.html', output_dir)
    copy_resource('matrix.html', output_dir)
    # write full json table
    _write_json2file(full_json, {"data": data})
    # write matrix
    _write_json2file(full_matrix, matrix_data)

    logger.info(f"Wrote all files to {Path(output_dir).absolute()}")


def copy_resource(filename, output_dir):
    index_from = Path(os.path.dirname(__file__)) / '..' / 'resource' / filename
    index_to = Path(output_dir).joinpath(filename).absolute()
    shutil.copy2(index_from, index_to)


def _setup_logger(args):
    level = "INFO"
    if args.trace:
        level = "TRACE"
    elif args.debug:
        level = "DEBUG"
    elif args.quiet:
        level = "WARN"
    logger.remove()
    logger.add(sys.stdout, colorize=True, level=level)
