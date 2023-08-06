__version__ = "0.10.9"
__author__ = 'Modelbit'

import os, sys, yaml
from typing import cast, Union, Callable, Any, Dict

# aliasing since some of these overlap with functions we want to expose to users
from . import datasets as m_datasets
from . import warehouses as m_warehouses
from . import deployments as m_deployments
from . import model as m_model
from . import runtime as m_runtime
from . import utils as m_utils
from . import helpers as m_helpers
from . import model_wrappers as m_model_wrappers

m_helpers.pkgVersion = __version__


# Nicer UX for customers: from modelbit import Deployment
class Deployment(m_runtime.Deployment):
  ...


class Model(m_model.Model):
  ...


def __str__():
  return "Modelbit Client"


def _repr_html_():  # type: ignore
  return __str__()


datasets = m_datasets.list

get_dataset = m_datasets.get

warehouses = m_warehouses.list

deployments = m_deployments.list

models = m_model.list


def save_model(modelObj: Any,
               name: Union[str, None] = None,
               properties: Union[Dict[str, Any], None] = None,
               helpers: Union[Dict[str, Any], None] = None):
  if type(modelObj) in [Model, m_model.Model]:
    modelObjM = cast(Model, modelObj)
    return modelObjM.save()
  return Model(modelObj, name=name, properties=properties, helpers=helpers).save()


load_model = m_model.get


def deploy(deployableObj: Union[Callable[..., Any], m_runtime.Deployment],
           name: Union[str, None] = None,
           python_version: Union[str, None] = None):
  if _objIsDeployment(deployableObj):
    deployableObj = cast(Deployment, deployableObj)
    return deployableObj.deploy()
  elif callable(deployableObj):
    dep = Deployment(name=name, deploy_function=deployableObj, python_version=python_version)
    return dep.deploy()
  elif hasattr(deployableObj, "__module__") and "sklearn" in deployableObj.__module__ and hasattr(
      deployableObj, "predict"):
    return m_model_wrappers.SklearnPredictor(deployableObj, name=name,
                                             python_version=python_version).makeDeployment().deploy()
  else:
    raise Exception("First argument must be a function or Deployment object.")


def login():
  m_helpers.performLogin(True)
  return sys.modules['modelbit']


def switch_branch(branch: str):
  m_helpers.setCurrentBranch(branch)


def _loginWithToken(runtimeToken: str):  # type: ignore
  m_helpers._loginWithToken(runtimeToken)  # type: ignore
  return sys.modules['modelbit']


isAuthenticated = m_helpers.isAuthenticated


def load_value(name: str):
  # if "snowparkZip" in os.environ:
  #   zipPath = [p for p in sys.path if p.endswith(os.environ["snowparkZip"])][0]
  #   importer = zipimport.zipimporter(zipPath)
  #   # Typing thinks the response is a string, but we get bytes
  #   val64 = cast(bytes, importer.get_data(f"{name}.pkl")).decode()
  #   return m_utils.unpickleObj(val64)
  extractPath = os.environ['MB_EXTRACT_PATH']
  objPath = os.environ['MB_RUNTIME_OBJ_DIR']
  if not extractPath or not objPath:
    raise Exception("Missing extractPath/objPath")
  with open(f"{extractPath}/metadata.yaml", "r") as f:
    yamlData = cast(Dict[str, Any], yaml.load(f, Loader=yaml.SafeLoader))  # type: ignore
  data: Dict[str, Dict[str, str]] = yamlData["data"]
  contentHash = data[name]["contentHash"]
  with open(f"{objPath}/{contentHash}.pkl.gz", "rb") as f:
    return m_utils.deserialize(contentHash, f.read)


def _objIsDeployment(obj: Any):
  try:
    if type(obj) in [Deployment, m_runtime.Deployment]:
      return True
    # catch modelbit._reload() class differences
    if obj.__class__.__name__ in ['Deployment']:
      return True
  except:
    return False
  return False


# def _reload():  # type: ignore
#   import importlib
#   importlib.reload(modelbit_core)
#   importlib.reload(datasets)
#   importlib.reload(warehouses)
#   importlib.reload(runtime)
#   importlib.reload(model)
#   importlib.reload(deployments)
#   importlib.reload(secure_storage)
#   importlib.reload(utils)
#   importlib.reload(ux)
#   importlib.reload(helpers)
#   importlib.reload(model_wrappers)
#   importlib.reload(importlib.import_module("modelbit"))
#   print("All modules reloaded, except session.")
