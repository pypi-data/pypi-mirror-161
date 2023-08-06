import click
from click_plugins import with_plugins
from pkg_resources import iter_entry_points

from vgscli.api import create_account_mgmt_api, create_vault_mgmt_api
from vgscli.errors import handle_errors
from vgscli.serializers import dump_camelized_yaml
from vgscli.utils import read_file


@with_plugins(iter_entry_points("vgs.generate.plugins"))
@click.group("generate")
def generate() -> None:
    """
    Output a VGS resource template. Edited templates can be applied with a
    corresponding command.
    """
    pass


@generate.command("vault")
@handle_errors()
def generate_vault() -> None:
    """
    Output a vault template.
    """
    click.echo(read_file("templates/vault-template.yaml"), nl=False)


@generate.command("access-credentials")
@click.option("--vault", "-V", help="Vault ID", required=True)
@click.pass_context
@handle_errors()
def generate_access_credentials(ctx, vault):
    """
    Generate a VGS access-credential
    """
    account_mgmt = create_account_mgmt_api(ctx)

    response = account_mgmt.vaults.get_by_id(vault)

    vault_mgmt = create_vault_mgmt_api(
        ctx, response.body["data"][0]["links"]["vault_management_api"]
    )

    response = vault_mgmt.credentials.create(headers={"VGS-Tenant": vault})

    click.echo(
        dump_camelized_yaml(
            {
                "apiVersion": "1.0.0",
                "kind": "AccessCredentials",
                "data": response.body["data"],
            }
        )
    )
