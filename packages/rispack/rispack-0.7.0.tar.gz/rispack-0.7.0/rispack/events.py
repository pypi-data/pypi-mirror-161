import json
import os
from abc import abstractmethod
from datetime import datetime
from uuid import uuid4

import boto3

from rispack.errors import EventBusNotSetError
from rispack.logger import logger
from rispack.schemas import BaseSchema


class BaseEvent(BaseSchema):
    @abstractmethod
    def get_type(self):
        raise NotImplementedError

    @abstractmethod
    def get_version(self):
        raise NotImplementedError

    @abstractmethod
    def get_aggregate_id(self):
        raise NotImplementedError

    def publish(self):
        client = boto3.client("sns")

        payload = self.dump()
        event_type = self.get_type()
        aggregate_id = self.get_aggregate_id()
        version = self.get_version()

        origin = "".join(["rispar", ".", os.environ.get("SERVICE_NAME", "platform")])
        event_bus = os.environ.get("EVENT_BUS")
        aws_region = os.environ.get("AWS_REGION")
        aws_account_id = os.environ.get("AWS_ACCOUNT_ID")

        if not event_bus:
            raise EventBusNotSetError

        arn = f"arn:aws:sns:{aws_region}:" f"{aws_account_id}" f":{event_bus}"

        message = json.dumps(
            {
                "id": str(uuid4()),
                "origin": origin,
                "type": event_type,
                "at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                "aggregate_id": str(aggregate_id),
                "version": version,
                "payload": payload,
            }
        )

        response = client.publish(
            TargetArn=arn,
            Message=message,
            MessageStructure="string",
            MessageAttributes={
                "event_type": {"DataType": "String", "StringValue": event_type},
                "event_origin": {"DataType": "String", "StringValue": origin},
            },
        )

        logger.info(
            {
                "logtype": "EVENT_PUBLISHED",
                "message": {
                    "type": event_type,
                    "origin": origin,
                    "aggregate_id": aggregate_id,
                },
            }
        )

        return response
