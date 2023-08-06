""" Utilities for storage backends

Provides
--------
- Initalize an S3 bucket for ARD delivery
- Revoke ARD delivery access from an S3 bucket

Example
-------
Initialize a bucket

>>> init_bucket('my-data-bucket')

Revoke access

>>> revoke_bucket('my-data-bucket')
"""
import json
import sys

import boto3
import botocore

from max_ard.exceptions import BucketInitError, BucketRevokeError


def init_bucket(location, profile=None):
    """Set up an S3 bucket for ARD delivery

    Parameters
    ----------
    location : str
        bucket name
    profile : str, optional
        name of S3 profile to use for access

    Notes
    -----
    If the bucket does not exist, it will be created.

    This adds the required bucket policy statement to the bucket granting the ARD API
    to write objects to the bucket. No other access is granted.

    This also changes the bucket's Object Ownership policy to "Owner Preferred", which
    transfers the ownership of ARD objects to the bucket owner instead of the ARD API."""

    location = location.replace("s3://", "")
    if profile is None:
        s3_resource = boto3.resource("s3")
        s3_client = boto3.client("s3")
    else:
        session = boto3.Session(profile_name=profile)
        s3_resource = session.resource("s3")
        s3_client = session.client("s3")
    # check if the bucket exists
    try:
        s3_resource.meta.client.head_bucket(Bucket=location)
        print(f"Bucket exists at {location}")
    except botocore.exceptions.ClientError as e:
        if "403" in str(e):
            msg = "That bucket name already exists in AWS. If you made the bucket, your user does not have permission to see it"
            raise BucketInitError(msg)
        try:
            s3_resource.create_bucket(Bucket=location)
            print(f'Created bucket "{location}"')
        except botocore.exceptions.ClientError as e:
            if "ExpiredToken" in str(e):
                msg = "Your AWS token has expired, please request a new token"
                raise BucketInitError(msg)
            else:
                raise e
        except botocore.errorfactory.BucketAlreadyExists:
            msg = "That bucket name already exists in AWS, try a different name"
            raise BucketInitError(msg)
    authorized = False
    try:
        policy = json.loads(s3_client.get_bucket_policy(Bucket=location)["Policy"])
    except botocore.exceptions.ClientError:
        policy = {"Version": "2012-10-17", "Statement": []}
    for statement in policy["Statement"]:
        if statement["Sid"] == "MaxarArdS3Access":
            authorized = True
            break
    if not authorized:
        statement = {
            "Sid": "MaxarARDS3Access",
            "Effect": "Allow",
            "Principal": {"AWS": "arn:aws:iam::334489843805:root"},
            "Action": "s3:PutObject",
            "Resource": [f"arn:aws:s3:::{location}/*", f"arn:aws:s3:::{location}"],
        }
        policy["Statement"].append(statement)
        s3_client.put_bucket_policy(Bucket=location, Policy=json.dumps(policy))
        print("Added ARD writer policy to bucket")
    else:
        print("Bucket already authorized")
    response = s3_client.put_bucket_ownership_controls(
        Bucket=location,
        OwnershipControls={
            "Rules": [
                {"ObjectOwnership": "BucketOwnerPreferred"},
            ]
        },
    )
    print("Object Ownership set to Bucket Owner Preferred")


def revoke_bucket(location, profile=None):
    """Revoke ARD API write access to a bucket

    Parameters
    ----------
    location : str
        bucket name
    profile : str, optional
        name of S3 profile to use for access

    Notes
    -----
    This removes the required bucket policy statement from the bucket granting the ARD API
    to write objects to the bucket.

    This does not change the bucket's Object Ownership policy."""

    location = location.replace("s3://", "")
    if profile is None:
        s3_resource = boto3.resource("s3")
        s3_client = boto3.client("s3")
    else:
        session = boto3.Session(profile_name=profile)
        s3_resource = session.resource("s3")
        s3_client = session.client("s3")

    # check if the bucket exists
    try:
        s3_resource.meta.client.head_bucket(Bucket=location)
    except botocore.exceptions.ClientError:
        msg = "Either this bucket does not exist or you do not have permission to access it"
        raise BucketRevokeError(msg)
    try:
        policy = json.loads(s3_client.get_bucket_policy(Bucket=location)["Policy"])
    except botocore.exceptions.ClientError:
        msg = "Bucket has no policy statements - nothing to revoke"
        raise BucketRevokeError(msg)
    statements = []
    for statement in policy["Statement"]:
        if statement["Sid"] != "MaxarARDS3Access":
            statements.append(statement)
    if len(statements) < len(policy["Statement"]):
        if len(statements) == 0:
            s3_client.delete_bucket_policy(Bucket=location)
        else:
            policy["Statement"] = statements
            s3_client.put_bucket_policy(Bucket=location, Policy=json.dumps(policy))
        print("Removed ARD writer policy from bucket")
    else:
        msg = "Could not find ARD writer policy in bucket"
        raise BucketRevokeError(msg)
