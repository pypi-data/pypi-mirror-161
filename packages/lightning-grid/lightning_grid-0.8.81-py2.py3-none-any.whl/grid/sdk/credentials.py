from dataclasses import dataclass, field
from datetime import date
from typing import Optional

import dateutil.parser
from dataclasses_json import dataclass_json, LetterCase, config
from dataclasses_json.mm import _IsoField

from grid.sdk import env
from grid.sdk.client import create_swagger_client
from grid.sdk.rest import GridRestClient
from grid.sdk.rest.exceptions import throw_with_message
from grid.sdk.utils.arnparser import arnparse, MalformedArnError


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class AWSBucketAccessSpec:
    role_arn: str
    external_id: str

    def validate(self):
        """Raises ValueError if the values are not valid for the bucket access spec.
        """
        if self.role_arn == "":
            raise ValueError("role_arn cannot be empty string")

        if self.external_id == "":
            raise ValueError("external_id cannot be empty string")

        try:
            arn = arnparse(self.role_arn)
        except MalformedArnError as e:
            raise ValueError(
                f"the role_arn: {self.role_arn} is not a valid AWS ARN. Please refer to "
                f"https://docs.aws.amazon.com/general/latest/gr/aws-arns-and-namespaces.html "
                f"for what a valid value looks like"
            ) from e

        if not arn.resource.startswith("grid-s3-access-"):
            raise ValueError(
                f"role_arn `{self.role_arn}` resource-id value `{arn.resource}` role "
                f"name does not start with the required prefix `grid-s3-access-`"
            )

        if arn.resource == "grid-s3-access-":
            raise ValueError(
                f"role_arn `{self.role_arn}` resource-id value `{arn.resource}` suffix must "
                f"consist of atleast one character after the required prefix `grid-s3-access-`"
            )


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class GCPBucketAccessSpec:
    pass


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class AzureBucketAccessSpec:
    pass


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class BucketAccessCredential:
    # one_of field
    aws: Optional[AWSBucketAccessSpec] = field(
        default=None,
        metadata=config(exclude=lambda x: x is None),
    )
    # one_of field
    gcp: Optional[GCPBucketAccessSpec] = field(
        default=None,
        metadata=config(exclude=lambda x: x is None),
    )
    # one_of field
    azure: Optional[AzureBucketAccessSpec] = field(
        default=None,
        metadata=config(exclude=lambda x: x is None),
    )

    # protobuf json serialization encodes/decodes to RFC 3339 format
    # see https://pkg.go.dev/google.golang.org/protobuf/types/known/timestamppb#Timestamp
    creation_timestamp: Optional[date] = field(
        default=None,
        metadata=config(
            encoder=lambda x: x.strftime('%Y-%m-%dT%H:%M:%S.%fZ') if x is not None else None,
            decoder=lambda x: dateutil.parser.parse(x) if x is not None else None,
            mm_field=_IsoField(),
            exclude=lambda x: x is None,
        )
    )
    # protobuf json serialization encodes/decodes to RFC 3339 format
    # see https://pkg.go.dev/google.golang.org/protobuf/types/known/timestamppb#Timestamp
    update_timestamp: Optional[date] = field(
        default=None,
        metadata=config(
            encoder=lambda x: x.strftime('%Y-%m-%dT%H:%M:%S.%fZ') if x is not None else None,
            decoder=lambda x: dateutil.parser.parse(x) if x is not None else None,
            mm_field=_IsoField(),
            exclude=lambda x: x is None,
        )
    )
    # protobuf json serialization encodes/decodes to RFC 3339 format
    # see https://pkg.go.dev/google.golang.org/protobuf/types/known/timestamppb#Timestamp
    deletion_timestamp: Optional[date] = field(
        default=None,
        metadata=config(
            encoder=lambda x: x.strftime('%Y-%m-%dT%H:%M:%S.%fZ') if x is not None else None,
            decoder=lambda x: dateutil.parser.parse(x) if x is not None else None,
            mm_field=_IsoField(),
            exclude=lambda x: x is None,
        )
    )

    phase: Optional[str] = field(
        default=None,
        metadata=config(exclude=lambda x: x is None),
    )
    reason: Optional[str] = field(
        default=None,
        metadata=config(exclude=lambda x: x is None),
    )
    message: Optional[str] = field(
        default=None,
        metadata=config(exclude=lambda x: x is None),
    )
    retry_count: Optional[int] = field(
        default=None,
        metadata=config(exclude=lambda x: x is None),
    )

    def name(self):
        if self.aws is not None:
            return arnparse(self.aws.role_arn).resource
        elif self.gcp is not None:
            raise NotImplementedError("gcp credentials are not currently supported")
        elif self.azure is not None:
            raise NotImplementedError("gcp credentials are not currently supported")
        else:
            raise RuntimeError("internal error occured - no provider access credential specified")


@throw_with_message
def get_cluster_account_id(cluster_id: str) -> str:
    c = GridRestClient(create_swagger_client())
    resp = c.cluster_service_get_cluster_cloud_provider_account_id(id=cluster_id)
    return resp.account_id


def get_cluster_controlplane_aws_account_id(cluster_id: str) -> str:
    """get the aws account principle which the controlplane assumes when making requests

    TODO
    ----
    This is a dummy method right now. Actually implement a way to get this from the backend!

    Since there's no easy way to get the account id of the grid-role principle account
    the controlplane assumes, we're going to hardcode this to the byoc-sandbox and grid-ai
    AWS accounts for staging/testing/prod. This isn't a problem until we have on-prem
    controlplane deployments as all BYOC clusters use the same aws principle account (i.e. ours!)
    """
    if env.TESTING or cluster_id == 'staging-3':
        return "158793097533"  # byoc-sandbox

    return "302180240179"  # grid-ai
