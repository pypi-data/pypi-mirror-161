from typing import List

from .helpers import GenericWarehouse, getJsonOrPrintError, isAuthenticated
from .utils import timeago
from .ux import makeHtmlTable, TableHeader


class WarehousesList:

  def __init__(self):
    self._warehouses: List[GenericWarehouse] = []
    resp = getJsonOrPrintError("jupyter/v1/warehouses/list")
    if resp and resp.warehouses:
      self._warehouses = resp.warehouses

  def _repr_html_(self):
    if not isAuthenticated():
      return ""
    return self._makeWarehousesHtmlTable()

  def _makeWarehousesHtmlTable(self):
    if len(self._warehouses) == 0:
      return ""
    headers = [
        TableHeader("Name", TableHeader.LEFT),
        TableHeader("Type", TableHeader.LEFT),
        TableHeader("Connected", TableHeader.LEFT),
        TableHeader("Deploy Status", TableHeader.LEFT),
    ]
    rows: List[List[str]] = []
    for w in self._warehouses:
      connectedAgo = timeago(w.createdAtMs)
      rows.append([w.displayName, str(w.type), connectedAgo, w.deployStatusPretty])
    return makeHtmlTable(headers, rows)


def list():
  return WarehousesList()