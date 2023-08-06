from grid.openapi import (
    ApiClient, AuthServiceApi, ClusterServiceApi, DatastoreServiceApi, RunServiceApi, SAMLOrganizationsServiceApi,
    SessionServiceApi, TensorboardServiceApi, ExperimentServiceApi, CredentialServiceApi
)


class GridRestClient(
    AuthServiceApi, ClusterServiceApi, DatastoreServiceApi, RunServiceApi, SAMLOrganizationsServiceApi,
    SessionServiceApi, TensorboardServiceApi, ExperimentServiceApi, CredentialServiceApi
):
    api_client: ApiClient

    def __init__(self, api_client: ApiClient):  # skipcq: PYL-W0231
        self.api_client = api_client
