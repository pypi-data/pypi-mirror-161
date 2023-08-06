"""
    Copyright 2017 Inmanta

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

    Contact: code@inmanta.com
"""
import logging
from collections import defaultdict

from inmanta.agent.handler import ResourceHandler, cache, provider
from inmanta.export import dependency_manager

LOGGER = logging.getLogger(__name__)


@dependency_manager
def apt_dependencies(config_model, resource_model):
    repo_files = defaultdict(list)
    pkgs = defaultdict(list)

    for _, resource in resource_model.items():
        if resource.id.entity_type == "std::File" and resource.path.startswith(
            "/etc/apt/sources.list.d/"
        ):
            repo_files[resource.id.agent_name].append(resource)

        elif resource.id.entity_type == "std::Package":
            pkgs[resource.id.agent_name].append(resource)

    # they require the tenant to exist
    for hostname, pkgs in pkgs.items():
        for pkg in pkgs:
            for repo in repo_files[hostname]:
                pkg.requires.add(repo)


@provider("std::Package", name="apt")
class AptPackage(ResourceHandler):
    """
    A Package handler that uses apt

    TODO: add latest support
    """

    def __init__(self, agent, io=None):
        super().__init__(agent, io)

    @cache(cacheNone=True)
    def run_update(self, version):
        LOGGER.info("Running apt-get update")
        self._io.run("/usr/bin/apt-get", ["update"])

    def pre(self, ctx, resource):
        """
        Ensure that apt-get update is execute upfront
        """
        self.run_update(resource.id.version)

    def available(self, resource):
        return (self._io.file_exists("/usr/bin/dpkg")) and self._io.file_exists(
            "/usr/bin/apt-get"
        )

    def check_resource(self, ctx, resource):
        dpkg_output = self._io.run("/usr/bin/dpkg", ["-s", resource.name])

        if len(dpkg_output[1]) > 0:
            return {"state": "removed"}

        lines = dpkg_output[0].split("\n")
        state = {}
        for line in lines:
            values = line.split(": ")
            if len(values) > 1:
                state[values[0]] = values[1]

        if not state["Status"].startswith("install ok"):
            return {"state": "removed"}

        return {"state": "installed"}

    def list_changes(self, ctx, resource):
        state = self.check_resource(ctx, resource)

        changes = {}
        if resource.state == "removed":
            if state["state"] != "removed":
                changes["state"] = (state["state"], resource.state)

        elif resource.state == "installed" or resource.state == "latest":
            if state["state"] != "installed":
                changes["state"] = (state["state"], "installed")

        return changes

    def _result(self, result):
        if result[2] > 0:
            raise Exception("An error occured while executing apt: " + result[1])

    def do_changes(self, ctx, resource, changes):
        changed = False

        env = {
            "LANG": "C",
            "DEBCONF_NONINTERACTIVE_SEEN": "true",
            "DEBIAN_FRONTEND": "noninteractive",
            "PATH": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
        }
        if "state" in changes:
            if changes["state"][1] == "removed":
                self._result(
                    self._io.run(
                        "/usr/bin/apt-get",
                        ["-qq", "--yes", "remove", resource.name],
                        env,
                    )
                )

            elif changes["state"][1] == "installed":
                self._result(
                    self._io.run(
                        "/usr/bin/apt-get",
                        ["-qq", "--yes", "--force-yes", "install", resource.name],
                        env,
                    )
                )
                changed = True

        return changed
