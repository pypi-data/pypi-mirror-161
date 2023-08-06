from typing import Union, Any, List, Dict, cast
from enum import Enum
import json, requests, os, uuid
from .utils import deprecated_pickleObj, sizeOfFmt, printError, printHtml, getEnvOrDefault, deprecated_unpickleObj

pkgVersion: str = ""  # set in __init__
_MAX_DATA_LEN = 50_000_000

_api_host = getEnvOrDefault('MB_JUPYTER_API_HOST', 'https://app.modelbit.com/')
_login_host = getEnvOrDefault('MB_JUPYTER_LOGIN_HOST', _api_host)

_api_url = f'{_api_host}api/'

_currentBranch = "main"


class OwnerInfo:

  def __init__(self, data: Dict[str, Any]):
    self.id: Union[str, None] = data.get("id", None)
    self.name: Union[str, None] = data.get("name", None)
    self.imageUrl: Union[str, None] = data.get("imageUrl", None)


class DatasetDesc:

  def __init__(self, data: Dict[str, Any]):
    self.name: str = data["name"]
    self.sqlModifiedAtMs: Union[int, None] = data.get("sqlModifiedAtMs", None)
    self.query: str = data["query"]
    self.recentResultMs: Union[int, None] = data.get("recentResultMs", None)
    self.numRows: Union[int, None] = data.get("numRows", None)
    self.numBytes: Union[int, None] = data.get("numBytes", None)
    self.ownerInfo = OwnerInfo(data["ownerInfo"])


class ResultDownloadInfo:

  def __init__(self, data: Dict[str, Any]):
    self.id: str = data["id"]
    self.signedDataUrl: str = data["signedDataUrl"]
    self.key64: str = data["key64"]
    self.iv64: str = data["iv64"]


class ObjectUploadInfo:

  def __init__(self, data: Dict[str, Any]):
    self.signedDataUrl: str = data["signedDataUrl"]
    self.key64: str = data["key64"]
    self.iv64: str = data["iv64"]
    self.objectExists: bool = data["objectExists"]


class KernelInfo:

  def __init__(self, data: Dict[str, str]):
    self.status: str = data["status"]
    self.address: Union[str, None] = data.get("address", None)
    self.sharedSecret: Union[str, None] = data.get("sharedSecret", None)
    self.error: Union[str, None] = data.get("error", None)
    self.kernelId: Union[str, None] = data.get("kernelId", None)


class WhType(Enum):
  Snowflake = 'Snowflake'
  Redshift = 'Redshift'


class GenericWarehouse:

  def __init__(self, data: Dict[str, Any]):
    self.type: WhType = data["type"]
    self.id: str = data["id"]
    self.displayName: str = data["displayName"]
    self.deployStatusPretty: str = data["deployStatusPretty"]
    self.createdAtMs: int = data["createdAtMs"]


class RuntimeFile:

  def __init__(self, name: str, contents: str):
    self.name = name
    self.contents = contents

  def asDict(self):
    return {"name": self.name, "contents": self.contents}


class RuntimePythonProps:
  excludeFromDict: List[str] = ['errors']

  def __init__(self):
    self.source: Union[str, None] = None
    self.name: Union[str, None] = None
    self.argNames: Union[List[str], None] = None
    self.argTypes: Union[Dict[str, str], None] = None
    self.namespaceVarsDesc: Union[Dict[str, str], None] = None
    self.namespaceFunctions: Union[Dict[str, str], None] = None
    self.namespaceImports: Union[Dict[str, str], None] = None
    self.namespaceFroms: Union[Dict[str, str], None] = None
    self.requirementsTxt: Union[str, None] = None
    self.pythonVersion: Union[str, None] = None
    self.customDockerRun: Union[str, None] = None
    self.errors: Union[List[str], None] = None
    self.namespaceVars: Union[Dict[str, Any], None] = None


class RuntimeType(Enum):
  Deployment = 'Deployment'


class RuntimeInfo:

  def __init__(self, data: Dict[str, Any]):
    self.id: str = data["id"]
    self.name: str = data["name"]
    self.version: str = data["version"]
    self.deployedAtMs: int = data["deployedAtMs"]
    self.ownerInfo = OwnerInfo(data["ownerInfo"])


class PickledObj:

  def __init__(self, obj: Any = None, jDict: Union[Dict[str, Any], None] = None):
    self.pkl: Union[str, None] = None
    self.desc: Union[str, None] = None
    self.kind: Union[str, None] = None
    self.size: Union[int, None] = None
    if obj:
      self.pkl = deprecated_pickleObj(obj)
      self.desc = str(obj)
      self.kind = self._getClassName(obj)
      self.size = len(self.pkl)
    elif jDict:
      self.pkl = jDict.get("pkl", None)
      self.desc = jDict.get("desc", None)
      self.kind = jDict.get("kind", None)
      self.size = jDict.get("size", None)

  def unpickle(self):
    if self.pkl:
      return deprecated_unpickleObj(self.pkl)
    else:
      return None

  def asDict(self):
    return self.__dict__

  def _getClassName(self, obj: Any):
    try:
      return f"{obj.__module__}.{obj.__class__.__name__}"
    except:
      return ""


class ModelPackage:

  def __init__(self, data: Dict[str, Any]):
    self.uuid: str = data.get("uuid", str(uuid.uuid4()))
    self.name: Union[str, None] = data.get("name", None)
    self.ownerInfo: Union[OwnerInfo, None] = None
    if "ownerInfo" in data:
      self.ownerInfo = OwnerInfo(data["ownerInfo"])
    self.model: Union[PickledObj, None] = None
    if "model" in data:
      self.model = PickledObj(jDict=data["model"])
    self.helpers: Dict[str, PickledObj] = {}
    if "helpers" in data:
      helpers = cast(Dict[str, Any], data["helpers"])
      for hName, hVal in helpers.items():
        self.helpers[hName] = PickledObj(jDict=hVal)
    self.properties: Dict[str, Any] = data.get("properties", {})
    self.requirementsTxt: Union[str, None] = data.get("requirementsTxt", None)
    self.pythonVersion: Union[str, None] = data.get("pythonVersion", None)
    self.createdAtMs: Union[int, None] = data.get("createdAtMs", None)

  def asDict(self):
    d = self.__dict__.copy()
    if self.model:
      d["model"] = self.model.asDict()
    d["helpers"] = {}
    for hName, hPkl in self.helpers.items():
      d["helpers"][hName] = hPkl.asDict()
    del d["ownerInfo"]
    return d


class DeploymentTestError(Enum):
  UnknownFormat = 'UnknownFormat'
  ExpectedNotJson = 'ExpectedNotJson'
  CannotParseArgs = 'CannotParseArgs'


class DeploymentTestDef:

  def __init__(self, data: Dict[str, Any]):
    self.command: str = data.get("command", "")
    self.expectedOutput: Union[str, Dict[Union[str, int, float, bool], Any]] = data.get("expectedOutput", "")
    self.args: Union[List[Any], None] = data.get("args", None)
    self.error: Union[str, None] = data.get("error", None)


class NotebookEnv:

  def __init__(self, data: Dict[str, Any]):
    self.userEmail: Union[str, None] = data.get("userEmail", None)
    self.signedToken: Union[str, None] = data.get("signedToken")
    self.uuid: Union[str, None] = data.get("uuid", None)
    self.authenticated: bool = data.get("authenticated", False)
    self.workspaceName: Union[str, None] = data.get("workspaceName", None)
    self.mostRecentVersion: Union[str, None] = data.get("mostRecentVersion", None)


class NotebookResponse:

  def __init__(self, data: Dict[str, Any]):
    self.error: Union[str, None] = data.get("error", None)
    self.message: Union[str, None] = data.get("message", None)

    self.notebookEnv: Union[NotebookEnv, None] = None
    if "notebookEnv" in data:
      self.notebookEnv = NotebookEnv(data["notebookEnv"])

    self.datasets: Union[List[DatasetDesc], None] = None
    if "datasets" in data:
      self.datasets = [DatasetDesc(d) for d in data["datasets"]]

    self.dsrDownloadInfo: Union[ResultDownloadInfo, None] = None
    if "dsrDownloadInfo" in data:
      self.dsrDownloadInfo = ResultDownloadInfo(data["dsrDownloadInfo"])

    self.warehouses: Union[List[GenericWarehouse], None] = None
    if "warehouses" in data:
      self.warehouses = [GenericWarehouse(w) for w in data["warehouses"]]

    self.runtimeOverviewUrl: Union[str, None] = None
    if "runtimeOverviewUrl" in data:
      self.runtimeOverviewUrl = data["runtimeOverviewUrl"]

    self.deployments: Union[List[RuntimeInfo], None] = None
    if "deployments" in data:
      self.deployments = [RuntimeInfo(d) for d in data["deployments"]]

    self.modelOverviewUrl: Union[str, None] = None
    if "modelOverviewUrl" in data:
      self.modelOverviewUrl = data["modelOverviewUrl"]

    self.models: Union[List[ModelPackage], None] = None
    if "models" in data:
      self.models = [ModelPackage(m) for m in data["models"]]

    self.modelDownloadInfo: Union[ResultDownloadInfo, None] = None
    if "modelDownloadInfo" in data:
      self.modelDownloadInfo = ResultDownloadInfo(data["modelDownloadInfo"])

    self.tests: Union[List[DeploymentTestDef], None] = None
    if "tests" in data:
      self.tests = [DeploymentTestDef(d) for d in data["tests"]]

    self.kernelInfo: Union[KernelInfo, None] = None
    if "kernelInfo" in data:
      self.kernelInfo = KernelInfo(data["kernelInfo"])

    self.objectUploadInfo: Union[ObjectUploadInfo, None] = None
    if "objectUploadInfo" in data:
      self.objectUploadInfo = ObjectUploadInfo(data["objectUploadInfo"])


def getJson(path: str, body: Dict[str, Any] = {}) -> NotebookResponse:
  global _state
  requestToken = _state.signedToken
  if requestToken == None:
    requestToken = os.getenv('MB_RUNTIME_TOKEN')
  data: Dict[str, Any] = {"requestToken": requestToken, "version": pkgVersion, "branch": _currentBranch}
  data.update(body)
  dataLen = len(json.dumps(data))
  if (dataLen > _MAX_DATA_LEN):
    return NotebookResponse({
        "error":
            f'API Error: Request is too large. (Request is {sizeOfFmt(dataLen)} Limit is {sizeOfFmt(_MAX_DATA_LEN)})'
    })
  with requests.post(f'{_api_url}{path}', json=data) as url:  # type: ignore
    nbResp = NotebookResponse(url.json())  # type: ignore
    if nbResp.notebookEnv:
      _state = nbResp.notebookEnv
    return nbResp


def getJsonOrPrintError(path: str, body: Dict[str, Any] = {}):
  nbResp = getJson(path, body)
  if not isAuthenticated():
    performLogin()
    return False
  if nbResp.error:
    printError(nbResp.error)
    return False
  return nbResp


def refreshAuthentication() -> bool:
  global _state
  nbResp = getJson("jupyter/v1/login")
  if nbResp.error:
    printError(nbResp.error)
    return False
  if nbResp.notebookEnv:
    _state = nbResp.notebookEnv
  return isAuthenticated()


def isAuthenticated() -> bool:
  return _state.authenticated


def performLogin(refreshAuth: bool = False, branch: str = _currentBranch):
  setCurrentBranch(branch)
  if (refreshAuth):
    refreshAuthentication()
  if isAuthenticated():
    _printAuthenticatedMsg()
    return
  printHtml(_getAuthMessage())


def _loginWithToken(runtimeToken: str):  # type: ignore
  if not isAuthenticated():
    _state.signedToken = runtimeToken
    refreshAuthentication()
  _printAuthenticatedMsg()


def _maybeGetUpgradeMessage():
  if os.getenv('MB_RUNTIME_TOKEN'):
    return ""  # runtime environments don't get upgraded
  latestVer = _state.mostRecentVersion

  def ver2ints(ver: str):
    return [int(v) for v in ver.split(".")]

  nbVer = pkgVersion
  if latestVer and ver2ints(latestVer) > ver2ints(nbVer):
    pipCmd = '<span style="color:#E7699A; font-family: monospace;">pip install --upgrade modelbit</span>'
    return (f'<div>Please run {pipCmd} to upgrade to the latest version. ' +
            f'(Installed: <span style="font-family: monospace">{nbVer}</span>. ' +
            f' Latest: <span style="font-family: monospace">{latestVer}</span>)<div>')
  return ""


def _printAuthenticatedMsg():
  connectedTag = '<span style="color:green; font-weight: bold;">connected</span>'
  email = _state.userEmail
  workspace = f'<span style="font-family: monospace; font-weight: 600; color: #888;">{_state.workspaceName}</span>'
  branch = f'<span style="font-family: monospace;	font-weight: 600; color: #888;">{_currentBranch}</span>'
  printHtml(
      f"<div>You're {connectedTag} to Modelbit as {email}. Workspace: {workspace}. Branch: {branch}.</div>" +
      _maybeGetUpgradeMessage())


def _getAuthMessage():
  displayUrl = f'modelbit.com/t/{_state.uuid}'
  linkUrl = f'{_login_host}/t/{_state.uuid}'
  aTag = f'<a style="text-decoration:none;" href="{linkUrl}?branch={_currentBranch}" target="_blank">{displayUrl}</a>'
  helpTag = '<a style="text-decoration:none;" href="https://doc.modelbit.com/getting-started.html" target="_blank">Learn more.</a>'
  return (
      f'<div style="font-weight: bold;">Connect to Modelbit</div><div>Open {aTag} to authenticate this kernel, then re-run this cell. {helpTag}</div>'
      + _maybeGetUpgradeMessage())


def _runtimeToken():  # type: ignore
  return _state.signedToken


def setCurrentBranch(branch: str):
  global _currentBranch
  if type(branch) != str:
    raise Exception("Branch must be a string.")
  _currentBranch = branch


def getCurrentBranch():
  return _currentBranch


_state = NotebookEnv({})
