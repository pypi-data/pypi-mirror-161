import base64
import textwrap
import uuid
from base64 import urlsafe_b64encode
from typing import Dict, List, Optional

import click
from click import Context
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

from grid.cli import rich_click
from grid.openapi import V1CredentialType, V1Credential
from grid.sdk import env
from grid.sdk.client import create_swagger_client
from grid.sdk.credentials import (
    get_cluster_account_id,
    get_cluster_controlplane_aws_account_id,
    AWSBucketAccessSpec,
    BucketAccessCredential,
)
from grid.sdk.rest import GridRestClient
from grid.sdk.rest.credentials import create_credential, list_credentials, delete_credential
from grid.sdk.user import get_user_team_members, user_from_logged_in_account


@rich_click.group(invoke_without_command=True)
@click.pass_context
def credential(ctx: Context) -> None:
    """Manage the credentials associated with your Grid account.

    You can use these credentials to provide access to data stored in private s3 buckets.

    You can find more information about using private s3 buckets with Grid [link=https://docs.grid.ai]here[/link]
    Please note that this feature is only available to BYOC users.
    """
    if ctx.invoked_subcommand is None:
        ctx.invoke(list)


@credential.command()
@click.pass_context
@click.option(
    '--type',
    'credential_type',
    type=click.Choice(['s3']),
    default='s3',
    show_default=True,
    help='The credential type to create.',
)
@click.option(
    '--cluster',
    'cluster_id',
    type=str,
    required=False,
    default=env.CONTEXT,
    show_default=True,
    help='The cluster id where the credential will be created.',
)
@click.option(
    '--s3-external-id',
    's3_external_id',
    type=str,
    default=None,
    show_default=False,
    hidden=True,  # should only be used during testing
    help='Must be paired with `--type s3 & --s3-role-arn`',
)
@click.option(
    '--s3-role-arn',
    's3_role_arn',
    type=str,
    default=None,
    show_default=False,
    hidden=True,  # should only be used during testing
    help='Must be paired with `--type s3 & --s3-external-id`',
)
def create(
    ctx,
    credential_type: str,
    cluster_id: str,
    s3_external_id: Optional[str] = None,
    s3_role_arn: Optional[str] = None
):
    """Create a credential associated with your Grid account.

    You can use this credential to mount a Datastore from a private s3 bucket.
    """
    if credential_type == 's3':
        if s3_role_arn is not None and s3_external_id is not None:
            click.echo("skipping create credential interactive mode...")
            aws_bucket_access_spec = AWSBucketAccessSpec(
                role_arn=s3_role_arn,
                external_id=s3_external_id,
            )
        else:
            aws_bucket_access_spec = ask_user_input_to_create_s3_credential(cluster_id)
        try:
            aws_bucket_access_spec.validate()
        except ValueError as e:
            Console(width=80).print(
                f"\n[bold red]ValueError[/bold red]: {e}. This credential has "
                f"not been saved. Please rerun the last command to try again"
            )
            return
        credential = BucketAccessCredential(aws=aws_bucket_access_spec)
        created_cred = create_credential(
            c=GridRestClient(create_swagger_client()),
            cluster_id=cluster_id,
            credential_type=V1CredentialType.BUCKET_ACCESS,
            credential_value=urlsafe_b64encode(bytes(credential.to_json(), 'utf-8')).decode('utf-8'),
        )

    success_message = (
        f"\n"
        "[bold][green]Success![/bold][/green]\n"
        "\n"
        f"Your credential has been created on cluster [dim]{created_cred.cluster_id}[/dim]. It "
        f"can be referred to in the future by its ID: [dim]{created_cred.id}[/dim]. \n"
        f"\n"
        f"This can also be found in the output of [i][dim]grid credential list --cluster {created_cred.cluster_id}[/i][/dim]"
    )
    Console(width=80, highlight=False).print(success_message)


@credential.command()
@click.pass_context
@click.option(
    '--cluster',
    'cluster_id',
    type=str,
    required=False,
    default=env.CONTEXT,
    show_default=True,
    help='The cluster id where the credential will be created.',
)
@click.option(
    "--type",
    "credential_type",
    type=click.Choice(['s3']),
    required=False,
    default=None,
    show_default=True,
    help="filter credentials to list by type."
)
def list(ctx, cluster_id: str, credential_type: str):
    """List all credentials associated with your Grid account.
    """
    team_members = get_user_team_members()
    if len(team_members) == 0:
        team_members = []

    if credential_type == 's3':
        credentials = list_credentials(
            c=GridRestClient(create_swagger_client()),
            cluster_id=cluster_id,
            user_ids=[u.user_id for u in team_members] if len(team_members) == 0 else None,
            credential_type_in=V1CredentialType.BUCKET_ACCESS,
        )
    else:
        credentials = list_credentials(
            c=GridRestClient(create_swagger_client()),
            cluster_id=cluster_id,
            user_ids=[u.user_id for u in team_members] if len(team_members) == 0 else None,
        )

    user_id_name_map: Dict[str, str] = {}
    for member in team_members:
        user_id_name_map[member.user_id] = member.username

    # add current user to members list so we can find the username from id when printing creds table
    user = user_from_logged_in_account()
    user_id_name_map[user.user_id] = user.username

    print_creds_table(creds=credentials, user_id_name_map=user_id_name_map)


@credential.command()
@click.pass_context
@rich_click.argument("id", type=str, required=True, nargs=1, help="The credential ID to delete.")
@click.option(
    '--cluster',
    'cluster_id',
    type=str,
    required=False,
    default=env.CONTEXT,
    show_default=True,
    help='The cluster id where the credential will be created.',
)
def delete(ctx, id: str, cluster_id: str):
    """Use this command to delete a credential you have previously created.

    Warning: Any resource (datastore, session, experiment) which uses this credential will
    become unusable after it has been deleted.

    Please note that only the Grid user who created a credential will be able to delete it.
    """
    delete_credential(
        c=GridRestClient(create_swagger_client()),
        cluster_id=cluster_id,
        credential_id=id,
    )
    Console().print(f"[bold][green]Success![/bold][/green] Credential [dim]{id}[/dim] has been deleted.")


def print_creds_table(creds: List[V1Credential], user_id_name_map: Dict[str, str]) -> Console:
    """Prints table with cloud credentials."""
    if not creds:
        message = """
            No credentials available. Add new credentials with:

                grid credential create ...

            Or learn more by executing:

                grid credential --help
            """
        raise click.ClickException(message)

    table = Table(show_header=True, header_style="bold green")
    table.add_column("ID", style='dim')
    table.add_column('Type', justify='center')
    table.add_column('Credential', justify='center', overflow='fold')
    table.add_column('Created At', justify='center', overflow='fold')
    table.add_column('Cluster', justify='center')
    table.add_column('Owner', justify='left')

    for row in creds:
        if row.type == V1CredentialType.BUCKET_ACCESS:
            cred_value = base64.urlsafe_b64decode(row.credential).decode()
            access_credential: BucketAccessCredential = BucketAccessCredential.from_json(cred_value)
            table.add_row(
                row.id,
                "s3",
                access_credential.aws.to_json(),
                row.creation_timestamp.strftime("%a, %d %b %Y %H:%M:%S %Z"),
                row.cluster_id,
                user_id_name_map.get(row.user_id, "<unknown owner>"),
            )
        else:
            raise NotImplementedError(f"listing {row.type} credential type is not supported yet")

    console = Console()
    console.print(table)

    #  We return the console for testing purposes.
    #  This isn't actually used anywhere else.
    return console


def ask_user_input_to_create_s3_credential(cluster_id: str) -> AWSBucketAccessSpec:
    cluster_aws_account = get_cluster_account_id(cluster_id)
    controlplane_aws_account = get_cluster_controlplane_aws_account_id(cluster_id)
    generated_external_id = uuid.uuid4().hex

    if cluster_aws_account != controlplane_aws_account:
        trust_policy_principle_msg = f'''["{cluster_aws_account}", "{controlplane_aws_account}"]'''
    else:
        trust_policy_principle_msg = f'''"{cluster_aws_account}"'''

    introduction_msg = (
        "Please refer the the [link=https://docs.grid.ai]the documentation[/link] "
        "for how to create an AWS role and permission policy."
    )
    trust_policy_before_msg = "The trust policy for the role should be:"
    trust_policy_json = textwrap.dedent(
        f'''\
            {{
                "Version": "2012-10-17",
                "Statement": [
                    {{
                        "Effect": "Allow",
                        "Action": "sts:AssumeRole",
                        "Principal": {{
                            "AWS": {trust_policy_principle_msg}
                        }},
                        "Condition": {{
                            "StringEquals": {{
                                "sts:ExternalId": "{generated_external_id}"
                            }}
                        }}
                    }}
                ]
            }}
    '''
    )

    permission_policy_before_msg = "The permission policy attached to the role should be:"
    permission_policy_json = textwrap.dedent(
        f'''\
            {{
                "Version": "2012-10-17",
                "Statement": [
                    {{
                        "Effect": "Allow",
                        "Action": [
                            "s3:GetBucketLocation",
                            "s3:GetObject",
                            "s3:ListBucket"
                        ],
                        "Resource" : [
                            "arn:aws:s3:::<replace-with-bucket-name>",
                            "arn:aws:s3:::<replace-with-bucket-name>/*"
                        ]
                    }}
                ]
            }}
    '''
    )
    permission_policy_after_msg = (
        "Please be sure to change the [bold][italic]<replace-with-bucket-name>[/bold][/italic] "
        "field with the bucket name you wish to grant access to. More information can be found "
        "[link=https://docs.grid.ai]on the docs[/link]."
    )
    end_msg = (
        "[bold]Please Note[/bold]: when creating the role name in the AWS console, the role name "
        "[italic]MUST[/italic] begin with the prefix: [bold]grid-s3-access-[/bold] any valid "
        "characters can follow the prefix."
    )

    c = Console(width=80)
    c.print(introduction_msg)
    c.print("")
    c.print(trust_policy_before_msg)
    c.print_json(trust_policy_json)
    c.print("")
    c.print(permission_policy_before_msg)
    c.print_json(permission_policy_json)
    c.print("")
    c.print(permission_policy_after_msg)
    c.print("")
    c.print(end_msg)
    c.print("")
    role_arn = Prompt.ask("[cyan]When complete, please enter the role ARN[/cyan]")

    return AWSBucketAccessSpec(role_arn=role_arn, external_id=generated_external_id)
