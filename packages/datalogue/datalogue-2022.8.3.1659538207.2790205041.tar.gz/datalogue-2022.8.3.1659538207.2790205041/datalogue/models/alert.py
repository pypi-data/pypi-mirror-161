from typing import List, Union, NamedTuple, Literal
from uuid import UUID
from datetime import datetime, timedelta
from datalogue.dtl_utils import (
    _parse_list,
    SerializableStringEnum,
)
from datalogue.errors import _enum_parse_error, DtlError
from datalogue.models import ComparisonOperator


class Metric(SerializableStringEnum):
    @staticmethod
    def parse_error(s: str) -> str:
        return _enum_parse_error("metric", s)

    @staticmethod
    def _from_payload(json: str) -> Union[DtlError, "Metric"]:
        return SerializableStringEnum.from_str(Metric)(json)

    TOTAL_RECORD_COUNT = "TotalRecordCount"
    REJECTED_RECORD_COUNT = "RejectedRecordCount"


class Comparison(NamedTuple):
    """
    Comparison(TOTAL_RECORD_COUNT, LT, 100) means
    an alert will be triggered if TotalRecordCount < 100
    """
    metric: Metric
    operator: ComparisonOperator
    value: float

    def _as_payload(self):
        return {
            "type": "Comparison",
            "metric": self.metric.value,
            "operator": self.operator.value,
            "value": self.value,
        }


class JobDuration(NamedTuple):
    """
    JobDuration(timedelta) means an alert will be
    triggered if the job runtime exceeds the specified timedelta
    """
    duration: timedelta

    def _as_payload(self):
        return {
            "type": "JobDuration",
            "durationSeconds": self.duration.total_seconds()
        }

class EmailChannel(NamedTuple):
    email: List[str]

    def _as_payload(self):
        return {
            "type": "Email",
            "email": self.email
        }


class PagerDuty(NamedTuple):
    integration_key: str

    def _as_payload(self):
        return {
            "type": "PagerDuty",
            "integrationKey": self.integration_key
        }


class SlackChannel(NamedTuple):
    webhook_url: str

    def _as_payload(self):
        return {
            "type": "Slack",
            "webhook": self.webhook_url
        }


AlertCondition = Union[Literal["JobFailure", "JobCancellation", "NoInput"], Comparison, JobDuration]
AlertChannel = Union[EmailChannel, PagerDuty, SlackChannel]


def _alert_channel_from_payload(json: dict) -> Union[DtlError, AlertChannel]:
    t = json.get("type")
    if t == "Email":
        email = json.get("email")
        if not isinstance(email, str):
            return DtlError("Email in EmailChannel should be a string")
        return EmailChannel(email)
    elif t == "PagerDuty":
        integration_key = json.get("integrationKey")
        if not isinstance(integration_key, str):
            return DtlError("Escalation policy in PagerDuty should be a string")
        return PagerDuty(
            integration_key=integration_key
        )
    elif t == "Slack":
        webhook_url = json.get("webhook")
        if not isinstance(webhook_url, str):
            return DtlError("Channel name in SlackChannel should be a string")
        return SlackChannel(webhook_url)


def _alert_condition_from_payload(json: dict) -> Union[DtlError, AlertCondition]:
    t = json.get("type")
    if t in ["JobFailure", "JobCancellation", "NoInput"]:
        return t
    elif t == "Comparison":
        metric = Metric._from_payload(json.get("metric"))
        if isinstance(metric, DtlError):
            return metric
        operator = ComparisonOperator._from_payload(json.get("operator"))
        if isinstance(operator, DtlError):
            return operator
        value = json.get("value")
        if not isinstance(value, float):
            return DtlError("Value in comparison should be a float")
        return Comparison(
            metric=metric, operator=operator, value=value
        )
    elif t == "JobDuration":
        duration_seconds = json.get("durationSeconds")
        if not isinstance(duration_seconds, int):
            return DtlError("The value of durationSeconds should be an int")
        return JobDuration(
            duration=timedelta(seconds=duration_seconds)
        )
    else:
        return DtlError("Unknown type for AlertCondition")


class Alert(NamedTuple):
    """
    :param id: ID of the alert, leave None when creating
    :param name: Name of the alert
    :param pipeline_ids: IDs of pipelines to check
    :param triggers: any of the alert conditions will trigger the alert
    :param channels: ways to be notified
    :param activated: no alerts will be sent if the alert is deactivated
    """
    id: UUID
    name: str
    pipeline_ids: List[UUID]
    triggers: List[AlertCondition]
    channels: List[AlertChannel]
    activated: bool = False

    def _as_payload(self) -> dict:
        return {
            "id": str(self.id),
            "name": self.name,
            "pipelineIds": list(map(lambda i: str(i), self.pipeline_ids)),
            "triggers": list(map(lambda t: {"type": t} if isinstance(t, str) else t._as_payload(), self.triggers)),
            "channels": list(map(lambda c: c._as_payload(), self.channels)),
            "activated": self.activated,
        }

    @staticmethod
    def _from_payload(json: dict) -> Union[DtlError, "Alert"]:
        alert_id = json.get("id")
        if alert_id is None:
            return DtlError("Alert object should have a 'id' property")
        alert_id = UUID(alert_id)

        name = json.get("name")
        if name is None:
            return DtlError("Alert object should have a 'name' property")

        pipeline_ids = json.get("pipelineIds")
        if pipeline_ids is None:
            return DtlError("Alert object should have a 'pipeline_ids' property")

        triggers = json.get("triggers")
        if triggers is None:
            return DtlError("Alert object should have a 'triggers' property")
        triggers = _parse_list(_alert_condition_from_payload)(triggers)
        channels = json.get("channels")
        if channels is None:
            return DtlError("Alert object should have a 'channels' property")
        channels = _parse_list(_alert_channel_from_payload)(channels)
        activated = json.get("activated")
        if not isinstance(activated, bool):
            return DtlError("Alert object should have a boolean 'activated' property")
        return Alert(
            id=alert_id,
            name=name,
            pipeline_ids=pipeline_ids,
            triggers=triggers,
            channels=channels,
            activated=activated,
        )
