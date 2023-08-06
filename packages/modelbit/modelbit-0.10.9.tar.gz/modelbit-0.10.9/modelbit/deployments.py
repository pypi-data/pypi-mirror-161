from typing import List, Dict

from .utils import formatImageTag, timeago
from .helpers import RuntimeInfo, getJsonOrPrintError, isAuthenticated
from .ux import makeHtmlTable, TableHeader


class DeploymentsList:

  def __init__(self):
    self._deployments: List[RuntimeInfo] = []
    resp = getJsonOrPrintError("jupyter/v1/runtimes/list?runtimeType=Deployment")
    if resp and resp.deployments:
      self._deployments = resp.deployments

  def _repr_html_(self):
    if not isAuthenticated():
      return ""
    return self._makeDeploymentsHtmlTable()

  def _makeDeploymentsHtmlTable(self):
    from collections import defaultdict

    if len(self._deployments) == 0:
      return "There are no deployments to show."
    deploymentsByName: Dict[str, List[RuntimeInfo]] = defaultdict(lambda: [])
    for d in self._deployments:
      deploymentsByName[d.name].append(d)

    headers = [
        TableHeader("Name", TableHeader.LEFT),
        TableHeader("Owner", TableHeader.CENTER, skipEscaping=True),
        TableHeader("Version", TableHeader.RIGHT),
        TableHeader("Deployed", TableHeader.LEFT),
    ]
    rows: List[List[str]] = []
    for dList in deploymentsByName.values():
      ld = dList[0]
      connectedAgo = timeago(ld.deployedAtMs)
      ownerImageTag = formatImageTag(ld.ownerInfo.imageUrl, ld.ownerInfo.name)
      rows.append([ld.name, ownerImageTag, ld.version, connectedAgo])
    return makeHtmlTable(headers, rows)


def list():
  return DeploymentsList()
