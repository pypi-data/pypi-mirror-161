# -*- coding: utf-8 -*-
import sys
from halo import Halo

from suite_py.lib import logger
from suite_py.lib.handler import prompt_utils
from suite_py.lib.handler.git_handler import GitHandler
from suite_py.lib.handler.github_handler import GithubHandler
from suite_py.lib.handler.drone_handler import DroneHandler


class Docker:
    # pylint: disable=too-many-instance-attributes
    def __init__(self, action, project, config, tokens, flags=None):
        self._action = action
        self._project = project
        self._flags = flags
        self._config = config
        self._tokens = tokens
        self._github = GithubHandler(tokens)
        self._repo = self._github.get_repo(project)
        self._git = GitHandler(project, config)
        self._drone = DroneHandler(config, tokens, repo=project)

    def run(self):
        if self._project != "docker":
            logger.error("`suite-py docker` must run inside docker repository.")
            sys.exit(-1)

        self._git.fetch()

        pipelines = self._drone.parse_yaml()

        if pipelines is None:
            logger.error("The file .drone.yml not found.")
            sys.exit(1)

        images = []
        for pipeline in pipelines:
            if "trigger" not in pipeline or "ref" not in pipeline["trigger"]:
                continue

            trigger_tags = pipeline["trigger"]["ref"]

            for tag in trigger_tags:
                images.append(tag.replace("refs/tags/", ""))

        image = prompt_utils.ask_choices(
            "Select an image",
            images,
        )
        versions = self._get_versions(image)

        if self._action == "release":
            print_versions(versions)
            new_version = self._ask_new_version(image)
            self._create_new_version(new_version)

        elif self._action == "versions":
            print_versions(versions)

    def _create_new_version(self, version):
        if prompt_utils.ask_confirm(f"Tag {version} will be deployed. Confirm?"):
            self._git.tag(version, version)
            self._git.push(version)

    def _ask_new_version(self, image):
        new = prompt_utils.ask_questions_input(
            "Write new version to be deployed (eg: 11.3-1):"
        )
        if new[0] == "v":
            logger.error("Insert new version without `v`")
            sys.exit(-1)
        return f'{image.replace("*", "")}{new}'

    def _get_versions(self, image):
        versions = []
        with Halo(text="Retrieving tags...", spinner="dots", color="magenta"):
            tags = self._github.get_tags("docker")
            for tag in tags:
                if image.replace("*", "") in tag.name:
                    versions.append(tag)
            return versions


def print_versions(versions):
    message = "\n".join(["* " + v.name for v in versions])

    logger.info(f"\nVersions list:\n{message}\n")
