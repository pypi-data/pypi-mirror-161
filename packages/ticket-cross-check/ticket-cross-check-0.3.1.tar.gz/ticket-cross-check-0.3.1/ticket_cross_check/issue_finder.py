import glob
import re
from collections import defaultdict
from pathlib import Path

from loguru import logger

from ticket_cross_check.models import IssueFileMatch


def scan_files(path: Path) -> dict[list[IssueFileMatch]]:
    """
    find issues in files
    :return: dict by issue (<int> w/o #) containing a list of files with line_nr
    """
    if not path.exists():
        logger.warning(f"'{path.absolute()}' does not exist")
        return {}
    files = glob.glob(f"{path}/**/*", recursive=True)
    issues_in_files = defaultdict(list)
    for afile in files:
        if Path(afile).is_dir():
            logger.trace(f"{afile} is dir, skipping")
            continue
        logger.debug(f"processing {afile}")
        with open(afile, 'r') as open_file:
            line_nr = 0
            try:
                for line in open_file:
                    line_nr += 1
                    match = re.findall('#([0-9]+)', line)
                    if match:
                        logger.trace(f"\t #{match[0]}, {afile}:{line_nr}")
                        for issue_nr in set(match):
                            issue_nr = int(issue_nr)
                            issues_in_files[issue_nr].append(IssueFileMatch(issue_nr, afile, line_nr, None))
            except UnicodeDecodeError:  # file is binary
                logger.debug("\t skip, is binary")
                continue
    return issues_in_files
