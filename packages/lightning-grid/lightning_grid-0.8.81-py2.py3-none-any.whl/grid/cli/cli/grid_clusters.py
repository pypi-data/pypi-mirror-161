import asyncio
from datetime import datetime
import json
import re
import time
from typing import List

import arrow
import click
from rich.table import Table
from rich.text import Text

from grid.cli import rich_click

# Not sure why we have this import Console
# When I import it normally from rich I have
# import issues
from grid.cli.cli.utilities import create_openapi_object, string2dict
from grid.cli.core.callbacks import arrow_time_callback
from grid.cli.core.formatter import Formatable, print_to_console
from grid.openapi import (
    Externalv1Cluster,
    V1AWSClusterDriverSpec,
    V1ClusterDriver,
    V1ClusterPerformanceProfile,
    V1ClusterSpec,
    V1ClusterState,
    V1ClusterType,
    V1CreateClusterRequest,
    V1InstanceSpec,
    V1KubernetesClusterDriver,
)
from grid.openapi.api import cluster_service_api
from grid.sdk.client import create_swagger_client, create_websocket_client
from grid.websocket.model import ClusterLogsRequest
from grid.websocket.service import ClusterService

CLUSTER_STATE_CHECKING_TIMEOUT = 60
MAX_CLUSTER_WAIT_TIME = 5400


class ClusterList(Formatable):
    def __init__(self, clusters: [Externalv1Cluster]):
        self.clusters = clusters

    def as_json(self) -> str:
        return json.dumps(self.clusters)

    def as_table(self) -> Table:
        table = Table("id", "name", "type", "status", "created", show_header=True, header_style="bold green")
        phases = {
            V1ClusterState.QUEUED: Text("queued", style="bold yellow"),
            V1ClusterState.PENDING: Text("pending", style="bold yellow"),
            V1ClusterState.RUNNING: Text("running", style="bold green"),
            V1ClusterState.FAILED: Text("failed", style="bold red"),
            V1ClusterState.DELETED: Text("deleted", style="bold red"),
        }

        cluster_type_lookup = {
            V1ClusterType.BYOC: Text("byoc", style="bold yellow"),
            V1ClusterType.GLOBAL: Text("grid-cloud", style="bold green"),
        }
        for cluster in self.clusters:
            cluster: Externalv1Cluster
            status = phases[cluster.status.phase]
            if cluster.spec.desired_state == V1ClusterState.DELETED \
                    and cluster.status.phase != V1ClusterState.DELETED:
                status = Text("terminating", style="bold red")

            # this guard is necessary only until 0.3.93 releases which includes the `created_at`
            # field to the external API
            created_at = datetime.now()
            if hasattr(cluster, "created_at"):
                created_at = cluster.created_at

            table.add_row(
                cluster.id,
                cluster.name,
                cluster_type_lookup.get(cluster.spec.cluster_type, Text("unknown", style="red")),
                status,
                arrow.get(created_at).humanize() if created_at else "",
            )
        return table


@rich_click.group(invoke_without_command=True)
@click.pass_context
def clusters(ctx: click.Context) -> None:
    if ctx.invoked_subcommand is not None:
        return

    api_client = create_swagger_client()
    cluster_api = cluster_service_api.ClusterServiceApi(api_client)
    resp = cluster_api.cluster_service_list_clusters(phase_not_in=[V1ClusterState.DELETED])
    print_to_console(ctx, ClusterList(resp.clusters if resp.clusters else []))


default_instance_types = [
    "g2.8xlarge",
    "g3.16xlarge",
    "g3.4xlarge",
    "g3.8xlarge",
    "g3s.xlarge",
    "g4dn.12xlarge",
    "g4dn.16xlarge",
    "g4dn.2xlarge",
    "g4dn.4xlarge",
    "g4dn.8xlarge",
    "g4dn.metal",
    "g4dn.xlarge",
    "p2.16xlarge",
    "p2.8xlarge",
    "p2.xlarge",
    "p3.16xlarge",
    "p3.2xlarge",
    "p3.8xlarge",
    "p3dn.24xlarge",
    # "p4d.24xlarge",  # currently not supported
    "t2.large",
    "t2.medium",
    "t2.xlarge",
    "t2.2xlarge",
    "t3.large",
    "t3.medium",
    "t3.xlarge",
    "t3.2xlarge",
]


def _check_cluster_name_is_valid(_ctx, _param, value):
    pattern = r"^(?!-)[a-z0-9-]{1,63}(?<!-)$"
    if not re.match(pattern, value):
        raise click.ClickException(
            f"cluster name doesn't match regex pattern {pattern}\nIn simple words, use lowercase letters, numbers, and occasional -"
        )
    return value


# https://docs.grid.ai/platform/known-issues#byoc
UNSUPPORTED_ARCHITECTURES = ["a1", "t4g", "m6g", "c6g", "g5g", "r6g"]


def assert_instance_types_are_supported(instance_types: List[str]):
    # Checking for unsupported architectures in instance types
    #   https://docs.grid.ai/platform/known-issues#byoc

    unsupported = [
        instance_type for instance_type in instance_types
        if any(instance_type.startswith(arch) for arch in UNSUPPORTED_ARCHITECTURES)
    ]

    if unsupported:
        raise click.ClickException(
            f"Instance types {', '.join(unsupported)} are not supported due to their architecture. "
            f"Currently we do not support following architectures {', '.join(UNSUPPORTED_ARCHITECTURES)}. "
            f"Please choose supported instance type."
        )


@clusters.command()
@click.argument('name', type=str, callback=_check_cluster_name_is_valid)
@click.option('--external-id', 'external_id', type=str, required=True)
@click.option(
    '--role-arn', 'role_arn', type=str, required=True, help="AWS role ARN attached to`the associated resources."
)
@click.option(
    '--region',
    'region',
    type=str,
    required=False,
    default="us-east-1",
    help="AWS region which is used to host the associated resources."
)
@click.option(
    '--instance-types',
    'instance_types',
    type=str,
    required=False,
    default=",".join(default_instance_types),
    help="Instance types which you desire to support for computer jobs within the cluster."
)
@click.option(
    '--cost-savings',
    'cost_savings',
    type=bool,
    required=False,
    default=False,
    is_flag=True,
    help='using this flag ensures that the cluster is created with a profile that is optimized for '
    'cost saving, making runs cheaper but start-up times may increase',
)
@click.option(
    '--wait',
    'wait',
    type=bool,
    required=False,
    default=False,
    is_flag=True,
    help='using this flag CLI will wait until the cluster is running',
)
@click.option(
    '--edit-before-creation',
    default=False,
    is_flag=True,
    help="Edit the created cluster spec before submitting to API server."
)
def aws(
    name: str,
    external_id: str,
    role_arn: str,
    region: str,
    instance_types: str,
    edit_before_creation: bool,
    cost_savings: bool,
    wait: bool,
) -> None:
    """Create a grid compute cluster with NAME from the provided AWS account details."""
    performance_profile = V1ClusterPerformanceProfile.DEFAULT
    if cost_savings:
        performance_profile = V1ClusterPerformanceProfile.COST_SAVING

    api_client = create_swagger_client()
    cluster_api = cluster_service_api.ClusterServiceApi(api_client)
    driver = V1ClusterDriver(
        kubernetes=V1KubernetesClusterDriver(
            aws=V1AWSClusterDriverSpec(
                region=region,
                role_arn=role_arn,
                external_id=external_id,
                instance_types=[V1InstanceSpec(name=x) for x in instance_types.split(",")]
            )
        )
    )
    spec = V1ClusterSpec(cluster_type=V1ClusterType.BYOC, performance_profile=performance_profile, driver=driver)
    body = V1CreateClusterRequest(name=name, spec=spec)

    new_body = body
    if edit_before_creation:
        after = click.edit(json.dumps(body.to_dict(), indent=4))
        if after is not None:
            new_body = create_openapi_object(string2dict(after), body)
        if new_body == body:
            click.echo("cluster unchanged")

    # Check if instance types are supported -> Throws Excetpion
    # instance_types = new_body.spec.driver.kubernetes.aws.instance_types
    assert_instance_types_are_supported([i.name for i in new_body.spec.driver.kubernetes.aws.instance_types])

    resp = cluster_api.cluster_service_create_cluster(body=new_body)

    if wait:
        api_client = create_swagger_client()
        cluster_api = cluster_service_api.ClusterServiceApi(api_client)
        start = time.time()
        elapsed = 0
        while elapsed < MAX_CLUSTER_WAIT_TIME:
            cluster_resp = cluster_api.cluster_service_list_clusters(phase_not_in=[V1ClusterState.DELETED])
            new_cluster = None
            for clust in cluster_resp.clusters:
                if clust.id == resp.id:
                    new_cluster = clust
                    break
            if new_cluster is not None:
                if new_cluster.status.phase == V1ClusterState.RUNNING:
                    break
                elif new_cluster.status.phase == V1ClusterState.FAILED:
                    raise click.ClickException(f"Creation failed for cluster {resp.id}")
                time.sleep(CLUSTER_STATE_CHECKING_TIMEOUT)
            elapsed = time.time() - start
        else:
            raise click.ClickException(f"Max time for cluster creation is elapsed")

    click.echo(resp.to_str())


# TODO(nmiculinic): refactor this to be under `grid logs`
# Though I don't want to break existing workflows...
@clusters.command()
@click.argument('cluster_id', type=str, callback=_check_cluster_name_is_valid)
@click.option("-t", "--tail", is_flag=True, default=False, help="whether to tail log lines")
@click.option(
    "--from",
    "from_time",
    default="24 hours ago",
    help="The starting timestamp to query cluster logs from.",
    callback=arrow_time_callback
)
@click.option(
    "--to",
    "to_time",
    default="0 seconds ago",
    callback=arrow_time_callback,
    help="The end timestamp / relative time increment to query logs for. This is ignored when tailing logs."
)
@click.option("--limit", default=1000, help="The max number of log lines returned.")
@click.option(
    "--time-format",
    default="iso8601",
    type=click.Choice(['human', 'iso8601'], case_sensitive=False),
    help="Timestamp formatting style",
)
def logs(time_format: str, limit: int, to_time: arrow.Arrow, from_time: arrow.Arrow, tail: bool, cluster_id: str):
    """Retrieve cluster logs from the managed cluster identified by CLUSTER_ID.

    These logs are streamed to stdout, and can either be tailed to view log
    lines as they are generated, or limited to a time range.
    """
    ws_client = create_websocket_client()
    cluster_service = ClusterService(ws_client)
    req = ClusterLogsRequest(
        cluster_id=cluster_id, follow=tail, start=from_time.int_timestamp, end=to_time.int_timestamp, limit=limit
    )
    for log_entry in cluster_service.cluster_logs(req):
        timestamp = arrow.get(log_entry.timestamp)
        if time_format == "human":
            timestamp_part = click.style("{:>15}".format(timestamp.humanize()), fg='green')
        elif time_format == "iso8601":
            timestamp_part = click.style(timestamp.format("YYYY-MM-DD HH:mm:ss"), fg='green')
        else:
            raise click.ClickException(f"Unknown time format: got {time_format}, valid entries: [human,iso8601]")
        log_level = click.style(log_entry.level, fg='magenta')
        message_part = log_entry.message.rstrip()
        click.echo(f"[{timestamp_part}] [{log_level}]: {message_part}")
