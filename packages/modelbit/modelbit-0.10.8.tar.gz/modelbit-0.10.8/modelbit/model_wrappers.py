from typing import Any, Union
import inspect, re, string
from .runtime import Deployment


class SklearnPredictor:

  def __init__(self,
               skpredictor: Any,
               name: Union[str, None] = None,
               python_version: Union[str, None] = None):
    self.skpredictor = skpredictor
    self.python_version = python_version
    if name:
      self.name = name
    else:
      self.name = self.guessModelName()

  def guessModelName(self):
    try:
      codeContexts = [f.code_context for f in inspect.stack()]
      for ccList in codeContexts:
        if not ccList:
          continue
        for cc in ccList:
          captures = re.search(r"\.(deploy|train)\(([^\s,)]+)", cc)
          if captures:
            return captures.group(2)
    except Exception as _:
      pass
    return None

  def guessNumArgs(self):
    for i in range(1, 25):
      try:
        args = [j for j in range(i)]
        self.skpredictor.predict([args])  # type: ignore
        return i
      except Exception:
        pass
    return None

  def makeDeployment(self):
    skpredictor = self.skpredictor

    varName = "skpredictor"
    if self.name:
      varName = self.name
    globals()[varName] = skpredictor  # put the same value to globals so it acts more like a notebook cell

    guessedArgCount = self.guessNumArgs()
    if guessedArgCount:
      letters = list(string.ascii_lowercase)
      argNames = letters[0:guessedArgCount]
      argsWithTypes = ", ".join([f"{ltr}: Any" for ltr in argNames])
      funcSource = "\n".join([
          f"def predict({argsWithTypes}):", f"  return {varName}.predict([[{', '.join(argNames)}]])[0]", f""
      ])
    else:
      funcSource = "\n".join([f"def predict(*args: Any):", f"  return {varName}.predict([args])[0]", f""])

    exec(funcSource)
    deploy_function = locals()["predict"]

    return Deployment(deploy_function=deploy_function,
                      source_override=funcSource,
                      python_version=self.python_version,
                      name=self.name)
