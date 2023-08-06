import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict
from uuid import UUID

from rispack.errors import UnhandledSourceError


class RecordBuilder:
    def __init__(self, event):
        self.event = event

    def build(self):
        try:
            return self._get_record()
        except UnhandledSourceError:
            print("unhandled soruce")
            return self.event

    def _get_record(self):
        source = self._get_source()

        if source == "s3":
            file = self.event.get("s3")

            return FileRecord(
                bucket=file["bucket"]["name"],
                bucket_arn=file["bucket"]["arn"],
                key=file["object"]["key"],
                size=file["object"]["size"],
                etag=file["object"]["eTag"],
            )

        if source == "sqs":
            body = self.event["body"]

            try:
                body = json.loads(body)
            except json.JSONDecodeError:
                return body

            message = json.loads(body.get("Message"))
            isotime = message.get("at").replace("Z", "+00:00")

            return EventRecord(
                id=message.get("id"),
                aggregate_id=message.get("aggregate_id"),
                payload=message.get("payload"),
                type=message.get("type"),
                origin=message.get("origin"),
                at=datetime.fromisoformat(isotime),
                version=message.get("version"),
            )

    def _get_source(self):
        source = self.event

        try:
            return source.get("eventSource").split(":")[1]
        except Exception:
            raise UnhandledSourceError("No eventSource key found")


@dataclass
class FileRecord:
    bucket: str
    bucket_arn: str
    key: str
    size: datetime
    etag: str


@dataclass
class EventRecord:
    id: UUID
    aggregate_id: UUID
    payload: Dict[str, Any]
    type: str
    origin: str
    at: datetime
    version: str
