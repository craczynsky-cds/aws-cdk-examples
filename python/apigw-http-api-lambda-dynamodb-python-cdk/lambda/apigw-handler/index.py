# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import boto3
import os
import json
import logging
import uuid
from datetime import datetime
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

# Patch all supported libraries for X-Ray tracing
patch_all()

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb_client = boto3.client("dynamodb")


def log_event(level, message, context, **kwargs):
    """Helper function for structured logging"""
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "level": level,
        "message": message,
        "function_name": os.environ.get("AWS_LAMBDA_FUNCTION_NAME"),
        "request_id": context.request_id if context else None,
        **kwargs
    }
    logger.info(json.dumps(log_entry))


def handler(event, context):
    table = os.environ.get("TABLE_NAME")
    
    log_event("INFO", "Processing request", context, table_name=table)
    
    if event["body"]:
        item = json.loads(event["body"])
        log_event("INFO", "Received payload", context, payload=item)
        
        year = str(item["year"])
        title = str(item["title"])
        id = str(item["id"])
        
        dynamodb_client.put_item(
            TableName=table,
            Item={"year": {"N": year}, "title": {"S": title}, "id": {"S": id}},
        )
        
        log_event("INFO", "Successfully inserted data", context, item_id=id)
        
        message = "Successfully inserted data!"
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": message}),
        }
    else:
        log_event("INFO", "Received request without payload, using default data", context)
        
        default_id = str(uuid.uuid4())
        dynamodb_client.put_item(
            TableName=table,
            Item={
                "year": {"N": "2012"},
                "title": {"S": "The Amazing Spider-Man 2"},
                "id": {"S": default_id},
            },
        )
        
        log_event("INFO", "Successfully inserted default data", context, item_id=default_id)
        
        message = "Successfully inserted data!"
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": message}),
        }
