"""
    Copyright 2016 Inmanta

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
from collections import defaultdict

from inmanta.export import dependency_manager


@dependency_manager
def yum_dependencies(config_model, resource_model):
    repo_files = defaultdict(list)
    pkgs = defaultdict(list)

    for _, resource in resource_model.items():
        if resource.id.entity_type == "std::File" and resource.path.startswith(
            "/etc/yum.repos.d"
        ):
            repo_files[resource.id.agent_name].append(resource)

        elif resource.id.entity_type == "std::Package":
            pkgs[resource.id.agent_name].append(resource)

    # they require the tenant to exist
    for hostname, pkgs in pkgs.items():
        for pkg in pkgs:
            for repo in repo_files[hostname]:
                pkg.requires.add(repo)
