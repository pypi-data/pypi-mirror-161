from typing import Dict

from phiterm.workspace.ws_enums import WorkspaceStarterTemplate

template_to_repo_map: Dict[WorkspaceStarterTemplate, str] = {
    WorkspaceStarterTemplate.aws: "https://github.com/phidatahq/phidata-starter-aws.git",
}
