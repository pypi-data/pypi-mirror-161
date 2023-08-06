# -*- coding: utf-8 -*-
import re

from pathlib import Path

TAG_REGEX = re.compile(r"\[[0-9]+\.[0-9]+.[0-9]+\]")
DEFAULT_CHANGELOG_PATH = "CHANGELOG.md"


def changelog_exists(path=DEFAULT_CHANGELOG_PATH):
    changelog_path = Path(path)
    return changelog_path.exists()


def get_latest_entry_with_tag(path=DEFAULT_CHANGELOG_PATH):
    latest_tag = None
    changelog = ""
    changelog_started = False

    for line in _read_file(path):
        if line is None:
            continue

        tag = re.search(TAG_REGEX, line)

        a_new_tag = tag and changelog_started
        link_section_starting = line.startswith("[")

        if a_new_tag or link_section_starting:
            break

        if tag:
            changelog_started = True
            latest_tag = tag[0][1:-1] if latest_tag is None else latest_tag
        elif changelog_started:
            changelog += _replace_h3_with_h1(line)

    return latest_tag, changelog.strip("\n")


def _read_file(path):
    """
    Read a file from a path and return lines as a generator
    """
    changelog_path = Path(path)
    if not changelog_path.exists():
        print(f"{path} not found")
        return None

    with open(changelog_path, "r", encoding="utf-8") as changelog_file:
        for line in changelog_file.readlines():
            yield line

    return None


def _replace_h3_with_h1(line):
    return re.sub("^###", "#", line)
