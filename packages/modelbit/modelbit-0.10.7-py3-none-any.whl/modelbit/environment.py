from typing import List, Union
import os, sys

from .utils import printHtml


def _listInstalledPackages():
  pkgResp = os.popen("pip freeze")
  return _parseReqsIntoList(pkgResp.read())


def _parseReqsIntoList(req: str):
  return req.strip().split("\n")


def _ensureReqsHaveVersions(reqList: List[str]):
  for req in reqList:
    if req.startswith("#"):
      continue
    if "==" not in req:
      return f"Specific version numbers are required (i.e. using ==), but are missing: {req}"
  return None


def _ensureListedReqsAreInstalled(reqList: List[str], pipList: List[str]):
  for req in reqList:
    if req not in pipList:
      return f"Requirement '{req}' is not installed. Is the version correct?"
  return None


def checkReqsForIssues(reqTxt: Union[str, None]) -> Union[str, None]:
  if reqTxt == None:
    return None

  if type(reqTxt) != str:
    raise Exception("reqTxt should be a string")

  reqList = _parseReqsIntoList(reqTxt)
  pipList = _listInstalledPackages()

  formatError = _ensureReqsHaveVersions(reqList)
  if formatError:
    return formatError

  installError = _ensureListedReqsAreInstalled(reqList, pipList)
  if installError:
    return installError

  return None


def getDefaultPythonVersion(allowedVersions: List[str]):
  installedVer = f"{sys.version_info.major}.{sys.version_info.minor}"
  if installedVer in allowedVersions:
    return installedVer
  else:
    defaultVersion = "3.8"
    printHtml(
        f"Warning: python {installedVer} is not a supported version ({', '.join(allowedVersions)}). Defaulting to {defaultVersion}."
    )
    return defaultVersion
