from ipykernel.kernelbase import Kernel
from typing import Dict, Any, Union, cast, Iterator, Optional
import json, time
import logging
import os
import asyncio

from .helpers import NotebookResponse, KernelInfo
from . import __version__
from .ipython_pb2 import JupyterMessage, CodeRequest, ShutdownRequest, EmptyMessage
from .ipython_pb2_grpc import KernelWrapperStub

from .cloud_kernel_client import CloudKernelClient


class ModelbitKernel(Kernel):
  implementation = "Modelbit"
  implementation_version = "1.0"
  language = "python"
  language_version = "3"
  language_info = {
      "codemirror_mode": {
          "name": "ipython",
          "version": 3
      },
      "name": "python",
      "nbconvert_exporter": "python",
      "file_extension": ".py",
      "mimetype": "text/x-python",
      "pygments_lexer": "ipython3",
      "version": "3",
  }
  banner = "Modelbit Kernel"

  def __init__(self, **kwargs: Any):
    super().__init__(**kwargs)  # type: ignore
    try:
      self._client = CloudKernelClient(self.send_io_response, self.sendHtml)
    except Exception as e:
      logging.exception("Error during init", e)

  # using warning so messages show up by default
  def logMsg(self, msg: Any) -> None:
    self.log.warning(msg)  # type: ignore

  def send_io_response(self, mode: str, content: Dict[str, Any]) -> None:
    super().send_response(self.iopub_socket, mode, content)  # type: ignore

  def sendText(self, msg: str, pipe: str = "stdout") -> None:
    self.send_io_response("stream", {"name": pipe, "text": msg})

  def sendHtml(self, html: str, id: Union[str, None] = None) -> str:
    mode = "update_display_data" if id != None else "display_data"
    id = str(time.time()) if id is None else id
    data = {"text/html": html} if html != "" else {"text/plain": ""}
    self.send_io_response(
        mode,
        {
            "data": data,
            "metadata": {},
            "transient": {
                "display_id": id
            },
        },
    )
    return id

  def clearOutput(self) -> None:
    self.send_io_response("clear_output", {"wait": False})

  def start(self) -> None:
    super().start()
    self.logMsg("NYI: starting remote kernel\n\n\n\n")

  async def _processLocalMagic(self, code) -> Optional[Dict[str, Any]]:
    if code.startswith("%%mbinfo"):
      self.sendText(
          f"kernelId={self._client._apiClient.kernelId} remoteAddress={self._client._apiClient.remoteAddress}"
      )
      return dict(status='ok')
    if code.startswith("%%kernel_id="):
      kernelId = code.splitlines()[0].split("=")[1]
      if kernelId:
        logging.info(f"Override to kernel {kernelId}")
        self._client._apiClient.kernelId = kernelId
    return None

  async def do_execute(
      self,
      code: str,
      silent: bool,
      store_history: bool = True,
      user_expressions: Union[Dict[str, Any], None] = None,
      allow_stdin: bool = False,
      *,
      cell_id: Union[str, None] = None,
  ) -> Dict[str, Any]:
    try:
      r = await self._processLocalMagic(code)
      if not r:
        r = await self._client.do_execute(code)
      if not r.get('execution_count'):
        r['execution_count'] = self.execution_count
      if r.get('status') == 'ok' and not r.get('payload'):
        r['payload'] = [{}]
      return r
    except Exception as err:
      logging.error("Error executing code: %s", err)
      self.sendText(
          "Error getting connection details: %s" % (err),
          "stderr",
      )

    return {
        "status": "error",
        "error": "Failed to connect to the cloud.",
        "execution_count": self.execution_count,
        "payload": [],
        "user_expressions": {},
    }

  async def do_complete(
      self,
      code: str,
      cursor_pos: int,
  ) -> Dict[str, Any]:
    try:
      return await self._client.do_complete(code, cursor_pos)
    except Exception as err:
      logging.error("Error completing code: %s", err)
      self.sendText(
          "Error getting connection details: %s" % (err),
          "stderr",
      )
    return {
        "status": "error",
        "error": "Failed to connect to the cloud.",
        "execution_count": self.execution_count,
        "payload": [],
        "user_expressions": {},
    }

  async def do_inspect(
      self,
      code: str,
      cursor_pos: int,
      detail_level: int = 0,
      omit_sections=(),
  ) -> Dict[str, Any]:
    try:
      return await self._client.do_inspect(code, cursor_pos, detail_level)
    except Exception as err:
      logging.error("Error completing code: %s", err)
      self.sendText(
          "Error getting connection details: %s" % (err),
          "stderr",
      )
    return {
        "status": "error",
        "error": "Failed to connect to the cloud.",
        "execution_count": self.execution_count,
        "payload": [],
        "user_expressions": {},
    }

  async def do_shutdown(self, restart: bool) -> None:
    await self._client.do_shutdown(restart)
    return super().do_shutdown(restart)  # type: ignore

  async def interrupt_request(self, stream, ident, parent) -> None:
    await self._client.do_interrupt()
    return super().interrupt_request(stream, ident, parent)


if __name__ == "__main__":
  from ipykernel.kernelapp import IPKernelApp

  logging.basicConfig(level=logging.DEBUG, datefmt='%X.%f')
  IPKernelApp.launch_instance(kernel_class=ModelbitKernel)  # type: ignore
