from typing import Optional, List

from grid.openapi import (
    V1Credential,
    V1CreateCredentialRequest,
    V1CredentialType,
)
from grid.sdk.rest import GridRestClient
from grid.sdk.rest.exceptions import throw_with_message


@throw_with_message
def create_credential(
    c: GridRestClient,
    cluster_id: str,
    credential_type: V1CredentialType,
    credential_value: str,
) -> V1Credential:
    """Create a credential
    """
    resp = c.credential_service_create_credential(
        credential_cluster_id=cluster_id,
        body=V1CreateCredentialRequest(
            credential=V1Credential(
                cluster_id=cluster_id,
                type=credential_type,
                credential=credential_value,
            )
        )
    )
    return resp


@throw_with_message
def list_credentials(
    c: GridRestClient,
    cluster_id: str,
    user_ids: Optional[List[str]] = None,
    credential_type_in: Optional[List[V1CredentialType]] = None,
    credential_type_not_in: Optional[List[V1CredentialType]] = None,
) -> List[V1Credential]:
    """List all credentials fitting the filter criteria.
    """
    credentials: List[V1Credential] = []

    kwargs = {}
    if user_ids is not None:
        kwargs['user_ids'] = user_ids
    if credential_type_in is not None:
        kwargs['credential_type_in'] = credential_type_in
    if credential_type_not_in is not None:
        kwargs['credential_type_not_in'] = credential_type_not_in

    # loop until we recieve all credentials (and not just the max page size limit enforced by the backend)
    done_once, continuation_token = False, ""
    while (done_once is False) and (continuation_token == ""):
        done_once = True
        if continuation_token != "":
            kwargs['page_token'] = continuation_token

        resp = c.credential_service_list_credentials(
            cluster_id=cluster_id,
            **kwargs,
        )
        continuation_token = resp.next_page_token
        credentials.extend(resp.credentials)

    return credentials


@throw_with_message
def delete_credential(
    c: GridRestClient,
    cluster_id: str,
    credential_id: str,
) -> None:
    """Delete a credential, raising exception on failure.
    """
    c.credential_service_delete_credential(
        id=credential_id,
        cluster_id=cluster_id,
    )
