from typing import Union, Optional, List
from uuid import UUID

from datalogue.models.permission import (
    Permission,
    SharePermission,
    UnsharePermission,
    ObjectType,
    Scope,
)
from datalogue.clients._http import _HttpClient, HttpMethod
from datalogue.errors import DtlError
from datalogue.models.alert import (Alert)
from datalogue.dtl_utils import _parse_list


class _AlertClient:
    """
    Client to interact with the Authentication Schemes
    """

    def __init__(self, http_client: _HttpClient):
        self.http_client = http_client
        self.service_uri = "/scout"

    def create(self, alert: Alert) -> Union[DtlError, Alert]:
        res = self.http_client.make_authed_request(
            self.service_uri + "/alerts", HttpMethod.POST, alert._as_payload()
        )
        if isinstance(res, DtlError):
            return res

        return Alert._from_payload(res)

    def update(self, alert: Alert) -> Union[DtlError, Alert]:
        res = self.http_client.make_authed_request(
            self.service_uri + "/alerts/" + str(alert.id), HttpMethod.PUT, alert._as_payload()
        )
        if isinstance(res, DtlError):
            return res

        return Alert._from_payload(res)

    def delete(self, alert_id: UUID) -> Optional[DtlError]:
        res = self.http_client.make_authed_request(
            self.service_uri + "/alerts/" + str(alert_id), HttpMethod.DELETE
        )
        if isinstance(res, DtlError):
            return res
        return None

    def activate(self, alert_id: UUID) -> Union[DtlError, Alert]:
        return self._toggle_activate(alert_id, activated=True)

    def deactivate(self, alert_id: UUID) -> Union[DtlError, Alert]:
        return self._toggle_activate(alert_id, activated=False)

    def test(self, alert_id: UUID) -> Optional[DtlError]:
        command = "/test"
        res = self.http_client.make_authed_request(
            self.service_uri + "/alerts/" + str(alert_id) + command, HttpMethod.POST
        )
        if isinstance(res, DtlError):
            return res
        return None

    def _toggle_activate(self, alert_id: UUID, activated: bool) -> Union[DtlError, Alert]:
        res = self.http_client.make_authed_request(
            self.service_uri + "/alerts/" + str(alert_id), HttpMethod.PATCH, {"activated": activated}
        )
        if isinstance(res, DtlError):
            return res

        return Alert._from_payload(res)

    def get(self, alert_id: UUID) -> Union[DtlError, Alert]:
        res = self.http_client.make_authed_request(
            self.service_uri + "/alerts/" + str(alert_id), HttpMethod.GET
        )
        if isinstance(res, DtlError):
            return res

        return Alert._from_payload(res)

    def list(self, page: int = 1, item_per_page: int = 25) -> Union[DtlError, List[Alert]]:
        """
        Retrieves a paginated array of alerts

        :param page: page of alert list to return
        :param item_per_page: number of alerts to return per page
        :return: Array of alerts if successful, DtlError if failed
        """
        params = {"page": str(page), "size": str(item_per_page)}

        res = self.http_client.make_authed_request(
            f"{self.service_uri}/alerts", HttpMethod.GET, params=params
        )

        if isinstance(res, DtlError):
            return DtlError(f"Encountered an error while listing alerts", res)
        entities = res["entities"]
        return _parse_list(Alert._from_payload)(entities)

    def share(
            self, alert_id: UUID, target_id: UUID, target_type: Scope, permission: Permission
    ) -> Union[SharePermission, DtlError]:
        url = f"{self.service_uri}/alerts/{str(alert_id)}/shares?targetType={str(target_type.value)}" \
              f"&targetId={str(target_id)}&permission={str(permission.value)}"
        rsp = self.http_client.execute_authed_request(url, HttpMethod.POST)

        if isinstance(rsp, DtlError):
            return rsp
        elif rsp.status_code == 200:
            return SharePermission(object_type=ObjectType.Alert).from_payload(rsp.json())
        else:
            return DtlError(rsp.text)

    def unshare(
            self, id: UUID, target_id: UUID, target_type: Scope, permission: Permission
    ) -> Union[UnsharePermission, DtlError]:
        """
        Withdraws Permissions for Alerts with another User or Group

        :param id: id of Alert to be unshared
        :param target_type: User or Group, as an enumeration of Scope
        :param target_id: id of the Permission-withdrawn User or Group
        :param permission: level of Permissions to unshare (Read, Write, or Share), as an enumeration of Permission
        :return: UnsharePermission if successful, DtlError if failed
        """

        url = f"{self.service_uri}/alerts/{str(id)}/shares?targetType={str(target_type.value)}" \
              f"&targetId={str(target_id)}&permission={str(permission.value)}"
        rsp = self.http_client.execute_authed_request(url, HttpMethod.DELETE)

        if isinstance(rsp, DtlError):
            return rsp
        elif rsp.status_code == 200:
            return UnsharePermission(object_type=ObjectType.Alert).from_payload(rsp.json())
        else:
            return DtlError(rsp.text)
