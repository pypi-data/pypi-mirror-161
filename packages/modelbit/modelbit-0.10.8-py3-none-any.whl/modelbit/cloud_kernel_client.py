#!/usr/bin/env python3
from __future__ import annotations
from typing import Callable, Dict, Any, NamedTuple, Awaitable, Optional
# from ipykernel.kernelbase import Kernel

import json, time
import logging
import os
import asyncio

from .helpers import NotebookResponse, KernelInfo, getJson, isAuthenticated, refreshAuthentication, _getAuthMessage, _runtimeToken  # type: ignore
from . import __version__
from .ipython_pb2 import JupyterMessage, ShutdownRequest, EmptyMessage, NotebookRequest
from .ipython_pb2_grpc import KernelWrapperStub

PROD_CA_CERT = """
-----BEGIN CERTIFICATE-----
MIIFZzCCA0+gAwIBAgIUeOrlZfltFm6S/4Iz36QRntCW8CkwDQYJKoZIhvcNAQEL
BQAwQzELMAkGA1UEBhMCVVMxCzAJBgNVBAgMAkNBMREwDwYDVQQKDAhNb2RlbGJp
dDEUMBIGA1UECwwLTW9kZWxiaXQgQ0EwHhcNMjIwNDI1MjIxODM3WhcNMzIwNDIy
MjIxODM3WjBDMQswCQYDVQQGEwJVUzELMAkGA1UECAwCQ0ExETAPBgNVBAoMCE1v
ZGVsYml0MRQwEgYDVQQLDAtNb2RlbGJpdCBDQTCCAiIwDQYJKoZIhvcNAQEBBQAD
ggIPADCCAgoCggIBAMLzsnSOG2pCA1wdk1kuJp7JtKzEdi618x5SNOSUE7+X9U17
j0grGXLI8xSLWW5PY3g6h9NNPps7mjO3TDxYqO8RvvCb9oouOvkW7wYPcfEZAS6K
0fjufmNPL9FX50vmb1eCFxuP8wcaWTDLBdbRYPr12alUnQ/DePctzMhnAr3bQQ/e
lQcjJJFwT6aa1ag12oW+SAWs/RH6kC5mgMXJYUHp5MKnkebEfuuZOTZD1wA/wAmX
Er71dLuPnRxIo8JNgVNeMXcGFGVfINTg8+30FBU02CHD0vLmOXdXWLOFntMTtMCq
vnVpmsOMECpfbleiClJQZJSQXsKxN56jQRf3E/0R/qN1xeU68qVPQ/0Hj+bejfoS
hGlpKtEHMddEwzI7JWVq67PtT29+Mk7dJm+kx7IqfOvsOKqvE94iFYSwFAgOv2sM
uoPdEnzRUDXrpzO7SEcK0NryMbrBlMr+j2nbH/oLklqlc3A7XL/tooV24ei80Hak
K1LPPbwSHmCYVvhjDxXyzqP4ehjZ3KQjwQcPUlyyGxOU/8NIVSEm9w1Voe46glzK
RlLc4tXHgQ3oae89PqpemixRTOUxk/Y46GfvDQ4BhwnMcGEygpPn2IUgS3snEvCb
tmwjFsLwGMiCH8CB7NjxQWO0KyMcbK1PYiGx1NE/mQpLqhySWPy1d0HMI8G/AgMB
AAGjUzBRMB0GA1UdDgQWBBSkKGYAm8qZY3ttTLCMMIEO1qMH2DAfBgNVHSMEGDAW
gBSkKGYAm8qZY3ttTLCMMIEO1qMH2DAPBgNVHRMBAf8EBTADAQH/MA0GCSqGSIb3
DQEBCwUAA4ICAQCuxnnBGLLJB6La4s0/DEL4dXGXTXgSxM9I9YoCbWHL2HZ+B0z4
OauIeDQXDs1cQIkRjRHs3Id9lMXLJA23WjbCSqqAXyPVqLhCch84H2beEuDhs+fU
1rk8v7a/dDxtyQxTnYXp/yOvC26cw8SjC6/nsWi8Wj7mnSuyaObcHv3AM7XDBCew
mF3saFgpMjvwg2OXys2SRx5YLQ5FaCBBYMYRNp3pzpC+7s5TFnxxUPz+LYuph8VJ
2MUawNxpWoU2gUWg1cb03sQVp5LIFKqGXWbOiL+TY5R/6MlGevEtdv3s0Rik/m8S
5I51ii7lHdxLmeXIvx3W5QWkH7yzi0pjt73yhFmM2vNm5jYXqRodWUhPoWCnbsqm
/n7WEVLvmDfiAhgaE4+HDXKW2EpYZev3JfTQ9/Wuop9GD1TfkawQFw2VLdB8ZZ4i
aU6MIGqe0l6+XHIXH8fanOrEQKpf4RhRCPTd9qBn4NVOC/hfE/WHeJo1hCftvZ98
icbIAiz9IJToB30/kNXvZsCGKngO3Z5/+ab5OSkDnMnap9zfWWEaug7QkQ0slWGF
l31eh5lyIV51a9/qWPvR8NCkDnaGdiOq8EIjrDsnUIHu4NWQL0UsE3EJA2inqksf
qwQn1TahV1l6EzhjM/ryga+vBniKxVePwc4ZZKtvWnwuOPPu9q57ZFGiKg==
-----END CERTIFICATE-----"""


def caCert():
  cert = bytes(os.environ.get("MODELBIT_CA_CERT", PROD_CA_CERT), 'utf-8')
  if len(cert) == 0:
    cert = bytes(PROD_CA_CERT, 'utf-8')
  return cert


class StateInfo(NamedTuple):
  expectedTimeSeconds: Optional[int]
  htmlFormatString: str


class StateMap:
  #  authing:
  finding: StateInfo = StateInfo(120, 'Preparing environment: allocating compute resources')
  starting: StateInfo = StateInfo(120, 'Preparing environment: installing dependencies')
  restoring: StateInfo = StateInfo(120, 'Preparing environment: Resuming kernel from hibernation')
  creating: StateInfo = StateInfo(30, 'Preparing environment: starting kernel')
  started: StateInfo = StateInfo(30, 'Preparing environment: starting kernel')
  connecting: StateInfo = StateInfo(30, 'Preparing environment: starting kernel')
  connected: StateInfo = StateInfo(None, '')
  # executing: 8 * 3600,
  # idle: 30 * 60,
  checkpointing: StateInfo = StateInfo(120, 'Stopping environment: Preparing kernel for hibernation')
  stopping: StateInfo = StateInfo(120, 'Stopping environment')
  stopped: StateInfo = StateInfo(None, 'Kernel Stopped')
  checkpointed: StateInfo = StateInfo(None, 'Kernel Paused')


class AsyncGrpcClient:
  channel = None

  def __init__(self, runtimeToken: Callable[[], Optional[str]]):
    self.runtimeToken = runtimeToken

  # def cancel(self):
  #   if self.channel is not None:
  #     self.channel.close(None)

  async def authenticatedClient(self, kernelInfo: KernelInfo, syncClient: bool = False) -> KernelWrapperStub:
    import grpc

    class GrpcAuth(grpc.AuthMetadataPlugin):
      """Used to pass JWT and runtime token via channel credentials."""

      def __init__(self, key: str, token: str):
        self._key = key
        self._token = token

      def __call__(self, context: grpc.AuthMetadataContext, callback: grpc.AuthMetadataPluginCallback):
        callback((("rpc-auth-header", self._key), ("mb-runtime-token-header", self._token)), None)

    sslCreds = grpc.ssl_channel_credentials(caCert())  # type: ignore
    authCreds = grpc.metadata_call_credentials(  # type: ignore
        GrpcAuth(kernelInfo.sharedSecret, self.runtimeToken()))  # type: ignore
    creds = grpc.composite_channel_credentials(sslCreds, authCreds)  # type: ignore

    channel = grpc.secure_channel(  # type: ignore
        kernelInfo.address,
        creds,
        (("grpc.ssl_target_name_override", "km.modelbit.com"),),
    ) if syncClient else grpc.aio.secure_channel(  # type: ignore
        kernelInfo.address,
        creds,
        (("grpc.ssl_target_name_override", "km.modelbit.com"),),
    )
    stub = KernelWrapperStub(channel)
    if not syncClient:
      await channel.channel_ready()
    return stub


class AsyncJupyterClient(AsyncGrpcClient):
  responseQueues: Dict[int, asyncio.Queue[JupyterMessage]] = {}
  cmdQueue: asyncio.Queue[NotebookRequest] = asyncio.Queue()
  task: Optional[asyncio.Task] = None
  connected = False

  def __init__(self, apiClient: ModelbitApiClient,
               processMessage: Callable[[JupyterMessage], Awaitable[Optional[JupyterMessage]]]):
    self._apiClient = apiClient
    self.processMessage = processMessage
    super().__init__(apiClient.runtimeToken)

  async def runCmd(self, cmd: NotebookRequest, startKernelIfNeeded: bool = True) -> Dict[str, Any]:
    self._ensureClient()
    cmd.request_id = int(time.time() * 1000)
    self.responseQueues[cmd.request_id] = asyncio.Queue(1)
    await self.cmdQueue.put(cmd)
    reply = await self.responseQueues[cmd.request_id].get()
    self.responseQueues.pop(cmd.request_id)
    if reply.error:
      raise Exception(reply.error)
    return json.loads(reply.content)

  async def doInterrupt(self) -> None:
    if self.connected:
      client = await self._client(True)
      if client:
        client.InterruptKernel(EmptyMessage())
        self._cancelAndReset()

  async def doShutdown(self, restart: bool, checkpoint: bool = False) -> None:
    if self.connected:
      client = await self._client(True)
      if client:
        client.ShutdownKernel(ShutdownRequest(restart=restart, checkpoint=checkpoint))

  def _ensureClient(self) -> None:
    if not self.connected:
      loop = asyncio.get_event_loop()
      if self.task and not self.task.cancelled():
        self.task.cancel()
        self.task = None
      self.task = loop.create_task(self._clientTask())

  # Co-routine functions

  async def _client(self, syncClient: bool = False) -> Optional[KernelWrapperStub]:
    kernelInfo = self._apiClient.waitForConnectionInfo()
    if kernelInfo is not None and kernelInfo.status == "ready":
      client = await self.authenticatedClient(kernelInfo, syncClient)
      return client
    return None

  async def _cmdIterator(self):
    while self.connected:
      try:
        cmd = await self.cmdQueue.get()
        if cmd is None:
          raise StopAsyncIteration()
        yield cmd
      except StopAsyncIteration:
        raise
      except Exception as e:
        logging.exception("Error in _cmdIterator")

  async def _clientTask(self) -> None:
    try:
      client = await self._client()
      if not client:
        raise NotConnectedError()
      replyStream = client.NotebookStream(self._cmdIterator())
      self.connected = True
      async for msg in replyStream:
        reply = await self.processMessage(msg)
        if reply and reply.request_id:
          responseQueue = self.responseQueues[reply.request_id]
          await responseQueue.put(reply)
    except NotConnectedError:
      self._cancelAndReset()
    except Exception as e:
      try:
        import grpc
        if not isinstance(e, grpc.aio.AioRpcError):
          logging.exception("Error making request")
        self._cancelAndReset('Disconnected')
      except Exception as e:
        logging.exception("Double fault!!!")
      finally:
        self.connected = False

  def _cancelAndReset(self, error: Optional[str] = None) -> None:
    logging.info(f"cancelAndReset: {error}")
    while self.cmdQueue.qsize():  # Empty queue
      self.cmdQueue.get_nowait()
    self.cmdQueue.put_nowait(NotebookRequest())  # Clear pending grpc async task
    for q in self.responseQueues.values():
      if error is None:
        q.put_nowait(JupyterMessage(content='{"status":"ok"}'))  #execution_count?
      else:
        q.put_nowait(JupyterMessage(error=error))


class CloudKernelClient:
  state: str = "unknown"
  stateDispId: Optional[str] = None

  def __init__(self, sendResponse: Callable[[str, Dict[str, Any]], None],
               sendHtml: Callable[[str, Optional[str]], str]):
    logging.basicConfig(level=logging.DEBUG, datefmt='%X.%f')
    self.sendResponse = sendResponse
    self.sendHtml = sendHtml
    self._apiClient = ModelbitApiClient(self._setState, self.sendStatusHtml, self._waitForKernelProgress)
    self._grpcClient = AsyncJupyterClient(self._apiClient, self._processMessage)

  def sendStatusHtml(self, msg: str) -> None:
    self.sendHtml(msg, self.stateDispId)

  def logMsg(self, msg: Any) -> None:
    logging.warning(msg)  # type: ignore

  def clearMessage(self, dispId: Optional[str]) -> None:
    if dispId is not None:
      self.sendResponse(
          "update_display_data",
          {
              "data": {},
              "metadata": {},
              "transient": {
                  "display_id": dispId
              },
          },
      )

  async def do_shutdown(self, restart: bool, checkpoint: bool = False) -> None:
    await self._grpcClient.doShutdown(restart, checkpoint)

  async def do_interrupt(self) -> None:
    self._apiClient.cancel()
    await self._grpcClient.doInterrupt()

  async def do_execute(
      self,
      code: str,
  ) -> Dict[str, Any]:
    if code == "%%checkpoint":
      return await self._checkpoint()
    req = NotebookRequest()
    req.execute.code = code
    return await self._runCmd(req)

  async def do_complete(
      self,
      code: str,
      cursor_pos: int,
  ) -> Dict[str, Any]:
    req = NotebookRequest()
    req.complete.code = code
    req.complete.cursor_pos = cursor_pos
    return await self._runCmd(req)

  async def do_inspect(
      self,
      code: str,
      cursor_pos: int,
      detail_level: int,
  ) -> Dict[str, Any]:
    req = NotebookRequest()
    req.inspect.code = code
    req.inspect.cursor_pos = cursor_pos
    req.inspect.detail_level = detail_level
    return await self._runCmd(req)

  async def _checkpoint(self) -> Dict[str, Any]:
    if self.stateDispId is not None:
      self.clearMessage(self.stateDispId)
      self.stateDispId = None
    self.stateDispId = self.sendHtml("Starting Checkpoint", None)
    await self.do_shutdown(False, True)
    return {"status": "ok", "execution_count": 0}

  async def _runCmd(self, req: NotebookRequest) -> Dict[str, Any]:
    if self.stateDispId is not None:
      self.clearMessage(self.stateDispId)
      self.stateDispId = None
    self.stateDispId = self.sendHtml("", None)
    return await self._grpcClient.runCmd(req)

  def _setState(self, state: str) -> None:
    logging.warn("State Change %s -> %s", self.state, state)
    if hasattr(StateMap, state):
      stateInfo: StateInfo = getattr(StateMap, state)
      self.stateDispId = self.sendHtml(stateInfo.htmlFormatString, self.stateDispId)
    self.state = state

  async def _processMessage(self, resp: JupyterMessage) -> Optional[JupyterMessage]:
    if resp.channel == JupyterMessage.Channel.SHELL:
      return resp
    elif resp.channel == JupyterMessage.Channel.IOPUB:
      self.sendResponse(resp.msg_type, json.loads(resp.content))
    elif resp.channel == JupyterMessage.Channel.MODELBIT:
      self._processMbMessage(resp.msg_type, json.loads(resp.content))
    else:
      logging.info("Got message type '%s' content: %s", resp.msg_type, resp.content)
    return None

  def _processMbMessage(self, msgType: str, msgData: Dict[str, Any]) -> None:
    if msgType == "state_change":
      newState = msgData.get("new_state", msgData.get("newState"))
      if newState:
        self._setState(newState)
    elif msgType == "state_progress":
      self._processStateProgress(msgData)

  def _processStateProgress(self, msgData: Dict[str, Any]) -> None:
    if hasattr(StateMap, self.state):
      stateInfo: StateInfo = getattr(StateMap, self.state)
      maxProgress = msgData.get('max_progress', stateInfo.expectedTimeSeconds)
      currentProgress = maxProgress - msgData['progress'] if maxProgress else msgData['progress']
      progressMessage = f": {currentProgress} {msgData['progress_unit']}" if currentProgress >= 5 else "." * (
          1 + (msgData['progress'] % 3))
      self.stateDispId = self.sendHtml(stateInfo.htmlFormatString + progressMessage, self.stateDispId)

  def _waitForKernelProgress(self, seconds: int) -> None:
    self._processStateProgress({"progress": seconds, "progress_unit": "s"})


class ModelbitApiClient:
  kernelId = ""
  remoteAddress = ""

  def __init__(self, setState: Callable[[str], None], sendStatusHtml: Callable[[str], None],
               progressCb: Callable[[int], None]):
    self.sendStatusHtml = sendStatusHtml
    self.setState = setState
    self.progressCb = progressCb

  def runtimeToken(self) -> Optional[str]:
    return _runtimeToken()

  def waitForConnectionInfo(self) -> Optional[KernelInfo]:
    self.pollingOkay = True
    kernelInfo = self._connectionInfo()

    if kernelInfo is None or kernelInfo.status == "preparing":
      self.setState("finding")
      start = time.time()
      while self.pollingOkay and kernelInfo is not None and kernelInfo.status == "preparing":
        time.sleep(1)
        kernelInfo = self._connectionInfo()
        self.progressCb(round(time.time() - start))
    return kernelInfo

  def cancel(self) -> None:
    self.pollingOkay = False

  def _connectionInfo(self, forShutdown: bool = False) -> Optional[KernelInfo]:
    args = {"requestedKernelId": self.kernelId}
    if forShutdown:
      args["forShutdown"] = "true"
    resp = self._callWeb("kernel_info", args)
    if resp.error:
      raise Exception(resp.error)
    if resp.kernelInfo and resp.kernelInfo.kernelId is not None:
      self.kernelId = resp.kernelInfo.kernelId
      if resp.kernelInfo.address != "":
        self.remoteAddress = resp.kernelInfo.address or ""
        logging.info("Connecting to kernel_id=%s address=%s", resp.kernelInfo.kernelId,
                     resp.kernelInfo.address)
    return resp.kernelInfo

  def _callWeb(self, path: str, data: Dict[str, Any]) -> NotebookResponse:
    if not isAuthenticated():
      self.setState("authing")
      refreshAuthentication()
      self.sendStatusHtml(_getAuthMessage())
      self._waitForAuth()
      if not isAuthenticated():
        raise NotConnectedError()

    try:
      return getJson(f"jupyter/v1/kernel/{path}", data)
    except Exception as err:
      return NotebookResponse({"error": str(err)})

  # using warning so messages show up by default
  def logMsg(self, msg: Any) -> None:
    logging.warning(msg)  # type: ignore

  def _waitForAuth(self) -> None:
    self.logMsg("Started polling")
    maxAttempts = 120
    self.pollingOkay = True
    while self.pollingOkay and maxAttempts > 0 and not refreshAuthentication():
      self.logMsg("Not yet authed")
      time.sleep(1)
      maxAttempts -= 1

    self.logMsg("Authed!" if self.pollingOkay and maxAttempts > 0 else "Auth timed out")


class NotConnectedError(Exception):
  pass
