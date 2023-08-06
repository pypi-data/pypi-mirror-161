import glob
import os.path
import re
from collections import defaultdict
from pathlib import Path

from loguru import logger

from ticket_cross_check.models import IssueFileMatch


def scan_files(path: Path, exclude_dirs: list = []) -> dict[list[IssueFileMatch]]:
    """
    find issues in files
    :return: dict by issue (<int> w/o #) containing a list of files with line_nr
    """
    logger.debug(f"Scanning files below {path.absolute()} and ignore all subdirs in {exclude_dirs}")
    if not path.exists():
        logger.warning(f"'{path.absolute()}' does not exist")
        return {}
    files = glob.glob(f"{path}/**/*", recursive=True)
    issues_in_files = defaultdict(list)
    for afile in files:
        if Path(afile).is_dir():
            logger.debug(f"{afile} is dir, skipping")
            continue
        dir_name = os.path.basename(os.path.dirname(afile))
        if exclude_dirs and dir_name in exclude_dirs:
            logger.debug(f"Skipping {afile} as it's in the excluded dir {dir_name}")
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
